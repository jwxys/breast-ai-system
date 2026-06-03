/**
 * 诊断管理列表页面
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Space,
  Button,
  Input,
  Select,
  Tag,
  Modal,
  message,
  Breadcrumb,
  Divider,
  Statistic,
  Row,
  Col,
  Progress,
  Badge,
  Tooltip,
  Popconfirm,
  Empty,
  Typography,
  DatePicker,
} from 'antd';
import {
  FileTextOutlined,
  ThunderboltOutlined,
  SearchOutlined,
  PlusOutlined,
  EyeOutlined,
  DeleteOutlined,
  ExportOutlined,
  HomeOutlined,
  CalendarOutlined,
  UserOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import dayjs from 'dayjs';
import { useNavigate } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import type { EChartOption } from 'echarts';

const { Title } = Typography;
const { RangePicker } = DatePicker;
const MotionCard = motion(Card);

interface DiagnosisRecord {
  id: number;
  report_no: string;
  patient_name: string;
  patient_no: string;
  exam_date: string;
  birads: string;
  conclusion: string;
  doctor: string;
  status: 'draft' | 'completed' | 'approved';
  created_at: string;
}

const DiagnosisList: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<DiagnosisRecord[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterBirads, setFilterBirads] = useState<string>('all');

  // 统计数据
  const stats = {
    total: 156,
    thisMonth: 45,
    birads4Plus: 12,
    pending: 8,
  };

  // BI-RADS 分级分布图
  const biradsDistributionOption: EChartOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}例 ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: 'BI-RADS 分级',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['55%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
          },
        },
        data: [
          { value: 35, name: 'BI-RADS 1', itemStyle: { color: '#10b981' } },
          { value: 52, name: 'BI-RADS 2', itemStyle: { color: '#3b82f6' } },
          { value: 38, name: 'BI-RADS 3', itemStyle: { color: '#f59e0b' } },
          { value: 18, name: 'BI-RADS 4a', itemStyle: { color: '#f97316' } },
          { value: 8, name: 'BI-RADS 4b', itemStyle: { color: '#ef4444' } },
          { value: 3, name: 'BI-RADS 4c', itemStyle: { color: '#dc2626' } },
          { value: 2, name: 'BI-RADS 5', itemStyle: { color: '#7c3aed' } },
        ],
      },
    ],
  };

  // 诊断趋势图
  const trendOption: EChartOption = {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['诊断总数', 'BI-RADS 3+', '恶性确诊'],
      bottom: 0,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: ['1 月', '2 月', '3 月', '4 月', '5 月', '6 月'],
    },
    yAxis: {
      type: 'value',
      name: '例数',
    },
    series: [
      {
        name: '诊断总数',
        type: 'bar',
        data: [22, 28, 25, 30, 26, 25],
        itemStyle: {
          color: '#667eea',
          borderRadius: [6, 6, 0, 0],
        },
      },
      {
        name: 'BI-RADS 3+',
        type: 'bar',
        data: [10, 15, 12, 18, 14, 13],
        itemStyle: {
          color: '#f59e0b',
          borderRadius: [6, 6, 0, 0],
        },
      },
      {
        name: '恶性确诊',
        type: 'line',
        data: [2, 3, 2, 5, 3, 4],
        itemStyle: {
          color: '#ef4444',
        },
        lineStyle: {
          width: 3,
        },
        symbol: 'circle',
        symbolSize: 8,
      },
    ],
  };

  // 模拟数据
  useEffect(() => {
    const mockData: DiagnosisRecord[] = [
      {
        id: 1,
        report_no: 'D20260530001',
        patient_name: '张三',
        patient_no: 'P20260527001',
        exam_date: '2026-05-28',
        birads: '3',
        conclusion: '双侧乳腺增生，建议 6 个月随访',
        doctor: '王医生',
        status: 'completed',
        created_at: '2026-05-28T10:30:00',
      },
      {
        id: 2,
        report_no: 'D20260530002',
        patient_name: '李四',
        patient_no: 'P20260527002',
        exam_date: '2026-05-29',
        birads: '4a',
        conclusion: '右乳低回声结节，建议穿刺活检',
        doctor: '李医生',
        status: 'pending',
        created_at: '2026-05-29T14:20:00',
      },
      {
        id: 3,
        report_no: 'D20260530003',
        patient_name: '王五',
        patient_no: 'P20260527003',
        exam_date: '2026-05-27',
        birads: '2',
        conclusion: '左乳囊肿，定期复查',
        doctor: '张医生',
        status: 'completed',
        created_at: '2026-05-27T09:15:00',
      },
      {
        id: 4,
        report_no: 'D20260530004',
        patient_name: '赵六',
        patient_no: 'P20260527004',
        exam_date: '2026-05-26',
        birads: '4b',
        conclusion: '右乳实性结节，恶性可能，建议手术',
        doctor: '王医生',
        status: 'approved',
        created_at: '2026-05-26T16:45:00',
      },
    ];
    setDataSource(mockData);
  }, []);

  const biradsConfig: any = {
    '1': { color: 'success', text: '阴性', icon: '✅' },
    '2': { color: 'blue', text: '良性', icon: '🔵' },
    '3': { color: 'warning', text: '可能良性', icon: '⚠️' },
    '4a': { color: 'orange', text: '低度可疑', icon: '🟠' },
    '4b': { color: 'red', text: '中度可疑', icon: '🔴' },
    '4c': { color: 'red', text: '高度可疑', icon: '🚨' },
    '5': { color: 'purple', text: '高度提示恶性', icon: '🔴' },
  };

  const statusConfig: any = {
    draft: { color: 'default', text: '草稿', icon: <ClockCircleOutlined /> },
    completed: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
    approved: { color: 'blue', text: '已审核', icon: <CheckCircleOutlined /> },
  };

  const columns = [
    {
      title: '报告编号',
      dataIndex: 'report_no',
      key: 'report_no',
      width: 140,
      sorter: (a: any, b: any) => a.report_no.localeCompare(b.report_no),
    },
    {
      title: '患者信息',
      key: 'patient',
      width: 180,
      render: (_: any, record: DiagnosisRecord) => (
        <Space>
          <Badge
            count={null}
            indicator={
              <span
                className={`status-dot ${
                  parseInt(record.birads) >= 4 ? 'high-risk' : 'low-risk'
                }`}
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: parseInt(record.birads) >= 4 ? '#ef4444' : '#10b981',
                  display: 'inline-block',
                }}
              />
            }
          >
            <div>
              <div style={{ fontWeight: 600 }}>{record.patient_name}</div>
              <div style={{ fontSize: 12, color: '#999' }}>{record.patient_no}</div>
            </div>
          </Badge>
        </Space>
      ),
    },
    {
      title: '检查日期',
      dataIndex: 'exam_date',
      key: 'exam_date',
      width: 120,
      sorter: (a: any, b: any) => a.exam_date.localeCompare(b.exam_date),
      render: (date: string) => (
        <Space>
          <CalendarOutlined style={{ color: '#667eea' }} />
          {dayjs(date).format('YYYY-MM-DD')}
        </Space>
      ),
    },
    {
      title: 'BI-RADS 分级',
      dataIndex: 'birads',
      key: 'birads',
      width: 130,
      filters: [
        { text: 'BI-RADS 1', value: '1' },
        { text: 'BI-RADS 2', value: '2' },
        { text: 'BI-RADS 3', value: '3' },
        { text: 'BI-RADS 4a', value: '4a' },
        { text: 'BI-RADS 4b', value: '4b' },
        { text: 'BI-RADS 4c', value: '4c' },
        { text: 'BI-RADS 5', value: '5' },
      ],
      onFilter: (value: any, record: any) => record.birads === value,
      render: (birads: string) => {
        const config = biradsConfig[birads] || { color: 'default', text: birads, icon: '❓' };
        return (
          <Tag color={config.color} style={{ fontWeight: 600 }}>
            {config.icon} BI-RADS {birads}
          </Tag>
        );
      },
    },
    {
      title: '诊断结论',
      dataIndex: 'conclusion',
      key: 'conclusion',
      width: 250,
      ellipsis: true,
    },
    {
      title: '诊断医生',
      dataIndex: 'doctor',
      key: 'doctor',
      width: 120,
      render: (doctor: string) => (
        <Space>
          <UserOutlined />
          {doctor}
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      filters: [
        { text: '草稿', value: 'draft' },
        { text: '已完成', value: 'completed' },
        { text: '已审核', value: 'approved' },
      ],
      onFilter: (value: any, record: any) => record.status === value,
      render: (status: string) => {
        const config = statusConfig[status];
        return (
          <Space>
            {config.icon}
            <span style={{ color: config.color }}>{config.text}</span>
          </Space>
        );
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      fixed: 'right' as const,
      render: (_: any, record: DiagnosisRecord) => (
        <Space>
          <Tooltip title="查看报告">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/diagnosis/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="导出报告">
            <Button
              type="text"
              icon={<ExportOutlined />}
              onClick={() => handleExport(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确认删除"
            description={`确定删除报告 ${record.report_no} 吗？`}
            onConfirm={() => handleDelete(record)}
            okText="确认"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleExport = (record: DiagnosisRecord) => {
    message.info(`导出报告：${record.report_no}`);
  };

  const handleDelete = (record: DiagnosisRecord) => {
    message.success(`已删除报告 ${record.report_no}`);
    setDataSource(dataSource.filter((item) => item.id !== record.id));
  };

  const statCards = [
    {
      title: '总诊断数',
      value: stats.total,
      icon: <FileTextOutlined />,
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      trend: '+15%',
      color: 'blue',
    },
    {
      title: '本月诊断',
      value: stats.thisMonth,
      icon: <CalendarOutlined />,
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      trend: '+8%',
      color: 'pink',
    },
    {
      title: 'BI-RADS 4+',
      value: stats.birads4Plus,
      icon: <ExclamationCircleOutlined />,
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      trend: '+3%',
      color: 'warning',
    },
    {
      title: '待审核',
      value: stats.pending,
      icon: <ClockCircleOutlined />,
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      trend: '-5%',
      color: 'cyan',
    },
  ];

  return (
    <div className="diagnosis-list-container" style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        {statCards.map((stat, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <MotionCard
              style={{
                background: stat.gradient,
                color: '#fff',
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -5, scale: 1.02 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: 14, opacity: 0.9 }}>{stat.title}</div>
                  <div style={{ fontSize: 32, fontWeight: 'bold', marginTop: 8 }}>{stat.value}</div>
                  <div
                    style={{
                      fontSize: 12,
                      marginTop: 4,
                      opacity: 0.9,
                    }}
                  >
                    {stat.trend} 较上月
                  </div>
                </div>
                <div style={{ fontSize: 48, opacity: 0.3 }}>{stat.icon}</div>
              </div>
            </MotionCard>
          </Col>
        ))}
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} lg={12}>
          <MotionCard
            title={
              <Space>
                <FileTextOutlined style={{ color: '#667eea' }} />
                <span>BI-RADS 分级分布</span>
              </Space>
            }
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <ReactECharts option={biradsDistributionOption} style={{ height: 300 }} />
          </MotionCard>
        </Col>
        <Col xs={24} lg={12}>
          <MotionCard
            title={
              <Space>
                <ThunderboltOutlined style={{ color: '#f59e0b' }} />
                <span>诊断趋势</span>
              </Space>
            }
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <ReactECharts option={trendOption} style={{ height: 300 }} />
          </MotionCard>
        </Col>
      </Row>

      {/* 诊断列表 */}
      <MotionCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Breadcrumb
            items={[
              { key: 'home', href: '/', title: <><HomeOutlined /> 首页</> },
              { key: 'diagnosis', title: '诊断管理' },
            ]}
          />
          <Space>
            <Button icon={<ExportOutlined />}>
              导出全部
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/diagnosis/create')}
            >
              新建诊断
            </Button>
          </Space>
        </div>

        {/* 筛选区域 */}
        <div style={{ marginBottom: 16, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <Input.Search
            placeholder="搜索患者姓名/编号/报告号"
            style={{ width: 320 }}
            allowClear
            onSearch={(value) => console.log('Search:', value)}
          />
          <Select
            placeholder="BI-RADS 分级"
            style={{ width: 160 }}
            allowClear
            onChange={setFilterBirads}
            options={[
              { value: '1', label: 'BI-RADS 1' },
              { value: '2', label: 'BI-RADS 2' },
              { value: '3', label: 'BI-RADS 3' },
              { value: '4a', label: 'BI-RADS 4a' },
              { value: '4b', label: 'BI-RADS 4b' },
              { value: '4c', label: 'BI-RADS 4c' },
              { value: '5', label: 'BI-RADS 5' },
            ]}
          />
          <Select
            placeholder="状态"
            style={{ width: 160 }}
            allowClear
            onChange={setFilterStatus}
            options={[
              { value: 'draft', label: '草稿' },
              { value: 'completed', label: '已完成' },
              { value: 'approved', label: '已审核' },
            ]}
          />
          <RangePicker style={{ width: 240 }} />
          <Button icon={<SearchOutlined />}>
            搜索
          </Button>
        </div>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={dataSource}
          loading={loading}
          rowKey="id"
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            pageSize: 20,
          }}
          scroll={{ x: 1400 }}
          size="middle"
        />
      </MotionCard>
    </div>
  );
};

export default DiagnosisList;
