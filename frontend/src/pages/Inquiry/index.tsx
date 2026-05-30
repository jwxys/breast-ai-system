import React, { useState, useEffect, useRef } from 'react';
import { Inbox } from '@icon-park/react';
import styles from './index.module.scss';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface CollectedFields {
  [key: string]: any;
}

interface InquirySession {
  session_id: string;
  messages: Message[];
  collected_fields: CollectedFields;
  status: 'active' | 'completed' | 'closed';
}

const AIInquiryPage: React.FC = () => {
  const [sessionId, setSessionId] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [collectedFields, setCollectedFields] = useState<CollectedFields>({});
  const [sessionStatus, setSessionStatus] = useState<'active' | 'completed' | 'closed'>('active');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 初始化会话
  useEffect(() => {
    createSession();
  }, []);

  // 创建会话
  const createSession = async () => {
    try {
      const response = await fetch('/api/v1/inquiry/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        throw new Error('创建会话失败');
      }

      const data = await response.json();
      setSessionId(data.session_id);

      // 添加欢迎消息
      const welcomeMessage: Message = {
        role: 'assistant',
        content: data.welcome_message,
        timestamp: data.created_at,
      };
      setMessages([welcomeMessage]);
    } catch (error) {
      console.error('创建会话失败:', error);
      alert('创建会话失败，请刷新页面重试');
    }
  };

  // 发送消息
  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || isLoading) {
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    // 添加用户消息到列表
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`/api/v1/inquiry/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
        }),
      });

      if (!response.ok) {
        throw new Error('发送消息失败');
      }

      const data = await response.json();

      // 添加 AI 回复
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: data.updated_at,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // 更新收集的字段
      setCollectedFields(data.collected_fields);
    } catch (error) {
      console.error('发送消息失败:', error);
      alert('发送消息失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 处理键盘事件
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 关闭会话
  const closeSession = async () => {
    if (!sessionId) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/inquiry/sessions/${sessionId}/close`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('关闭会话失败');
      }

      setSessionStatus('closed');
      alert('会话已结束，信息已保存');
    } catch (error) {
      console.error('关闭会话失败:', error);
    }
  };

  // 格式化时间
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={styles.inquiryPage}>
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <Inbox theme="outline" size="32" fill="#1890ff" />
          <div className={styles.headerTitle}>
            <h1>AI 超声前问诊</h1>
            <p>智能交互式问诊助手 - 小樱</p>
          </div>
        </div>
        {sessionStatus === 'active' && (
          <button className={styles.closeButton} onClick={closeSession}>
            结束问诊
          </button>
        )}
      </div>

      <div className={styles.mainContent}>
        {/* 对话区域 */}
        <div className={styles.chatContainer}>
          <div className={styles.messagesContainer}>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`${styles.message} ${
                  message.role === 'user' ? styles.userMessage : styles.assistantMessage
                }`}
              >
                <div className={styles.messageContent}>
                  <div className={styles.messageHeader}>
                    <span className={styles.messageRole}>
                      {message.role === 'user' ? '您' : '小樱'}
                    </span>
                    <span className={styles.messageTime}>{formatTime(message.timestamp)}</span>
                  </div>
                  <div className={styles.messageBody}>{message.content}</div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className={`${styles.message} ${styles.assistantMessage}`}>
                <div className={styles.messageContent}>
                  <div className={styles.typingIndicator}>
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className={styles.inputContainer}>
            <textarea
              className={styles.input}
              placeholder="请输入您的消息...（按 Enter 发送，Shift+Enter 换行）"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={sessionStatus !== 'active' || isLoading}
              rows={3}
            />
            <button
              className={styles.sendButton}
              onClick={sendMessage}
              disabled={!inputMessage.trim() || sessionStatus !== 'active' || isLoading}
            >
              发送
            </button>
          </div>
        </div>

        {/* 信息收集面板 */}
        <div className={styles.infoPanel}>
          <div className={styles.panelHeader}>
            <h3>已收集的信息</h3>
            {sessionStatus === 'active' && (
              <span className={styles.statusBadge}>进行中</span>
            )}
          </div>
          <div className={styles.panelContent}>
            {Object.keys(collectedFields).length === 0 ? (
              <div className={styles.emptyState}>
                <p>暂无收集的信息</p>
                <p className={styles.hint}>AI 助手会在对话中自动提取关键信息</p>
              </div>
            ) : (
              <div className={styles.fieldsList}>
                {Object.entries(collectedFields).map(([key, value]) => (
                  <div key={key} className={styles.fieldItem}>
                    <span className={styles.fieldLabel}>{key}:</span>
                    <span className={styles.fieldValue}>{String(value)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className={styles.panelFooter}>
            <p className={styles.hint}>
              问诊结束后，信息将自动保存到患者的就诊记录中
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIInquiryPage;
