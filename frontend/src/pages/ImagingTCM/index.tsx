/**
 * 影像 - 中医病机分析页面
 * 
 * 显示超声影像的中医病机倾向分析结果
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Alert, 
  Descriptions, 
  Tag, 
  Progress, 
  Divider, 
  Button, 
  Spin,
  message,
  Badge
} from 'antd';
import { 
  ArrowLeftOutlined,
  ExperimentOutlined,
  WarningOutlined,
  CheckCircleOutlined 
} from '@ant-design/icons';
import axios from 'axios';
import './index.css';

// ========== 类型定义 ==============

interface PathomechanismTendency {
  pathomechanism: string;
  score: number;
  level: string;
  evidence: string;
}

interface ImagingFeatures {
  boundary_type: string;
  morphology: string;
  aspect_ratio: number;
  echo_type: string;
  calcification_type: string;
  cdfi_grade: string;
  elasticity_score: number;
  growth_rate: string;
  lesion_size_cm: number;
}

interface TCMAnalysisData {
  ultrasound_id: number;
  patient_id: number;
  imaging_features: ImagingFeatures;
  tcm_tendencies: {
    stasis: PathomechanismTendency;
    phlegm: PathomechanismTendency;
    toxin: PathomechanismTendency;
    deficiency: PathomechanismTendency;
  };
  primary_pathomechanism: string;
  secondary_pathomechanism: string;
  pattern_combination: string;
  nature: string;
  overall_evidence_level: string;
  confidence: number;
  recommended_therapy: string;
  recommended_formula: string;
  disclaimer: {
    warning: string;
    evidence_statement: string;
    usage_limitation: string;
    research_status: string;
  };
  created_at: string;
}

// ========== 病机名称映射 ==============

const PATHOMECHANISM_NAMES: Record<string, string> = {
  stasis: '瘀血',
  phlegm: '痰浊',
  toxin: '毒邪',
  deficiency: '正虚',
};

const EVIDENCE_LEVEL_COLORS: Record<string, string> = {
  A: 'green',
  B: 'blue',
  C: 'orange',
};

// ========== 主组件 ==============

const ImagingTCMPage: React.FC = () => {
  const { ultrasoundId } = useParams<{ ultrasoundId: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<TCMAnalysisData | null>(null);

  useEffect(() => {
    if (ultrasoundId) {
      fetchAnalysisResult(ultrasoundId);
    }
  }, [ultrasoundId]);

  // 获取分析结果
  const fetchAnalysisResult = async (id: string) => {
    try {
      setLoading(true);
      const response = await axios.get(
        `http://localhost:8000/api/v1/imaging-tcm/ultrasound/${id}/result`
      );
      setData(response.data);
    } catch (error) {
      console.error('获取分析结果失败:', error);
      message.error('获取分析结果失败，请检查网络连接');
    } finally {
      setLoading(false);
    }
  };

  // 渲染病机倾向进度条
  const renderTendencyBar = (name: string, tendency: PathomechanismTendency) => {
    const getColor = (score: number) => {
      if (score >= 0.7) return '#ff4d4f'; // 显著 - 红
      if (score >= 0.5) return '#faad14'; // 明显 - 橙
      if (score >= 0.3) return '#1890ff'; // 中度 - 蓝
      return '#d9d9d9'; // 轻度 - 灰
    };

    return (
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
          <span style={{ fontWeight: 500 }}>{name}</span>
          <Tag color={getColor(tendency.score)}>{tendency.level}</Tag>
        </div>
        <Progress
          percent={Math.round(tendency.score * 100)}
          strokeColor={getColor(tendency.score)}
          showInfo={false}
          size="small"
        />
        {tendency.evidence && (
          <div style={{ fontSize: 12, color: '#666', marginTop: 4, paddingLeft: 8 }}>
            📋 {tendency.evidence}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" tip="正在分析影像特征..." />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="page-container">
        <Alert
          message="未找到分析结果"
          description="该超声检查尚未进行中医病机分析"
          type="warning"
          showIcon
          action={
            <Button size="small" onClick={() => navigate(-1)}>
              返回
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* 头部导航 */}
      <div className="page-header">
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate(-1)}
          size="small"
        >
          返回
        </Button>
      </div>

      <div className="page-content">
        {/* 警告提示 */}
        <Alert
          message={
            <span>
              <WarningOutlined style={{ color: '#faad14', marginRight: 8 }} />
              研究用途声明
            </span>
          }
          description={
            <div>
              <p style={{ marginBottom: 8 }}>{data.disclaimer.warning}</p>
              <p style={{ marginBottom: 8 }}>{data.disclaimer.evidence_statement}</p>
              <p style={{ marginBottom: 8 }}>{data.disclaimer.usage_limitation}</p>
              <p style={{ marginBottom: 0 }}>{data.disclaimer.research_status}</p>
            </div>
          }
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
          closable
        />

        {/* 主要内容 */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          {/* 左侧：病机倾向 */}
          <Card 
            title="📊 病机倾向分析"
            extra={
              <Badge
                count={
                  <ExperimentOutlined />
                }
                text="证据等级"
              />
            }
          >
            <div style={{ marginBottom: 16 }}>
              <Tag color={EVIDENCE_LEVEL_COLORS[data.overall_evidence_level]}>
                {data.overall_evidence_level} 级证据
              </Tag>
              <span style={{ marginLeft: 8, fontSize: 12, color: '#666' }}>
                置信度：{Math.round(data.confidence * 100)}%
              </span>
            </div>

            <Divider orientation="left" style={{ fontSize: 12 }}>四大病机维度</Divider>

            {renderTendencyBar(PATHOMECHANISM_NAMES.stasis, data.tcm_tendencies.stasis)}
            {renderTendencyBar(PATHOMECHANISM_NAMES.phlegm, data.tcm_tendencies.phlegm)}
            {renderTendencyBar(PATHOMECHANISM_NAMES.toxin, data.tcm_tendencies.toxin)}
            {renderTendencyBar(PATHOMECHANISM_NAMES.deficiency, data.tcm_tendencies.deficiency)}
          </Card>

          {/* 右侧：综合判断 */}
          <Card title="🔍 综合判断">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="主要病机">
                <Tag color="red">{PATHOMECHANISM_NAMES[data.primary_pathomechanism] || data.primary_pathomechanism}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="次要病机">
                {data.secondary_pathomechanism ? (
                  <Tag color="blue">
                    {PATHOMECHANISM_NAMES[data.secondary_pathomechanism] || data.secondary_pathomechanism}
                  </Tag>
                ) : (
                  <span style={{ color: '#999' }}>无明显次要病机</span>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="病机组合">
                <Tag color="purple">{data.pattern_combination}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="病性">
                <Tag color={data.nature.includes('实') ? 'orange' : 'green'}>
                  {data.nature}
                </Tag>
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <div style={{ marginTop: 16 }}>
              <h4 style={{ marginBottom: 8 }}>💊 推荐治法</h4>
              <p style={{ 
                padding: '12px', 
                backgroundColor: '#f6ffed', 
                border: '1px solid #b7eb8f',
                borderRadius: 4,
                margin: 0 
              }}>
                {data.recommended_therapy || '暂无推荐'}
              </p>
            </div>

            <div style={{ marginTop: 16 }}>
              <h4 style={{ marginBottom: 8 }}>🌿 参考方剂</h4>
              <p style={{ 
                padding: '12px', 
                backgroundColor: '#e6f7ff', 
                border: '1px solid #91d5ff',
                borderRadius: 4,
                margin: 0 
              }}>
                {data.recommended_formula || '暂无推荐'}
              </p>
            </div>

            <div style={{ marginTop: 16 }}>
              <h4 style={{ marginBottom: 8 }}>
                <CheckCircleOutlined style={{ color: '#52c41a' }} /> 下一步建议
              </h4>
              <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13 }}>
                <li>结合舌象、脉象进行四诊合参</li>
                <li>询问患者全身症状和体征</li>
                <li>由执业中医师综合判断</li>
                <li>必要时调整治法方剂</li>
              </ul>
            </div>
          </Card>
        </div>

        {/* 底部：影像特征摘要 */}
        <Card title="📋 影像特征摘要" style={{ marginTop: 16 }}>
          <Descriptions column={3} size="small" bordered>
            <Descriptions.Item label="边界类型">
              {data.imaging_features.boundary_type || '未知'}
            </Descriptions.Item>
            <Descriptions.Item label="形态">
              {data.imaging_features.morphology || '未知'}
            </Descriptions.Item>
            <Descriptions.Item label="纵横比">
              {data.imaging_features.aspect_ratio?.toFixed(2) || '未知'}
            </Descriptions.Item>
            <Descriptions.Item label="回声类型">
              {data.imaging_features.echo_type || '未知'}
            </Descriptions.Item>
            <Descriptions.Item label="钙化">
              {data.imaging_features.calcification_type || '无'}
            </Descriptions.Item>
            <Descriptions.Item label="血流分级">
              {data.imaging_features.cdfi_grade || '未知'}
            </Descriptions.Item>
            <Descriptions.Item label="弹性评分">
              {data.imaging_features.elasticity_score || '未知'}
            </Descriptions.Item>
            <Descriptions.Item label="生长速度">
              {data.imaging_features.growth_rate || '未知'}
            </Descriptions.Item>
            <Descriptions.Item label="大小 (cm)">
              {data.imaging_features.lesion_size_cm?.toFixed(2) || '未知'}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </div>
    </div>
  );
};

export default ImagingTCMPage;
