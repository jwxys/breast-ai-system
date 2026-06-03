/**
 * 患者详情页面
 */
import React, { useEffect, useState } from 'react';
import {
  Descriptions,
  Card,
  Space,
  Avatar,
  Tag,
  Divider,
  Button,
  Breadcrumb,
  Timeline,
  Statistic,
  Row,
  Col,
  Empty,
  message,
  Skeleton,
} from 'antd';
import {
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
  EnvironmentOutlined,
  CalendarOutlined,
  FileTextOutlined,
  HeartOutlined,
  ExperimentOutlined,
  EditOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  PlusOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { patientApi } from '@/api';
import type { Patient } from '@/types';

const PatientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [patient, setPatient] = useState<Patient | null>(null);

  useEffect(() => {
    loadPatient();
  }, [id]);

  const loadPatient = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await patientApi.get(parseInt(id));
      setPatient(data);
    } catch (error) {
      message.error('加载患者信息失败');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: 24 }}>
        <Skeleton active paragraph={{ rows: 10 }} />
      </div>
    );
  }

  if (!patient) {
    return (
      <div style={{ padding: 24 }}>
        <Empty description="患者不存在" />
      </div>
    );
  }

  const riskLevelConfig: any = {
    low: { color: 'success', text: '低风险', icon: '✅' },
    medium: { color: 'warning', text: '中风险', icon: '⚠️' },
    high: { color: 'error', text: '高风险', icon: '🔴' },
    very_high: { color: 'purple', text: '极高风险', icon: '🚨' },
  };

  const riskConfig = riskLevelConfig[patient.risk_level || 'low'] || riskLevelConfig.low;

  return (
    <div style={{ padding: 24 }}>
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          { key: 'home', href: '/', title: (<><HomeOutlined /> 首页</>) },
          { key: 'patient', href: '/patient', title: '患者管理' },
          { key: 'detail', title: patient.name },
        ]}
      />

      {/* 头部信息卡 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Avatar
            size={80}
            src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${patient.patient_no}`}
            style={{ background: '#667eea' }}
          />
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
              <h1 style={{ margin: 0, fontSize: 24 }}>{patient.name}</h1>
              <Tag color="blue">{patient.gender === 'F' ? '女' : '男'}</Tag>
              <Tag color="green">{patient.age}岁</Tag>
              <Tag color={riskConfig.color}>
                {riskConfig.icon} {riskConfig.text}
              </Tag>
            </div>
            <Space size="large">
              <span>
                <strong>患者编号：</strong>{patient.patient_no}
              </span>
              <span>
                <CalendarOutlined /> 出生日期：{dayjs(patient.birth_date).format('YYYY-MM-DD')}
              </span>
              <span>
                <ClockCircleOutlined /> 建档时间：{dayjs(patient.created_at).format('YYYY-MM-DD')}
              </span>
            </Space>
          </div>
          <Space>
            <Button
              icon={<EditOutlined />}
              onClick={() => navigate(`/patient/${id}/edit`)}
            >
              编辑
            </Button>
            <Button
              type="primary"
              icon={<ThunderboltOutlined />}
              onClick={() => navigate(`/diagnosis/create?patientId=${id}`)}
            >
              AI 诊断
            </Button>
          </Space>
        </div>
      </Card>

      <Row gutter={16}>
        {/* 左侧：基本信息 */}
        <Col span={16}>
          {/* 基本信息 */}
          <Card
            title={<><UserOutlined /> 基本信息</>}
            style={{ marginBottom: 16 }}
          >
            <Descriptions column={2} bordered>
              <Descriptions.Item label="姓名">{patient.name}</Descriptions.Item>
              <Descriptions.Item label="性别">
                {patient.gender === 'F' ? '女' : '男'}
              </Descriptions.Item>
              <Descriptions.Item label="年龄">{patient.age}岁</Descriptions.Item>
              <Descriptions.Item label="出生日期">
                {dayjs(patient.birth_date).format('YYYY-MM-DD')}
              </Descriptions.Item>
              <Descriptions.Item label="身份证号">
                {patient.id_card || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="联系电话">
                <Space>
                  <PhoneOutlined />
                  {patient.phone || '-'}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="电子邮箱">
                <Space>
                  <MailOutlined />
                  {patient.email || '-'}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="居住地址" span={2}>
                <Space>
                  <EnvironmentOutlined />
                  {patient.address || '-'}
                </Space>
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 风险评估 */}
          <Card
            title={<><ExperimentOutlined /> 风险评估</>}
            style={{ marginBottom: 16 }}
          >
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="风险等级"
                  value={riskConfig.text}
                  prefix={riskConfig.icon}
                  valueStyle={{ color: riskConfig.color === 'default' ? undefined : riskConfig.color }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="风险评分"
                  value={patient.risk_score || 0}
                  precision={2}
                  suffix="分"
                />
              </Col>
            </Row>
            <Divider />
            <Descriptions column={1}>
              <Descriptions.Item label="最后评估时间">
                {dayjs(patient.updated_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 中医信息 */}
          <Card title={<><HeartOutlined /> 中医信息</>}>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="体质类型">
                {patient.constitution || <span style={{ color: '#999' }}>未评估</span>}
              </Descriptions.Item>
              <Descriptions.Item label="体质评分">
                {patient.constitution_score || <span style={{ color: '#999' }}>-</span>}
              </Descriptions.Item>
              <Descriptions.Item label="中医证型" span={2}>
                {patient.zheng_type || <span style={{ color: '#999' }}>未辨证</span>}
              </Descriptions.Item>
              <Descriptions.Item label="证型程度" span={2}>
                {patient.zheng_severity || <span style={{ color: '#999' }}>-</span>}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 右侧：时间线和快捷操作 */}
        <Col span={8}>
          {/* 快捷操作 */}
          <Card title="快捷操作" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Button
                block
                icon={<CalendarOutlined />}
                onClick={() => navigate(`/visit/create?patientId=${id}`)}
              >
                新建随访
              </Button>
              <Button
                block
                icon={<FileTextOutlined />}
                onClick={() => navigate(`/ultrasound/create?patientId=${id}`)}
              >
                新建检查
              </Button>
              <Button
                block
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={() => navigate(`/diagnosis/create?patientId=${id}`)}
              >
                AI 辅助诊断
              </Button>
              <Button
                block
                icon={<PlusOutlined />}
                onClick={() => navigate(`/patient/${id}/tcm-analysis`)}
              >
                中医病机分析
              </Button>
            </Space>
          </Card>

          {/* 随访记录 */}
          <Card title={<><CalendarOutlined /> 随访记录</>}>
            <Timeline
              items={[
                {
                  color: 'blue',
                  children: (
                    <div>
                      <div>2026-05-15</div>
                      <div style={{ fontSize: 12, color: '#999' }}>常规随访</div>
                    </div>
                  ),
                },
                {
                  color: 'green',
                  children: (
                    <div>
                      <div>2026-04-01</div>
                      <div style={{ fontSize: 12, color: '#999' }}>首次就诊</div>
                    </div>
                  ),
                },
              ]}
            />
            <Button
              block
              type="link"
              onClick={() => navigate(`/visit?patientId=${id}`)}
            >
              查看全部
            </Button>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default PatientDetail;
