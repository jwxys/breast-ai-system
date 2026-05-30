import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, message, Typography, Divider, theme } from 'antd';
import {
  LockOutlined,
  UserOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  MedicineBoxOutlined,
  CheckCircleOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '@/stores/appStore';
import './index.css';

const { Title, Text } = Typography;

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [loginMethod, setLoginMethod] = useState<'traditional' | 'ai'>('traditional');
  const navigate = useNavigate();
  const { login } = useAppStore();
  const { token } = theme.useToken();

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      message.success('登录成功！欢迎回来');
      navigate('/');
    } catch (error: any) {
      message.error(error.message || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  const handleAiLogin = () => {
    message.info('AI 人脸识别功能开发中...');
  };

  return (
    <div className="login-container">
      {/* 动态背景 */}
      <div className="login-background">
        <div className="floating-shapes">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className={`shape shape-${i + 1}`}
              animate={{
                y: [0, -20, 0],
                rotate: [0, 360],
              }}
              transition={{
                duration: 20 + i * 5,
                repeat: Infinity,
                ease: 'linear',
              }}
            />
          ))}
        </div>
      </div>

      {/* 登录卡片 */}
      <motion.div
        className="login-card-wrapper"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <Card className="login-card" bordered={false}>
          {/* Logo 和标题 */}
          <motion.div
            className="login-header"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <div className="logo-icon">
              <MedicineBoxOutlined style={{ fontSize: 48, color: token.colorPrimary }} />
            </div>
            <Title level={2} className="login-title">
              乳腺 AI 辅助诊断系统
              <span className="subtitle">Breast AI Diagnostic Platform</span>
            </Title>
            <Text type="secondary" className="login-subtitle">
              中西医结合 · 智能诊疗 · 精准医疗
            </Text>
          </motion.div>

          <Divider />

          {/* AI 快速登录 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="ai-login-section"
          >
            <Button
              type="primary"
              className="ai-login-btn"
              size="large"
              icon={<RobotOutlined />}
              onClick={handleAiLogin}
              disabled
            >
              AI 人脸识别登录 (开发中)
            </Button>
            <Text type="secondary" className="ai-hint">
              <CheckCircleOutlined style={{ color: token.colorSuccess }} />
              快速 · 安全 · 便捷
            </Text>
          </motion.div>

          <Divider>或使用账号登录</Divider>

          {/* 传统登录表单 */}
          <AnimatePresence>
            {loginMethod === 'traditional' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Form
                  name="login"
                  onFinish={handleSubmit}
                  layout="vertical"
                  size="large"
                  autoComplete="off"
                >
                  <Form.Item
                    name="username"
                    rules={[{ required: true, message: '请输入用户名' }]}
                    className="form-item"
                  >
                    <Input
                      prefix={<UserOutlined className="input-icon" />}
                      placeholder="用户名"
                      className="custom-input"
                    />
                  </Form.Item>

                  <Form.Item
                    name="password"
                    rules={[{ required: true, message: '请输入密码' }]}
                    className="form-item"
                  >
                    <Input.Password
                      prefix={<LockOutlined className="input-icon" />}
                      type={passwordVisible ? 'text' : 'password'}
                      iconRender={(visible) =>
                        visible ? (
                          <EyeOutlined className="input-icon" />
                        ) : (
                          <EyeInvisibleOutlined className="input-icon" />
                        )
                      }
                      placeholder="密码"
                      className="custom-input"
                    />
                  </Form.Item>

                  <Form.Item>
                    <div className="form-footer">
                      <a href="/forgot-password">忘记密码？</a>
                    </div>
                  </Form.Item>

                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      loading={loading}
                      className="login-button"
                      size="large"
                      block
                    >
                      {loading ? '登录中...' : '登 录'}
                    </Button>
                  </Form.Item>

                  <div className="demo-hint">
                    <Text type="secondary" className="hint-text">
                      <RobotOutlined className="hint-icon" />
                      演示账号：admin / admin123
                    </Text>
                  </div>
                </Form>
              </motion.div>
            )}
          </AnimatePresence>

          {/* 页脚信息 */}
          <motion.div
            className="login-footer"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            <Divider type="vertical" />
            <Text type="secondary" className="footer-text">
              © 2026 乳腺 AI 系统 · v1.0.0 · NMPA 二类医疗器械
            </Text>
          </motion.div>
        </Card>
      </motion.div>

      {/* 特性展示 */}
      <motion.div
        className="features-section"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.8 }}
      >
        <div className="feature-item">
          <motion.div
            className="feature-icon"
            whileHover={{ scale: 1.1, rotate: 5 }}
          >
            🎯
          </motion.div>
          <Text strong>AI 精准诊断</Text>
          <Text type="secondary" className="feature-desc">
            PBS-Net 分割准确率 94%
          </Text>
        </div>

        <div className="feature-item">
          <motion.div
            className="feature-icon"
            whileHover={{ scale: 1.1, rotate: -5 }}
          >
            🌿
          </motion.div>
          <Text strong>中医辨证</Text>
          <Text type="secondary" className="feature-desc">
            智能证型识别 + 方剂推荐
          </Text>
        </div>

        <div className="feature-item">
          <motion.div
            className="feature-icon"
            whileHover={{ scale: 1.1, rotate: 5 }}
          >
            📊
          </motion.div>
          <Text strong>多模态融合</Text>
          <Text type="secondary" className="feature-desc">
            超声 + 钼靶+MRI 综合分析
          </Text>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
