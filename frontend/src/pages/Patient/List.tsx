import { useEffect, useState } from 'react';
import { Card, Table, Space, Button, Input, Select, Tag, message, Modal, Dropdown, Menu, Avatar, Badge, Tooltip, Drawer, Form, DatePicker, Radio, InputNumber, Statistic, Row, Col, Descriptions, Popconfirm, Empty, Divider, Breadcrumb, Switch } from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  MoreOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CalendarOutlined,
  PhoneOutlined,
  MailOutlined,
  EnvironmentOutlined,
  HeartOutlined,
  ExperimentOutlined,
  FileTextOutlined,
  ThunderboltOutlined,
  UsergroupAddOutlined,
  ExportOutlined,
  ImportOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '@/stores/appStore';
import { patientApi } from '@/api';
import type { Patient } from '@/types';
import dayjs from 'dayjs';
import './index.css';

const { Search } = Input;

const MotionCard = motion(Card);

const PatientList = () => {
  const navigate = useNavigate();
  const { patients, fetchPatients } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });
  const [filters, setFilters] = useState({
    name: '',
    constitution: '',
    riskLevel: '',
  });

  useEffect(() => {
    loadData();
  }, [pagination.current, pagination.pageSize]);

  const loadData = async () => {
    setLoading(true);
    try {
      await fetchPatients({
        page: pagination.current,
        page_size: pagination.pageSize,
        ...filters,
      });
    } catch (error) {
      message.error('加载患者列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = (patient: Patient) => {
    setSelectedPatient(patient);
    setDetailVisible(true);
  };

  const handleDelete = (patient: Patient) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除患者 ${patient.name} 吗？此操作不可恢复。`,
      icon: <DeleteOutlined style={{ color: '#ef4444' }} />,
      okText: '确认删除',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          await patientApi.delete(patient.id);
          message.success('删除成功');
          loadData();
        } catch {
          message.error('删除失败');
        }
      },
    });
  };

  const constitutionConfig: any = {
    '气郁质': { color: 'orange', icon: '🌸' },
    '痰湿质': { color: 'purple', icon: '💧' },
    '血瘀质': { color: 'red', icon: '🩸' },
    '平和质': { color: 'green', icon: '🌿' },
    '气虚质': { color: 'blue', icon: '💨' },
    '阳虚质': { color: 'cyan', icon: '☀️' },
    '阴虚质': { color: 'magenta', icon: '🌙' },
  };

  const riskLevelConfig: any = {
    low: { color: 'success', text: '低风险', icon: '✅' },
    medium: { color: 'warning', text: '中风险', icon: '⚠️' },
    high: { color: 'error', text: '高风险', icon: '🔴' },
    very_high: { color: 'purple', text: '极高风险', icon: '🚨' },
  };

  const actionMenu = (patient: Patient) => (
    <Menu>
      <Menu.Item
        key="view"
        icon={<EyeOutlined />}
        onClick={() => handleViewDetail(patient)}
      >
        查看详情
      </Menu.Item>
      <Menu.Item
        key="edit"
        icon={<EditOutlined />}
        onClick={() => navigate(`/patient/${patient.id}/edit`)}
      >
        编辑信息
      </Menu.Item>
      <Menu.Item
        key="visit"
        icon={<CalendarOutlined />}
        onClick={() => navigate(`/visit/create?patientId=${patient.id}`)}
      >
        新建随访
      </Menu.Item>
      <Menu.Item
        key="diagnosis"
        icon={<ThunderboltOutlined />}
        onClick={() => navigate(`/diagnosis/create?patientId=${patient.id}`)}
      >
        AI 诊断
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item
        key="export"
        icon={<ExportOutlined />}
        onClick={() => message.info('导出功能开发中...')}
      >
        导出报告
      </Menu.Item>
    </Menu>
  );

  const columns = [
    {
      title: '患者',
      dataIndex: 'name',
      key: 'patient',
      width: 200,
      render: (_: unknown, record: Patient) => (
        <Space>
          <Avatar
            size={48}
            src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${record.patient_no}`}
            style={{ background: '#667eea' }}
          />
          <div className="patient-info">
            <div className="patient-name">{record.name}</div>
            <div className="patient-no">{record.patient_no}</div>
          </div>
        </Space>
      ),
    },
    {
      title: '基本信息',
      key: 'basic',
      width: 150,
      render: (_: unknown, record: Patient) => (
        <div className="basic-info">
          <div className="info-item">
            <span className="info-label">年龄</span>
            <span className="info-value">{record.age}岁</span>
          </div>
          <div className="info-item">
            <span className="info-label">性别</span>
            <span className="info-value">{record.gender === 'F' ? '女' : '男'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">电话</span>
            <span className="info-value">{record.phone || '-'}</span>
          </div>
        </div>
      ),
    },
    {
      title: '体质',
      dataIndex: 'constitution',
      key: 'constitution',
      width: 120,
      render: (constitution: string) => {
        const config = constitutionConfig[constitution] || { color: 'blue', icon: '❓' };
        return (
          <Tooltip title={constitution || '未评估'}>
            <Tag color={config.color} className="constitution-tag">
              {config.icon} {constitution || '未评估'}
            </Tag>
          </Tooltip>
        );
      },
    },
    {
      title: '中医证型',
      dataIndex: 'zheng_type',
      key: 'zheng_type',
      width: 140,
      ellipsis: true,
      render: (zheng_type: string) => (
        <div className="zheng-type">
          <HeartOutlined style={{ color: '#ec4899', marginRight: 4 }} />
          {zheng_type || '未辨证'}
        </div>
      ),
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      width: 120,
      render: (risk_level: string) => {
        const config = riskLevelConfig[risk_level] || { color: 'default', text: '未评估', icon: '❓' };
        return (
          <Badge
            count={
              <span className="risk-badge">{config.icon}</span>
            }
          >
            <Tag color={config.color} className="risk-tag">
              {config.text}
            </Tag>
          </Badge>
        );
      },
    },
    {
      title: '下次随访',
      key: 'next_followup',
      width: 130,
      render: (_: unknown, record: Patient) => (
        <div className="followup-date">
          <CalendarOutlined style={{ marginRight: 6, color: '#667eea' }} />
          <span>未安排</span>
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 140,
      fixed: 'right' as const,
      render: (_: unknown, record: Patient) => (
        <Space className="action-buttons">
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => navigate(`/patient/${record.id}/edit`)}
            />
          </Tooltip>
          <Dropdown
            overlay={actionMenu(record)}
            trigger={['click']}
            placement="bottomRight"
          >
            <Button type="text" icon={<MoreOutlined />} />
          </Dropdown>
          <Tooltip title="删除">
            <Popconfirm
              title="确认删除"
              description={`确定删除患者 ${record.name} 吗？`}
              onConfirm={() => handleDelete(record)}
              okText="确认"
              cancelText="取消"
            >
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div className="patient-list-container">
      <MotionCard
        className="list-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {/* 头部区域 */}
        <div className="card-header">
          <div className="header-left">
            <h2 className="page-title">
              <UsergroupAddOutlined className="title-icon" />
              患者管理
            </h2>
            <Breadcrumb
              separator="/"
              items={[
                { title: '首页', href: '/' },
                { title: '患者管理' },
              ]}
            />
          </div>
          <div className="header-right">
            <Space>
              <Button icon={<ImportOutlined />}>
                批量导入
              </Button>
              <Button icon={<ExportOutlined />}>
                导出
              </Button>
              <Button
                type="primary"
                size="large"
                icon={<PlusOutlined />}
                onClick={() => navigate('/patient/create')}
              >
                新建患者
              </Button>
            </Space>
          </div>
        </div>

        {/* 筛选区域 */}
        <div className="filter-section">
          <div className="filter-row">
            <Search
              placeholder="搜索患者姓名/编号/电话"
              style={{ width: 320 }}
              allowClear
              onSearch={(value) => {
                setFilters({ ...filters, name: value });
                setPagination({ ...pagination, current: 1 });
              }}
            />
            <Select
              placeholder="体质类型"
              style={{ width: 160 }}
              allowClear
              onChange={(value) => {
                setFilters({ ...filters, constitution: value });
                setPagination({ ...pagination, current: 1 });
              }}
              options={[
                { value: '气郁质', label: '🌸 气郁质' },
                { value: '痰湿质', label: '💧 痰湿质' },
                { value: '血瘀质', label: '🩸 血瘀质' },
                { value: '平和质', label: '🌿 平和质' },
                { value: '气虚质', label: '💨 气虚质' },
                { value: '阳虚质', label: '☀️ 阳虚质' },
                { value: '阴虚质', label: '🌙 阴虚质' },
              ]}
            />
            <Select
              placeholder="风险等级"
              style={{ width: 160 }}
              allowClear
              onChange={(value) => {
                setFilters({ ...filters, riskLevel: value });
                setPagination({ ...pagination, current: 1 });
              }}
              options={[
                { value: 'low', label: '✅ 低风险' },
                { value: 'medium', label: '⚠️ 中风险' },
                { value: 'high', label: '🔴 高风险' },
                { value: 'very_high', label: '🚨 极高风险' },
              ]}
            />
            <Button icon={<FilterOutlined />}>
              更多筛选
            </Button>
          </div>
          <div className="filter-info">
            <Space size="large">
              <span>共 <strong>{pagination.total}</strong> 位患者</span>
              <Divider type="vertical" />
              <span>高风险：<strong className="text-error">{patientApi?.highRiskCount || 0}</strong></span>
              <Divider type="vertical" />
              <span>本月新增：<strong className="text-primary">+12</strong></span>
            </Space>
          </div>
        </div>

        {/* 表格区域 */}
        <div className="table-section">
          <Table
            columns={columns}
            dataSource={patients}
            loading={loading}
            rowKey="id"
            pagination={{
              ...pagination,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条`,
              pageSizeOptions: ['10', '20', '50', '100'],
              onChange: (page, pageSize) => {
                setPagination({ ...pagination, current: page, pageSize });
              },
            }}
            scroll={{ x: 1200 }}
            size="middle"
            locale={{
              emptyText: (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description={
                    <span>
                      暂无患者数据，<Button type="link" onClick={() => navigate('/patient/create')}>立即新建</Button>
                    </span>
                  }
                />
              ),
            }}
          />
        </div>
      </MotionCard>

      {/* 患者详情 Drawer */}
      <AnimatePresence>
        {detailVisible && selectedPatient && (
          <Drawer
            title={
              <Space>
                <Avatar
                  size="large"
                  src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${selectedPatient.patient_no}`}
                  style={{ background: '#667eea' }}
                />
                <div>
                  <div>{selectedPatient.name}</div>
                  <div className="drawer-subtitle">{selectedPatient.patient_no}</div>
                </div>
              </Space>
            }
            placement="right"
            size="large"
            open={detailVisible}
            onClose={() => setDetailVisible(false)}
            maskClosable={false}
            extra={
              <Space>
                <Button icon={<EditOutlined />} onClick={() => {
                  setDetailVisible(false);
                  navigate(`/patient/${selectedPatient.id}/edit`);
                }}>
                  编辑
                </Button>
              </Space>
            }
            footer={
              <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                <Button onClick={() => navigate(`/visit/create?patientId=${selectedPatient.id}`)}>
                  新建随访
                </Button>
                <Button type="primary" onClick={() => navigate(`/diagnosis/create?patientId=${selectedPatient.id}`)}>
                  AI 诊断
                </Button>
              </Space>
            }
          >
            <div className="patient-detail">
              <Descriptions title={<><FileTextOutlined /> 基本信息</>} column={2} bordered>
                <Descriptions.Item label="姓名">{selectedPatient.name}</Descriptions.Item>
                <Descriptions.Item label="性别">{selectedPatient.gender === 'F' ? '女' : '男'}</Descriptions.Item>
                <Descriptions.Item label="年龄">{selectedPatient.age}岁</Descriptions.Item>
                <Descriptions.Item label="出生日期">{dayjs(selectedPatient.birth_date).format('YYYY-MM-DD')}</Descriptions.Item>
                <Descriptions.Item label="联系电话"><PhoneOutlined /> {selectedPatient.phone || '-'}</Descriptions.Item>
                <Descriptions.Item label="电子邮箱"><MailOutlined /> {selectedPatient.email || '-'}</Descriptions.Item>
                <Descriptions.Item label="居住地址" span={2}>
                  <EnvironmentOutlined /> {selectedPatient.address || '-'}
                </Descriptions.Item>
              </Descriptions>

              <Divider />

              <Descriptions title={<><HeartOutlined /> 中医信息</>} column={2} bordered>
                <Descriptions.Item label="体质类型">
                  {selectedPatient.constitution || '未评估'}
                </Descriptions.Item>
                <Descriptions.Item label="体质评分">
                  {selectedPatient.constitution_score || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="中医证型" span={2}>
                  {selectedPatient.zheng_type || '未辨证'}
                </Descriptions.Item>
                <Descriptions.Item label="证型程度" span={2}>
                  {selectedPatient.zheng_severity || '-'}
                </Descriptions.Item>
              </Descriptions>

              <Divider />

              <Descriptions title={<><ExperimentOutlined /> 风险评估</>} column={2} bordered>
                <Descriptions.Item label="风险等级">
                  <Tag color={riskLevelConfig[selectedPatient.risk_level || 'low']?.color || 'default'}>
                    {riskLevelConfig[selectedPatient.risk_level || 'low']?.text || '未评估'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="风险评分">
                  {selectedPatient.risk_score || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="最后评估时间" span={2}>
                  {dayjs(selectedPatient.updated_at).format('YYYY-MM-DD HH:mm')}
                </Descriptions.Item>
              </Descriptions>
            </div>
          </Drawer>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PatientList;
