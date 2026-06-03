/**
 * 诊断详情页面
 * 
 * 展示完整的诊断信息：
 * - 基本信息
 * - BI-RADS 评估
 * - AI 分析结果
 * - 病理数据
 * - 分子分型
 * - 报告版本历史
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, Descriptions, Tag, Space, Button, 
  Timeline, Modal, Divider, Statistic, Row, Col,
  Typography, Alert, Badge, Tabs 
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  HistoryOutlined,
  RobotOutlined,
  ExperimentOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;
const { TabPane } = Tabs;

// 类型定义
interface Diagnosis {
  id: number;
  report_no: string;
  patient_name: string;
  patient_age: number;
  lesion_location: string;
  birads_category: string;
  malignancy_risk: number;
  recommendation: string;
  ai_assisted: boolean;
  ai_model_name?: string;
  ai_birads_prediction?: string;
  ai_confidence?: number;
  pathology_type?: string;
  molecular_subtype?: string;
  report_status: string;
  created_at: string;
  reviewed_by?: number;
}

interface ReportVersion {
  id: number;
  version_no: number;
  ultrasound_findings: string;
  impression: string;
  recommendations: string;
  changes_from_previous?: string;
  created_at: string;
  created_by?: number;
}

/**
 * BI-RADS 分级颜色映射
 */
