import { useState } from 'react';
import { Card, Form, Input, Button, Select, Row, Col, Divider, Typography, Space, Alert, Descriptions, Tag, Rate, Progress, Result, Steps, Collapse, Timeline, Badge, Avatar, message } from 'antd';
import {
  ThunderboltOutlined,
  MedicineBoxOutlined,
  CheckCircleOutlined,
  ApiOutlined,
  HeartOutlined,
  ExperimentOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import ReactECharts from 'echarts-for-react';
import type { EChartOption } from 'echarts';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;
const MotionCard = motion(Card);

const AIDiagnosis = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [hasResult, setHasResult] = useState(false);

  const handleSubmit = (values: any) => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setHasResult(true);
      message.success('AI 诊断完成');
    }, 2000);
  };

  // 诊断准确性展示
  const accuracyOption: EChartOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%',
    },
    series: [
      {
        name: '诊断准确性',
        type: 'gauge',
        progress: {
          show: true,
          width: 18,
        },
        axisLine: {
          lineStyle: {
            width: 18,
          },
        },
        axisTick: {
          show: false,
        },
        splitLine: {
          length: 15,
          lineStyle: {
            width: 2,
            color: '#999',
          },
        },
        axisLabel: {
          distance: 25,
          color: '#999',
          fontSize: 12,
        },
        anchor: {
          show: true,
          showAbove: true,
          size: 25,
          itemStyle: {
            borderWidth: 10,
          },
        },
        title: {
          show: false,
        },
        detail: {
          valueAnimation: true,
          fontSize: 30,
          fontWeight: 'bold',
          offsetCenter: [0, '70%'],
          formatter: '{value}%',
          color: '#667eea',
        },
        data: [
          {
            value: 94.6,
            name: 'AI 诊断准确率',
          },
        ],
      },
    ],
  };

  return (
    <div className="ai-diagnosis-container">
      <Row gutter={[20, 20]}>
        <Col xs={24} lg={14}>
          <MotionCard
            title={
              <Space>
                <ThunderboltOutlined style={{ color: '#667eea' }} />
                <span>AI 辅助诊断</span>
              </Space>
            }
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              size="large"
            >
              <Alert
                message="AI 诊断说明"
                description="本系统采用 PBS-Net + DFMFI + HXM-Net 多模态融合模型，综合超声、钼靶、MRI 及临床信息进行智能诊断"
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
                icon={<ApiOutlined />}
              />

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="patient_age"
                    label="患者年龄"
                    rules={[{ required: true, message: '请输入年龄' }]}
                  >
                    <Input placeholder="岁" addonAfter="岁" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="family_history"
                    label="家族史"
                    initialValue={false}
                    valuePropName="checked"
                  >
                    <Select>
                      <Select.Option value={false}>无</Select.Option>
                      <Select.Option value={true}>有</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Divider orientation="left">BI-RADS 特征</Divider>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="shape" label="形状">
                    <Select placeholder="请选择">
                      <Select.Option value="oval">椭圆形</Select.Option>
                      <Select.Option value="round">圆形</Select.Option>
                      <Select.Option value="irregular">不规则</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="margin" label="边界">
                    <Select placeholder="请选择">
                      <Select.Option value="circumscribed">清晰</Select.Option>
                      <Select.Option value="microlobulated">微分叶</Select.Option>
                      <Select.Option value="spiculated">毛刺</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="orientation" label="方向">
                    <Select placeholder="请选择">
                      <Select.Option value="parallel">平行位</Select.Option>
                      <Select.Option value="not_parallel">垂直位</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="echo" label="回声模式">
                    <Select placeholder="请选择">
                      <Select.Option value="anechoic">无回声</Select.Option>
                      <Select.Option value="hypoechoic">低回声</Select.Option>
                      <Select.Option value="marked_hypoechoic">显著低回声</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item>
                <Button
                  type="primary"
                  size="large"
                  htmlType="submit"
                  loading={loading}
                  block
                  icon={<ThunderboltOutlined />}
                >
                  {loading ? 'AI 诊断中...' : '开始诊断'}
                </Button>
              </Form.Item>
            </Form>
          </MotionCard>
        </Col>

        <Col xs={24} lg={10}>
          <MotionCard
            title={
              <Space>
                <ExperimentOutlined style={{ color: '#f093fb' }} />
                <span>诊断模型</span>
              </Space>
            }
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div style={{ height: 300 }}>
              <ReactECharts option={accuracyOption} style={{ height: '100%' }} />
            </div>
            
            <Divider />
            
            <Timeline>
              <Timeline.Item
                dot={<CheckCircleOutlined style={{ color: '#10b981' }} />}
                color="green"
              >
                <div className="model-info">
                  <Text strong>PBS-Net 病灶分割</Text>
                  <BR />
                  <Text type="secondary">Dice: 0.87 | 推理：45ms</Text>
                </div>
              </Timeline.Item>
              <Timeline.Item
                dot={<CheckCircleOutlined style={{ color: '#10b981' }} />}
                color="green"
              >
                <div className="model-info">
                  <Text strong>DFMFI 特征融合</Text>
                  <BR />
                  <Text type="secondary">参数量：12.8M | Acc: 0.94</Text>
                </div>
              </Timeline.Item>
              <Timeline.Item
                dot={<CheckCircleOutlined style={{ color: '#10b981' }} />}
                color="green"
              >
                <div className="model-info">
                  <Text strong>HXM-Net 多模态诊断</Text>
                  <BR />
                  <Text type="secondary">AUC: 0.97 | 可解释性强</Text>
                </div>
              </Timeline.Item>
            </Timeline>
          </MotionCard>
        </Col>
      </Row>
    </div>
  );
};

export default AIDiagnosis;
