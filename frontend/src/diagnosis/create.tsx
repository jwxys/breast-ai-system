/**
 * 诊断创建页面
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button, Form, Input, Select, Breadcrumb } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';

const { TextArea } = Input;

const DiagnosisCreate: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const onFinish = (values: any) => {
    console.log('诊断数据:', values);
    // TODO: 调用 API 创建诊断
    navigate('/diagnosis');
  };

  return (
    <div style={{ padding: 24 }}>
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          { title: '诊断管理', href: '/diagnosis' },
          { title: '新建诊断' },
        ]}
      />

      <Card
        title="新建诊断"
        extra={
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/diagnosis')}>
            返回列表
          </Button>
        }
      >
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item label="患者 ID" name="patientId" rules={[{ required: true, message: '请输入患者 ID' }]}>
            <Input placeholder="请输入患者 ID" />
          </Form.Item>

          <Form.Item label="检查编号" name="examId" rules={[{ required: true, message: '请输入检查编号' }]}>
            <Input placeholder="请输入检查编号" />
          </Form.Item>

          <Form.Item label="病灶位置" name="location" rules={[{ required: true, message: '请选择病灶位置' }]}>
            <Select placeholder="请选择病灶位置">
              <Select.Option value="left_upper_outer">左乳外上象限</Select.Option>
              <Select.Option value="left_upper_inner">左乳内上象限</Select.Option>
              <Select.Option value="left_lower_outer">左乳外下象限</Select.Option>
              <Select.Option value="left_lower_inner">左乳内下象限</Select.Option>
              <Select.Option value="right_upper_outer">右乳外上象限</Select.Option>
              <Select.Option value="right_upper_inner">右乳内上象限</Select.Option>
              <Select.Option value="right_lower_outer">右乳外下象限</Select.Option>
              <Select.Option value="right_lower_inner">右乳内下象限</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="病灶大小" name="size">
            <Input placeholder="例如：12.5 × 8.3 mm" />
          </Form.Item>

          <Form.Item label="影像所见" name="findings">
            <TextArea rows={4} placeholder="描述超声影像所见特征" />
          </Form.Item>

          <Form.Item label="印象" name="impression">
            <TextArea rows={3} placeholder="诊断印象" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit">
              提交诊断
            </Button>
            <Button style={{ marginLeft: 8 }} onClick={() => navigate('/diagnosis')}>
              取消
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default DiagnosisCreate;
