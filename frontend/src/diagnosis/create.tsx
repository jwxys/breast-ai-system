/**
 * 诊断创建/编辑表单页面
 * 
 * 提供：
 * - 新建诊断
 * - 编辑现有诊断
 * - BI-RADS 智能评估集成
 * - AI 辅助诊断
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Form, Input, InputNumber, Select, Button, Card, 
  Row, Col, Space, message, Steps, Checkbox,
  Divider, Typography, Alert, Modal
} from 'antd';
import {
  ArrowLeftOutlined,
  SaveOutlined,
  RobotOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';

const { Title } = Typography;
const { TextArea } = Input;
const { Step } = Steps;

// 类型定义
interface UltrasoundFeatures {
  shape?: string;
  orientation?: string;
  margin_types?: string[];
  echo_pattern?: string;
  calcification_present?: boolean;
  vascularity_grade?: string;
}

interface BIRADSResult {
  birads_category: string;
  malignancy_risk: number;
  recommendation: string;
  key_features: string[];
}

/**
 * 诊断创建/编辑组件
 */
const DiagnosisCreate: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  
  // 状态管理
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [biradsModalVisible, setBiradsModalVisible] = useState(false);
  const [biradsFeatures, setBiradsFeatures] = useState<UltrasoundFeatures>({});
  const [biradsResult, setBiradsResult] = useState<BIRADSResult | null>(null);
  const [aiAnalyzing, setAiAnalyzing] = useState(false);
  
  const isEdit = !!id;
  
  // 加载现有诊断 (编辑模式)
  useEffect(() => {
    if (isEdit && id) {
      loadDiagnosis(id);
    }
  }, [id]);
  
  const loadDiagnosis = async (diagnosisId: string) => {
    try {
      const response = await fetch(`/api/v1/diagnosis/${diagnosisId}`);
      if (response.ok) {
        const data = await response.json();
        form.setFieldsValue(data);
      }
    } catch (error) {
      console.error('加载诊断失败:', error);
      message.error('加载诊断失败');
    }
  };
  
  /**
   * BI-RADS 智能评估
   */
  const handleBIRADSAssess = async () => {
    const features = form.getFieldsValue([
      'shape',
      'orientation',
      'margin_types',
      'echo_pattern',
      'calcification_present',
      'vascularity_grade',
    ]);
    
    try {
      const response = await fetch('/api/v1/diagnosis/assess-birads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ultrasound_features: features,
          include_explanation: true,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setBiradsResult(data);
        setBiradsModalVisible(true);
        
        // 自动填充 BI-RADS 分级
        form.setFieldsValue({
          birads_category: data.birads_category,
          malignancy_risk: data.malignancy_risk / 100,
          recommendation: data.recommendation,
        });
        
        message.success('BI-RADS 评估完成，已自动填充');
      }
    } catch (error) {
      console.error('BI-RADS 评估失败:', error);
      message.error('评估失败');
    }
  };
  
  /**
   * AI 辅助分析
   */
  const handleAIAnalyze = async () => {
    setAiAnalyzing(true);
    
    // TODO: 实现图像上传和 AI 分析
    try {
      message.info('AI 分析功能开发中...');
    } catch (error) {
      console.error('AI 分析失败:', error);
      message.error('AI 分析失败');
    } finally {
      setAiAnalyzing(false);
    }
  };
  
  /**
   * 提交表单
   */
  const handleSubmit = async (values: any) => {
    setLoading(true);
    
    try {
      const url = isEdit ? `/api/v1/diagnosis/${id}` : '/api/v1/diagnosis';
      const method = isEdit ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      
      if (response.ok) {
        message.success(isEdit ? '更新成功' : '创建成功');
        navigate('/diagnosis');
      } else {
        const error = await response.json();
        message.error(error.detail || '操作失败');
      }
    } catch (error) {
      console.error('提交失败:', error);
      message.error('提交失败');
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * 步骤条内容
   */
  const steps = [
    {
      title: '基本信息',
      content: (
        <>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="patient_id"
                label="患者 ID"
                rules={[{ required: true, message: '请选择患者' }]}
              >
                <Select
                  showSearch
                  placeholder="选择患者"
                  optionFilterProp="children"
                  filterOption={(input, option) =>
                    (option?.children ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                >
                  <Select.Option value={1}>张三</Select.Option>
                  <Select.Option value={2}>李四</Select.Option>
                  <Select.Option value={3}>王五</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="lesion_id"
                label="病灶 ID"
                rules={[{ required: true, message: '请选择病灶' }]}
              >
                <Select placeholder="选择病灶">
                  <Select.Option value={1}>左侧乳腺外上象限结节</Select.Option>
                  <Select.Option value={2}>右侧乳腺内上象限结节</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            name="report_type"
            label="报告类型"
            initialValue="initial"
          >
            <Select>
              <Select.Option value="initial">初诊报告</Select.Option>
              <Select.Option value="follow_up">随访报告</Select.Option>
              <Select.Option value="post_op">术后报告</Select.Option>
              <Select.Option value="pathology">病理报告</Select.Option>
            </Select>
          </Form.Item>
          
          <Divider />
          
          <Alert
            message="提示"
            description="选择病灶后，可点击右侧'智能评估'按钮自动计算 BI-RADS 分级"
            type="info"
            showIcon
          />
        </>
      ),
    },
    {
      title: '超声征象',
      content: (
        <>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="shape" label="形状">
                <Select>
                  <Select.Option value="oval">椭圆形</Select.Option>
                  <Select.Option value="round">圆形</Select.Option>
                  <Select.Option value="irregular">不规则形</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="orientation" label="纵横比">
                <Select>
                  <Select.Option value="parallel">平行 （宽＞高）</Select.Option>
                  <Select.Option value="not_parallel">非平行 (高＞宽)</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="echo_pattern" label="回声模式">
                <Select>
                  <Select.Option value="anechoic">无回声</Select.Option>
                  <Select.Option value="hypoechoic">低回声</Select.Option>
                  <Select.Option value="isoechoic">等回声</Select.Option>
                  <Select.Option value="hyperechoic">高回声</Select.Option>
                  <Select.Option value="heterogeneous">混合回声</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item name="margin_types" label="边缘特征">
            <Select mode="multiple">
              <Select.Option value="circumscribed">边界清晰</Select.Option>
              <Select.Option value="indistinct">边界不清</Select.Option>
              <Select.Option value="angular">成角</Select.Option>
              <Select.Option value="microlobulated">微小分叶</Select.Option>
              <Select.Option value="spiculated">毛刺状</Select.Option>
            </Select>
          </Form.Item>
          
          <Form.Item name="calcification_present" label="伴钙化" valuePropName="checked">
            <Checkbox />
          </Form.Item>
          
          <Form.Item name="vascularity_grade" label="血流分级">
            <Select>
              <Select.Option value="grade_0">0 级 (无血流)</Select.Option>
              <Select.Option value="grade_1">1 级 (少许血流)</Select.Option>
              <Select.Option value="grade_2">2 级 (中等血流)</Select.Option>
              <Select.Option value="grade_3">3 级 (丰富血流)</Select.Option>
            </Select>
          </Form.Item>
          
          <Divider />
          
          <Space>
            <Button
              icon={<RobotOutlined />}
              onClick={handleBIRADSAssess}
            >
              BI-RADS 智能评估
            </Button>
            <Button
              icon={<ThunderboltOutlined />}
              loading={aiAnalyzing}
              onClick={handleAIAnalyze}
            >
              AI 辅助分析
            </Button>
          </Space>
        </>
      ),
    },
    {
      title: '诊断结论',
      content: (
        <>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="birads_category"
                label="BI-RADS 分级"
                rules={[{ required: true, message: '请选择 BI-RADS 分级' }]}
              >
                <Select>
                  <Select.Option value="0">0 级 - 评估不完全</Select.Option>
                  <Select.Option value="1">1 级 - 阴性</Select.Option>
                  <Select.Option value="2">2 级 - 良性</Select.Option>
                  <Select.Option value="3">3 级 - 可能良性</Select.Option>
                  <Select.Option value="4A">4A 级 - 低度可疑</Select.Option>
                  <Select.Option value="4B">4B 级 - 中度可疑</Select.Option>
                  <Select.Option value="4C">4C 级 - 高度可疑</Select.Option>
                  <Select.Option value="5">5 级 - 高度提示恶性</Select.Option>
                  <Select.Option value="6">6 级 - 已证实恶性</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="malignancy_risk"
                label="恶性风险"
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.01}
                  formatter={(value) => `${(value! * 100).toFixed(1)}%`}
                  parser={(value) => Number(value?.replace('%', '')) / 100}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="ai_assisted"
                label="AI 辅助"
                valuePropName="checked"
              >
                <Checkbox>是</Checkbox>
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            name="recommendation"
            label="处理建议"
            rules={[{ required: true, message: '请输入处理建议' }]}
          >
            <TextArea rows={3} placeholder="如：建议穿刺活检、建议手术切除、建议 3 个月随访等" />
          </Form.Item>
          
          <Form.Item
            name="birads_assessment_basis"
            label="BI-RADS 评估依据"
          >
            <TextArea rows={4} placeholder="详细说明 BI-RADS 分级的依据，包括关键超声征象" />
          </Form.Item>
        </>
      ),
    },
  ];
  
  return (
    <div className="diagnosis-create">
      <Card loading={loading}>
        {/* 页面标题 */}
        <div style={{ marginBottom: 24 }}>
          <Space>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate(isEdit ? `/diagnosis/${id}` : '/diagnosis')}
            >
              返回
            </Button>
            <Title level={3} style={{ margin: 0 }}>
              {isEdit ? '编辑诊断' : '新建诊断'}
            </Title>
          </Space>
        </div>
        
        {/* 步骤条 */}
        <Steps current={currentStep} items={steps} style={{ marginBottom: 24 }} />
        
        {/* 表单内容 */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          {steps[currentStep].content}
          
          {/* 步骤导航 */}
          <Divider />
          
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Button
              disabled={currentStep === 0}
              onClick={() => setCurrentStep(currentStep - 1)}
            >
              上一步
            </Button>
            
            <Space>
              {currentStep < steps.length - 1 ? (
                <Button type="primary" onClick={() => setCurrentStep(currentStep + 1)}>
                  下一步
                </Button>
              ) : (
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={loading}
                >
                  {isEdit ? '保存更新' : '创建诊断'}
                </Button>
              )}
            </Space>
          </div>
        </Form>
      </Card>
      
      {/* BI-RADS 评估结果弹窗 */}
      <Modal
        title="BI-RADS 智能评估结果"
        open={biradsModalVisible}
        onCancel={() => setBiradsModalVisible(false)}
        footer={[
          <Button key="ok" type="primary" onClick={() => setBiradsModalVisible(false)}>
            确定
          </Button>,
        ]}
      >
        {biradsResult && (
          <>
            <Alert
              message={`BI-RADS ${biradsResult.birads_category} 类`}
              description={`恶性风险：${biradsResult.malignancy_risk}%`}
              type={
                ['4A', '4B', '4C', '5', '6'].includes(biradsResult.birads_category)
                  ? 'warning'
                  : 'info'
              }
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <p><strong>处理建议：</strong>{biradsResult.recommendation}</p>
            
            <p><strong>关键征象：</strong></p>
            <ul>
              {biradsResult.key_features.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
            
            <Alert
              message="已自动填充"
              description="BI-RADS 分级、恶性风险和处理建议已自动填充到表单中，您可以手动调整。"
              type="success"
              showIcon
            />
          </>
        )}
      </Modal>
    </div>
  );
};

export default DiagnosisCreate;