const getBiradsColor = (category: string): string => {
  const colors: Record<string, string> = {
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
  return colors[category] || 'default';
};

/**
 * BI-RADS 分级说明
 */
const getBiradsExplanation = (category: string): string => {
  const explanations: Record<string, string> = {
    '0': '评估不完全 - 需要进一步检查',
    '1': '阴性 - 无异常发现',
    '2': '良性 - 明确良性病变',
    '3': '可能良性 - 恶性风险≤2%',
    '4A': '低度可疑 - 恶性风险 2-10%',
    '4B': '中度可疑 - 恶性风险 10-50%',
    '4C': '高度可疑 - 恶性风险 50-95%',
    '5': '高度提示恶性 - 恶性风险>95%',
    '6': '已证实恶性 - 活检证实',
  };
  return explanations[category] || '未知分级';
};

/**
 * 分子分型颜色
 */
const getSubtypeColor = (subtype: string): string => {
  const colors: Record<string, string> = {
    'Luminal A': 'green',
    'Luminal B': 'blue',
    'HER2-enriched': 'orange',
    'Basal-like': 'red',
    'Normal-like': 'purple',
  };
  return colors[subtype] || 'default';
};

/**
 * 诊断详情页组件
 */
const DiagnosisDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  // 状态管理
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
  const [loading, setLoading] = useState(true);
  const [reportVersions, setReportVersions] = useState<ReportVersion[]>([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [versionModalVisible, setVersionModalVisible] = useState(false);
  
  // 加载诊断详情
  const loadDiagnosis = async () => {
    try {
      const response = await fetch(`/api/v1/diagnosis/${id}`);
      if (response.ok) {
        const data = await response.json();
        setDiagnosis(data);
      } else {
        throw new Error('加载失败');
      }
    } catch (error) {
      console.error('加载诊断详情失败:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // 加载报告版本历史
  const loadReportVersions = async () => {
    try {
      const response = await fetch(`/api/v1/diagnosis/${id}/reports`);
      if (response.ok) {
        const data = await response.json();
        setReportVersions(data);
      }
    } catch (error) {
      console.error('加载报告版本失败:', error);
    }
  };
  
  // 组件加载
  useEffect(() => {
    if (id) {
      loadDiagnosis();
      loadReportVersions();
    }
  }, [id]);
  
  // 打开版本历史弹窗
  const showVersionHistory = () => {
    setVersionModalVisible(true);
  };
  
  /**
   * 基本信息标签页
   */
  const renderOverview = () => (
    <Card loading={loading}>
      <Alert
        message={`BI-RADS ${diagnosis?.birads_category} 类`}
        description={getBiradsExplanation(diagnosis?.birads_category || '')}
        type={
          diagnosis && ['4A', '4B', '4C', '5', '6'].includes(diagnosis.birads_category)
            ? 'warning'
            : 'info'
        }
        showIcon
        style={{ marginBottom: 24 }}
        icon={
          diagnosis && diagnosis.birads_category.includes('4') ? (
            <WarningOutlined />
          ) : diagnosis && diagnosis.birads_category === '5' ? (
            <WarningOutlined />
          ) : (
            <CheckCircleOutlined />
          )
        }
      />
      
      {/* 关键指标 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="恶性风险"
              value={diagnosis?.malignancy_risk ? (diagnosis.malignancy_risk * 100).toFixed(1) : 0}
              suffix="%"
              valueStyle={{ 
                color: diagnosis && diagnosis.malignancy_risk > 0.5 ? '#cf1322' : '#3f8600' 
              }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="AI 置信度"
              value={diagnosis?.ai_confidence ? (diagnosis.ai_confidence * 100).toFixed(0) : 0}
              suffix="%"
              precision={0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="报告状态"
              value={
                diagnosis?.report_status === 'final' ? '正式' :
                diagnosis?.report_status === 'preliminary' ? '初步' : '草稿'
              }
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="报告版本"
              value={reportVersions.length}
              suffix="个"
            />
          </Card>
        </Col>
      </Row>
      
      {/* 基本信息 */}
      <Descriptions title="基本信息" bordered column={2}>
        <Descriptions.Item label="报告编号">{diagnosis?.report_no}</Descriptions.Item>
        <Descriptions.Item label="报告日期">
          {diagnosis?.created_at ? new Date(diagnosis.created_at).toLocaleDateString() : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="患者姓名">{diagnosis?.patient_name}</Descriptions.Item>
        <Descriptions.Item label="患者年龄">{diagnosis?.patient_age} 岁</Descriptions.Item>
        <Descriptions.Item label="病灶位置">{diagnosis?.lesion_location}</Descriptions.Item>
        <Descriptions.Item label="AI 辅助">
          {diagnosis?.ai_assisted ? (
            <Tag color="blue">是</Tag>
          ) : (
            <Tag>否</Tag>
          )}
        </Descriptions.Item>
      </Descriptions>
      
      <Divider />
      
      {/* BI-RADS 评估 */}
      <Descriptions title="BI-RADS 评估" bordered column={1}>
        <Descriptions.Item label="BI-RADS 分级">
          <Tag color={getBiradsColor(diagnosis?.birads_category || '')}>
            {diagnosis?.birads_category}
          </Tag>
        </Descriptions.Item>
        <Descriptions.Item label="恶性风险">
          {diagnosis?.malignancy_risk ? `${(diagnosis.malignancy_risk * 100).toFixed(1)}%` : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="处理建议">
          <Text strong>{diagnosis?.recommendation}</Text>
        </Descriptions.Item>
      </Descriptions>
      
      <Divider />
      
      {/* AI 分析结果 */}
      {diagnosis?.ai_assisted && (
        <>
          <Alert
            message={
              <Space>
                <RobotOutlined />
                <Text strong>AI 辅助诊断结果</Text>
              </Space>
            }
            type="success"
            showIcon
            style={{ marginBottom: 16 }}
          />
          
          <Descriptions title="AI 分析" bordered column={2}>
            <Descriptions.Item label="AI 模型">
              {diagnosis.ai_model_name || 'Kimi-vision'}
            </Descriptions.Item>
            <Descriptions.Item label="AI 预测 BI-RADS">
              <Tag color={getBiradsColor(diagnosis.ai_birads_prediction || '')}>
                {diagnosis.ai_birads_prediction}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="恶性概率">
              {diagnosis.ai_confidence ? `${(diagnosis.ai_confidence * 100).toFixed(1)}%` : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="置信度">
              {diagnosis.ai_confidence ? `${(diagnosis.ai_confidence * 100).toFixed(0)}%` : '-'}
            </Descriptions.Item>
          </Descriptions>
        </>
      )}
      
      <Divider />
      
      {/* 病理与分子分型 */}
      {diagnosis?.pathology_type && (
        <>
          <Alert
            message={
              <Space>
                <ExperimentOutlined />
                <Text strong>病理诊断</Text>
              </Space>
            }
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          
          <Descriptions title="病理结果" bordered column={2}>
            <Descriptions.Item label="病理类型">{diagnosis.pathology_type}</Descriptions.Item>
            <Descriptions.Item label="分子分型">
              {diagnosis.molecular_subtype ? (
                <Tag color={getSubtypeColor(diagnosis.molecular_subtype)}>
                  {diagnosis.molecular_subtype}
                </Tag>
              ) : '-'}
            </Descriptions.Item>
          </Descriptions>
        </>
      )}
    </Card>
  );
  
  /**
   * 报告内容标签页
   */
  const renderReport = () => {
    const latestVersion = reportVersions.length > 0 ? reportVersions[reportVersions.length - 1] : null;
    
    return (
      <Card loading={loading}>
        {latestVersion ? (
          <>
            <div style={{ marginBottom: 16 }}>
              <Space>
                <Badge count={latestVersion.version_no} overflowCount={99}>
                  <FileTextOutlined />
                </Badge>
                <Text strong>版本 {latestVersion.version_no}</Text>
                <Text type="secondary">
                  创建时间：{new Date(latestVersion.created_at).toLocaleString()}
                </Text>
              </Space>
            </div>
            
            <Descriptions title="超声所见" bordered column={1}>
              <Descriptions.Item>
                <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
                  {latestVersion.ultrasound_findings}
                </Paragraph>
              </Descriptions.Item>
            </Descriptions>
            
            <Divider />
            
            <Descriptions title="诊断印象" bordered column={1}>
              <Descriptions.Item>
                <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
                  {latestVersion.impression}
                </Paragraph>
              </Descriptions.Item>
            </Descriptions>
            
            <Divider />
            
            <Descriptions title="建议" bordered column={1}>
              <Descriptions.Item>
                <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
                  {latestVersion.recommendations}
                </Paragraph>
              </Descriptions.Item>
            </Descriptions>
            
            {latestVersion.changes_from_previous && (
              <>
                <Divider />
                <Alert
                  message="版本变更说明"
                  description={latestVersion.changes_from_previous}
                  type="warning"
                  showIcon
                />
              </>
            )}
          </>
        ) : (
          <Alert
            message="暂无报告"
            description="该诊断尚未创建报告版本"
            type="info"
            showIcon
          />
        )}
      </Card>
    );
  };
  
  /**
   * 版本历史标签页
   */
  const renderHistory = () => (
    <Card loading={loading}>
      <Timeline
        items={reportVersions.map((version) => ({
          key: version.id,
          color: version.version_no === 1 ? 'green' : 'blue',
          children: (
            <Card size="small" style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Space>
                  <Badge count={version.version_no} />
                  <Text strong>版本 {version.version_no}</Text>
                </Space>
                <Text type="secondary">
                  {new Date(version.created_at).toLocaleString()}
                </Text>
              </div>
              
              {version.changes_from_previous && (
                <Paragraph type="secondary" style={{ marginTop: 8 }}>
                  变更：{version.changes_from_previous}
                </Paragraph>
              )}
              
              <div style={{ marginTop: 12 }}>
                <Button
                  type="link"
                  size="small"
                  onClick={() => {
                    // 查看版本详情
                  }}
                >
                  查看详情
                </Button>
                {reportVersions.length > 1 && (
                  <Button
                    type="link"
                    size="small"
                    onClick={() => {
                      // 比较版本
                    }}
                  >
                    比较版本
                  </Button>
                )}
              </div>
            </Card>
          ),
        }))}
      />
    </Card>
  );
  
  return (
    <div className="diagnosis-detail">
      {/* 顶部导航栏 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/diagnosis')}
          >
            返回列表
          </Button>
          <Space style={{ marginLeft: 'auto' }}>
            <Button icon={<HistoryOutlined />} onClick={showVersionHistory}>
              版本历史
            </Button>
            <Button icon={<EditOutlined />} type="primary">
              编辑诊断
            </Button>
          </Space>
        </Space>
      </div>
      
      {/* 标签页 */}
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="基本信息" key="overview">
          {renderOverview()}
        </TabPane>
        <TabPane tab="报告内容" key="report">
          {renderReport()}
        </TabPane>
        <TabPane tab="版本历史" key="history">
          {renderHistory()}
        </TabPane>
      </Tabs>
      
      {/* 版本历史弹窗 */}
      <Modal
        title="版本历史"
        open={versionModalVisible}
        onCancel={() => setVersionModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setVersionModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        <Timeline
          items={reportVersions.map((version, index) => ({
            key: version.id,
            title: `版本 ${version.version_no}`,
            children: (
              <div>
                <Text type="secondary">
                  {new Date(version.created_at).toLocaleString()}
                </Text>
                {version.changes_from_previous && (
                  <Paragraph type="secondary" style={{ marginTop: 8 }}>
                    变更：{version.changes_from_previous}
                  </Paragraph>
                )}
              </div>
            ),
          }))}
        />
      </Modal>
    </div>
  );
};

export default DiagnosisDetail;
