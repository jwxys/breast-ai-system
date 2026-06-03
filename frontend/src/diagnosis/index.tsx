/**
 * 诊断管理页面
 * 
 * 提供完整的诊断决策功能：
 * - 诊断列表
 * - BI-RADS 智能评估
 * - 分子分型预测
 * - AI 影像分析
 * - 综合报告生成
 */

import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Space, Modal, Form, Input, Select, Row, Col, message } from 'antd';
import { 
  PlusOutlined, 
  EyeOutlined, 
  DeleteOutlined, 
  RobotOutlined,
  ExperimentOutlined,
  FileTextOutlined 
} from '@ant-design/icons';

// 类型定义
interface Diagnosis {
  id: number;
  report_no: string;
  patient_name: string;
  lesion_location: string;
  birads_category: string;
  malignancy_risk: number;
  ai_assisted: boolean;
  report_status: string;
  created_at: string;
}

interface BIRADSAssessment {
  birads_category: string;
  malignancy_risk: number;
  recommendation: string;
  key_features: string[];
}

/**
 * 诊断管理主组件
 */
const DiagnosisList: React.FC = () => {
  // 状态管理
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [assessmentModal, setAssessmentModal] = useState(false);
  const [selectedDiagnosis, setSelectedDiagnosis] = useState<Diagnosis | null>(null);
  
  // BI-RADS 评估结果
  const [biradsResult, setBiradsResult] = useState<BIRADSAssessment | null>(null);
  
  // 表单实例
  const [form] = Form.useForm();
  
  // BI-RADS 分级颜色映射
  const biradsColors: Record<string, string> = {
    '0': 'default',
    '1': 'success',
    '2': 'success',
    '3': 'processing',
    '4A': 'warning',
    '4B': 'warning',
    '4C': 'error',
    '5': 'error',
    '6': 'error',
  };
  
  // 加载诊断列表
  const loadDiagnoses = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/diagnosis?page=1&page_size=10');
      const data = await response.json();
      setDiagnoses(data.data);
    } catch (error) {
      console.error('加载诊断列表失败:', error);
      message.error('加载诊断列表失败');
    } finally {
      setLoading(false);
    }
  };
  
  // 组件加载时获取数据
  useEffect(() => {
    loadDiagnoses();
  }, []);
  
  // 创建诊断
  const handleCreate = () => {
    form.resetFields();
    setModalVisible(true);
  };
  
  // 提交诊断
  const handleSubmit = async (values: any) => {
    try {
      const response = await fetch('/api/v1/diagnosis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      
      if (response.ok) {
        message.success('创建诊断成功');
        setModalVisible(false);
        loadDiagnoses();
      } else {
        message.error('创建诊断失败');
      }
    } catch (error) {
      console.error('创建诊断失败:', error);
      message.error('创建诊断失败');
    }
  };
  
  // 查看诊断详情
  const handleView = (record: Diagnosis) => {
    setSelectedDiagnosis(record);
    // 导航到详情页或打开详情弹窗
    window.location.href = `/diagnosis/${record.id}`;
  };
  
  // 删除诊断
  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除该诊断记录吗？',
      onOk: async () => {
        try {
          const response = await fetch(`/api/v1/diagnosis/${id}`, {
            method: 'DELETE',
          });
          
          if (response.ok) {
            message.success('删除成功');
            loadDiagnoses();
          } else {
            message.error('删除失败');
          }
        } catch (error) {
          console.error('删除失败:', error);
          message.error('删除失败');
        }
      },
    });
  };
  
  // BI-RADS 智能评估
  const handleBIRADSAssess = async (features: any) => {
    try {
      const response = await fetch('/api/v1/diagnosis/assess-birads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(features),
      });
      
      const data = await response.json();
      setBiradsResult(data);
      message.success('BI-RADS 评估完成');
    } catch (error) {
      console.error('BI-RADS 评估失败:', error);
      message.error('评估失败');
    }
  };
  
  // 打开评估弹窗
  const openAssessmentModal = () => {
    setBiradsResult(null);
    setAssessmentModal(true);
  };
  
  // 表格列定义
  const columns = [
    {
      title: '报告编号',
      dataIndex: 'report_no',
      key: 'report_no',
    },
    {
      title: '患者姓名',
      dataIndex: 'patient_name',
      key: 'patient_name',
    },
    {
      title: '病灶位置',
      dataIndex: 'lesion_location',
      key: 'lesion_location',
    },
    {
      title: 'BI-RADS 分级',
      dataIndex: 'birads_category',
      key: 'birads_category',
      render: (text: string) => (
        <Tag color={biradsColors[text] || 'default'}>
          {text}
        </Tag>
      ),
    },
    {
      title: '恶性风险',
      dataIndex: 'malignancy_risk',
      key: 'malignancy_risk',
      render: (risk: number) => `${(risk * 100).toFixed(1)}%`,
    },
    {
      title: 'AI 辅助',
      dataIndex: 'ai_assisted',
      key: 'ai_assisted',
      render: (aiAssisted: boolean) => 
        aiAssisted ? <Tag color="blue">是</Tag> : <Tag>否</Tag>,
    },
    {
      title: '报告状态',
      dataIndex: 'report_status',
      key: 'report_status',
      render: (status: string) => {
        const statusMap: Record<string, string> = {
          draft: '草稿',
          preliminary: '初步',
          final: '正式',
          amended: '修改',
        };
        return <Tag>{statusMap[status] || status}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Diagnosis) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];
  
  return (
    <div className="diagnosis-container">
      {/* 顶部操作栏 */}
      <div className="toolbar" style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            新建诊断
          </Button>
          <Button
            icon={<RobotOutlined />}
            onClick={openAssessmentModal}
          >
            BI-RADS 智能评估
          </Button>
          <Button
            icon={<ExperimentOutlined />}
          >
            分子分型预测
          </Button>
        </Space>
      </div>
      
      {/* 诊断列表表格 */}
      <Card loading={loading}>
        <Table
          columns={columns}
          dataSource={diagnoses}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>
      
      {/* 创建诊断弹窗 */}
      <Modal
        title="创建诊断"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="patient_id"
                label="患者 ID"
                rules={[{ required: true, message: '请选择患者' }]}
              >
                <Select placeholder="选择患者" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="lesion_id"
                label="病灶 ID"
                rules={[{ required: true, message: '请选择病灶' }]}
              >
                <Select placeholder="选择病灶" />
              </Form.Item>
            </Col>
          </Row>
          
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
          
          <Form.Item
            name="recommendation"
            label="处理建议"
          >
            <Input.TextArea rows={3} placeholder="请输入处理建议" />
          </Form.Item>
          
          <Form.Item
            name="ai_assisted"
            label="AI 辅助"
            valuePropName="checked"
          >
            <Select>
              <Select.Option value={false}>否</Select.Option>
              <Select.Option value={true}>是</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
      
      {/* BI-RADS 评估弹窗 */}
      <Modal
        title={
          <Space>
            <RobotOutlined />
            BI-RADS 智能评估
          </Space>
        }
        open={assessmentModal}
        onCancel={() => setAssessmentModal(false)}
        footer={[
          <Button key="close" onClick={() => setAssessmentModal(false)}>
            关闭
          </Button>,
        ]}
        width={900}
      >
        <div className="birads-assessment">
          {/* 评估结果展示 */}
          {biradsResult ? (
            <div>
              <h3>评估结果</h3>
              <p>
                <strong>BI-RADS 分级：</strong>
                <Tag color={biradsColors[biradsResult.birads_category]}>
                  {biradsResult.birads_category}
                </Tag>
              </p>
              <p>
                <strong>恶性风险：</strong>
                <span style={{ color: 'red', fontWeight: 'bold' }}>
                  {biradsResult.malignancy_risk}%
                </span>
              </p>
              <p>
                <strong>处理建议：</strong>{' '}
                {biradsResult.recommendation}
              </p>
              <p>
                <strong>关键征象：</strong>
              </p>
              <ul>
                {biradsResult.key_features.map((feature, idx) => (
                  <li key={idx}>{feature}</li>
                ))}
              </ul>
            </div>
          ) : (
            <p>请输入超声征象进行评估</p>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default DiagnosisList;
