/**
 * 统计分析看板页面
 */

import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Tag, Spin } from 'antd';
import { BarChartOutlined, CheckCircleOutlined, RobotOutlined, FileTextOutlined, WarningOutlined } from '@ant-design/icons';
import { Bar } from '@ant-design/charts';

const StatisticsDashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [statsData, setStatsData] = useState<any>(null);

  const loadStats = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/statistics/dashboard?days=30');
      const data = await response.json();
      setStatsData(data.data);
    } catch (error) {
      console.error('加载统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadStats(); }, []);

  const biradsChartConfig = {
    data: statsData?.birads_distribution 
      ? Object.entries(statsData.birads_distribution.distribution).map(([key, value]) => ({
          type: `BI-RADS ${key}`,
          value,
        }))
      : [],
    xField: 'type',
    yField: 'value',
    color: ['#2ca02c', '#98df8a', '#1f77b4', '#17becf', '#ff7f0e', '#ffbb78', '#d62728', '#ff9896', '#9467bd'],
  };

  const accuracyMetrics = statsData?.accuracy_metrics || {};
  const qualityMetrics = statsData?.quality_control || {};

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 60 }}><Spin size="large" tip="加载统计数据..." /></div>;
  }

  return (
    <div className="statistics-dashboard">
      {/* 核心指标 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="AI 使用率" value={qualityMetrics.ai_usage_rate || 0} suffix="%" valueStyle={{ color: '#1890ff' }} prefix={<RobotOutlined />} />
            <Progress percent={qualityMetrics.ai_usage_rate || 0} status={(qualityMetrics.ai_usage_rate || 0) > 50 ? 'success' : 'normal'} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="报告完整率" value={qualityMetrics.report_complete_rate || 0} suffix="%" valueStyle={{ color: '#52c41a' }} prefix={<FileTextOutlined />} />
            <Progress percent={qualityMetrics.report_complete_rate || 0} status="success" />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="AI 准确率" value={(accuracyMetrics.accuracy || 0) * 100} suffix="%" valueStyle={{ color: '#faad14' }} prefix={<CheckCircleOutlined />} />
            <Progress percent={(accuracyMetrics.accuracy || 0) * 100} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="活检率" value={qualityMetrics.biopsy_rate || 0} suffix="%" valueStyle={{ color: '#f5222d' }} prefix={<WarningOutlined />} />
            <Progress percent={qualityMetrics.biopsy_rate || 0} status={(qualityMetrics.biopsy_rate || 0) > 80 ? 'success' : 'warning'} />
          </Card>
        </Col>
      </Row>

      {/* BI-RADS 分布 */}
      <Card title="BI-RADS 分级分布" style={{ marginBottom: 16 }}>
        <Bar {...biradsChartConfig} height={300} />
      </Card>

      {/* 准确率详情 */}
      <Card title="AI 诊断准确率">
        <Table
          size="small"
          pagination={false}
          dataSource={[
            { metric: '准确率', value: (accuracyMetrics.accuracy * 100).toFixed(1) },
            { metric: '敏感度', value: (accuracyMetrics.sensitivity * 100).toFixed(1) },
            { metric: '特异度', value: (accuracyMetrics.specificity * 100).toFixed(1) },
          ]}
          columns={[
            { title: '指标', dataIndex: 'metric' },
            { title: '数值', dataIndex: 'value', render: (val: string) => `${val}%` },
          ]}
        />
      </Card>
    </div>
  );
};

export default StatisticsDashboard;
