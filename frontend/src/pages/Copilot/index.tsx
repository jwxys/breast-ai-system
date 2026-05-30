import React, { useState, useEffect, useRef } from 'react';
import { Inbox, Unlock, FileText, Setting, Send } from '@icon-park/react';
import styles from './index.module.scss';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: any;
}

interface ChatSession {
  session_id: string;
  mode: 'general' | 'imaging' | 'diagnosis' | 'control';
  messages: Message[];
  status: 'active' | 'paused' | 'closed';
}

interface SuggestedAction {
  icon: React.ReactNode;
  label: string;
  action: string;
}

const MedicalCopilotPage: React.FC = () => {
  const [sessionId, setSessionId] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentMode, setCurrentMode] = useState<'general' | 'imaging' | 'diagnosis' | 'control'>('general');
  const [suggestedActions, setSuggestedActions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 模式配置
  const modeConfig = {
    general: {
      name: '通用对话',
      icon: <Inbox theme="outline" size="20" fill="#667eea" />,
      color: '#667eea',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    },
    imaging: {
      name: '影像分析',
      icon: <Unlock theme="outline" size="20" fill="#11998e" />,
      color: '#11998e',
      gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    },
    diagnosis: {
      name: '诊断辅助',
      icon: <FileText theme="outline" size="20" fill="#f093fb" />,
      color: '#f093fb',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    },
    control: {
      name: '系统控制',
      icon: <Setting theme="outline" size="20" fill="#fa709a" />,
      color: '#fa709a',
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    },
  };

  // 自动滚动
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
      const response = await fetch('/api/v1/copilot/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mode: 'general' }),
      });

      if (!response.ok) {
        throw new Error('创建会话失败');
      }

      const data = await response.json();
      setSessionId(data.session_id);
      setCurrentMode(data.mode as any);

      const welcomeMessage: Message = {
        role: 'assistant',
        content: data.welcome_message,
        timestamp: data.created_at,
      };
      setMessages([welcomeMessage]);
      setSuggestedActions(getDefaultSuggestions());
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

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`/api/v1/copilot/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) {
        throw new Error('发送消息失败');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: data.updated_at,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setCurrentMode(data.mode as any);
      setSuggestedActions(data.suggested_actions || []);
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

  // 获取默认建议操作
  const getDefaultSuggestions = (): string[] => {
    return [
      '影像分析',
      '诊断辅助',
      '患者管理',
      '系统操作',
    ];
  };

  // 点击建议操作
  const handleSuggestedAction = (action: string) => {
    setInputMessage(action);
  };

  // 切换模式
  const switchMode = (mode: 'general' | 'imaging' | 'diagnosis' | 'control') => {
    setCurrentMode(mode);
    setInputMessage(`切换到${modeConfig[mode].name}模式`);
  };

  // 格式化时间
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 关闭会话
  const closeSession = async () => {
    if (!sessionId) return;

    try {
      await fetch(`/api/v1/copilot/sessions/${sessionId}/close`, {
        method: 'POST',
      });
      alert('会话已结束');
    } catch (error) {
      console.error('关闭会话失败:', error);
    }
  };

  return (
    <div className={styles.copilotPage}>
      {/* 顶部导航 */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logo}>
            <Inbox theme="outline" size="36" fill="url(#gradient)" />
          </div>
          <div className={styles.headerTitle}>
            <h1>医疗 Copilot 智能助手</h1>
            <p>医助小樱 - 您的诊疗工作伙伴</p>
          </div>
        </div>
        <button className={styles.closeButton} onClick={closeSession}>
          结束会话
        </button>
      </div>

      {/* 主体内容 */}
      <div className={styles.mainContent}>
        {/* 左侧：模式切换 */}
        <div className={styles.modePanel}>
          <h3>工作模式</h3>
          <div className={styles.modeList}>
            {(Object.keys(modeConfig) as Array<keyof typeof modeConfig>).map((mode) => (
              <div
                key={mode}
                className={`${styles.modeItem} ${
                  currentMode === mode ? styles.modeItemActive : ''
                }`}
                onClick={() => switchMode(mode)}
              >
                <div className={styles.modeIcon}>{modeConfig[mode].icon}</div>
                <span className={styles.modeName}>{modeConfig[mode].name}</span>
                {currentMode === mode && (
                  <div className={styles.modeIndicator}></div>
                )}
              </div>
            ))}
          </div>

          <div className={styles.modeDescription}>
            <h4>{modeConfig[currentMode].name}</h4>
            <p>
              {currentMode === 'general' && '通用对话模式，回答各类医疗相关问题'}
              {currentMode === 'imaging' && '影像分析模式，解释 AI 超声分析结果'}
              {currentMode === 'diagnosis' && '诊断辅助模式，提供中西医结合诊断建议'}
              {currentMode === 'control' && '系统控制模式，执行患者管理、报告生成等操作'}
            </p>
          </div>
        </div>

        {/* 中间：聊天区域 */}
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
                  {message.role === 'assistant' && message.metadata?.mode_switch && (
                    <div className={styles.modeSwitchBadge}>
                      {message.content}
                    </div>
                  )}
                  {!message.metadata?.mode_switch && (
                    <>
                      <div className={styles.messageHeader}>
                        <span className={styles.messageRole}>
                          {message.role === 'user' ? '您' : '小樱'}
                        </span>
                        <span className={styles.messageTime}>{formatTime(message.timestamp)}</span>
                      </div>
                      <div className={styles.messageBody}>{message.content}</div>
                    </>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className={`${styles.message} ${styles.assistantMessage}`}>
                <div className={styles.typingIndicator}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className={styles.inputContainer}>
            <textarea
              className={styles.input}
              placeholder="请输入您的问题或指令...（Enter 发送，Shift+Enter 换行）"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={!sessionId || isLoading}
              rows={3}
            />
            <button
              className={styles.sendButton}
              onClick={sendMessage}
              disabled={!inputMessage.trim() || !sessionId || isLoading}
            >
              <Send theme="outline" size="20" fill="#fff" />
              发送
            </button>
          </div>
        </div>

        {/* 右侧：建议操作 */}
        <div className={styles.suggestionPanel}>
          <div className={styles.panelHeader}>
            <h3>建议操作</h3>
          </div>
          <div className={styles.panelContent}>
            {suggestedActions.length === 0 ? (
              <div className={styles.emptyState}>
                <p>暂无建议操作</p>
                <p className={styles.hint}>输入问题后，我会为您提供相关建议</p>
              </div>
            ) : (
              <div className={styles.actionList}>
                {suggestedActions.map((action, index) => (
                  <div
                    key={index}
                    className={styles.actionItem}
                    onClick={() => handleSuggestedAction(action)}
                  >
                    <span className={styles.actionIcon}>➤</span>
                    <span className={styles.actionLabel}>{action}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MedicalCopilotPage;
