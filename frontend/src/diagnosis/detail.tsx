/**
 * 诊断详情页面
 */

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Descriptions, Tag, Space, Breadcrumb } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';

const DiagnosisDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div style={{ padding: 24 }}>
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          { title: '诊断管理', href: '/diagnosis' },
          { title: `详情 ${id}` },
        ]}
      />

      <Card
        title="诊断详情"
        extra={
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/diagnosis')}>
            返回列表
          </Button>
        }
      >
        <Descriptions bordered column={2}>
          <Descriptions.Item label="诊断 ID">{id}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color="green">已完成</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="BI-RADS 分级">4A</Descriptions.Item>
          <Descriptions.Item label="恶性风险">15.3%</Descriptions.Item>
          <Descriptions.Item label="病灶位置">左乳外上象限</Descriptions.Item>
          <Descriptions.Item label="病灶大小">12.5 × 8.3 mm</Descriptions.Item>
          <Descriptions.Item label="边缘特征">不规则</Descriptions.Item>
          <Descriptions.Item label="钙化">无</Descriptions.Item>
          <Descriptions.Item label="AI 置信度" span={2}>
            <Tag color="blue">92.5%</Tag>
          </Descriptions.Item>
        </Descriptions>

        <Space style={{ marginTop: 24 }}>
          <Button type="primary">生成报告</Button>
          <Button>导出 DICOM</Button>
          <Button>申请会诊</Button>
        </Space>
      </Card>
    </div>
  );
};

export default DiagnosisDetail;
