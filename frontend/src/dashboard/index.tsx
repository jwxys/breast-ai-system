import { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Tag, Spin, Empty, Timeline, Avatar, Button, Space, Badge, Tooltip } from 'antd';
import {
  UserOutlined,
  CalendarOutlined,
  WarningOutlined,
  FileTextOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  ThunderboltOutlined,
  HeartOutlined,
  ExperimentOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { motion } from 'framer-motion';
import { useAppStore } from '@/stores/appStore';
import { patientApi } from '@/api';
import type { EChartOption } from 'echarts';
import './index.css';

const MotionCard = motion(Card);

const Dashboard = () => {
  const { patientStats, patients, loading, fetchPatientStats, fetchPatients } = useAppStore();
  const [todoList, setTodoList] = useState([]);
  const [followupStats, setFollowupStats] = useState<any>({});

  useEffect(() => {
    loadData();
    loadTodoList();
    loadFollowupStats();
  }, []);

  const loadData = async () => {
    fetchPatientStats();
    fetchPatients({ page: 1, page_size: 10 });
  };

  const loadTodoList = () => {
    // 模拟待办事项
    setTodoList([
      {
        id: 1,
        type: 'followup',
        title: '张三 - 3 个月复查',
        time: '今天 14:30',
        priority: 'high',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhangsan',
      },
      {
        id: 2,
        type: 'report',
        title: '李四 - 超声报告审核',
        time: '今天 16:00',
        priority: 'medium',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=lisi',
      },
      {
        id: 3,
        type: 'diagnosis',
        title: '王五 - AI 诊断待确认',
        time: '明天 09:00',
        priority: 'high',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=wangwu',
      },
      {
        id: 4,
        type: 'visit',
        title: '赵六 - 术后首次随访',
        time: '明天 11:30',
        priority: 'medium',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhaoliu',
      },
    ]);
  };

  const loadFollowupStats = () => {
    setFollowupStats({
      today: 12,
      thisWeek: 45,
      thisMonth: 189,
      overdue: 8,
    });
  };

  // 统计卡片数据
  const statsCards = [
    {
      title: '总患者数',
      value: patientStats?.total || 1250,
      icon: <UserOutlined />,
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      trend: 12,
      trendLabel: '较上月',
    },
    {
      title: '今日随访',
      value: followupStats.today || 12,
      icon: <CalendarOutlined />,
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      trend: 5,
      trendLabel: '较昨日',
    },
    {
      title: '高风险患者',
      value: patientStats?.high_risk_count || 89,
      icon: <WarningOutlined />,
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      trend: -3,
      trendLabel: '较上月',
    },
    {
      title: '待审核报告',
      value: 12,
      icon: <FileTextOutlined />,
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      trend: 0,
      trendLabel: '待处理',
    },
  ];

  // BI-RADS 分布图配置
  const biradsOption: EChartOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}例 ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['1 类', '2 类', '3 类', '4A 类', '4B 类', '4C 类', '5 类'],
    },
    series: [
      {
        name: 'BI-RADS 分级',
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
            fontSize: 16,
            fontWeight: 'bold',
          },
          itemStyle: {
            shadowBlur: 20,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.3)',
          },
        },
        labelLine: {
          show: false,
        },
        data: [
          { value: 62, name: '1 类', itemStyle: { color: '#95d5b2' } },
          { value: 312, name: '2 类', itemStyle: { color: '#52b69a' } },
          { value: 375, name: '3 类', itemStyle: { color: '#45b8ac' } },
          { value: 250, name: '4A 类', itemStyle: { color: '#f9c74f' } },
          { value: 150, name: '4B 类', itemStyle: { color: '#f3722c' } },
          { value: 62, name: '4C 类', itemStyle: { color: '#f8961e' } },
          { value: 39, name: '5 类', itemStyle: { color: '#f94144' } },
        ],
      },
    ],
  };

  // 体质分布图配置
  const constitutionOption: EChartOption = {
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
      data: ['气郁质', '痰湿质', '血瘀质', '平和质', '气虚质', '阳虚质', '其他'],
      axisLabel: {
        interval: 0,
        rotate: 30,
        fontSize: 12,
      },
    },
    yAxis: {
      type: 'value',
      name: '患者数',
      axisLabel: {
        formatter: '{value}',
      },
    },
    series: [
      {
        name: '体质分布',
        type: 'bar',
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' },
          ]),
          borderRadius: [8, 8, 0, 0],
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 20,
            shadowColor: 'rgba(0,0,0,0.3)',
          },
        },
        data: [312, 285, 220, 198, 156, 89, 90],
        label: {
          show: true,
          position: 'top',
          formatter: '{c}人',
          fontSize: 12,
        },
      },
    ],
  };

  // 诊断准确率趋势
  const accuracyOption: EChartOption = {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['AI 诊断', '病理结果'],
      left: 'center',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['1 月', '2 月', '3 月', '4 月', '5 月', '6 月'],
    },
    yAxis: {
      type: 'value',
      name: '准确率 (%)',
      max: 100,
    },
    series: [
      {
        name: 'AI 诊断',
        type: 'line',
        smooth: true,
        data: [91.2, 92.5, 93.1, 93.8, 94.2, 94.6],
        itemStyle: {
          color: '#667eea',
        },
        lineStyle: {
          width: 3,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' },
          ]),
        },
        symbol: 'circle',
        symbolSize: 8,
      },
      {
        name: '病理结果',
        type: 'line',
        smooth: true,
        data: [92.0, 92.8, 93.5, 94.0, 94.5, 95.0],
        itemStyle: {
          color: '#f093fb',
        },
        lineStyle: {
          width: 3,
          type: 'dashed',
        },
        symbol: 'circle',
        symbolSize: 8,
      },
    ],
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      high: 'volcano',
      medium: 'orange',
      low: 'green',
    };
    return colors[priority as keyof typeof colors] || 'blue';
  };

  const getTypeIcon = (type: string) => {
    const icons: any = {
      followup: <CalendarOutlined />,
      report: <FileTextOutlined />,
      diagnosis: <ThunderboltOutlined />,
      visit: <HeartOutlined />,
    };
    return icons[type] || <ClockCircleOutlined />;
  };

  if (loading && !patientStats) {
    return (
      <div className="dashboard-loading">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* 统计卡片 */}
      <Row gutter={[20, 20]} className="stats-row">
        {statsCards.map((stat, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <MotionCard
              className="stat-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -5, transition: { duration: 0.2 } }}
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
                <div className={`stat-trend ${stat.trend >= 0 ? 'trend-up' : 'trend-down'}`}>
                  {stat.trend >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                  {Math.abs(stat.trend)}% {stat.trendLabel}
                </div>
              </div>
            </MotionCard>
          </Col>
        ))}
      </Row>

      {/* 图表区域 */}
      <Row gutter={[20, 20]} className="charts-row">
        {/* BI-RADS 分布 */}
        <Col xs={24} lg={12}>
          <MotionCard
            title={
              <Space>
                <ExperimentOutlined style={{ color: '#667eea' }} />
                <span>BI-RADS 分级分布</span>
              </Space>
            }
            className="chart-card"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <ReactECharts option={biradsOption} style={{ height: 400 }} />
          </MotionCard>
        </Col>

        {/* 体质分布 */}
        <Col xs={24} lg={12}>
          <MotionCard
            title={
              <Space>
                <UserOutlined style={{ color: '#f093fb' }} />
                <span>患者体质分布</span>
              </Space>
            }
            className="chart-card"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            <ReactECharts option={constitutionOption} style={{ height: 400 }} />
          </MotionCard>
        </Col>
      </Row>

      <Row gutter={[20, 20]} className="charts-row">
        {/* 诊断准确率 */}
        <Col xs={24} lg={12}>
          <MotionCard
            title={
              <Space>
                <ThunderboltOutlined style={{ color: '#4facfe' }} />
                <span>AI 诊断准确率趋势</span>
              </Space>
            }
            className="chart-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <ReactECharts option={accuracyOption} style={{ height: 350 }} />
          </MotionCard>
        </Col>

        {/* 待办事项 */}
        <Col xs={24} lg={12}>
          <MotionCard
            title={
              <Space>
                <ClockCircleOutlined style={{ color: '#fa709a' }} />
                <span>待办事项</span>
              </Space>
            }
            className="chart-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            extra={
              <Button type="primary" size="small" icon={<PlusOutlined />}>
                新建
              </Button>
            }
          >
            <Timeline className="todo-timeline">
              {todoList.map((todo: any) => (
                <Timeline.Item
                  key={todo.id}
                  dot={
                    <Badge
                      count={null}
                      indicator={<span className={`status-dot ${todo.priority}`} />}
                    />
                  }
                  color={getPriorityColor(todo.priority)}
                >
                  <div className="todo-item">
                    <div className="todo-avatar">
                      <Avatar src={todo.avatar} size={40} />
                    </div>
                    <div className="todo-content">
                      <div className="todo-header">
                        <span className="todo-icon">{getTypeIcon(todo.type)}</span>
                        <span className="todo-title">{todo.title}</span>
                      </div>
                      <div className="todo-meta">
                        <ClockCircleOutlined />
                        <span>{todo.time}</span>
                        <Tag color={getPriorityColor(todo.priority)} size="small">
                          {todo.priority === 'high' ? '高优先级' : '中优先级'}
                        </Tag>
                      </div>
                    </div>
                    <div className="todo-actions">
                      <Button size="small" type="primary">
                        处理
                      </Button>
                    </div>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </MotionCard>
        </Col>
      </Row>

      {/* 失访预警 */}
      <Row gutter={[20, 20]} className="charts-row">
        <Col xs={24}>
          <MotionCard
            title={
              <Space>
                <WarningOutlined style={{ color: '#f59e0b' }} />
                <span>失访预警</span>
              </Space>
            }
            className="chart-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <div className="followup-warning">
              <div className="warning-stats">
                <div className="warning-item">
                  <div className="warning-value">5.6%</div>
                  <div className="warning-label">当前失访率</div>
                </div>
                <div className="warning-divider" />
                <div className="warning-item">
                  <div className="warning-value">8</div>
                  <div className="warning-label">超期未随访</div>
                </div>
                <div className="warning-divider" />
                <div className="warning-item">
                  <div className="warning-value">45</div>
                  <div className="warning-label">本月应随访</div>
                </div>
              </div>
              <div className="warning-progress">
                <div className="progress-header">
                  <span>目标：&lt;5%</span>
                  <span className={5.6 < 5 ? 'text-success' : 'text-warning'}>
                    当前：5.6%
                  </span>
                </div>
                <Progress
                  percent={(5.6 / 10) * 100}
                  strokeColor={{
                    '0%': '#f59e0b',
                    '100%': '#ef4444',
                  }}
                  status="exception"
                  showInfo={false}
                />
              </div>
              <Table
                columns={[
                  {
                    title: '患者',
                    dataIndex: 'patient',
                    key: 'patient',
                    render: (name: string, record: any) => (
                      <Space>
                        <Avatar size="small" src={record.avatar} />
                        {name}
                      </Space>
                    ),
                  },
                  { title: '应随访日期', dataIndex: 'date', key: 'date' },
                  {
                    title: '超期天数',
                    dataIndex: 'days',
                    key: 'days',
                    render: (days: number) => (
                      <Tag color={days > 7 ? 'red' : 'orange'}>
                        {days}天
                      </Tag>
                    ),
                  },
                  {
                    title: '风险等级',
                    dataIndex: 'risk',
                    key: 'risk',
                    render: (risk: string) => (
                      <Badge
                        count={null}
                        indicator={<span className={`status-dot ${risk}`} />}
                      />
                    ),
                  },
                  {
                    title: '操作',
                    key: 'action',
                    render: () => (
                      <Button size="small" type="link">
                        立即随访
                      </Button>
                    ),
                  },
                ]}
                dataSource={[
                  {
                    key: '1',
                    patient: '赵六',
                    date: '2026-05-15',
                    days: 12,
                    risk: 'high',
                    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhaoliu',
                  },
                  {
                    key: '2',
                    patient: '钱七',
                    date: '2026-05-18',
                    days: 9,
                    risk: 'medium',
                    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=qianqi',
                  },
                  {
                    key: '3',
                    patient: '孙八',
                    date: '2026-05-20',
                    days: 7,
                    risk: 'low',
                    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=sunba',
                  },
                ]}
                pagination={false}
                size="small"
              />
            </div>
          </MotionCard>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
