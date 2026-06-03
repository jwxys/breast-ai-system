/**
 * 3D 乳腺建模页面 - 新手引导版
 * 
 * 支持 DICOM 导入、3D 重建、模型查看和导出
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  Card,
  Upload,
  Button,
  Space,
  Steps,
  Progress,
  message,
  Modal,
  InputNumber,
  Switch,
  Select,
  Slider,
  Divider,
  Typography,
  Row,
  Col,
  Spin,
  Alert,
  Timeline,
  Result,
  Statistic,
  Tag,
} from 'antd';

import { motion } from 'framer-motion';
import Breast3DViewer from '@/components/Breast3DViewer';

const { Title, Paragraph, Text } = Typography;
const { Step } = Steps;
const { Dragger } = Upload;
const {
  UploadOutlined,
  ThunderboltOutlined,
  DownloadOutlined,
  RotateLeftOutlined,
  ZoomInOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  LoadingOutlined,
  FileImageOutlined,
  BoxOutlined,
  QuestionCircleOutlined,
  HomeOutlined,
} = require('@ant-design/icons');
const MotionCard = motion(Card);

const Breast3DModelingPage: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [reconstructing, setReconstructing] = useState(false);
  const [volumeId, setVolumeId] = useState<string | null>(null);
  const [modelId, setModelId] = useState<string | null>(null);
  const [modelInfo, setModelInfo] = useState<any>(null);
  const [guideVisible, setGuideVisible] = useState(true);
  
  // 重建参数
  const [reconstructParams, setReconstructParams] = useState({
    algorithm: 'marching_cubes',
    threshold: 0.5,
    smooth: true,
  });

  // 新手引导步骤
  const guideSteps = [
    {
      title: '准备 DICOM 影像',
      description: '从超声/钼靶设备导出 DICOM 格式影像（建议 10 层以上）',
      icon: <FileImageOutlined />,
    },
    {
      title: '上传文件',
      description: '将 DICOM 文件拖拽到上传区域',
      icon: <UploadOutlined />,
    },
    {
      title: '3D 重建',
      description: '点击重建按钮生成 3D 模型',
      icon: <ThunderboltOutlined />,
    },
    {
      title: '查看模型',
      description: '旋转、缩放查看 3D 模型',
      icon: <EyeOutlined />,
    },
    {
      title: '导出模型',
      description: '导出 OBJ/STL 格式用于 3D 打印',
      icon: <DownloadOutlined />,
    },
  ];

  // 上传配置
  const uploadProps = {
    name: 'dicom_files',
    multiple: true,
    accept: '.dcm',
    beforeUpload: (file: File) => {
      if (!file.name.toLowerCase().endsWith('.dcm')) {
        message.error('只能上传 DICOM 文件 (.dcm)');
        return false;
      }
      return true;
    },
    onRemove: (file: any) => {
      // 处理文件移除
    },
  };

  // 处理 DICOM 上传
  const handleUpload = async () => {
    setUploading(true);
    try {
      // TODO: 实际调用 API
      // const formData = new FormData();
      // files.forEach(file => formData.append('files', file));
      // formData.append('patient_id', '1');
      // const result = await fetch('/api/v1/3d-models/import-dicom', {...});
      
      // 模拟上传
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockVolumeId = '20260530_120000';
      setVolumeId(mockVolumeId);
      message.success('DICOM 影像导入成功！');
      setCurrentStep(2);
      
      // 获取模型信息
      fetchModelInfo(mockVolumeId);
    } catch (error) {
      message.error('上传失败');
    } finally {
      setUploading(false);
    }
  };

  // 获取模型信息
  const fetchModelInfo = async (vid: string) => {
    // TODO: 调用 API
    setModelInfo({
      slice_count: 25,
      volume_shape: [256, 256, 25],
      patient_name: '张*三',
      study_date: '2026-05-30',
    });
  };

  // 执行 3D 重建
  const handleReconstruct = async () => {
    if (!volumeId) {
      message.error('请先上传 DICOM 影像');
      return;
    }
    
    setReconstructing(true);
    try {
      // TODO: 调用 API
      // const result = await fetch(`/api/v1/3d-models/reconstruct?volume_id=${volumeId}&...`);
      
      // 模拟重建
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const mockModelId = '20260530_120500';
      setModelId(mockModelId);
      message.success('3D 模型重建成功！');
      setCurrentStep(3);
    } catch (error) {
      message.error('重建失败');
    } finally {
      setReconstructing(false);
    }
  };

  // 导出模型
  const handleExport = (format: string) => {
    if (!modelId) {
      message.error('请先生成 3D 模型');
      return;
    }
    message.info(`开始导出 ${format.toUpperCase()} 格式模型...`);
    // TODO: 调用下载 API
  };

  // 3D 模型预览（使用真实 Three.js 渲染）
  const ModelPreview = () => {
    if (reconstructing) {
      return (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Spin size="large" tip="正在重建 3D 模型..." />
          <Progress
            percent={65}
            status="active"
            style={{ marginTop: 16, width: 300 }}
          />
        </div>
      );
    }
    
    if (modelId) {
      return (
        <Breast3DViewer
          modelUrl={`/api/v1/3d-models/${modelId}/download?format=gltf`}
          width={600}
          height={500}
        />
      );
    }
    
    return (
      <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
        <BoxOutlined style={{ fontSize: 64, marginBottom: 16 }} />
        <div>请先上传 DICOM 影像并执行 3D 重建</div>
      </div>
    );
  };

  return (
    <div style={{ padding: 24 }}>
      {/* 新手引导弹窗 */}
      <Modal
        title="🎓 乳腺 3D 建模新手引导"
        open={guideVisible}
        onCancel={() => setGuideVisible(false)}
        footer={[
          <Button key="close" type="primary" onClick={() => setGuideVisible(false)}>
            开始使用
          </Button>,
        ]}
        width={800}
      >
        <Steps
          current={currentStep}
          onChange={setCurrentStep}
          items={guideSteps.map(step => ({
            title: step.title,
            description: step.description,
            icon: step.icon,
          }))}
        />
        
        <Divider />
        
        <Alert
          type="info"
          message="温馨提示"
          description={
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              <li>DICOM 影像建议 10 层以上，层数越多精度越高</li>
              <li>重建过程大约需要 10-30 秒</li>
              <li>导出的 STL 格式可用于 3D 打印</li>
              <li>过程中可随时查看新手引导（右上角问号图标）</li>
            </ul>
          }
          showIcon
        />
      </Modal>

      {/* 页面标题 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <BoxOutlined style={{ fontSize: 28, color: '#667eea' }} />
          <div>
            <Title level={2} style={{ margin: 0 }}>乳腺 3D 建模</Title>
            <Text type="secondary">DICOM 影像导入 → 3D 重建 → 模型查看 → 导出打印</Text>
          </div>
        </div>
        <Space>
          <Button icon={<HomeOutlined />} onClick={() => setCurrentStep(0)}>
            返回首页
          </Button>
          <Button icon={<QuestionCircleOutlined />} onClick={() => setGuideVisible(true)}>
            新手引导
          </Button>
        </Space>
      </div>

      {/* 进度步骤 */}
      <Card style={{ marginBottom: 16 }}>
        <Steps
          current={currentStep}
          items={[
            {
              title: '准备影像',
              subTitle: 'DICOM 文件',
            },
            {
              title: '上传文件',
              subTitle: '拖拽上传',
            },
            {
              title: '3D 重建',
              subTitle: '算法处理',
            },
            {
              title: '查看模型',
              subTitle: '交互预览',
            },
            {
              title: '导出模型',
              subTitle: 'OBJ/STL',
            },
          ]}
        />
      </Card>

      <Row gutter={16}>
        {/* 左侧：操作面板 */}
        <Col span={12}>
          {/* 步骤 1: 上传 DICOM */}
          {currentStep === 0 && (
            <MotionCard
              title="上传 DICOM 影像"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Dragger {...uploadProps}>
                <p className="ant-upload-drag-icon">
                  <FileImageOutlined style={{ color: '#1890ff' }} />
                </p>
                <p className="ant-upload-text">点击或拖拽 DICOM 文件到此处上传</p>
                <p className="ant-upload-hint">
                  支持.dcm 格式，建议 10 层以上，层厚≤1mm
                </p>
              </Dragger>
              
              <Divider />
              
              <div style={{ textAlign: 'center' }}>
                <Space>
                  <Button
                    type="primary"
                    size="large"
                    icon={<UploadOutlined />}
                    loading={uploading}
                    onClick={handleUpload}
                  >
                    开始上传
                  </Button>
                  <Button
                    size="large"
                    icon={<QuestionCircleOutlined />}
                    onClick={() => setGuideVisible(true)}
                  >
                    查看帮助
                  </Button>
                </Space>
              </div>
            </MotionCard>
          )}

          {/* 步骤 2: 重建参数 */}
          {currentStep === 1 && modelInfo && (
            <MotionCard
              title="模型信息"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic title="切片数量" value={modelInfo.slice_count} suffix="层" />
                  </Col>
                  <Col span={8}>
                    <Statistic title="影像尺寸" value={`${modelInfo.volume_shape[0]}×${modelInfo.volume_shape[1]}`} />
                  </Col>
                  <Col span={8}>
                    <Statistic title="患者" value={modelInfo.patient_name} />
                  </Col>
                </Row>

                <Divider />

                <div>
                  <Title level={5}>重建参数设置</Title>
                  
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text>重建算法：</Text>
                      <Select
                        value={reconstructParams.algorithm}
                        onChange={(v) => setReconstructParams({...reconstructParams, algorithm: v})}
                        style={{ width: 200 }}
                      >
                        <Select.Option value="marching_cubes">Marching Cubes（推荐）</Select.Option>
                        <Select.Option value="ray_casting">Ray Casting</Select.Option>
                      </Select>
                    </div>

                    <div>
                      <Text>分割阈值：</Text>
                      <Slider
                        min={0}
                        max={1}
                        step={0.05}
                        value={reconstructParams.threshold}
                        onChange={(v) => setReconstructParams({...reconstructParams, threshold: v})}
                        style={{ width: 300 }}
                        marks={{ 0: '低', 0.5: '中', 1: '高' }}
                      />
                      <Text type="secondary">阈值越高提取的组织密度越高</Text>
                    </div>

                    <div>
                      <Text>网格平滑：</Text>
                      <Switch
                        checked={reconstructParams.smooth}
                        onChange={(v) => setReconstructParams({...reconstructParams, smooth: v})}
                        checkedChildren="开启"
                        unCheckedChildren="关闭"
                      />
                      <Text type="secondary" style={{ marginLeft: 8 }}>
                        平滑处理可改善视觉效果
                      </Text>
                    </div>
                  </Space>
                </div>

                <Divider />

                <div style={{ textAlign: 'center' }}>
                  <Button
                    type="primary"
                    size="large"
                    icon={<ThunderboltOutlined />}
                    loading={reconstructing}
                    onClick={handleReconstruct}
                  >
                    开始 3D 重建
                  </Button>
                </div>
              </Space>
            </MotionCard>
          )}

          {/* 步骤 3: 查看和导出 */}
          {currentStep >= 2 && (
            <MotionCard
              title="模型导出"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <Result
                  status="success"
                  title="3D 模型已生成！"
                  subTitle="可以查看、旋转、导出模型"
                  extra={[
                    <Button
                      key="export-obj"
                      type="primary"
                      icon={<DownloadOutlined />}
                      onClick={() => handleExport('obj')}
                    >
                      导出 OBJ
                    </Button>,
                    <Button
                      key="export-stl"
                      icon={<DownloadOutlined />}
                      onClick={() => handleExport('stl')}
                    >
                      导出 STL
                    </Button>,
                  ]}
                />
              </div>
            </MotionCard>
          )}
        </Col>

        {/* 右侧：3D 预览 */}
        <Col span={12}>
          <MotionCard
            title="3D 模型预览"
            extra={
              <Space>
                <Tag color="blue">实时渲染</Tag>
                <Tag color="green">Three.js</Tag>
              </Space>
            }
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <ModelPreview />
          </MotionCard>

          {/* 操作提示 */}
          <Card
            title={<><QuestionCircleOutlined /> 操作提示</>}
            size="small"
            style={{ marginTop: 16 }}
          >
            <Timeline
              items={[
                {
                  color: 'blue',
                  children: '上传 DICOM 文件（支持多选）',
                },
                {
                  color: 'green',
                  children: '设置重建参数（阈值、平滑）',
                },
                {
                  color: 'orange',
                  children: '等待重建完成（10-30 秒）',
                },
                {
                  color: 'purple',
                  children: '查看、旋转、导出模型',
                },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Breast3DModelingPage;
