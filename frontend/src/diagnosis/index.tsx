/**
 * 优化的诊断管理页面
 * 
 * 功能:
 * - 诊断列表 (搜索/筛选/分页)
 * - BI-RADS 分级可视化
 * - 快速操作
 * - 批量操作
 */

import React, { useState } from 'react';
import { Card, Table, Button, Tag, Space, Input, Select, Row, Col, Typography, Empty, Badge, theme } from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  FilterOutlined,
  FileTextOutlined,
  FileImageOutlined,
  ExportOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;
const { Search } = Input;

// 类型定义
interface DiagnosisRecord {
  key: string;
  id: string;
  patientName: string;
  patientAge: number;
  reportNo: string;
  lesionLocation: string;
  birads: string;
  malignancyRisk: number;
  aiConfidence: number;
  status: 'completed' | 'pending' | 'review';
  createdAt: string;
  actions?: any;
}

// 模拟数据
const mockData: DiagnosisRecord[] = [
  {
    key: '1',
    id: 'D2026060501',
    patientName: '张三',
    patientAge: 45,
    reportNo: 'R20260605001',
    lesionLocation: '左乳外上象限',
    birads: '4A',
    malignancyRisk: 15.3,
    aiConfidence: 92.5,
    status: 'completed',
    createdAt: '2026-06-05 10:30',
  },
  {
    key: '2',
    id: 'D2026060502',
    patientName: '李四',
    patientAge: 52,
    reportNo: 'R20260605002',
    lesionLocation: '右乳内上象限',
    birads: '3',
    malignancyRisk: 3.2,
    aiConfidence: 88.7,
    status: 'pending',
    createdAt: '2026-06-05 09:15',
  },
  {
    key: '3',
    id: 'D2026060401',
    patientName: '王五',
    patientAge: 38,
    reportNo: 'R20260604001',
    lesionLocation: '左乳外下象限',
    birads: '2',
    malignancyRisk: 0.5,
    aiConfidence: 95.2,
    status: 'completed',
    createdAt: '2026-06-04 16:20',
  },
];

