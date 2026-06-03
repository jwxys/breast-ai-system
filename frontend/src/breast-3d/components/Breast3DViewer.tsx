/**
 * 3D 模型查看器组件 - 基于 Three.js
 * 支持旋转、缩放、平移、剖切等功能
 */
import React, { useEffect, useRef, useState } from 'react';
import { Card, Space, Button, Slider, Switch, Typography, message } from 'antd';
import { RotateLeftOutlined, ZoomInOutlined, HomeOutlined, ScissorOutlined } from '@ant-design/icons';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const { Text } = Typography;

interface Breast3DViewerProps {
  modelUrl?: string;
  width?: number;
  height?: number;
}

const Breast3DViewer: React.FC<Breast3DViewerProps> = ({
  modelUrl,
  width = 600,
  height = 500,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const meshRef = useRef<THREE.Mesh | null>(null);

  const [showAxes, setShowAxes] = useState(true);
  const [showGrid, setShowGrid] = useState(true);
  const [rotationSpeed, setRotationSpeed] = useState(0.5);
  const [autoRotate, setAutoRotate] = useState(false);

  // 初始化 Three.js 场景
  useEffect(() => {
    if (!containerRef.current) return;

    // 创建场景
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f5f5);
    sceneRef.current = scene;

    // 创建相机
    const camera = new THREE.PerspectiveCamera(
      75,
      width / height,
      0.1,
      1000
    );
    camera.position.set(0, 0, 5);
    cameraRef.current = camera;

    // 创建渲染器
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true 
    });
    renderer.setSize(width, height);
    renderer.setClearColor(0xffffff);
    rendererRef.current = renderer;
    containerRef.current.appendChild(renderer.domElement);

    // 添加轨道控制器
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controlsRef.current = controls;

    // 添加光源
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    // 添加坐标轴
    const axesHelper = new THREE.AxesHelper(3);
    axesHelper.visible = showAxes;
    scene.add(axesHelper);

    // 添加网格
    const gridHelper = new THREE.GridHelper(10, 10);
    gridHelper.visible = showGrid;
    scene.add(gridHelper);

    // 动画循环
    const animate = () => {
      requestAnimationFrame(animate);
      
      if (controlsRef.current) {
        controlsRef.current.update();
      }
      
      if (autoRotate && meshRef.current) {
        meshRef.current.rotation.y += rotationSpeed * 0.01;
      }
      
      if (rendererRef.current && sceneRef.current && cameraRef.current) {
        rendererRef.current.render(sceneRef.current, cameraRef.current);
      }
    };

    animate();

    // 清理
    return () => {
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // 加载 3D 模型
  useEffect(() => {
    if (!modelUrl || !sceneRef.current) return;

    const loadModel = async () => {
      try {
        const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader');
        const loader = new GLTFLoader();
        
        loader.load(
          modelUrl,
          (gltf) => {
            const model = gltf.scene;
            model.scale.set(1, 1, 1);
            model.position.set(0, 0, 0);
            
            if (meshRef.current) {
              sceneRef.current?.remove(meshRef.current);
            }
            
            meshRef.current = model as THREE.Mesh;
            sceneRef.current?.add(model);
            
            message.success('3D 模型加载成功！');
          },
          (progress) => {
            if (progress.total > 0) {
              const percent = (progress.loaded / progress.total) * 100;
              console.log(`加载进度：${percent.toFixed(0)}%`);
            }
          },
          (error) => {
            console.error('加载模型失败:', error);
            message.error('加载模型失败');
          }
        );
      } catch (error) {
        console.error('模型加载错误:', error);
      }
    };

    loadModel();
  }, [modelUrl]);

  // 更新坐标轴显示
  useEffect(() => {
    if (sceneRef.current) {
      sceneRef.current.children.forEach((child) => {
        if (child instanceof THREE.AxesHelper) {
          child.visible = showAxes;
        }
      });
    }
  }, [showAxes]);

  // 更新网格显示
  useEffect(() => {
    if (sceneRef.current) {
      sceneRef.current.children.forEach((child) => {
        if (child instanceof THREE.GridHelper) {
          child.visible = showGrid;
        }
      });
    }
  }, [showGrid]);

  // 重置视图
  const handleResetView = () => {
    if (cameraRef.current && controlsRef.current) {
      cameraRef.current.position.set(0, 0, 5);
      controlsRef.current.target.set(0, 0, 0);
      controlsRef.current.update();
    }
  };

  return (
    <div>
      <div
        ref={containerRef}
        style={{
          width,
          height,
          border: '1px solid #d9d9d9',
          borderRadius: 8,
          overflow: 'hidden',
        }}
      />
      
      <div style={{ marginTop: 16, padding: '0 16px' }}>
        <Space wrap size="middle">
          <Button
            icon={<HomeOutlined />}
            onClick={handleResetView}
            size="small"
          >
            重置视图
          </Button>
          
          <Button
            icon={<RotateLeftOutlined />}
            onClick={() => setAutoRotate(!autoRotate)}
            size="small"
            type={autoRotate ? 'primary' : 'default'}
          >
            {autoRotate ? '停止旋转' : '自动旋转'}
          </Button>
          
          <Space>
            <Text>旋转速度:</Text>
            <Slider
              value={rotationSpeed}
              onChange={setRotationSpeed}
              min={0}
              max={2}
              step={0.1}
              style={{ width: 120 }}
              disabled={!autoRotate}
            />
          </Space>
          
          <Space>
            <Text>坐标轴:</Text>
            <Switch
              size="small"
              checked={showAxes}
              onChange={setShowAxes}
              checkedChildren="开"
              unCheckedChildren="关"
            />
          </Space>
          
          <Space>
            <Text>网格:</Text>
            <Switch
              size="small"
              checked={showGrid}
              onChange={setShowGrid}
              checkedChildren="开"
              unCheckedChildren="关"
            />
          </Space>
        </Space>
        
        <div style={{ marginTop: 12, fontSize: 12, color: '#999' }}>
          <Space size="large">
            <span>
              <strong>左键拖动:</strong> 旋转模型
            </span>
            <span>
              <strong>右键拖动:</strong> 平移模型
            </span>
            <span>
              <strong>滚轮:</strong> 缩放
            </span>
          </Space>
        </div>
      </div>
    </div>
  );
};

export default Breast3DViewer;
