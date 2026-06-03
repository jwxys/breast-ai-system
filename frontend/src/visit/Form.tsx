/**
 * 随访新建页面
 */
import React, { useState } from 'react';
import {
  Form,
  Input,
  Select,
  DatePicker,
  TimePicker,
  Card,
  Button,
  Space,
  Breadcrumb,
  message,
  Divider,
  Row,
  Col,
  Radio,
  Checkbox,
  AutoComplete,
} from 'antd';
import {
  HomeOutlined,
  CalendarOutlined,
  UserOutlined,
  PhoneOutlined,
  VideoCameraOutlined,
  FileTextOutlined,
  SaveOutlined,
  ReloadOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import dayjs from 'dayjs';
import { visitApi } from '@/api';
import type { VisitCreate } from '@/types';

const { TextArea } = Input;
const { Option } = Select;

const VisitCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [patientName, setPatientName] = useState('');

  // 从 URL 获取患者 ID
  const patientId = searchParams.get('patientId');

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const formData: VisitCreate = {
        patient_id: parseInt(values.patient_id),
        visit_type: values.visit_type,
        visit_date: values.visit_date.toISOString(),
        purpose: values.purpose,
        method: values.method,
        doctor_id: values.doctor_id,
        notes: values.notes,
      };

      await visitApi.create(formData);
      message.success('随访创建成功');
      navigate('/visit');
    } catch (error: any) {
      message.error('创建失败：' + (error.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  // 随访方式选项
  const methodOptions = [
    { value: 'outpatient', label: '🏥 门诊随访', icon: <HomeOutlined /> },
    { value: 'phone', label: '📞 电话随访', icon: <PhoneOutlined /> },
    { value: 'video', label: '📹 视频随访', icon: <VideoCameraOutlined /> },
    { value: 'home', label: '🏠 家庭随访', icon: <HomeOutlined /> },
    { value: 'wechat', label: '💬 微信随访', icon: <MessageOutlined /> },
  ];

  // 随访类型选项
  const visitTypeOptions = [
    { value: 'initial', label: '🏥 初诊随访' },
    { value: 'followup', label: '🔄 复诊随访' },
    { value: 'postsurgery', label: '💊 术后随访' },
    { value: 'regular', label: '📋 常规随访' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          { key: 'home', href: '/', title: (<><HomeOutlined /> 首页</>) },
          { key: 'visit', href: '/visit', title: '随访管理' },
          { key: 'create', title: '新建随访' },
        ]}
      />

      <Card
        title={<><CalendarOutlined /> 新建随访</>}
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={() => form.resetFields()}>
              重置
            </Button>
            <Button type="primary" icon={<SaveOutlined />} onClick={() => form.submit()} loading={loading}>
              保存
            </Button>
          </Space>
        }
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            visit_date: dayjs().add(7, 'day'),
            method: 'outpatient',
            visit_type: 'regular',
          }}
        >
          {/* 患者选择 */}
          <Divider orientation="left"><UserOutlined /> 患者信息</Divider>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="patient_id"
                label="患者"
                rules={[{ required: true, message: '请选择患者' }]}
                initialValue={patientId || undefined}
              >
                <AutoComplete
                  placeholder="搜索患者姓名或编号"
                  filterOption={(inputValue, option) =>
                    (option?.label ?? '').toUpperCase().includes(inputValue.toUpperCase())
                  }
                  options={[
                    { value: '1', label: '张三 - P20260527001' },
                    { value: '2', label: '李四 - P20260527002' },
                    { value: '3', label: '王五 - P20260527003' },
                  ]}
                  allowClear
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="patient_name_display"
                label="患者姓名"
              >
                <Input
                  placeholder="选择患者后自动填充"
                  disabled
                  value={patientName}
                />
              </Form.Item>
            </Col>
          </Row>

          {/* 随访基本信息 */}
          <Divider orientation="left"><CalendarOutlined /> 随访安排</Divider>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="visit_type"
                label="随访类型"
                rules={[{ required: true, message: '请选择随访类型' }]}
              >
                <Select placeholder="请选择随访类型">
                  {visitTypeOptions.map(opt => (
                    <Option key={opt.value} value={opt.value}>
                      {opt.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="visit_date"
                label="随访日期"
                rules={[{ required: true, message: '请选择随访日期' }]}
              >
                <DatePicker
                  style={{ width: '100%' }}
                  format="YYYY-MM-DD"
                  placeholder="请选择"
                  disabledDate={(current) => current && current < dayjs().startOf('day')}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="visit_time"
                label="随访时间"
              >
                <TimePicker
                  style={{ width: '100%' }}
                  format="HH:mm"
                  placeholder="请选择"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="method"
                label="随访方式"
                rules={[{ required: true, message: '请选择随访方式' }]}
              >
                <Select placeholder="请选择随访方式">
                  {methodOptions.map(opt => (
                    <Option key={opt.value} value={opt.value}>
                      {opt.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="doctor_id"
                label="负责医生"
                rules={[{ required: true, message: '请选择医生' }]}
              >
                <Select placeholder="请选择医生" showSearch allowClear>
                  <Option value="1">王医生</Option>
                  <Option value="2">李医生</Option>
                  <Option value="3">张医生</Option>
                  <Option value="4">赵医生</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="location"
                label="随访地点"
              >
                <Input placeholder="请输入随访地点" />
              </Form.Item>
            </Col>
          </Row>

          {/* 随访内容 */}
          <Divider orientation="left"><FileTextOutlined /> 随访内容</Divider>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="purpose"
                label="随访目的"
                rules={[{ required: true, message: '请输入随访目的' }]}
              >
                <TextArea
                  rows={3}
                  placeholder="请输入本次随访的主要目的，例如：术后恢复情况、化疗反应评估、定期复查等"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="items"
                label="随访项目"
              >
                <Checkbox.Group style={{ width: '100%' }}>
                  <Row>
                    <Col span={12}>
                      <Checkbox value="physical_exam">体格检查</Checkbox>
                    </Col>
                    <Col span={12}>
                      <Checkbox value="ultrasound">超声检查</Checkbox>
                    </Col>
                    <Col span={12}>
                      <Checkbox value="mammography">钼靶检查</Checkbox>
                    </Col>
                    <Col span={12}>
                      <Checkbox value="mri">MRI 检查</Checkbox>
                    </Col>
                    <Col span={12}>
                      <Checkbox value="biopsy">穿刺活检</Checkbox>
                    </Col>
                    <Col span={12}>
                      <Checkbox value="blood_test">血液检查</Checkbox>
                    </Col>
                  </Row>
                </Checkbox.Group>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="notes"
                label="备注说明"
              >
                <TextArea
                  rows={3}
                  placeholder="请输入其他需要注意的事项，例如：患者特殊需求、随访前准备等"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="reminder"
                label="随访提醒"
                initialValue={true}
              >
                <Checkbox>提前 1 天发送提醒</Checkbox>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="reminder_method"
                label="提醒方式"
              >
                <Checkbox.Group>
                  <Checkbox value="sms">短信</Checkbox>
                  <Checkbox value="phone">电话</Checkbox>
                  <Checkbox value="wechat">微信</Checkbox>
                </Checkbox.Group>
              </Form.Item>
            </Col>
          </Row>

          {/* 表单操作 */}
          <Divider />
          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => navigate('/visit')}>
                取消
              </Button>
              <Button icon={<ReloadOutlined />} onClick={() => form.resetFields()}>
                重置
              </Button>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={loading}
              >
                保存
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default VisitCreatePage;