const DiagnosisList: React.FC = () => {
  const navigate = useNavigate();
  const { token } = theme.useToken();
  const [searchText, setSearchText] = useState('');
  const [filterBirads, setFilterBirads] = useState<string>();

  // BI-RADS 分级颜色
  const getBiradsColor = (birads: string) => {
    const map: Record<string, string> = {
      '0': 'gray',
      '1': 'green',
      '2': 'green',
      '3': 'blue',
      '4A': 'orange',
      '4B': 'orange',
      '4C': 'red',
      '5': 'red',
      '6': 'purple',
    };
    return map[birads] || 'default';
  };

  // 风险等级标签
  const getRiskLevel = (risk: number) => {
    if (risk >= 50) return { color: 'red', text: '高风险' };
    if (risk >= 20) return { color: 'orange', text: '中风险' };
    if (risk >= 5) return { color: 'blue', text: '低风险' };
    return { color: 'green', text: '极低风险' };
  };

  // 表格列配置
  const columns = [
    {
      title: '报告编号',
      dataIndex: 'reportNo',
      key: 'reportNo',
      fixed: 'left',
      width: 140,
    },
    {
      title: '患者姓名',
      dataIndex: 'patientName',
      key: 'patientName',
      width: 100,
      render: (name: string, record: DiagnosisRecord) => (
        <Space>
          <span>{name}</span>
          <Tag color="blue" style={{ fontSize: 10 }}>{record.patientAge}岁</Tag>
        </Space>
      ),
    },
    {
      title: '病灶位置',
      dataIndex: 'lesionLocation',
      key: 'lesionLocation',
      width: 120,
      ellipsis: true,
    },
    {
      title: 'BI-RADS',
      dataIndex: 'birads',
      key: 'birads',
      width: 90,
      render: (birads: string) => (
        <Badge
          count={birads}
          style={{
            backgroundColor: getBiradsColor(birads) === 'red' ? '#f5222d' :
                           getBiradsColor(birads) === 'orange' ? '#fa8c16' :
                           getBiradsColor(birads) === 'blue' ? '#1890ff' :
                           getBiradsColor(birads) === 'green' ? '#52c41a' : '#d9d9d9',
            fontSize: 12,
          }}
        />
      ),
    },
    {
      title: '恶性风险',
      dataIndex: 'malignancyRisk',
      key: 'malignancyRisk',
      width: 100,
      render: (risk: number) => {
        const { color, text } = getRiskLevel(risk);
        return (
          <Space>
            <Tag color={color}>{risk.toFixed(1)}%</Tag>
            <span style={{ fontSize: 12, color: '#999' }}>{text}</span>
          </Space>
        );
      },
    },
    {
      title: 'AI 置信度',
      dataIndex: 'aiConfidence',
      key: 'aiConfidence',
      width: 100,
      render: (confidence: number) => (
        <span style={{ color: confidence >= 90 ? '#52c41a' : confidence >= 70 ? '#fa8c16' : '#f5222d' }}>
          {confidence.toFixed(1)}%
        </span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      render: (status: string) => {
        const map: Record<string, { color: string; text: string }> = {
          completed: { color: 'green', text: '已完成' },
          pending: { color: 'orange', text: '待审核' },
          review: { color: 'blue', text: '需复核' },
        };
        const config = map[status] || { color: 'gray', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 160,
      sorter: (a: any, b: any) => a.createdAt.localeCompare(b.createdAt),
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 220,
      render: (_: any, record: DiagnosisRecord) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<FileTextOutlined />}
            onClick={() => navigate(`/diagnosis/${record.id}`)}
          >
            详情
          </Button>
          <Button
            type="link"
            size="small"
            icon={<FileImageOutlined />}
            onClick={() => navigate(`/ultrasound?reportNo=${record.reportNo}`)}
          >
            影像
          </Button>
        </Space>
      ),
    },
  ];

  // 筛选后的数据
  const filteredData = mockData.filter(item => {
    const matchSearch = !searchText || 
      item.patientName.includes(searchText) ||
      item.reportNo.includes(searchText);
    const matchFilter = !filterBirads || item.birads === filterBirads;
    return matchSearch && matchFilter;
  });

  return (
    <div style={{ padding: 24 }}>
      {/* 页面头部 */}
      <div style={{ marginBottom: 24 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={3} style={{ margin: 0 }}>
              <FileTextOutlined style={{ marginRight: 8 }} />
              诊断管理
            </Title>
          </Col>
          <Col>
            <Space>
              <Button icon={<ExportOutlined />}>导出</Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/diagnosis/create')}
              >
                新建诊断
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 筛选区域 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={8}>
            <Search
              placeholder="搜索患者姓名/报告编号"
              allowClear
              onSearch={setSearchText}
              onChange={(e) => setSearchText(e.target.value)}
              prefix={<SearchOutlined />}
              style={{ width: '100%' }}
            />
          </Col>
          <Col span={6}>
            <Select
              placeholder="BI-RADS 分级"
              allowClear
              style={{ width: '100%' }}
              onChange={setFilterBirads}
              options={[
                { value: '0', label: '0 - 需进一步评估' },
                { value: '1', label: '1 - 阴性' },
                { value: '2', label: '2 - 良性' },
                { value: '3', label: '3 - 可能良性' },
                { value: '4A', label: '4A - 低度可疑' },
                { value: '4B', label: '4B - 中度可疑' },
                { value: '4C', label: '4C - 高度可疑' },
                { value: '5', label: '5 - 恶性' },
              ]}
            />
          </Col>
        </Row>
      </Card>

      {/* 数据表格 */}
      <Card>
        {filteredData.length > 0 ? (
          <Table
            columns={columns}
            dataSource={filteredData}
            scroll={{ x: 1200 }}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条`,
            }}
            rowSelection={{
              type: 'checkbox',
              onChange: (selectedRowKeys: any) => {
                console.log('已选择:', selectedRowKeys);
              },
            }}
          />
        ) : (
          <Empty
            description="暂无诊断数据"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" onClick={() => navigate('/diagnosis/create')}>
              创建第一个诊断
            </Button>
          </Empty>
        )}
      </Card>

      {/* 统计信息 */}
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic title="今日诊断" value={12} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="待审核" value={5} valueStyle={{ color: '#fa8c16' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="BI-RADS 4+" value={8} valueStyle={{ color: '#f5222d' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="平均置信度" value={91.2} suffix="%" valueStyle={{ color: '#52c41a' }} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DiagnosisList;
