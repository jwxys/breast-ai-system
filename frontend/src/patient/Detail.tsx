/**
 * 患者详情页面
 */

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Descriptions, Tag, Space, Breadcrumb, Table } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';

const PatientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // 诊断历史数据
  const diagnosisHistory = [
    { key: '1', date: '2026-05-15', birads: '3', status: 'completed' },
    { key: '2', date: '2026-04-20', birads: '2', status: 'completed' },
    { key: '3', date: '2026-03-10', birads: '3', status: 'completed' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          { title: '患者管理', href: '/patient' },
          { title: `详情 ${id}` },
        ]}
      />

      <Card
        title="患者详情"
        extra={
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/patient')}>
            返回列表
          </Button>
        }
      >
        <Descriptions bordered column={2}>
          <Descriptions.Item label="患者 ID">{id}</Descriptions.Item>
          <Descriptions.Item label="姓名">张三</Descriptions.Item>
          <Descriptions.Item label="年龄">45</Descriptions.Item>
          <Descriptions.Item label="性别">女</Descriptions.Item>
          <Descriptions.Item label="联系电话">138****1234</Descriptions.Item>
          <Descriptions.Item label="家族史">
            <Tag color="red">有</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="初诊日期">2026-03-10</Descriptions.Item>
          <Descriptions.Item label="最近随访">2026-05-15</Descriptions.Item>
        </Descriptions>

        <div style={{ marginTop: 24 }}>
          <h3>诊断历史</h3>
          <Table
            dataSource={diagnosisHistory}
            columns={[
              { title: '日期', dataIndex: 'date', key: 'date' },
              { title: 'BI-RADS', dataIndex: 'birads', key: 'birads' },
              {
                title: '状态',
                dataIndex: 'status',
                key: 'status',
                render: (status: string) => <Tag color="green">{status}</Tag>,
              },
              {
                title: '操作',
                key: 'action',
                render: () => <Button type="link">查看详情</Button>,
              },
            ]}
            pagination={false}
          />
        </div>

        <Space style={{ marginTop: 24 }}>
          <Button type="primary">新建诊断</Button>
          <Button>编辑信息</Button>
          <Button>设置随访</Button>
        </Space>
      </Card>
    </div>
  );
};

export default PatientDetail;
