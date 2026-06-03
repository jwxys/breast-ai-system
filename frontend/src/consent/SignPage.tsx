/**
 * 知情同意书签署页面
 * 支持在线预览、电子签名、确认签署
 */
import React, { useState, useRef } from 'react';
import {
  Card,
  Button,
  Typography,
  Input,
  DatePicker,
  Checkbox,
  Divider,
  Space,
  Modal,
  message,
  Row,
  Col,
  Statistic,
  Steps,
  Alert,
} from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  SignatureOutlined,
  CalendarOutlined,
  UserOutlined,
  SaveOutlined,
  PrintOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import SignatureCanvas from 'react-signature-canvas';
import { motion } from 'framer-motion';

const { Title, Paragraph, Text } = Typography;
const { Step } = Steps;

interface InformedConsentSignPageProps {
  patientId?: string;
  patientName?: string;
}

const InformedConsentSignPage: React.FC<InformedConsentSignPageProps> = ({
  patientId,
  patientName,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [agreed, setAgreed] = useState(false);
  const [signatureData, setSignatureData] = useState<string | null>(null);
  const [signDate, setSignDate] = useState<string>('');
  const [relativeName, setRelativeName] = useState<string>('');
  const [relationship, setRelationship] = useState<string>('');
  const signatureRef = useRef<SignatureCanvas>(null);

  // 清空签名
  const handleClearSignature = () => {
    if (signatureRef.current) {
      signatureRef.current.clear();
      setSignatureData(null);
    }
  };

  // 处理签名完成
  const handleSignComplete = () => {
    if (signatureRef.current) {
      const dataUrl = signatureRef.current.toDataURL('image/png');
      setSignatureData(dataUrl);
    }
  };

  // 提交签署
  const handleSubmit = async () => {
    // 验证必填项
    if (!signatureData) {
      message.error('请先签名');
      return;
    }
    if (!signDate) {
      message.error('请选择签署日期');
      return;
    }
    if (patientId === 'minor' && (!relativeName || !relationship)) {
      message.error('未成年患者需填写监护人信息');
      return;
    }
    if (!agreed) {
      message.error('请确认同意接受检查/治疗');
      return;
    }

    try {
      // TODO: 调用 API 保存签署记录
      // await fetch('/api/v1/informed-consents', {
      //   method: 'POST',
      //   body: JSON.stringify({
      //     patient_id: patientId,
      //     signature: signatureData,
      //     sign_date: signDate,
      //     relative_name: relativeName,
      //     relationship: relationship,
      //   }),
      // });

      // 模拟保存
      await new Promise(resolve => setTimeout(resolve, 1000));

      message.success('知情同意书签署成功！');
      setCurrentStep(3);
    } catch (error) {
      message.error('签署失败，请重试');
    }
  };

  // 打印同意书
  const handlePrint = () => {
    window.print();
  };

  // 下载 PDF
  const handleDownload = () => {
    message.info('正在生成 PDF...');
    // TODO: 调用 PDF 生成 API
  };

  // 同意书内容（简化版，实际应使用完整法律文本）
  const consentContent = `
甲方（医疗机构）：_____________
乙方（患者/受检者）：${patientName || '_____________'}
身份证号：___________________

一、检查/治疗项目
□ 乳腺超声检查
□ 乳腺钼靶检查
□ 乳腺 MRI 检查
□ AI 辅助诊断
□ 3D 重建分析
□ 中医辨证分析（研究性质）

二、风险告知
1. 本检查/治疗可能存在以下风险：
   - 影像学检查的辐射暴露（钼靶）
   - 造影剂可能引起过敏反应（增强 MRI）
   - AI 辅助诊断结果仅供参考，最终诊断以医生判断为准
   - 中医辨证分析为研究性质，不作为临床诊断依据

2. 数据使用风险：
   - 您的医疗数据将被加密存储
   - 数据可能用于医学研究（已脱敏）
   - 您有权要求删除个人数据

三、患者权利
1. 知情权：您有权了解检查/治疗的目的、方法、风险和预期效果
2. 选择权：您有权选择是否接受本检查/治疗
3. 隐私权：您的个人信息和医疗记录将被严格保密
4. 撤销权：您有权在任何时候撤销本同意书

四、费用说明
1. 检查/治疗费用：按医院收费标准执行
2. AI 辅助诊断：□ 自费 □ 医保（以实际政策为准）
3. 中医辨证分析：免费（研究项目）

五、特别说明
1. 中医辨证分析为研究性质，基于有限临床数据开发
2. 中医分析结果为健康参考，不作为疾病诊断和治疗依据
3. 中医体质辨识需结合望闻问切四诊合参
4. 中医证候分析仅供参考，不能替代正规医疗诊断

六、患者确认
1. 医生已向本人详细解释上述内容
2. 本人已充分理解并回答了相关问题
3. 本人自愿接受上述检查/治疗
4. 本人同意医疗数据用于医学研究（脱敏后）

甲方（医师签名）：___________    日期：____年____月____日
乙方（患者签名）：___________    日期：____年____月____日
`;

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      {/* 进度步骤 */}
      <Card style={{ marginBottom: 16 }}>
        <Steps
          current={currentStep}
          onChange={setCurrentStep}
          items={[
            {
              title: '阅读同意书',
              icon: <FileTextOutlined />,
            },
            {
              title: '确认同意',
              icon: <CheckCircleOutlined />,
            },
            {
              title: '电子签名',
              icon: <SignatureOutlined />,
            },
            {
              title: '签署完成',
              icon: <SaveOutlined />,
            },
          ]}
        />
      </Card>

      {/* 步骤 1: 阅读同意书 */}
      {currentStep === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card
            title={
              <Space>
                <FileTextOutlined style={{ color: '#1890ff' }} />
                知情同意书
              </Space>
            }
            extra={
              <Space>
                <Button icon={<PrintOutlined />} onClick={handlePrint}>
                  打印
                </Button>
                <Button icon={<DownloadOutlined />} onClick={handleDownload}>
                  下载 PDF
                </Button>
              </Space>
            }
          >
            <div style={{ 
              padding: 24, 
              background: '#fafafa', 
              border: '1px solid #d9d9d9',
              fontFamily: 'SimSun, serif',
              fontSize: 14,
              lineHeight: 1.8,
              maxHeight: 500,
              overflowY: 'auto',
            }}>
              <pre style={{ 
                whiteSpace: 'pre-wrap',
                fontFamily: 'SimSun, serif',
                fontSize: 14,
              }}>
                {consentContent}
              </pre>
            </div>

            <Divider />

            <Alert
              type="info"
              message="阅读提示"
              description={
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  <li>请仔细阅读上述知情同意书的全部内容</li>
                  <li>特别关注风险告知和特别说明部分</li>
                  <li>如有疑问，请咨询医生</li>
                  <li>确认理解并同意后，点击"下一步"</li>
                </ul>
              }
              showIcon
              style={{ marginTop: 16 }}
            />

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <Checkbox
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
                style={{ fontSize: 16 }}
              >
                <Text style={{ fontSize: 16 }}>
                  我已阅读并充分理解上述内容，同意接受检查/治疗
                </Text>
              </Checkbox>

              <div style={{ marginTop: 24 }}>
                <Space size="large">
                  <Button
                    type="primary"
                    size="large"
                    disabled={!agreed}
                    onClick={() => setCurrentStep(1)}
                  >
                    下一步：填写信息
                  </Button>
                </Space>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* 步骤 2: 填写信息 */}
      {currentStep === 1 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card
            title={
              <Space>
                <UserOutlined style={{ color: '#1890ff' }} />
                填写签署信息
              </Space>
            }
          >
            <Row gutter={24}>
              <Col span={12}>
                <Statistic
                  title="患者姓名"
                  value={patientName || '_____________'}
                  suffix=""
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="患者 ID"
                  value={patientId || '_____________'}
                  suffix=""
                />
              </Col>
            </Row>

            <Divider />

            <div style={{ marginBottom: 24 }}>
              <Title level={5}>
                <CalendarOutlined /> 签署日期
              </Title>
              <DatePicker
                value={signDate ? new Date(signDate) : null}
                onChange={(date, dateString) => setSignDate(dateString)}
                size="large"
                style={{ width: 250 }}
              />
            </div>

            <Alert
              type="warning"
              message="监护人信息（仅未成年患者需要填写）"
              description={
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Input
                    placeholder="监护人姓名"
                    value={relativeName}
                    onChange={(e) => setRelativeName(e.target.value)}
                    size="large"
                  />
                  <Input
                    placeholder="与患者关系（如：父子/母女）"
                    value={relationship}
                    onChange={(e) => setRelationship(e.target.value)}
                    size="large"
                  />
                </Space>
              }
              showIcon
            />

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <Space size="large">
                <Button
                  size="large"
                  onClick={() => setCurrentStep(0)}
                >
                  上一步
                </Button>
                <Button
                  type="primary"
                  size="large"
                  disabled={!signDate}
                  onClick={() => setCurrentStep(2)}
                >
                  下一步：电子签名
                </Button>
              </Space>
            </div>
          </Card>
        </motion.div>
      )}

      {/* 步骤 3: 电子签名 */}
      {currentStep === 2 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card
            title={
              <Space>
                <SignatureOutlined style={{ color: '#1890ff' }} />
                电子签名
              </Space>
            }
          >
            <div style={{ textAlign: 'center', padding: 24 }}>
              <Text type="secondary">请在下方空白区域签名</Text>
              
              <div style={{ 
                margin: '24px auto', 
                border: '2px dashed #1890ff',
                borderRadius: 8,
                display: 'inline-block',
              }}>
                <SignatureCanvas
                  ref={signatureRef}
                  canvasProps={{
                    width: 500,
                    height: 300,
                    style: {
                      background: '#fff',
                      borderRadius: 8,
                    },
                  }}
                  onEnd={handleSignComplete}
                />
              </div>

              <div style={{ marginTop: 16 }}>
                <Space>
                  <Button
                    icon={<SaveOutlined />}
                    onClick={handleClearSignature}
                  >
                    清空重签
                  </Button>
                  <Button
                    type="primary"
                    disabled={!signatureData}
                    onClick={handleSubmit}
                    size="large"
                  >
                    确认签署
                  </Button>
                </Space>
              </div>

              <Alert
                type="info"
                message="签名提示"
                description="签名将与同意书绑定，具有法律效力，请谨慎操作"
                showIcon
                style={{ marginTop: 24 }}
              />
            </div>
          </Card>
        </motion.div>
      )}

      {/* 步骤 4: 签署完成 */}
      {currentStep === 3 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card>
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <Result
                status="success"
                title="知情同意书签署成功！"
                subTitle={`签署日期：${signDate}`}
                extra={[
                  <Button
                    key="view"
                    type="primary"
                    onClick={() => {/* 查看详情 */}}
                  >
                    查看同意书
                  </Button>,
                  <Button
                    key="print"
                    icon={<PrintOutlined />}
                    onClick={handlePrint}
                  >
                    打印
                  </Button>,
                  <Button
                    key="download"
                    icon={<DownloadOutlined />}
                    onClick={handleDownload}
                  >
                    下载 PDF
                  </Button>,
                ]}
              />
              
              <div style={{ marginTop: 32, padding: 24, background: '#f9f9f9' }}>
                <Title level={5}>签署信息</Title>
                <Space direction="vertical">
                  <Text>患者姓名：{patientName || '_____________'}</Text>
                  <Text>签署日期：{signDate}</Text>
                  {relativeName && (
                    <Text>监护人：{relativeName}（{relationship}）</Text>
                  )}
                  <Text>签名状态：
                    <span style={{ color: '#52c41a', fontWeight: 600 }}>
                      {' '}已签名{' '}
                    </span>
                  </Text>
                </Space>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* 底部操作栏 */}
      {currentStep < 3 && (
        <div style={{ marginTop: 24, textAlign: 'center', color: '#999', fontSize: 12 }}>
          <Text>本知情同意书符合 NMPA 二类医疗器械认证要求</Text>
        </div>
      )}
    </div>
  );
};

export default InformedConsentSignPage;
