import React, { useState } from 'react';
import { Card, Form, Input, Button, Switch, Select, Space, message, Divider, Alert } from 'antd';
import { SaveOutlined, SettingOutlined } from '@ant-design/icons';

const { Option } = Select;

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    setLoading(true);
    // 模拟保存
    setTimeout(() => {
      message.success('设置保存成功');
      setLoading(false);
    }, 1000);
  };

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <Alert
        message="系统设置"
        description="配置系统参数和 AI 模型设置"
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Card title="AI 模型配置" style={{ marginBottom: 16 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            kimi_api_enabled: true,
            kimi_api_key: 'sk-********',
            model_provider: 'kimi',
          }}
        >
          <Form.Item
            name="model_provider"
            label="默认 AI 模型"
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="kimi">Kimi AI (推荐)</Option>
              <Option value="qwen">Qwen-7B (本地)</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="kimi_api_enabled"
            label="启用 Kimi API"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="kimi_api_key"
            label="Kimi API Key"
            rules={[{ required: true }]}
          >
            <Input.Password placeholder="sk-xxxxxxxx" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                保存配置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card title="系统设置" style={{ marginBottom: 16 }}>
        <Form
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            system_name: '乳腺 AI 辅助诊断系统',
            max_upload_size: 50,
          }}
        >
          <Form.Item
            name="system_name"
            label="系统名称"
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="max_upload_size"
            label="最大上传大小 (MB)"
          >
            <Input type="number" min={1} max={100} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} icon={<SettingOutlined />}>
              保存设置
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default SettingsPage;
