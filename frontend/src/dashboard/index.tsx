/**
 * 优化的仪表盘页面
 * 
 * 功能:
 * - 统计数据卡片
 * - 诊断趋势图表
 * - 待处理任务
 * - 快速入口
 */

import { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Tag, Space, Button, Avatar } from 'antd';
import {
  UserOutlined,
  FileTextOutlined,
  RiseOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  WarningOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { Column } from '@ant-design/charts';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalPatients: 0,
    totalDiagnoses: 0,
    pendingTasks: 0,
    completionRate: 0,
  });

  useEffect(() => {
    // 模拟加载数据
    setTimeout(() => {
      setStats({
        totalPatients: 1258,
        totalDiagnoses: 3421,
        pendingTasks: 12,
        completionRate: 94.5,
      });
      setLoading(false);
    }, 800);
  }, []);

  // 诊断趋势数据
  const trendData = [
    { month: '1 月', count: 156 },
    { month: '2 月', count: 189 },
    { month: '3 月', count: 234 },
    { month: '4 月', count: 287 },
    { month: '5 月', count: 321 },
    { month: '6 月', count: 356 },
  ];

  // 待处理任务
  const pendingTasks = [
    { key: '1', type: 'diagnosis', patient: '张三', priority: 'high', date: '2026-06-05' },
    { key: '2', type: 'followup', patient: '李四', priority: 'medium', date: '2026-06-04' },
    { key: '3', type: 'review', patient: '王五', priority: 'low', date: '2026-06-03' },
    { key: '4', type: 'diagnosis', patient: '赵六', priority: 'high', date: '2026-06-05' },
  ];

  // 最近诊断
  const recentDiagnoses = [
    { key: '1', patient: '陈七', birads: '3', status: 'completed', date: '2026-06-05' },
    { key: '2', patient: '周八', birads: '4A', status: 'pending', date: '2026-06-04' },
    { key: '3', patient: '吴九', birads: '2', status: 'completed', date: '2026-06-04' },
    { key: '4', patient: '郑十', birads: '4B', status: 'urgent', date: '2026-06-03' },
  ];

  const taskColumns = [
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const map: Record<string, string> = {
          diagnosis: '📋 诊断',
          followup: '📞 随访',
          review: '🔍 复核',
        };
        return map[type] || type;
      },
    },
    { title: '患者', dataIndex: 'patient', key: 'patient' },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: string) => {
        const colorMap: Record<string, string> = {
          high: 'red',
          medium: 'orange',
          low: 'blue',
        };
        return <Tag color={colorMap[priority]}>{priority.toUpperCase()}</Tag>;
      },
    },
    { title: '截止日期', dataIndex: 'date', key: 'date' },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="small">
          <Button type="link" size="small">处理</Button>
        </Space>
      ),
    },
  ];

  const diagnosisColumns = [
    { title: '患者', dataIndex: 'patient', key: 'patient' },
    {
      title: 'BI-RADS',
      dataIndex: 'birads',
      key: 'birads',
      render: (birads: string) => {
        const colorMap: Record<string, string> = {
          '1': 'green',
          '2': 'green',
          '3': 'blue',
          '4A': 'orange',
          '4B': 'orange',
          '4C': 'red',
          '5': 'red',
        };
        return <Tag color={colorMap[birads] || 'gray'}>{birads}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const map: Record<string, { color: string; text: string }> = {
          completed: { color: 'green', text: '已完成' },
          pending: { color: 'orange', text: '待处理' },
          urgent: { color: 'red', text: '紧急' },
        };
        const config = map[status] || { color: 'gray', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    { title: '日期', dataIndex: 'date', key: 'date' },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Button type="link" size="small" onClick={() => navigate(`/diagnosis/${record.key}`)}>
          详情
        </Button>
      ),
    },
  ];

  return (
    <div className="dashboard-page" style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="患者总数"
              value={stats.totalPatients}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3b82f6' }}
              loading={loading}
            />
            <Progress percent={12} strokeColor="#3b82f6" style={{ marginTop: 16 }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="诊断总数"
              value={stats.totalDiagnoses}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#10b981' }}
              loading={loading}
            />
            <Progress percent={28} strokeColor="#10b981" style={{ marginTop: 16 }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="待处理任务"
              value={stats.pendingTasks}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#f59e0b' }}
              loading={loading}
            />
            <div style={{ marginTop: 16, color: '#999', fontSize: 12 }}>
              <WarningOutlined /> 3 个紧急任务
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="完成率"
              value={stats.completionRate}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#10b981' }}
              loading={loading}
            />
            <Progress percent={stats.completionRate} strokeColor="#10b981" style={{ marginTop: 16 }} />
          </Card>
        </Col>
      </Row>

      {/* 诊断趋势图 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="📊 月度诊断趋势">
            <Column
              data={trendData}
              xField="month"
              yField="count"
              height={300}
              color={{
                type: 'linear',
                range: ['#3b82f6', '#2563eb'],
              }}
              columnStyle={{
                radius: [4, 4, 0, 0],
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* 待处理任务和最近诊断 */}
      <Row gutter={[16, 16]}>
        <Col span={24} lg={12}>
          <Card
            title={
              <Space>
                <ClockCircleOutlined />
                待处理任务
              </Space>
            }
            extra={
              <Button type="link" onClick={() => navigate('/tasks')}>
                查看全部
              </Button>
            }
          >
            <Table
              dataSource={pendingTasks}
              columns={taskColumns}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col span={24} lg={12}>
          <Card
            title={
              <Space>
                <FileTextOutlined />
                最近诊断
              </Space>
            }
            extra={
              <Button type="link" onClick={() => navigate('/diagnosis')}>
                查看全部
              </Button>
            }
          >
            <Table
              dataSource={recentDiagnoses}
              columns={diagnosisColumns}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      {/* 快速入口 */}
      <div style={{ marginTop: 24, textAlign: 'center' }}>
        <h3 style={{ marginBottom: 16 }}>快速操作</h3>
        <Space size="large">
          <Button
            type="primary"
            icon={<PlusOutlined />}
            size="large"
            onClick={() => navigate('/patient/create')}
          >
            新建患者
          </Button>
          <Button
            icon={<FileImageOutlined />}
            size="large"
            onClick={() => navigate('/ultrasound')}
          >
            上传影像
          </Button>
          <Button
            icon={<FileTextOutlined />}
            size="large"
            onClick={() => navigate('/diagnosis/create')}
          >
            创建诊断
          </Button>
        </Space>
      </div>
    </div>
  );
};

export default Dashboard;
