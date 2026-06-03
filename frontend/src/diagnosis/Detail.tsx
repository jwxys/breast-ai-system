import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Card, Descriptions, Space, Tag, message } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';

interface DiagnosisDetail {
  id: number;
  report_no: string;
  patient_name: string;
  patient_no: string;
  age: number;
  gender: string;
  exam_date: string;
  exam_type: string;
  birads: string;
  birads_score: number;
  features: {
    shape: string;
    margin: string;
    echogenicity: string;
    calcification: string;
    blood_flow: string;
    elasticity: string;
  };
  conclusion: string;
  suggestion: string;
  ai_confidence: number;
}

const DiagnosisDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [diagnosis, setDiagnosis] = useState<DiagnosisDetail | null>(null);

  useEffect(() => {
    loadDiagnosis();
  }, [id]);

  const loadDiagnosis = async () => {
    setLoading(true);
    // 模拟数据
    setTimeout(() => {
      const mockData: DiagnosisDetail = {
        id: parseInt(id || '1'),
        report_no: 'D20260530001',
        patient_name: '张三',
        patient_no: 'P20260527001',
        age: 35,
        gender: '女',
        exam_date: '2026-05-28',
        exam_type: '乳腺超声',
        birads: '3',
        birads_score: 0.85,
        features: {
          shape: '椭圆形',
          margin: '清晰',
          echogenicity: '等回声',
          calcification: '无',
          blood_flow: '无血流信号',
          elasticity: '中等硬度',
        },
        conclusion: '双侧乳腺增生，右乳低回声结节（BI-RADS 3 类）',
        suggestion: '建议 6 个月后复查超声',
        ai_confidence: 0.92,
      };
      setDiagnosis(mockData);
      setLoading(false);
    }, 500);
  };

  if (loading || !diagnosis) {
    return <div>加载中...</div>;
  }

  return (
    <div style={{ padding: 24 }}>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/diagnosis')}>
          返回
        </Button>
      </Space>

      <Card title="诊断详情" style={{ marginBottom: 16 }}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="报告编号">{diagnosis.report_no}</Descriptions.Item>
          <Descriptions.Item label="患者姓名">{diagnosis.patient_name}</Descriptions.Item>
          <Descriptions.Item label="患者 ID">{diagnosis.patient_no}</Descriptions.Item>
          <Descriptions.Item label="年龄">{diagnosis.age}</Descriptions.Item>
          <Descriptions.Item label="性别">{diagnosis.gender}</Descriptions.Item>
          <Descriptions.Item label="检查日期">{diagnosis.exam_date}</Descriptions.Item>
          <Descriptions.Item label="BI-RADS 分级">
            <Tag color="blue">BI-RADS {diagnosis.birads}类</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="AI 置信度">
            <Tag color="green">{(diagnosis.ai_confidence * 100).toFixed(1)}%</Tag>
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="病灶特征" style={{ marginBottom: 16 }}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="形状">{diagnosis.features.shape}</Descriptions.Item>
          <Descriptions.Item label="边界">{diagnosis.features.margin}</Descriptions.Item>
          <Descriptions.Item label="回声">{diagnosis.features.echogenicity}</Descriptions.Item>
          <Descriptions.Item label="钙化">{diagnosis.features.calcification}</Descriptions.Item>
          <Descriptions.Item label="血流">{diagnosis.features.blood_flow}</Descriptions.Item>
          <Descriptions.Item label="弹性">{diagnosis.features.elasticity}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="诊断结论">
        <p style={{ fontSize: 16, marginBottom: 16 }}>{diagnosis.conclusion}</p>
        <div style={{ background: '#f5f5f5', padding: 16, borderRadius: 4 }}>
          <strong>建议：</strong>
          <p style={{ margin: 0 }}>{diagnosis.suggestion}</p>
        </div>
      </Card>
    </div>
  );
};

export default DiagnosisDetailPage;
