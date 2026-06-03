/**
 * 患者新建/编辑页面
 */
import React, { useEffect, useState } from 'react';
import {
  Form,
  Input,
  InputNumber,
  Select,
  DatePicker,
  Card,
  Button,
  Space,
  Breadcrumb,
  message,
  Divider,
  Row,
  Col,
  Radio,
} from 'antd';
import {
  HomeOutlined,
  UserOutlined,
  PhoneOutlined,
  FileTextOutlined,
  HeartOutlined,
  SaveOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import dayjs from 'dayjs';
import { patientApi } from '@/api';
import type { PatientCreate, PatientUpdate } from '@/types';

const { TextArea } = Input;
const { Option } = Select;

const PatientFormPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(!!id);

  const isEdit = !!id;

  useEffect(() => {
    if (isEdit) {
      loadPatient();
    }
  }, [id]);

  const loadPatient = async () => {
    if (!id) return;
    setInitialLoading(true);
    try {
      const data = await patientApi.get(parseInt(id));
      form.setFieldsValue({
        name: data.name,
        gender: data.gender,
        birth_date: dayjs(data.birth_date),
        id_card: data.id_card,
        phone: data.phone,
        email: data.email,
        address: data.address,
        constitution: data.constitution,
        constitution_score: data.constitution_score,
        zheng_type: data.zheng_type,
        zheng_severity: data.zheng_severity,
      });
    } catch (error) {
      message.error('加载患者信息失败');
    } finally {
      setInitialLoading(false);
    }
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const formData = {
        ...values,
        birth_date: values.birth_date.toISOString(),
        gender: values.gender || 'F',
      };

      if (isEdit) {
        await patientApi.update(parseInt(id!), formData as PatientUpdate);
        message.success('患者信息更新成功');
      } else {
        await patientApi.create(formData as PatientCreate);
        message.success('患者创建成功');
      }
      navigate(`/patient/${isEdit ? id : ''}`);
    } catch (error: any) {
      message.error(isEdit ? '更新失败：' + (error.message || '未知错误') : '创建失败');
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return (
      <div style={{ padding: 24 }}>
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40 }}>
            <Space size="large">
              <UserOutlined spin style={{ fontSize: 48, color: '#1890ff' }} />
              <div>加载中...</div>
            </Space>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          { key: 'home', href: '/', title: (<><HomeOutlined /> 首页</>) },
          { key: 'patient', href: '/patient', title: '患者管理' },
          { key: isEdit ? 'edit' : 'create', title: isEdit ? '编辑患者' : '新建患者' },
        ]}
      />

      <Card
        title={isEdit ? <><UserOutlined /> 编辑患者信息</> : <><UserOutlined /> 新建患者</>}
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
            gender: 'F',
            constitution_score: 0,
          }}
        >
          {/* 基本信息 */}
          <Divider orientation="left"><UserOutlined /> 基本信息</Divider>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="name"
                label="姓名"
                rules={[{ required: true, message: '请输入姓名' }]}
              >
                <Input placeholder="请输入患者姓名" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="gender"
                label="性别"
              >
                <Radio.Group>
                  <Radio value="F">女</Radio>
                  <Radio value="M">男</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="birth_date"
                label="出生日期"
                rules={[{ required: true, message: '请选择出生日期' }]}
              >
                <DatePicker
                  style={{ width: '100%' }}
                  format="YYYY-MM-DD"
                  placeholder="请选择"
                  showNow={false}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="id_card"
                label="身份证号"
                rules={[{ pattern: /^\d{17}[\dXx]?$/, message: '请输入正确的身份证号' }]}
              >
                <Input placeholder="请输入身份证号" maxLength={18} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="phone"
                label="联系电话"
                rules={[{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }]}
              >
                <Input placeholder="请输入手机号" maxLength={11} prefix={<PhoneOutlined />} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="email"
                label="电子邮箱"
                rules={[{ type: 'email', message: '请输入正确的邮箱' }]}
              >
                <Input placeholder="请输入邮箱" prefix={<FileTextOutlined />} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="address"
                label="居住地址"
              >
                <TextArea
                  rows={2}
                  placeholder="请输入详细居住地址"
                />
              </Form.Item>
            </Col>
          </Row>

          {/* 中医信息 */}
          <Divider orientation="left"><HeartOutlined /> 中医信息（可选）</Divider>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="constitution"
                label="体质类型"
              >
                <Select placeholder="请选择体质类型" allowClear>
                  <Option value="气郁质">🌸 气郁质</Option>
                  <Option value="痰湿质">💧 痰湿质</Option>
                  <Option value="血瘀质">🩸 血瘀质</Option>
                  <Option value="平和质">🌿 平和质</Option>
                  <Option value="气虚质">💨 气虚质</Option>
                  <Option value="阳虚质">☀️ 阳虚质</Option>
                  <Option value="阴虚质">🌙 阴虚质</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="constitution_score"
                label="体质评分"
              >
                <InputNumber
                  min={0}
                  max={100}
                  style={{ width: '100%' }}
                  placeholder="0-100"
                  formatter={value => `${value}%`}
                  parser={value => Number(value?.replace('%', ''))}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="zheng_type"
                label="中医证型"
              >
                <Select placeholder="请选择证型" allowClear>
                  <Option value="肝郁气滞">肝郁气滞</Option>
                  <Option value="痰凝气滞">痰凝气滞</Option>
                  <Option value="气滞血瘀">气滞血瘀</Option>
                  <Option value="冲任失调">冲任失调</Option>
                  <Option value="气血两虚">气血两虚</Option>
                  <Option value="脾肾阳虚">脾肾阳虚</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="zheng_severity"
                label="证型程度"
              >
                <Select placeholder="请选择" allowClear>
                  <Option value="轻度">轻度</Option>
                  <Option value="中度">中度</Option>
                  <Option value="重度">重度</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          {/* 表单操作 */}
          <Divider />
          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => navigate('/patient')}>
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

export default PatientFormPage;
