import { useState } from 'react';
import { Card, Form, Input, Button, Select, DatePicker, InputNumber, Row, Col, Radio, Divider, message, Space, Steps, Typography, Upload } from 'antd';
import {
  ArrowLeftOutlined,
  UserOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  CheckOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import dayjs from 'dayjs';
import { patientApi } from '@/api';
import './Form.css';

const { Step } = Steps;
const { Title, Text } = Typography;

const MotionCard = motion(Card);

const PatientForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = !!id;
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: '基本信息',
      icon: <UserOutlined />,
      description: '患者身份信息',
    },
    // ⚠️ 中医信息步骤已移除 (2026-05-29)
    // 原因：无四诊信息采集（舌象、脉象），体质和证型判定无依据
    // 详见：docs/TCM_INTEGRATION_ANALYSIS_AND_FIX.md
    {
      title: '风险评估',
      icon: <ExperimentOutlined />,
      description: '风险等级评估',
    },
  ];

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      if (isEdit) {
        await patientApi.update(Number(id), values);
        message.success('更新成功');
      } else {
        await patientApi.create(values);
        message.success('创建成功');
      }
      navigate('/patient');
    } catch (error: any) {
      message.error(isEdit ? '更新失败' : '创建失败');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    try {
      const values = await form.validateFields();
      setCurrentStep(currentStep + 1);
    } catch (error) {
      message.error('请填写完整信息');
    }
  };

  const handlePrev = () => {
    setCurrentStep(currentStep - 1);
  };

  return (
    <div className="patient-form-container">
      <MotionCard
        className="form-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {/* 返回按钮 */}
        <Button
          className="back-btn"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/patient')}
        >
          返回列表
        </Button>

        {/* 标题 */}
        <div className="form-header">
          <Title level={2}>
            {isEdit ? '编辑患者信息' : '新建患者'}
          </Title>
          <Text type="secondary">
            {isEdit ? '更新患者档案信息' : '完善患者基本信息，建立电子档案'}
          </Text>
        </div>

        {/* 步骤条 */}
        <Steps
          current={currentStep}
          items={steps}
          className="form-steps"
          responsive
        />

        {/* 表单 */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          className="patient-form"
          autoComplete="off"
        >
          {/* 步骤 1: 基本信息 */}
          {currentStep === 0 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="step-content"
            >
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="name"
                    label="姓名"
                    rules={[{ required: true, message: '请输入姓名' }]}
                  >
                    <Input placeholder="请输入患者姓名" size="large" />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    name="gender"
                    label="性别"
                    rules={[{ required: true, message: '请选择性别' }]}
                    initialValue="F"
                  >
                    <Radio.Group buttonStyle="solid">
                      <Radio.Button value="F">女</Radio.Button>
                      <Radio.Button value="M">男</Radio.Button>
                    </Radio.Group>
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item
                    name="birth_date"
                    label="出生日期"
                    rules={[{ required: true, message: '请选择出生日期' }]}
                  >
                    <DatePicker
                      style={{ width: '100%' }}
                      size="large"
                      disabledDate={(current) => current > dayjs()}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="id_card"
                    label="身份证号"
                    rules={[
                      { pattern: /^\d{17}[\dXx]$/, message: '请输入正确的身份证号' }
                    ]}
                  >
                    <Input placeholder="请输入身份证号" size="large" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="phone"
                    label="联系电话"
                    rules={[
                      { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }
                    ]}
                  >
                    <Input placeholder="请输入手机号码" size="large" addonBefore="+86" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="email"
                    label="电子邮箱"
                    rules={[{ type: 'email', message: '请输入正确的邮箱' }]}
                  >
                    <Input placeholder="example@email.com" size="large" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="address"
                    label="居住地址"
                  >
                    <Input placeholder="请输入居住地址" size="large" />
                  </Form.Item>
                </Col>
              </Row>

              {/* 证件上传 */}
              <Form.Item label="身份证照片">
                <Upload.Dragger
                  name="file"
                  multiple={false}
                  maxCount={1}
                  accept="image/*"
                  style={{ marginTop: 8 }}
                >
                  <Button icon={<UploadOutlined />}>点击上传</Button>
                  <div style={{ marginTop: 8, color: '#94a3b8', fontSize: 13 }}>
                    支持 JPG、PNG 格式，大小不超过 2MB
                  </div>
                </Upload.Dragger>
              </Form.Item>
            </motion.div>
          )}

          {/* 步骤 2: 中医信息 */}
          {/* ⚠️ 中医信息步骤已移除 (2026-05-29) - 见 docs/TCM_INTEGRATION_ANALYSIS_AND_FIX.md */}
          {/* 原因：无四诊信息采集（舌象、脉象），体质和证型判定无依据 */}

          {/* 步骤 3: 风险评估 */}
          {currentStep === 2 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="step-content"
            >
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="risk_level"
                    label="风险等级"
                  >
                    <Select
                      placeholder="请选择风险等级"
                      size="large"
                      allowClear
                      options={[
                        { value: 'low', label: '✅ 低风险 - 定期随访即可' },
                        { value: 'medium', label: '⚠️ 中风险 - 需要关注' },
                        { value: 'high', label: '🔴 高风险 - 密切监测' },
                        { value: 'very_high', label: '🚨 极高风险 - 立即干预' },
                      ]}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="risk_score"
                    label="风险评分"
                  >
                    <InputNumber
                      placeholder="0.00-1.00"
                      min={0}
                      max={1}
                      step={0.01}
                      style={{ width: '100%' }}
                      size="large"
                      addonAfter="分"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Divider orientation="left">风险因素评估</Divider>

              <Row gutter={24}>
                <Col span={24}>
                  <Form.Item
                    name="risk_factors"
