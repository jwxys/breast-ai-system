import { useEffect, useState } from 'react';
import { Card, Table, Space, Button, Input, Select, Tag, Modal, Form, DatePicker, TimePicker, InputNumber, Radio, Checkbox, Divider, Typography, Calendar, Badge, Row, Col, Timeline, Statistic, Progress, Tooltip, Popconfirm, message, Drawer, Descriptions, Empty, Steps } from 'antd';
import {
  CalendarOutlined,
  PlusOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  UserOutlined,
  FileTextOutlined,
  HeartOutlined,
  ThunderboltOutlined,
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
  PhoneOutlined,
  VideoCameraOutlined,
  HomeOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import dayjs from 'dayjs';
import ReactECharts from 'echarts-for-react';
import type { EChartOption } from 'echarts';
import './index.css';

const { Title, Text } = Typography;
const { Step } = Steps;
const MotionCard = motion(Card);

const VisitList = () => {
  const [loading, setLoading] = useState(false);
  const [followupStats, setFollowupStats] = useState({
    today: 12,
    thisWeek: 45,
    thisMonth: 189,
    overdue: 8,
    completionRate: 94.5,
  });
  const [filterType, setFilterType] = useState('all');

  // 随访统计数据
  const statCards = [
    {
      title: '今日随访',
      value: followupStats.today,
      icon: <CalendarOutlined />,
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      trend: '+5%',
      color: 'blue',
    },
    {
      title: '本周随访',
      value: followupStats.thisWeek,
      icon: <ClockCircleOutlined />,
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      trend: '+12%',
      color: 'pink',
    },
    {
      title: '本月随访',
      value: followupStats.thisMonth,
      icon: <FileTextOutlined />,
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      trend: '+8%',
      color: 'cyan',
    },
    {
      title: '超期未访',
      value: followupStats.overdue,
      icon: <ExclamationCircleOutlined />,
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      trend: '-3%',
      color: 'warning',
    },
  ];

  // 随访完成率趋势图
  const completionOption: EChartOption = {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['计划随访', '已完成', '完成率'],
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
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    },
    yAxis: [
      {
        type: 'value',
        name: '人数',
        position: 'left',
      },
      {
        type: 'value',
        name: '完成率',
        position: 'right',
        max: 100,
        axisLabel: {
          formatter: '{value}%',
        },
      },
    ],
    series: [
      {
        name: '计划随访',
        type: 'bar',
        data: [15, 18, 12, 20, 16, 8, 5],
        itemStyle: {
          color: '#667eea',
          borderRadius: [8, 8, 0, 0],
        },
      },
      {
        name: '已完成',
        type: 'bar',
        data: [14, 17, 11, 19, 15, 7, 4],
        itemStyle: {
          color: '#10b981',
          borderRadius: [8, 8, 0, 0],
        },
      },
      {
        name: '完成率',
        type: 'line',
        yAxisIndex: 1,
        data: [93.3, 94.4, 91.7, 95.0, 93.8, 87.5, 80.0],
        itemStyle: {
          color: '#f59e0b',
        },
        lineStyle: {
          width: 3,
        },
        symbol: 'circle',
        symbolSize: 8,
      },
    ],
  };

  // 随访方式分布
  const methodOption: EChartOption = {
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
        name: '随访方式',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['55%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
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
          { value: 156, name: '门诊随访', itemStyle: { color: '#667eea' } },
          { value: 89, name: '电话随访', itemStyle: { color: '#4facfe' } },
          { value: 67, name: '视频随访', itemStyle: { color: '#f093fb' } },
          { value: 45, name: '家庭随访', itemStyle: { color: '#10b981' } },
          { value: 23, name: '微信随访', itemStyle: { color: '#f59e0b' } },
        ],
      },
    ],
  };

  const columns = [
    {
      title: '患者信息',
      dataIndex: 'patient',
      key: 'patient',
      width: 200,
      render: (_: unknown, record: any) => (
        <Space>
          <Badge
            count={null}
            indicator={
              <span className={`status-dot ${record.riskLevel}`} />
            }
          >
            <div className="patient-cell">
              <div className="patient-name">{record.patientName}</div>
              <div className="patient-no">{record.patientNo}</div>
            </div>
          </Badge>
        </Space>
      ),
    },
    {
      title: '随访类型',
      dataIndex: 'visitType',
      key: 'visitType',
      width: 120,
      render: (type: string) => {
        const typeConfig: any = {
          initial: { color: 'blue', text: '初诊', icon: '🏥' },
          followup: { color: 'green', text: '复诊', icon: '🔄' },
          postsurgery: { color: 'purple', text: '术后', icon: '💊' },
          regular: { color: 'cyan', text: '常规', icon: '📋' },
        };
        const config = typeConfig[type] || { color: 'default', text: type, icon: '📝' };
        return (
          <Tag color={config.color}>
            {config.icon} {config.text}
          </Tag>
        );
      },
    },
    {
      title: '随访日期',
      dataIndex: 'visitDate',
      key: 'visitDate',
      width: 130,
      sorter: true,
      render: (date: string) => (
        <div className="visit-date">
          <CalendarOutlined style={{ marginRight: 6, color: '#667eea' }} />
          {dayjs(date).format('YYYY-MM-DD')}
        </div>
      ),
    },
    {
      title: '随访方式',
      dataIndex: 'method',
      key: 'method',
      width: 120,
      render: (method: string) => {
        const methodConfig: any = {
          outpatient: { icon: <HomeOutlined />, color: '#667eea', text: '门诊' },
          phone: { icon: <PhoneOutlined />, color: '#4facfe', text: '电话' },
          video: { icon: <VideoCameraOutlined />, color: '#f093fb', text: '视频' },
          home: { icon: <HomeOutlined />, color: '#10b981', text: '家庭' },
          wechat: { icon: <MessageOutlined />, color: '#f59e0b', text: '微信' },
        };
        const config = methodConfig[method] || { icon: null, color: '#94a3b8', text: method };
        return (
          <Space>
            <span style={{ color: config.color }}>{config.icon}</span>
            {config.text}
          </Space>
        );
      },
    },
    {
      title: '负责医生',
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
        { text: '待随访', value: 'pending' },
        { text: '已完成', value: 'completed' },
        { text: '已取消', value: 'cancelled' },
      ],
      onFilter: (value: string, record: any) => record.status === value,
      render: (status: string) => {
        const statusConfig: any = {
          pending: { color: 'warning', text: '待随访', icon: <ClockCircleOutlined /> },
          completed: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
          cancelled: { color: 'error', text: '已取消', icon: <CloseCircleOutlined /> },
        };
        const config = statusConfig[status];
        return (
          <Space>
            <span style={{ color: config.color }}>{config.icon}</span>
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
      render: (_: unknown, record: any) => (
        <Space className="action-buttons">
          {record.status === 'pending' && (
            <>
              <Button
                size="small"
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={() => handleComplete(record)}
              >
                完成
              </Button>
              <Button
                size="small"
                icon={<PhoneOutlined />}
                onClick={() => handleContact(record)}
              >
                联系
              </Button>
            </>
          )}
          {record.status === 'completed' && (
            <Button
              size="small"
              icon={<FileTextOutlined />}
              onClick={() => handleViewRecord(record)}
            >
              查看记录
            </Button>
          )}
          <Popconfirm
            title="确认取消"
            description="确定取消此随访吗？"
            onConfirm={() => handleCancel(record)}
            okText="确认"
            cancelText="取消"
          >
            <Button size="small" danger icon={<CloseCircleOutlined />}>
              取消
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 模拟数据
  const dataSource = [
    {
      key: '1',
      patientName: '张三',
      patientNo: 'P20260527001',
      riskLevel: 'high',
      visitType: 'followup',
      visitDate: '2026-05-28',
      method: 'outpatient',
      doctor: '王医生',
      status: 'pending',
    },
    {
      key: '2',
      patientName: '李四',
      patientNo: 'P20260527002',
      riskLevel: 'medium',
      visitType: 'postsurgery',
      visitDate: '2026-05-28',
      method: 'video',
      doctor: '李医生',
      status: 'pending',
    },
    {
      key: '3',
      patientName: '王五',
      patientNo: 'P20260527003',
      riskLevel: 'low',
      visitType: 'regular',
      visitDate: '2026-05-27',
      method: 'phone',
      doctor: '张医生',
      status: 'completed',
    },
  ];

  const handleComplete = (record: any) => {
    message.success(`已完成患者 ${record.patientName} 的随访`);
  };

  const handleContact = (record: any) => {
    message.info(`正在联系患者 ${record.patientName}...`);
  };

  const handleViewRecord = (record: any) => {
    message.info('查看随访记录');
  };

  const handleCancel = (record: any) => {
    message.success(`已取消患者 ${record.patientName} 的随访`);
  };

  return (
    <div className="visit-list-container">
      {/* 统计卡片 */}
      <Row gutter={[20, 20]} className="stats-row">
        {statCards.map((stat, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <MotionCard
              className="stat-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -5 }}
            >
              <div
                className="stat-icon"
                style={{ background: stat.gradient }}
              >
                {stat.icon}
              </div>
              <div className="stat-content">
                <div className="stat-title">{stat.title}</div>
                <div className="stat-value">{stat.value}</div>
                <div className={`stat-trend ${stat.trend.startsWith('+') ? 'trend-up' : 'trend-down'}`}>
                  {stat.trend} 较上周
                </div>
              </div>
            </MotionCard>
          </Col>
        ))}
      </Row>

      {/* 图表区域 */}
      <Row gutter={[20, 20]} className="charts-row">
        <Col xs={24} lg={16}>
          <MotionCard
            title={
              <Space>
                <ClockCircleOutlined style={{ color: '#667eea' }} />
                <span>随访完成率趋势</span>
              </Space>
            }
            className="chart-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <ReactECharts option={completionOption} style={{ height: 350 }} />
          </MotionCard>
        </Col>
        <Col xs={24} lg={8}>
          <MotionCard
            title={
              <Space>
                <VideoCameraOutlined style={{ color: '#f093fb' }} />
                <span>随访方式分布</span>
              </Space>
            }
            className="chart-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <ReactECharts option={methodOption} style={{ height: 350 }} />
          </MotionCard>
        </Col>
      </Row>

      {/* 随访列表 */}
      <MotionCard
        className="list-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <div className="card-header">
          <div className="header-left">
            <Title level={2} className="page-title">
              <CalendarOutlined className="title-icon" />
              随访管理
            </Title>
          </div>
          <div className="header-right">
            <Space>
              <Button icon={<ExportOutlined />}>
                导出
              </Button>
              <Button
                type="primary"
                size="large"
                icon={<PlusOutlined />}
                onClick={() => navigate('/visit/create')}
              >
                新建随访
              </Button>
            </Space>
          </div>
        </div>

        {/* 筛选区域 */}
        <div className="filter-section">
          <div className="filter-row">
            <Search
              placeholder="搜索患者姓名/编号"
              style={{ width: 320 }}
              allowClear
            />
            <Select
              placeholder="随访类型"
              style={{ width: 160 }}
              allowClear
              options={[
                { value: 'initial', label: '🏥 初诊' },
                { value: 'followup', label: '🔄 复诊' },
                { value: 'postsurgery', label: '💊 术后' },
                { value: 'regular', label: '📋 常规' },
              ]}
            />
            <Select
              placeholder="随访方式"
              style={{ width: 160 }}
              allowClear
              options={[
                { value: 'outpatient', label: '🏥 门诊' },
                { value: 'phone', label: '📞 电话' },
                { value: 'video', label: '📹 视频' },
                { value: 'home', label: '🏠 家庭' },
              ]}
            />
            <Select
              placeholder="状态"
              style={{ width: 160 }}
              allowClear
              options={[
                { value: 'pending', label: '⏰ 待随访' },
                { value: 'completed', label: '✅ 已完成' },
                { value: 'cancelled', label: '❌ 已取消' },
              ]}
            />
          </div>
          <div className="filter-info">
            <Space size="large">
              <span>完成率：<Progress type="line" percent={followupStats.completionRate} size="small" style={{ width: 100 }} /></span>
              <Divider type="vertical" />
              <span>本月已完成：<strong className="text-success">178</strong></span>
              <Divider type="vertical" />
              <span>平均满意度：<strong className="text-primary">4.8/5.0</strong></span>
            </Space>
          </div>
        </div>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={dataSource}
          loading={loading}
          rowKey="key"
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            pageSize: 20,
          }}
          scroll={{ x: 1200 }}
          size="middle"
        />
      </MotionCard>
    </div>
  );
};

export default VisitList;
