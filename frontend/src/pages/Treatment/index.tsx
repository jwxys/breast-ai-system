import { useState } from 'react';
import { Card, Table, Button, Space, Tag, Badge, Modal, Form, Input, Select, DatePicker, Descriptions, Timeline, Progress, Alert, Typography, Divider, Steps, Rate, message } from 'antd';
import {
  MedicineBoxOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExperimentOutlined,
  HeartOutlined,
  PlusOutlined,
  EyeOutlined,
  EditOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import dayjs from 'dayjs';
import ReactECharts from 'echarts-for-react';
import type { EChartOption } from 'echarts';

const { Title, Text } = Typography;
const MotionCard = motion(Card);

const TreatmentList = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 治疗效果分布
  const outcomeOption: EChartOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}例',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '治疗效果',
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        data: [
          { value: 156, name: '完全缓解', itemStyle: { color: '#10b981' } },
          { value: 234, name: '部分缓解', itemStyle: { color: '#10b981' } },
          { value: 89, name: '疾病稳定', itemStyle: { color: '#f59e0b' } },
          { value: 34, name: '疾病进展', itemStyle: { color: '#ef4444' } },
        ],
      },
    ],
  };

  const columns = [
    {
      title: '患者信息',
      dataIndex: 'patient',
      key: 'patient',
      width: 180,
      render: (_: unknown, record: any) => (
        <Space>
          <Badge
            count={null}
            indicator={<span className={`status-dot ${record.risk}`} />}
          >
            <div>
              <div className="patient-name">{record.patient}</div>
              <div className="patient-no">{record.no}</div>
            </div>
          </Badge>
        </Space>
      ),
    },
    {
      title: '治疗方案',
      dataIndex: 'regimen',
      key: 'regimen',
      width: 150,
      render: (regimen: string) => (
        <Tag color="blue">{regimen}</Tag>
      ),
    },
    {
      title: '治疗类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type: string) => {
        const config: any = {
          surgery: { color: 'purple', text: '手术' },
          chemo: { color: 'blue', text: '化疗' },
          radio: { color: 'orange', text: '放疗' },
          endocrine: { color: 'green', text: '内分泌' },
          target: { color: 'cyan', text: '靶向' },
        };
        return <Tag color={config[type]?.color || 'default'}>{config[type]?.text || type}</Tag>;
      },
    },
    {
      title: '开始时间',
      dataIndex: 'startDate',
      key: 'startDate',
      width: 120,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '周期',
      dataIndex: 'cycles',
      key: 'cycles',
      width: 80,
      render: (cycles: number) => `${cycles}周期`,
    },
    {
      title: '疗效',
      dataIndex: 'response',
      key: 'response',
      width: 120,
      render: (response: string) => {
        const config: any = {
          CR: { color: 'green', text: '完全缓解' },
          PR: { color: 'lime', text: '部分缓解' },
          SD: { color: 'orange', text: '疾病稳定' },
          PD: { color: 'red', text: '疾病进展' },
        };
        return <Tag color={config[response]?.color || 'default'}>{config[response]?.text || response}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const config: any = {
          completed: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
          ongoing: { color: 'processing', text: '进行中', icon: <ClockCircleOutlined /> },
          planned: { color: 'warning', text: '待开始', icon: <ClockCircleOutlined /> },
        };
        return (
          <Space>
            <span style={{ color: config[status]?.color }}>{config[status]?.icon}</span>
            <span style={{ color: config[status]?.color }}>{config[status]?.text}</span>
          </Space>
        );
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 140,
      render: (_: unknown, record: any) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />}>
            详情
          </Button>
          <Button size="small" icon={<EditOutlined />}>
            调整
          </Button>
        </Space>
      ),
    },
  ];

  const dataSource = [
    {
      key: '1',
      patient: '张三',
      no: 'P20260527001',
      risk: 'high',
      regimen: 'TC 方案',
      type: 'chemo',
      startDate: '2026-03-15',
      cycles: 6,
      response: 'PR',
      status: 'ongoing',
    },
    {
      key: '2',
      patient: '李四',
      no: 'P20260527002',
      risk: 'medium',
      regimen: '改良根治术',
      type: 'surgery',
      startDate: '2026-04-20',
      cycles: 1,
      response: 'CR',
      status: 'completed',
    },
  ];

  return (
    <div className="treatment-container">
      <Row gutter={[20, 20]}>
        <Col xs={24} lg={16}>
          <MotionCard
            title={
              <Space>
                <MedicineBoxOutlined style={{ color: '#667eea' }} />
                <span>治疗管理</span>
              </Space>
            }
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setIsModalOpen(true)}
              >
                新建治疗
              </Button>
            }
          >
            <Table
              columns={columns}
              dataSource={dataSource}
              rowKey="key"
              pagination={{
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条`,
              }}
              scroll={{ x: 1000 }}
            />
          </MotionCard>
        </Col>

        <Col xs={24} lg={8}>
          <MotionCard
            title={
              <Space>
                <ExperimentOutlined style={{ color: '#f093fb' }} />
                <span>治疗效果统计</span>
              </Space>
            }
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <ReactECharts option={outcomeOption} style={{ height: 300 }} />
            <Divider />
            <Descriptions column={1} size="small">
              <Descriptions.Item label="总治疗人数">
                <Text strong>513</Text>
              </Descriptions.Item>
              <Descriptions.Item label="客观缓解率">
                <Progress
                  percent={76.1}
                  strokeColor={{ '0%': '#10b981', '100%': '#10b981' }}
                  format={() => '76.1%'}
                />
              </Descriptions.Item>
              <Descriptions.Item label="疾病控制率">
                <Progress
                  percent={93.3}
                  strokeColor={{ '0%': '#667eea', '100%': '#764ba2' }}
                  format={() => '93.3%'}
                />
              </Descriptions.Item>
            </Descriptions>
          </MotionCard>
        </Col>
      </Row>
    </div>
  );
};

export default TreatmentList;
