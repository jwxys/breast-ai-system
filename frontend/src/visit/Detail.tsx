/**
 * 随访详情页
 * 展示随访记录详情、AI 分析结果、随访计划
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  Descriptions,
  Tag,
  Space,
  Button,
  Typography,
  Divider,
  Row,
  Col,
  Statistic,
  Timeline,
  Badge,
  Alert,
  Modal,
  message,
  Steps,
  Progress,
} from 'antd';
import {
  FileTextOutlined,
  MedicineBoxOutlined,
  CalendarOutlined,
  UserOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ThunderboltOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;
const { Step } = Steps;

interface VisitDetail {
  id: number;
  patient_id: number;
  patient_name: string;
  visit_date: string;
  visit_type: '术后' | '化疗' | '放疗' | '常规' | '紧急';
  chief_complaint: string;
  present_illness: string;
  physical_exam: string;
  treatment_plan: string;
  doctor: string;
  status: '待随访' | '已随访' | '已取消';
  ai_analysis?: {
    risk_level: '低危' | '中危' | '高危';
    recurrence_risk: number;
    recommendations: string[];
    kimid_response?: string;
  };
  next_visit_date?: string;
}

const VisitDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [visit, setVisit] = useState<VisitDetail | null>(null);
  const [aiAnalyzing, setAiAnalyzing] = useState(false);
  const [showAiResult, setShowAiResult] = useState(false);

  // 获取随访详情
  useEffect(() => {
    fetchVisitDetail();
  }, [id]);

  const fetchVisitDetail = async () => {
    setLoading(true);
    try {
      // TODO: 调用 API
      // const response = await fetch(`/api/v1/visits/${id}`);
      // const data = await response.json();
      
      // 模拟数据
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const mockData: VisitDetail = {
        id: Number(id),
        patient_id: 1,
        patient_name: '张**',
        visit_date: '2026-05-25',
        visit_type: '术后',
        chief_complaint: '术后 2 周复诊，切口恢复良好',
        present_illness: '患者 2 周前行乳腺癌根治术，术后恢复良好，无发热，切口愈合良好。',
        physical_exam: '生命体征平稳，心肺听诊无异常，腹部软，无压痛反跳痛，切口敷料干燥。',
        treatment_plan: '1. 继续抗感染治疗 3 天\n2. 术后 4 周开始化疗\n3. 定期复查血常规',
        doctor: '李医生',
        status: '已随访',
        next_visit_date: '2026-06-25',
      };
      
      setVisit(mockData);
    } catch (error) {
      message.error('获取随访详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 执行 AI 分析
  const handleAiAnalysis = async () => {
    if (!visit) return;
    
    setAiAnalyzing(true);
    try {
      // TODO: 调用 AI 分析 API
      // await fetch(`/api/v1/visits/${id}/ai-analysis`, { method: 'POST' });
      
      // 模拟分析
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      setVisit({
        ...visit,
        ai_analysis: {
          risk_level: '中危',
          recurrence_risk: 23.5,
          recommendations: [
            '建议术后 4 周开始辅助化疗',
            '定期复查肿瘤标志物',
            '注意切口感染迹象',
            '保持良好心态，适度运动',
          ],
          kimid_response: '基于患者术后恢复情况和病理结果，复发风险中等。建议按 NCCN 指南进行辅助治疗。',
        },
      });
      
      setShowAiResult(true);
      message.success('AI 分析完成！');
    } catch (error) {
      message.error('AI 分析失败');
    } finally {
      setAiAnalyzing(false);
    }
  };

  // 风险等级颜色
  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case '低危': return 'green';
      case '中危': return 'orange';
      case '高危': return 'red';
      default: return 'default';
    }
  };

  // 随访类型颜色
  const getVisitTypeColor = (type: string) => {
    switch (type) {
      case '术后': return 'blue';
      case '化疗': return 'purple';
      case '放疗': return 'cyan';
      case '常规': return 'green';
      case '紧急': return 'red';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <div style={{ fontSize: 64, marginBottom: 16 }}><FileTextOutlined /></div>
        <div>加载中...</div>
      </div>
    );
  }

  if (!visit) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <ExclamationCircleOutlined style={{ fontSize: 64, color: 'red' }} />
        <div>随访记录不存在</div>
      </div>
    );
  }

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>
      {/* 页面标题 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <FileTextOutlined style={{ fontSize: 28, color: '#1890ff' }} />
          <div>
            <Title level={2} style={{ margin: 0 }}>随访详情</Title>
            <Text type="secondary">ID: {visit.id} | 患者：{visit.patient_name}</Text>
          </div>
        </div>
        <Space>
          <Button icon={<HomeOutlined />} onClick={() => navigate('/visits')}>
            返回列表
          </Button>
          <Button icon={<EditOutlined />} onClick={() => {/* 编辑 */}}>
            编辑
          </Button>
          <Button danger icon={<DeleteOutlined />} onClick={() => {/* 删除 */}}>
            删除
          </Button>
        </Space>
      </div>

      <Row gutter={16}>
        {/* 左侧：随访信息 */}
        <Col span={16}>
          <Card
            title="随访信息"
            style={{ marginBottom: 16 }}
          >
            <Descriptions bordered column={2}>
              <Descriptions.Item label="患者姓名">
                <UserOutlined /> {visit.patient_name}
              </Descriptions.Item>
              <Descriptions.Item label="随访日期">
                <CalendarOutlined /> {visit.visit_date}
              </Descriptions.Item>
              <Descriptions.Item label="随访类型">
                <Tag color={getVisitTypeColor(visit.visit_type)}>{visit.visit_type}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="随访状态">
                <Badge
                  status={visit.status === '已随访' ? 'success' : visit.status === '待随访' ? 'processing' : 'default'}
                  text={visit.status}
                />
              </Descriptions.Item>
              <Descriptions.Item label="接诊医生">
                <MedicineBoxOutlined /> {visit.doctor}
              </Descriptions.Item>
              <Descriptions.Item label="下次随访">
                {visit.next_visit_date ? (
                  <Tag color="blue"><CalendarOutlined /> {visit.next_visit_date}</Tag>
                ) : (
                  <Text type="secondary">未安排</Text>
                )}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 病情信息 */}
          <Card
            title={<><MedicineBoxOutlined /> 病情记录</>}
            style={{ marginBottom: 16 }}
          >
            <div style={{ marginBottom: 16 }}>
              <Title level={5} style={{ marginBottom: 8 }}>主诉</Title>
              <Paragraph style={{ background: '#fafafa', padding: 12, borderRadius: 4 }}>
                {visit.chief_complaint}
              </Paragraph>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Title level={5} style={{ marginBottom: 8 }}>现病史</Title>
              <Paragraph style={{ background: '#fafafa', padding: 12, borderRadius: 4 }}>
                {visit.present_illness}
              </Paragraph>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Title level={5} style={{ marginBottom: 8 }}>体格检查</Title>
              <Paragraph style={{ background: '#fafafa', padding: 12, borderRadius: 4 }}>
                {visit.physical_exam}
              </Paragraph>
            </div>

            <div>
              <Title level={5} style={{ marginBottom: 8 }}>治疗方案</Title>
              <Paragraph style={{ background: '#f0f5ff', padding: 12, borderRadius: 4 }}>
                {visit.treatment_plan}
              </Paragraph>
            </div>
          </Card>

          {/* AI 分析结果 */}
          {visit.ai_analysis && (
            <Card
              title={
                <Space>
                  <ThunderboltOutlined style={{ color: '#fadb14' }} />
                  AI 辅助分析
                </Space>
              }
              style={{ marginBottom: 16 }}
            >
              <Row gutter={16}>
                <Col span={8}>
                  <Card size="small">
                    <Statistic
                      title="复发风险"
                      value={visit.ai_analysis.recurrence_risk}
                      suffix="%"
                      valueStyle={{ color: '#f5222d' }}
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card size="small">
                    <Statistic
                      title="风险等级"
                      value={visit.ai_analysis.risk_level}
                      valueStyle={{ color: '#fa8c16' }}
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card size="small">
                    <Statistic
                      title="分析时间"
                      value="2.3"
                      suffix="秒"
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Card>
                </Col>
              </Row>

              <Divider />

              <Title level={5}>Kimi AI 分析</Title>
              <Paragraph style={{ background: '#fffbe6', padding: 12, borderRadius: 4 }}>
                {visit.ai_analysis.kimid_response}
              </Paragraph>

              <Divider />

              <div>
                <Title level={5}>随访建议</Title>
                <Timeline
                  items={visit.ai_analysis.recommendations.map((rec, index) => ({
                    color: 'blue',
                    children: rec,
                  }))}
                />
              </div>
            </Card>
          )}
        </Col>

        {/* 右侧：随访计划 */}
        <Col span={8}>
          {/* AI 分析按钮 */}
          {!visit.ai_analysis && (
            <Card style={{ marginBottom: 16 }}>
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <ThunderboltOutlined style={{ fontSize: 48, color: '#fadb14', marginBottom: 16 }} />
                <Title level={5}>AI 辅助分析</Title>
                <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
                  基于患者病史和检查结果，AI 将提供复发风险评估和随访建议
                </Text>
                <Button
                  type="primary"
                  size="large"
                  icon={<ThunderboltOutlined />}
                  loading={aiAnalyzing}
                  onClick={handleAiAnalysis}
                  block
                >
                  {aiAnalyzing ? '分析中...' : '开始 AI 分析'}
                </Button>
                
                {aiAnalyzing && (
                  <div style={{ marginTop: 16 }}>
                    <Progress percent={70} status="active" />
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* 随访时间轴 */}
          <Card title="随访时间轴" style={{ marginBottom: 16 }}>
            <Timeline
              mode="left"
              items={[
                {
                  color: 'green',
                  children: (
                    <div>
                      <Text strong>{visit.visit_date}</Text>
                      <div>本次随访</div>
                    </div>
                  ),
                },
                {
                  color: 'blue',
                  children: (
                    <div>
                      <Text strong>2026-05-10</Text>
                      <div>术后首次随访</div>
                    </div>
                  ),
                },
                {
                  color: 'gray',
                  children: (
                    <div>
                      <Text strong>2026-05-01</Text>
                      <div>手术日期</div>
                    </div>
                  ),
                },
              ]}
            />
          </Card>

          {/* 下次随访提醒 */}
          {visit.next_visit_date && (
            <Card title="下次随访提醒">
              <Alert
                message="随访提醒"
                description={
                  <div>
                    <Text strong>日期：</Text>{visit.next_visit_date}
                    <br />
                    <Text strong>类型：</Text>常规复查
                    <br />
                    <Text strong>注意：</Text>提前 3 天预约
                  </div>
                }
                type="info"
                showIcon
                style={{ marginTop: 8 }}
              />
              
              <Button
                type="primary"
                block
                style={{ marginTop: 16 }}
                icon={<PlusOutlined />}
                onClick={() => {/* 安排随访 */}}
              >
                安排下次随访
              </Button>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default VisitDetailPage;
