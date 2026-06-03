"""
3D 乳腺建模服务

支持 DICOM 影像导入、三维重建、模型导出
"""
import os
import io
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json


class Breast3DReconstructionService:
    """乳腺 3D 重建服务"""
    
    def __init__(self, workspace_dir: str = "/workspace/breast-ai-system/data/3d_models"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # DICOM 标签映射
        self.dicom_tags = {
            "PatientName": "患者姓名",
            "PatientID": "患者 ID",
            "StudyDate": "检查日期",
            "Modality": "影像类型",
            "Manufacturer": "设备厂商",
            "SliceThickness": "层厚",
            "PixelSpacing": "像素间距",
        }
    
    async def import_dicom_series(
        self,
        dicom_files: List[str],
        patient_id: int,
        ultrasound_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        导入 DICOM 序列
        
        Args:
            dicom_files: DICOM 文件路径列表
            patient_id: 患者 ID
            ultrasound_id: 超声检查 ID（可选）
            
        Returns:
            导入结果
        """
        try:
            import pydicom
        except ImportError:
            return {
                "success": False,
                "error": "未安装 pydicom 库，请执行：pip install pydicom",
            }
        
        if not dicom_files:
            return {"success": False, "error": "未提供 DICOM 文件"}
        
        # 排序 DICOM 文件（按 Instance Number 或 Slice Location）
        sorted_files = self._sort_dicom_files(dicom_files)
        
        # 读取第一个文件获取基本信息
        first_slice = pydicom.dcmread(sorted_files[0])
        
        # 提取元数据
        metadata = self._extract_dicom_metadata(first_slice)
        metadata["patient_id"] = patient_id
        metadata["ultrasound_id"] = ultrasound_id
        metadata["slice_count"] = len(sorted_files)
        metadata["file_paths"] = sorted_files
        
        # 构建 3D 体积数据
        volume_data = self._build_volume_data(sorted_files)
        
        # 保存体积数据
        volume_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        volume_path = self.workspace_dir / f"volume_{volume_id}.npy"
        np.save(volume_path, volume_data)
        
        metadata["volume_path"] = str(volume_path)
        metadata["volume_id"] = volume_id
        
        # 保存元数据
        metadata_path = self.workspace_dir / f"metadata_{volume_id}.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
        
        return {
            "success": True,
            "volume_id": volume_id,
            "slice_count": len(sorted_files),
            "metadata": metadata,
            "volume_shape": volume_data.shape,
            "message": f"成功导入 {len(sorted_files)} 层 DICOM 影像",
        }
    
    def _sort_dicom_files(self, files: List[str]) -> List[str]:
        """排序 DICOM 文件"""
        import pydicom
        
        def get_slice_position(filepath):
            try:
                ds = pydicom.dcmread(filepath)
                # 优先使用 Slice Location
                if hasattr(ds, 'SliceLocation'):
                    return ds.SliceLocation
                # 其次使用 Instance Number
                elif hasattr(ds, 'InstanceNumber'):
                    return ds.InstanceNumber
                else:
                    return 0
            except:
                return 0
        
        return sorted(files, key=get_slice_position)
    
    def _extract_dicom_metadata(self, ds: Any) -> Dict[str, Any]:
        """提取 DICOM 元数据"""
        metadata = {}
        
        # 患者信息
        metadata["patient_name"] = str(getattr(ds, 'PatientName', ''))
        metadata["patient_id"] = str(getattr(ds, 'PatientID', ''))
        metadata["study_date"] = str(getattr(ds, 'StudyDate', ''))
        
        # 影像信息
        metadata["modality"] = str(getattr(ds, 'Modality', 'US'))
        metadata["manufacturer"] = str(getattr(ds, 'Manufacturer', 'Unknown'))
        
        # 空间信息
        metadata["slice_thickness"] = float(getattr(ds, 'SliceThickness', 1.0))
        
        pixel_spacing = getattr(ds, 'PixelSpacing', [1, 1])
        if isinstance(pixel_spacing, list):
            metadata["pixel_spacing_x"] = float(pixel_spacing[0])
            metadata["pixel_spacing_y"] = float(pixel_spacing[1])
        else:
            metadata["pixel_spacing_x"] = 1.0
            metadata["pixel_spacing_y"] = 1.0
        
        # 图像尺寸
        metadata["rows"] = ds.Rows if hasattr(ds, 'Rows') else 0
        metadata["columns"] = ds.Columns if hasattr(ds, 'Columns') else 0
        
        return metadata
    
    def _build_volume_data(self, dicom_files: List[str]) -> np.ndarray:
        """构建 3D 体积数据"""
        import pydicom
        
        slices = []
        for filepath in dicom_files:
            ds = pydicom.dcmread(filepath)
            pixel_array = ds.pixel_array.astype(np.float32)
            
            # 标准化到 0-1 范围
            if pixel_array.max() > 0:
                pixel_array = (pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min())
            
            slices.append(pixel_array)
        
        # 堆叠成 3D 体积
        volume = np.stack(slices, axis=-1)
        
        # 转置使 z 轴为切片方向
        volume = np.transpose(volume, (2, 0, 1))
        
        return volume
    
    async def reconstruct_3d_model(
        self,
        volume_id: str,
        algorithm: str = "marching_cubes",
        threshold: float = 0.5,
        smooth: bool = True,
    ) -> Dict[str, Any]:
        """
        3D 模型重建
        
        Args:
            volume_id: 体积数据 ID
            algorithm: 重建算法（marching_cubes / ray_casting）
            threshold: 分割阈值
            smooth: 是否平滑
            
        Returns:
            重建结果
        """
        try:
            import numpy as np
            from skimage import measure
        except ImportError:
            return {
                "success": False,
                "error": "未安装 scikit-image 库，请执行：pip install scikit-image",
            }
        
        # 加载体积数据
        volume_path = self.workspace_dir / f"volume_{volume_id}.npy"
        if not volume_path.exists():
            return {"success": False, "error": f"体积数据不存在：{volume_id}"}
        
        volume = np.load(volume_path)
        
        # 执行 Marching Cubes 算法
        try:
            verts, faces, normals, values = measure.marching_cubes(volume, level=threshold)
        except ValueError as e:
            return {
                "success": False,
                "error": f"重建失败：{str(e)}",
            }
        
        # 平滑处理
        if smooth:
            verts = self._smooth_mesh(verts, iterations=5)
        
        # 导出为 OBJ 格式
        model_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        obj_path = self.workspace_dir / f"model_{model_id}.obj"
        self._export_obj(obj_path, verts, faces)
        
        # 导出为 STL 格式
        stl_path = self.workspace_dir / f"model_{model_id}.stl"
        self._export_stl(stl_path, verts, faces)
        
        # 生成预览图
        preview_path = self.workspace_dir / f"preview_{model_id}.png"
        self._generate_preview(preview_path, verts, faces)
        
        return {
            "success": True,
            "model_id": model_id,
            "mesh_info": {
                "vertices_count": len(verts),
                "faces_count": len(faces),
            },
            "files": {
                "obj": str(obj_path),
                "stl": str(stl_path),
                "preview": str(preview_path),
            },
            "message": "3D 模型重建成功",
        }
    
    def _smooth_mesh(self, verts: np.ndarray, iterations: int = 5) -> np.ndarray:
        """平滑网格"""
        from scipy.ndimage import gaussian_filter
        
        # 简单的高斯平滑
        smoothed = np.zeros_like(verts)
        for i in range(3):
            smoothed[:, i] = gaussian_filter(verts[:, i], sigma=0.5)
        
        return smoothed
    
    def _export_obj(self, filepath: Path, verts: np.ndarray, faces: np.ndarray) -> None:
        """导出为 OBJ 格式"""
        with open(filepath, 'w') as f:
            f.write("# 3D Breast Model\n")
            f.write(f"# Vertices: {len(verts)}, Faces: {len(faces)}\n\n")
            
            # 写入顶点
            for v in verts:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            
            f.write("\n")
            
            # 写入面（OBJ 使用 1-based 索引）
            for face in faces + 1:
                f.write(f"f {face[0]} {face[1]} {face[2]}\n")
    
    def _export_stl(self, filepath: Path, verts: np.ndarray, faces: np.ndarray) -> None:
        """导出为 STL 格式"""
        import struct
        
        with open(filepath, 'wb') as f:
            # STL 文件头（80 字节）
            f.write(b'Binary STL exported by Breast AI System')
            f.write(b'\x00' * 40)
            
            # 三角形数量
            f.write(struct.pack('<I', len(faces)))
            
            # 写入每个三角形
            for face in faces:
                # 法向量（设为 0）
                f.write(struct.pack('<fff', 0.0, 0.0, 0.0))
                
                # 三个顶点
                for i in face:
                    v = verts[i]
                    f.write(struct.pack('<fff', float(v[0]), float(v[1]), float(v[2])))
                
                # 属性字节
                f.write(struct.pack('<H', 0))
    
    def _generate_preview(self, filepath: Path, verts: np.ndarray, faces: np.ndarray) -> None:
        """生成预览图"""
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # 绘制网格
            ax.plot_trisurf(
                verts[:, 0], verts[:, 1], verts[:, 2],
                triangles=faces,
                alpha=0.7,
                cmap='viridis'
            )
            
            ax.set_xlabel('X (mm)')
            ax.set_ylabel('Y (mm)')
            ax.set_zlabel('Z (mm)')
            ax.set_title('3D Breast Model Preview')
            
            # 设置视角
            ax.view_init(elev=20, azim=45)
            
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
        except ImportError:
            # 如果 matplotlib 不可用，创建空文件
            filepath.touch()
    
    async def export_model(
        self,
        model_id: str,
        format: str = "obj",
    ) -> Dict[str, Any]:
        """
        导出 3D 模型
        
        Args:
            model_id: 模型 ID
            format: 导出格式（obj / stl / gltf）
            
        Returns:
            导出结果
        """
        model_path = self.workspace_dir / f"model_{model_id}.{format}"
        
        if not model_path.exists():
            return {
                "success": False,
                "error": f"模型文件不存在：{model_id}",
            }
        
        return {
            "success": True,
            "filepath": str(model_path),
            "format": format,
            "download_url": f"/api/v1/3d-models/download/{model_id}.{format}",
        }
    
    async def get_model_info(self, volume_id: str) -> Dict[str, Any]:
        """获取模型信息"""
        metadata_path = self.workspace_dir / f"metadata_{volume_id}.json"
        
        if not metadata_path.exists():
            return {"success": False, "error": "模型信息不存在"}
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 检查是否有重建的模型
        model_files = list(self.workspace_dir.glob(f"model_*.obj"))
        
        return {
            "success": True,
            "metadata": metadata,
            "model_files": len(model_files),
        }


# 全局服务实例
_reconstruction_service: Optional[Breast3DReconstructionService] = None


def get_reconstruction_service() -> Breast3DReconstructionService:
    """获取 3D 重建服务实例"""
    global _reconstruction_service
    
    if _reconstruction_service is None:
        _reconstruction_service = Breast3DReconstructionService()
    
    return _reconstruction_service
