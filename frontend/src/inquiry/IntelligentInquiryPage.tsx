/**
 * 智能问诊聊天页面 (优化版)
 * 增强错误处理、UI 细节和用户体验
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Typography,
  Space,
  Divider,
  Tag,
  Progress,
  Spin,
  Alert,
  Timeline,
  Collapse,
  Row,
  Col,
  Statistic,
  Badge,
  Result,
  message,
  Modal,
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  FileTextOutlined,
  HistoryOutlined,
  SaveOutlined,
  ExportOutlined,
  RedoOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import { sendChatMessage, getChatReport, endChatSession } from '@/api/symptomChat';

const { Title, Paragraph, Text } = Typography;
const { Panel } = Collapse;

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isError?: boolean;
}

interface CollectedInfo {
  age?: number;
  primary_symptom?: string;
  onset_time?: string;
  menstrual_status?: string;
  family_history?: boolean;
  [key: string]: any;
}

interface RiskAssessment {
  level: '低危' | '中危' | '高危';
  score: number;
  factors: string[];
  recommendation: string;
}

interface ChatState {
  completeness: number;
  is_complete: boolean;
  risk_assessment?: RiskAssessment;
  follow_up_questions: string[];
  next_step: string;
}

const IntelligentInquiryPage: React.FC = () => {
  // 聊天状态
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '您好，我是您的 AI 乳腺健康助手。我会通过一些问题了解您的情况，以便为您提供更专业的建议。请问您哪里不舒服？',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const sessionId = useRef(`session_${Date.now()}_${Math.random().toString(36).substring(7)}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // 采集信息状态
  const [collectedInfo, setCollectedInfo] = useState<CollectedInfo>({});
  const [chatState, setChatState] = useState<ChatState>({
    completeness: 0,
    is_complete: false,
    follow_up_questions: [],
    next_step: '',
  });

  // 错误状态
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isSending) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsSending(true);
    setHasError(false);

    try {
      // 调用 API
      const data = await sendChatMessage({
        session_id: sessionId.current,
        message: currentInput,
      });

      // AI 回复
      const aiMessage: Message = {
        id: `msg_${Date.now()}_ai`,
        role: 'assistant',
        content: data.response || '抱歉，我没有理解您的意思，能再说一遍吗？',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);

      // 更新状态
      setCollectedInfo(data.collected_info || {});
      setChatState({
        completeness: data.completeness || 0,
        is_complete: data.is_complete || false,
        risk_assessment: data.risk_assessment,
        follow_up_questions: data.follow_up_questions || [],
        next_step: data.next_step || '',
      });

      // 提示信息
      if (data.is_complete) {
        message.success('信息采集完成！可以保存问诊记录了');
      }
    } catch (error: any) {
      console.error('发送消息失败:', error);
      
      // 降级回复
      const errorMessage: Message = {
        id: `msg_${Date.now()}_error`,
        role: 'assistant',
        content: error.message || '抱歉，系统暂时繁忙，请稍后再试。',
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
      setHasError(true);
      setErrorMessage(error.message || '网络请求失败');
      message.error('发送失败，请重试');
    } finally {
      setIsSending(false);
    }
  };

  // 处理回车发送
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // 保存问诊记录
  const handleSaveRecord = async () => {
    try {
      const data = await getChatReport(sessionId.current);
      console.log('问诊报告:', data.report);
      message.success('问诊记录已保存');
    } catch (error: any) {
      message.error(`保存失败：${error.message}`);
    }
  };

  // 结束问诊
  const handleEndChat = async () => {
    Modal.confirm({
      title: '确认结束问诊？',
      content: '结束后的问诊记录将无法继续编辑，确定要结束吗？',
      onOk: async () => {
        try {
          await endChatSession(sessionId.current);
          message.success('问诊已结束');
          // 重置状态
          setMessages([{
            id: '1',
            role: 'assistant',
            content: '您好，我是您的 AI 乳腺健康助手。请问您哪里不舒服？',
            timestamp: new Date(),
          }]);
          setCollectedInfo({});
          setChatState({ completeness: 0, is_complete: false, follow_up_questions: [], next_step: '' });
          sessionId.current = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
        } catch (error: any) {
          message.error(`结束失败：${error.message}`);
        }
      },
    });
  };

  // 重试连接
  const handleRetry = () => {
    setHasError(false);
    setErrorMessage('');
    message.info('已重试连接');
  };

  // 获取风险等级颜色
  const getRiskColor = (level: string) => {
    switch (level) {
      case '低危': return 'green';
      case '中危': return 'orange';
      case '高危': return 'red';
      default: return 'default';
    }
  };

  // 获取风险等级图标
  const getRiskIcon = (level: string) => {
    switch (level) {
      case '低危': return <CheckCircleOutlined />;
      case '中危': return <ExclamationCircleOutlined />;
      case '高危': return <ExclamationCircleOutlined />;
      default: return null;
    }
  };

  return (
    <div style={{ 
      padding: 24, 
      minHeight: 'calc(100vh - 64px)', 
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' 
    }}>
      <Row gutter={16}>
        {/* 左侧：聊天窗口 */}
        <Col span={16}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card
              title={
                <Space>
                  <RobotOutlined style={{ color: '#1890ff', fontSize: 24 }} />
                  <Title level={3} style={{ margin: 0 }}>AI 智能问诊</Title>
                  <Tag color="blue">beta</Tag>
                </Space>
              }
              extra={
                <Space>
                  <Button
                    icon={<SaveOutlined />}
                    onClick={handleSaveRecord}
                    disabled={!chatState.is_complete}
                    size="small"
                  >
                    保存
                  </Button>
                  <Button
                    icon={<StopOutlined />}
                    onClick={handleEndChat}
                    danger
                    size="small"
                  >
                    结束
                  </Button>
                </Space>
              }
              style={{ 
                borderRadius: 16,
                boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
                overflow: 'hidden',
              }}
            >
              {/* 错误提示 */}
              <AnimatePresence>
                {hasError && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    style={{ marginBottom: 16 }}
                  >
                    <Alert
                      type="error"
                      message="连接失败"
                      description={
                        <Space>
                          <Text>{errorMessage}</Text>
                          <Button type="link" size="small" icon={<RedoOutlined />} onClick={handleRetry}>
                            重试
                          </Button>
                        </Space>
                      }
                      showIcon
                      closable
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* 聊天消息列表 */}
              <div 
                ref={chatContainerRef}
                style={{ 
                  height: 'calc(100vh - 380px)', 
                  overflowY: 'auto',
                  padding: '0 8px',
                  scrollbarWidth: 'thin',
                }}
              >
                <AnimatePresence>
                  {messages.map((msg) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 20, scale: 0.8 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ duration: 0.2 }}
                      style={{
                        display: 'flex',
                        justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        marginBottom: 16,
                      }}
                    >
                      <Space
                        align="start"
                        style={{
                          maxWidth: '70%',
                          padding: '12px 16px',
                          background: msg.role === 'user' 
                            ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                            : '#f0f0f0',
                          color: msg.role === 'user' ? '#fff' : '#000',
                          borderRadius: 16,
                          boxShadow: msg.role === 'user' 
                            ? '0 4px 12px rgba(102, 126, 234, 0.4)' 
                            : '0 2px 8px rgba(0,0,0,0.1)',
                        }}
                      >
                        {msg.role === 'assistant' && (
                          <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            style={{ fontSize: 20 }}
                          >
                            <RobotOutlined />
                          </motion.div>
                        )}
                        <div>
                          <div style={{ fontSize: 14, lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                            {msg.content}
                          </div>
                          <div style={{ 
                            fontSize: 12, 
                            opacity: msg.role === 'user' ? 0.8 : 0.6,
                            marginTop: 4,
                          }}>
                            {msg.timestamp.toLocaleTimeString()}
                          </div>
                          {msg.isError && (
                            <Tag color="red" style={{ marginTop: 4 }}>错误</Tag>
                          )}
                        </div>
                        {msg.role === 'user' && (
                          <UserOutlined style={{ fontSize: 20 }} />
                        )}
                      </Space>
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                {isSending && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    style={{
                      display: 'flex',
                      justifyContent: 'flex-start',
                      marginBottom: 16,
                    }}
                  >
                    <Space
                      style={{
                        padding: '12px 16px',
                        background: '#f0f0f0',
                        borderRadius: 16,
                      }}
                    >
                      <RobotOutlined style={{ fontSize: 20 }} />
                      <Spin size="small" />
                      <Text>AI 思考中...</Text>
                    </Space>
                  </motion.div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              <Divider style={{ margin: '12px 0' }} />

              {/* 输入区域 */}
              <div style={{ padding: '0 8px' }}>
                <Space.Compact style={{ width: '100%' }}>
                  <Input.TextArea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="请描述您的症状，例如：乳房有肿块、疼痛..."
                    rows={3}
                    disabled={isSending}
                    style={{ 
                      resize: 'none',
                      borderRadius: '8px 0 0 8px',
                    }}
                  />
                  <Button
                    type="primary"
                    icon={<SendOutlined />}
                    onClick={handleSendMessage}
                    loading={isSending}
                    size="large"
                    style={{ borderRadius: '0 8px 8px 0' }}
                  >
                    发送
                  </Button>
                </Space.Compact>
                
                <div style={{ 
                  marginTop: 8, 
                  fontSize: 12, 
                  color: '#666',
                  textAlign: 'center' 
                }}>
                  <Space split={<Divider type="vertical" />}>
                    <span>按 Enter 发送</span>
                    <span>Shift+Enter 换行</span>
                  </Space>
                </div>
              </div>
            </Card>
          </motion.div>
        </Col>

        {/* 右侧：信息面板 */}
        <Col span={8}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            {/* 信息完整度 */}
            <Card
              title={<><FileTextOutlined /> 信息采集进度</>}
              size="small"
              style={{ 
                marginBottom: 16,
                borderRadius: 12,
                boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
              }}
            >
              <div style={{ marginBottom: 16 }}>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  marginBottom: 8,
                  alignItems: 'center',
                }}>
                  <Text strong>完整度</Text>
                  <Badge 
                    count={`${(chatState.completeness * 100).toFixed(0)}%`}
                    color={chatState.completeness > 0.8 ? 'green' : 'blue'}
                  />
                </div>
                <Progress
                  percent={Math.round(chatState.completeness * 100)}
                  status={chatState.is_complete ? 'success' : 'active'}
                  strokeWidth={12}
                  trailColor="#f0f0f0"
                  strokeColor={{
                    '0%': '#667eea',
                    '100%': '#764ba2',
                  }}
                />
              </div>

              <Collapse 
                size="small" 
                ghost
                items={[{
                  key: '1',
                  header: '已采集信息',
                  children: (
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                      {Object.entries(collectedInfo).map(([key, value]) => (
                        <div key={key} style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between',
                          padding: '4px 8px',
                          background: '#f9f9f9',
                          borderRadius: 4,
                        }}>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            {key.replace(/_/g, ' ')}:
                          </Text>
                          <Text strong style={{ fontSize: 12 }}>
                            {value?.toString()}
                          </Text>
                        </div>
                      ))}
                      {Object.keys(collectedInfo).length === 0 && (
                        <Text type="secondary" style={{ fontSize: 12 }}>等待采集...</Text>
                      )}
                    </Space>
                  ),
                }]}
              />
            </Card>

            {/* 风险评估 */}
            {chatState.risk_assessment && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <Card
                  title={<><ExclamationCircleOutlined /> 风险评估</>}
                  size="small"
                  style={{ 
                    marginBottom: 16,
                    borderRadius: 12,
                    boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
                  }}
                >
                  <div style={{ marginBottom: 16, textAlign: 'center' }}>
                    <Tag 
                      color={getRiskColor(chatState.risk_assessment.level)} 
                      style={{ 
                        fontSize: 18, 
                        padding: '6px 16px',
                        fontWeight: 'bold',
                      }}
                    >
                      {getRiskIcon(chatState.risk_assessment.level)}
                      {' '}{chatState.risk_assessment.level}
                    </Tag>
                  </div>
                  
                  <Alert
                    type={
                      chatState.risk_assessment.level === '高危' ? 'error' :
                      chatState.risk_assessment.level === '中危' ? 'warning' : 'info'
                    }
                    message="专业建议"
                    description={chatState.risk_assessment.recommendation}
                    showIcon
                    style={{ marginBottom: 12 }}
                  />
                  
                  {chatState.risk_assessment.factors.length > 0 && (
                    <>
                      <Divider style={{ margin: '12px 0', fontSize: 12 }}>
                        <Text type="secondary">风险因素</Text>
                      </Divider>
                      <Space wrap>
                        {chatState.risk_assessment.factors.map((factor, idx) => (
                          <Tag key={idx} color="default" style={{ fontSize: 12 }}>
                            {factor}
                          </Tag>
                        ))}
                      </Space>
                    </>
                  )}
                </Card>
              </motion.div>
            )}

            {/* 问诊步骤 */}
            <Card
              title={<><HistoryOutlined /> 问诊流程</>}
              size="small"
              style={{ 
                borderRadius: 12,
                boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
              }}
            >
              <Timeline
                mode="left"
                items={[
                  { title: '问候', color: chatState.completeness > 0 ? 'green' : 'gray' },
                  { title: '主诉', color: chatState.completeness > 0.15 ? 'green' : 'gray' },
                  { title: '症状详情', color: chatState.completeness > 0.3 ? 'green' : 'gray' },
                  { title: '患者信息', color: chatState.completeness > 0.5 ? 'green' : 'gray' },
                  { title: '既往史', color: chatState.completeness > 0.7 ? 'green' : 'gray' },
                  { title: '家族史', color: chatState.completeness > 0.85 ? 'green' : 'gray' },
                  { title: '总结', color: chatState.is_complete ? 'green' : 'gray' },
                ]}
              />
            </Card>
          </motion.div>
        </Col>
      </Row>
    </div>
  );
};

export default IntelligentInquiryPage;
