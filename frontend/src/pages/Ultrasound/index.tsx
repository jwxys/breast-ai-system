import { useState, useRef } from 'react';
import { Card, Upload, Button, Space, message, Image, Progress, Tag, Descriptions, Divider, Typography, Row, Col, Spin, Result, Steps, InputNumber, Select, Slider, Switch, Alert, Badge, Tooltip } from 'antd';
import {
  InboxOutlined,
  UploadOutlined,
  ScanOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  EyeOutlined,
  DeleteOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  ZoomInOutlined,
  RotateLeftOutlined,
  ApiOutlined,
  FileImageOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import ReactECharts from 'echarts-for-react';
import type { EChartOption } from 'echarts';
import type { UploadFile, UploadProps } from 'antd';
import './index.css';

const { Title, Text, Paragraph } = Typography;
const { Dragger } = Upload;
const MotionCard = motion(Card);

const UltrasoundExam = () => {
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState<UploadFile[]>([]);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  // 处理上传
  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    accept: 'image/*',
    maxCount: 5,
    beforeUpload: (file) => {
      // 模拟上传进度
      let progress = 0;
      const interval = setInterval(() => {
        progress += 10;
        setUploadProgress(progress);
        if (progress >= 100) {
          clearInterval(interval);
          setUploading(false);
          setUploadedFiles(prev => [...prev, file]);
          message.success(`${file.name} 上传成功`);
        }
      }, 100);
      return false; // 阻止自动上传
    },
    onRemove: (file) => {
      setUploadedFiles(prev => prev.filter(f => f.uid !== file.uid));
    },
  };

  // AI 分析
  const handleAIAnalysis = () => {
    if (uploadedFiles.length === 0) {
      message.warning('请先上传超声图像');
      return;
    }
    
    setAnalyzing(true);
    let progress = 0;
    const interval = setInterval(() => {
      progress += 5;
      setAnalysisProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
        setAnalyzing(false);
        // 模拟分析结果
        setAnalysisResult({
          birads: '4A',
          malignancy: '可疑恶性 (低度)',
          confidence: 0.85,
          segmentation: {
            area: 234.5,
            perimeter: 58.3,
            circularity: 0.72,
          },
          features: {
            shape: '不规则',
            margin: '毛刺征',
            orientation: '垂直位',
            echoPattern: '低回声',
            posteriorFeature: '声影',
          },
          suggestion: '建议穿刺活检',
        });
        message.success('AI 分析完成');
      }
    }, 200);
  };

  // BI-RADS 特征雷达图
  const radarOption: EChartOption = {
    tooltip: {},
    radar: {
      indicator: [
        { name: '形状', max: 5 },
        { name: '边界', max: 5 },
        { name: '方向', max: 5 },
        { name: '回声', max: 5 },
        { name: '后方特征', max: 5 },
        { name: '钙化', max: 5 },
      ],
      radius: '65%',
      axisName: {
        color: '#667eea',
        fontSize: 12,
      },
      splitLine: {
        lineStyle: {
          color: '#e2e8f0',
        },
      },
      splitArea: {
        areaStyle: {
          color: ['#f8fafc', '#f1f5f9', '#e2e8f0', '#cbd5e1'],
        },
      },
    },
    series: [{
      name: 'BI-RADS 特征评分',
      type: 'radar',
      data: [
        {
          value: [4, 5, 4, 4, 3, 2],
          name: '当前病灶',
          areaStyle: {
            color: 'rgba(102, 126, 234, 0.3)',
          },
          lineStyle: {
            color: '#667eea',
            width: 2,
          },
          itemStyle: {
            color: '#667eea',
          },
        },
      ],
    }],
  };

  // 恶性概率分布
  const probabilityOption: EChartOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: ['良性', '4A', '4B', '4C', '恶性'],
      axisLabel: {
        color: '#64748b',
      },
    },
    yAxis: {
      type: 'value',
      name: '概率 (%)',
      max: 100,
      axisLabel: {
        formatter: '{value}%',
        color: '#64748b',
      },
    },
    series: [{
      data: [
        {
          value: 5,
          itemStyle: { color: '#10b981' },
          label: { show: true, formatter: '{c}%', position: 'top' },
        },
        {
          value: 85,
          itemStyle: { color: '#f59e0b' },
          label: { show: true, formatter: '{c}%', position: 'top' },
        },
        {
          value: 7,
          itemStyle: { color: '#f97316' },
          label: { show: true, formatter: '{c}%', position: 'top' },
        },
        {
          value: 2,
          itemStyle: { color: '#ef4444' },
          label: { show: true, formatter: '{c}%', position: 'top' },
        },
        {
          value: 1,
          itemStyle: { color: '#7c3aed' },
          label: { show: true, formatter: '{c}%', position: 'top' },
        },
      ],
      type: 'bar',
      barWidth: '50%',
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
      },
    }],
  };

  return (
    <div className="ultrasound-container">
      <Row gutter={[20, 20]}>
        {/* 左侧：上传区域 */}
        <Col xs={24} lg={12}>
          <MotionCard
            title={
              <Space>
                <FileImageOutlined style={{ color: '#667eea' }} />
                <span>图像上传</span>
              </Space>
            }
            className="upload-card"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
          >
            <Dragger {...uploadProps}>
              <div className="upload-content">
                <p className="ant-upload-drag-icon">
                  <InboxOutlined style={{ color: '#667eea' }} />
                </p>
                <Paragraph className="ant-upload-text">
                  点击或拖拽文件到此区域上传
                </Paragraph>
                <Paragraph className="ant-upload-hint">
                  支持 PNG、JPG 格式，单次最多上传 5 张图像
                  <br />
                  建议使用 DICOM 格式以获得最佳分析效果
                </Paragraph>
              </div>
            </Dragger>

            {uploading && (
              <div className="upload-progress">
                <Text>上传中...</Text>
                <Progress percent={uploadProgress} showInfo={false} />
              </div>
            )}

            {uploadedFiles.length > 0 && (
              <div className="uploaded-list">
                <Divider orientation="left">已上传图像</Divider>
                <div className="image-grid">
                  {uploadedFiles.map((file, index) => (
                    <div key={file.uid} className="image-item">
                      <Badge count={index + 1} size="small">
                        <div className="image-preview">
                          <Image
                            src={URL.createObjectURL(file as any)}
                            preview={{
                              mask: <EyeOutlined />,
                            }}
                            fallback="/fallback.png"
                          />
                        </div>
                      </Badge>
                      <div className="image-actions">
                        <Tooltip title="删除">
                          <Button
                            size="small"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={() => uploadProps.onRemove?.(file)}
                          />
                        </Tooltip>
                      </div>
                    </div>
                  ))}
                </div>

                <Divider />

                <Button
                  type="primary"
                  size="large"
                  block
                  icon={<ThunderboltOutlined />}
                  loading={analyzing}
                  onClick={handleAIAnalysis}
                  className="analyze-btn"
                >
                  {analyzing ? '分析中...' : '开始 AI 分析'}
                </Button>
              </div>
            )}
          </MotionCard>

          {/* 分析进度 */}
          {analyzing && (
            <MotionCard
              className="analysis-progress-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="analysis-steps">
                <Steps
                  current={Math.floor(analysisProgress / 25)}
                  items={[
                    {
                      title: '图像预处理',
                      description: '去噪、增强、标准化',
                      icon: <ScanOutlined />,
                    },
                    {
                      title: '病灶分割',
                      description: 'PBS-Net 模型推理',
                      icon: <ApiOutlined />,
                    },
                    {
                      title: '特征提取',
                      description: 'DFMFI 特征融合',
                      icon: <ThunderboltOutlined />,
                    },
                    {
                      title: '诊断分析',
                      description: 'HXM-Net 多模态诊断',
                      icon: <CheckCircleOutlined />,
                    },
                  ]}
                />
              </div>
              <div className="analysis-progress">
                <Text>整体进度</Text>
                <Progress
                  percent={analysisProgress}
                  strokeColor={{
                    '0%': '#667eea',
                    '100%': '#764ba2',
                  }}
                />
              </div>
            </MotionCard>
          )}
        </Col>

        {/* 右侧：分析结果 */}
        <Col xs={24} lg={12}>
          <MotionCard
            title={
              <Space>
                <ThunderboltOutlined style={{ color: '#f093fb' }} />
                <span>AI 诊断结果</span>
              </Space>
            }
            className="result-card"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
          >
            {!analysisResult ? (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={
                  <span>
                    上传图像并点击"AI 分析"获取诊断结果
                  </span>
                }
              />
            ) : (
              <div className="analysis-result">
                {/* 诊断结论 */}
                <Alert
                  message={
                    <Space size="large">
                      <div className="result-main">
                        <div className="result-label">BI-RADS 分级</div>
                        <div className="result-value birads">{analysisResult.birads}</div>
                      </div>
                      <div className="result-divider" />
                      <div className="result-main">
                        <div className="result-label">恶性概率</div>
                        <div className="result-value probability">
                          {(analysisResult.confidence * 100).toFixed(1)}%
                        </div>
                      </div>
                      <div className="result-divider" />
                      <div className="result-main">
                        <div className="result-label">诊断结果</div>
                        <div className="result-value diagnosis">{analysisResult.malignancy}</div>
                      </div>
                    </Space>
                  }
                  type="info"
                  showIcon={false}
                  className="result-summary"
                />

                <Divider>病灶特征分析</Divider>

                {/* 特征描述 */}
                <Descriptions
                  bordered
                  column={1}
                  size="small"
                  className="features-descriptions"
                >
                  <Descriptions.Item label="形状">
                    <Tag color="red">{analysisResult.features.shape}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="边界">
                    <Tag color="orange">{analysisResult.features.margin}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="方向">
                    <Tag color="volcano">{analysisResult.features.orientation}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="回声模式">
                    <Tag color="blue">{analysisResult.features.echoPattern}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="后方特征">
                    <Tag color="purple">{analysisResult.features.posteriorFeature}</Tag>
                  </Descriptions.Item>
                </Descriptions>

                <Divider />

                {/* 图表区域 */}
                <Row gutter={[16, 16]}>
                  <Col span={12}>
                    <div className="chart-container">
                      <Text strong className="chart-title">BI-RADS 特征评分</Text>
                      <ReactECharts option={radarOption} style={{ height: 280 }} />
                    </div>
                  </Col>
                  <Col span={12}>
                    <div className="chart-container">
                      <Text strong className="chart-title">恶性概率分布</Text>
                      <ReactECharts option={probabilityOption} style={{ height: 280 }} />
                    </div>
                  </Col>
                </Row>

                <Divider />

                {/* 测量数据 */}
                <Descriptions
                  title={<><ScanOutlined /> 病灶测量</>}
                  bordered
                  column={2}
                  size="small"
                >
                  <Descriptions.Item label="病灶面积">
                    {analysisResult.segmentation.area} mm²
                  </Descriptions.Item>
                  <Descriptions.Item label="病灶周长">
                    {analysisResult.segmentation.perimeter} mm
                  </Descriptions.Item>
                  <Descriptions.Item label="圆度">
                    {analysisResult.segmentation.circularity.toFixed(2)}
                  </Descriptions.Item>
                </Descriptions>

                {/* 建议 */}
                <Alert
                  message={
                    <Space>
                      <ExclamationCircleOutlined />
                      <Text strong>诊疗建议：{analysisResult.suggestion}</Text>
                    </Space>
                  }
                  type="warning"
                  showIcon={false}
                  className="suggestion-alert"
                />

                {/* 操作按钮 */}
                <div className="result-actions">
                  <Space>
                    <Button icon={<DownloadOutlined />}>
                      导出报告
                    </Button>
                    <Button icon={<ShareAltOutlined />}>
                      分享结果
                    </Button>
                    <Button type="primary" icon={<FileTextOutlined />}>
                      生成诊断
                    </Button>
                  </Space>
                </div>
              </div>
            )}
          </MotionCard>
        </Col>
      </Row>
    </div>
  );
};

export default UltrasoundExam;
