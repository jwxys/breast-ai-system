/**
 * 患者创建页面
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button, Form, Input, DatePicker, Radio, Breadcrumb } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

const PatientCreate: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const onFinish = (values: any) => {
    console.log('患者数据:', values);
    // TODO: 调用 API 创建患者
    navigate('/patient');
  };

  return (
    <div style={{ padding: 24 }}>
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          { title: '患者管理', href: '/patient' },
          { title: '新建患者' },
        ]}
      />

      <Card
        title="新建患者"
        extra={
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/patient')}>
            返回列表
          </Button>
        }
      >
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item label="姓名" name="name" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input placeholder="请输入患者姓名" />
          </Form.Item>

          <Form.Item label="性别" name="gender" rules={[{ required: true, message: '请选择性别' }]}>
            <Radio.Group>
              <Radio value="female">女</Radio>
              <Radio value="male">男</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item label="年龄" name="age" rules={[{ required: true, message: '请输入年龄' }]}>
            <Input type="number" placeholder="请输入年龄" style={{ width: 200 }} />
          </Form.Item>

          <Form.Item label="联系电话" name="phone" rules={[{ required: true, message: '请输入联系电话' }]}>
            <Input placeholder="请输入联系电话" />
          </Form.Item>

          <Form.Item label="身份证号" name="idCard">
            <Input placeholder="请输入身份证号" />
          </Form.Item>

          <Form.Item label="家族史" name="familyHistory" rules={[{ required: true, message: '请选择' }]}>
            <Radio.Group>
              <Radio value="yes">有</Radio>
              <Radio value="no">无</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item label="初诊日期" name="firstVisitDate">
            <DatePicker style={{ width: '100%' }} defaultValue={dayjs()} />
          </Form.Item>

          <Form.Item label="备注" name="remarks">
            <Input.TextArea rows={3} placeholder="备注信息" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit">
              提交
            </Button>
            <Button style={{ marginLeft: 8 }} onClick={() => navigate('/patient')}>
              取消
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default PatientCreate;
