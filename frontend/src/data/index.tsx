import React, { useState } from 'react';
import { 
  Row, Col, Card, Table, Tabs, Tag, Space, Button, Statistic, 
  Descriptions, Typography, Badge, Progress, Tooltip, Divider 
} from 'antd';
import {
  DatabaseOutlined,
  FolderOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  MedicineBoxOutlined,
  EyeOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  GoldOutlined,
  ApiOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import ReactECharts from 'echarts-for-react';
import type { EChartOption } from 'echarts';
import './index.css';

const { Title, Text } = Typography;
const MotionCard = motion(Card);

const DataManagement = () => {
  const [activeTab, setActiveTab] = useState('overview');

  // 模型权重数据
  const modelWeights = [
    {
      key: '1',
      modelName: 'PBS-Net',
      modelCode: 'pbs-net',
      version: 'v1.2',
      branch: 'western',
      weightFile: 'pbs_net_v12.pth',
      fileSize: 128.0,
      trainingData: '2,500 例',
      dice: 0.87,
      ethicsApproval: 'IRB-2023-BREAST-001',
      status: 'active',
    },
    {
      key: '2',
      modelName: 'DFMFI',
      modelCode: 'dfmfi',
      version: 'v2.0',
      branch: 'western',
      weightFile: 'dfmfi_v20.pth',
      fileSize: 96.0,
      trainingData: '3,000 例',
      auc: 0.97,
      ethicsApproval: 'IRB-2023-BREAST-001',
      status: 'active',
    },
    {
      key: '3',
      modelName: 'HXM-Net',
      modelCode: 'hxm-net',
      version: 'v1.5',
      branch: 'western',
      weightFile: 'hxm_net_v15.pth',
      fileSize: 256.0,
      trainingData: '1,500 例',
      accuracy: 0.94,
      ethicsApproval: 'IRB-2023-BREAST-001',
      status: 'active',
    },
    {
      key: '4',
      modelName: 'TCM-CIN',
      modelCode: 'tcm-cin',
      version: 'v3.1',
      branch: 'tcm',
      weightFile: 'tcm_constitution_v31.pth',
      fileSize: 64.0,
      trainingData: '5,000 例',
      accuracy: 0.89,
      ethicsApproval: 'IRB-2025-TCM-001',
      status: 'active',
    },
    {
      key: '5',
      modelName: 'TCM-SDN',
      modelCode: 'tcm-sdn',
      version: 'v2.3',
      branch: 'tcm',
      weightFile: 'tcm_syndrome_v23.pth',
      fileSize: 72.0,
      trainingData: '3,200 例',
      accuracy: 0.86,
      ethicsApproval: 'IRB-2025-TCM-002',
      status: 'active',
    },
  ];

  // 训练数据集
  const trainingDatasets = [
    {
      key: '1',
      name: '本院乳腺超声数据集',
      code: 'breast-us-local',
      type: 'ultrasound',
      source: '本院超声科',
      region: '中国',
      totalCount: 2500,
      format: 'DICOM',
      ethics: 'IRB-2023-BREAST-001',
    },
    {
      key: '2',
      name: '多模态乳腺影像数据集',
      code: 'breast-multi-modal',
      type: 'multi-modality',
      source: '本院 + 协作',
      region: '中国',
      totalCount: 3000,
      format: 'DICOM',
      ethics: 'IRB-2023-BREAST-001',
    },
    {
      key: '3',
      name: '中医体质问卷数据集',
      code: 'tcm-constitution',
      type: 'questionnaire',
      source: '3 家三甲医院',
      region: '北京/上海/广州',
      totalCount: 5000,
      format: 'CSV',
      ethics: 'IRB-2025-TCM-001',
    },
    {
      key: '4',
      name: '中医证型临床数据集',
      code: 'tcm-syndrome',
      type: 'clinical',
      source: '本院 + 协作',
      region: '6 省市',
      totalCount: 3200,
      format: 'CSV',
      ethics: 'IRB-2025-TCM-002',
    },
  ];

  // 公开数据集
  const publicDatasets = [
    {
      key: '1',
      name: 'BUSI 乳腺超声数据集',
      code: 'busi',
      publisher: 'PACS Journal',
      year: 2018,
      modality: 'ultrasound',
      imageCount: 780,
      patientCount: 600,
      size: 2.5,
      access: 'open',
      downloaded: true,
    },
    {
      key: '2',
      name: 'DDSM 乳腺钼靶数据集',
      code: 'ddsm',
      publisher: 'USF',
      year: 1996,
      modality: 'mammography',
      imageCount: 2620,
      patientCount: 2620,
      size: 15.0,
      access: 'open',
      downloaded: false,
    },
    {
      key: '3',
      name: 'TCGA-BRCA 数据集',
      code: 'tcga-brca',
      publisher: 'NCI/NIH',
      year: 2012,
      modality: 'pathology',
      imageCount: 10000,
      patientCount: 1000,
      size: 500.0,
      access: 'restricted',
      downloaded: true,
    },
  ];

  // 分支分布图
  const branchOption: EChartOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} MB ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '权重存储',
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2,
        },
        data: [
          { value: 480, name: '西医分支', itemStyle: { color: '#667eea' } },
          { value: 138.4, name: '中医分支', itemStyle: { color: '#f093fb' } },
        ],
        label: {
          formatter: '{b}\n{c} MB',
        },
      },
    ],
  };

  // 数据类型分布图
  const dataTypeOption: EChartOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    xAxis: {
      type: 'category',
      data: ['ultrasound', 'multi-modal', 'questionnaire', 'clinical'],
    },
    yAxis: {
      type: 'value',
      name: '数据例数',
    },
    series: [
      {
        data: [2500, 3000, 5000, 3200],
        type: 'bar',
        showBackground: true,
        itemStyle: {
          color: new (require('echarts')).graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' },
          ]),
        },
      },
    ],
  };

  // 表格列定义
  const weightColumns = [
    {
      title: '模型名称',
      dataIndex: 'modelName',
      key: 'modelName',
      render: (name: string, record: any) => (
        <Space>
          <MedicineBoxOutlined style={{ color: record.branch === 'western' ? '#667eea' : '#f093fb' }} />
          <Text strong>{name}</Text>
          <Tag color={record.branch === 'western' ? 'blue' : 'pink'}>
            {record.branch === 'western' ? '西医' : '中医'}
          </Tag>
        </Space>
      ),
    },
    {
      title: '版本号',
      dataIndex: 'version',
      key: 'version',
      render: (version: string) => <Tag color="purple">{version}</Tag>,
    },
    {
      title: '权重文件',
      dataIndex: 'weightFile',
      key: 'weightFile',
      render: (file: string, record: any) => (
        <Space>
          <FileTextOutlined />
          <Text code>{file}</Text>
          <Text type="secondary">({record.fileSize} MB)</Text>
        </Space>
      ),
    },
    {
      title: '训练数据',
      dataIndex: 'trainingData',
      key: 'trainingData',
    },
    {
      title: '性能指标',
      key: 'metrics',
      render: (_: unknown, record: any) => (
        <Space>
          {record.dice && <Badge count={`Dice ${record.dice}`} style={{ backgroundColor: '#10b981' }} />}
          {record.auc && <Badge count={`AUC ${record.auc}`} style={{ backgroundColor: '#667eea' }} />}
          {record.accuracy && <Badge count={`Acc ${record.accuracy}`} style={{ backgroundColor: '#f59e0b' }} />}
        </Space>
      ),
    },
    {
      title: '伦理审批',
      dataIndex: 'ethicsApproval',
      key: 'ethicsApproval',
      render: (approval: string) => (
        <Tooltip title={approval}>
          <Tag icon={<CheckCircleOutlined />} color="success">已审批</Tag>
        </Tooltip>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        status === 'active' ? 
          <Badge status="processing" text="启用" /> : 
          <Badge status="default" text="停用" />
      ),
    },
  ];

  const datasetColumns = [
    {
      title: '数据集名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: any) => (
        <Space>
          <DatabaseOutlined />
          <Text strong>{name}</Text>
          <Tag color="default">{record.code}</Tag>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => <Tag color="blue">{type}</Tag>,
    },
    {
      title: '来源',
      dataIndex: 'source',
      key: 'source',
    },
    {
      title: '地区',
      dataIndex: 'region',
      key: 'region',
    },
    {
      title: '数据量',
      dataIndex: 'totalCount',
      key: 'totalCount',
      render: (count: number) => <Text strong>{count.toLocaleString()} 例</Text>,
    },
    {
      title: '格式',
      dataIndex: 'format',
      key: 'format',
      render: (format: string) => <Tag>{format}</Tag>,
    },
  ];

  const publicDatasetColumns = [
    {
      title: '数据集名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: any) => (
        <Space>
          <FolderOutlined />
          <Text strong>{name}</Text>
          <Tag color={record.access === 'open' ? 'green' : 'orange'}>
            {record.access === 'open' ? '开放' : '受限'}
          </Tag>
        </Space>
      ),
    },
    {
      title: '发布机构',
      dataIndex: 'publisher',
      key: 'publisher',
    },
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
    },
    {
      title: '模态',
      dataIndex: 'modality',
      key: 'modality',
      render: (modality: string) => <Tag color="blue">{modality}</Tag>,
    },
    {
      title: '图像数',
      dataIndex: 'imageCount',
      key: 'imageCount',
      render: (count: number) => count.toLocaleString(),
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      render: (size: number) => `${size} GB`,
    },
    {
      title: '下载状态',
      dataIndex: 'downloaded',
      key: 'downloaded',
      render: (downloaded: boolean) => (
        downloaded ? 
          <Badge status="success" text="已下载" /> : 
          <Button size="small">下载</Button>
      ),
    },
  ];

  const tabItems = [
    {
      key: 'overview',
      label: (
        <Space>
          <GoldOutlined />
          <span>总览</span>
        </Space>
      ),
      children: (
        <Row gutter={[20, 20]}>
          <Col xs={24} sm={12} lg={6}>
            <MotionCard>
              <Statistic
                title="模型权重"
                value={5}
                suffix="个"
                valueStyle={{ color: '#667eea' }}
                prefix={<MedicineBoxOutlined />}
              />
            </MotionCard>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <MotionCard>
              <Statistic
                title="训练数据集"
                value={4}
                suffix="个"
                valueStyle={{ color: '#10b981' }}
                prefix={<DatabaseOutlined />}
              />
            </MotionCard>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <MotionCard>
              <Statistic
                title="公开数据集"
                value={3}
                suffix="个"
                valueStyle={{ color: '#f59e0b' }}
                prefix={<FolderOutlined />}
              />
            </MotionCard>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <MotionCard>
              <Statistic
                title="总存储"
                value={620.4}
                suffix="MB"
                valueStyle={{ color: '#f093fb' }}
                prefix={<GoldOutlined />}
              />
            </MotionCard>
          </Col>

          <Col xs={24} lg={12}>
            <MotionCard
              title="分支权重分布"
              style={{ marginTop: 20 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <ReactECharts option={branchOption} style={{ height: 300 }} />
            </MotionCard>
          </Col>
          <Col xs={24} lg={12}>
            <MotionCard
              title="数据类型分布"
              style={{ marginTop: 20 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <ReactECharts option={dataTypeOption} style={{ height: 300 }} />
            </MotionCard>
          </Col>
        </Row>
      ),
    },
    {
      key: 'weights',
      label: (
        <Space>
          <MedicineBoxOutlined />
          <span>模型权重</span>
        </Space>
      ),
      children: (
        <MotionCard
          title="AI 模型权重列表"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Table columns={weightColumns} dataSource={modelWeights} rowKey="key" pagination={false} />
        </MotionCard>
      ),
    },
    {
      key: 'datasets',
      label: (
        <Space>
          <DatabaseOutlined />
          <span>训练数据集</span>
        </Space>
      ),
      children: (
        <MotionCard
          title="训练数据集列表"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Table columns={datasetColumns} dataSource={trainingDatasets} rowKey="key" pagination={false} />
        </MotionCard>
      ),
    },
    {
      key: 'public',
      label: (
        <Space>
          <FolderOutlined />
          <span>公开数据集</span>
        </Space>
      ),
      children: (
        <MotionCard
          title="公开数据集列表"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Table columns={publicDatasetColumns} dataSource={publicDatasets} rowKey="key" pagination={false} />
        </MotionCard>
      ),
    },
  ];

  return (
    <div className="data-management-container">
      <Title level={3} style={{ marginBottom: 24 }}>
        <Space>
          <DatabaseOutlined style={{ color: '#667eea' }} />
          <span>数据管理</span>
        </Space>
      </Title>

      <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} size="large" />
    </div>
  );
};

export default DataManagement;
