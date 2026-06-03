/**
 * 应急联系人管理页面
 */
import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Typography, 
  Card, 
  Tag, 
  Modal, 
  Form, 
  Input, 
  Select, 
  message,
  Space,
  Popconfirm
} from 'antd';
import { 
  PlusOutlined, 
  PhoneOutlined, 
  MailOutlined, 
  EditOutlined, 
  DeleteOutlined,
  UserOutlined
} from '@ant-design/icons';
import { getContactList, createContact, updateContact, deleteContact, getContactTypes } from '@/api/emergencyContacts';
import type { ColumnsType } from 'antd/es/table';
import type { ContactResponse, ContactType } from '@/types/emergency';

const { Title } = Typography;
const { TextArea } = Input;

interface ContactFormData {
  name: string;
  title?: string;
  organization?: string;
  contact_type: ContactType;
  phone_primary: string;
  phone_secondary?: string;
  email?: string;
  wechat?: string;
  address?: string;
  responsibilities?: string;
  available_hours?: string;
  priority: number;
  notes?: string;
}

const EmergencyContacts: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [contacts, setContacts] = useState<ContactResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingContact, setEditingContact] = useState<ContactResponse | null>(null);
  const [contactTypes, setContactTypes] = useState<{ value: string; label: string; color: string }[]>([]);
  const [form] = Form.useForm();

  // 加载联系人列表
  const loadContacts = async () => {
    setLoading(true);
    try {
      const result = await getContactList({
        skip: (currentPage - 1) * pageSize,
        limit: pageSize
      });
      setContacts(result.items);
      setTotal(result.total);
    } catch (error) {
      message.error('加载联系人列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载联系人类型
  const loadContactTypes = async () => {
    try {
      const types = await getContactTypes();
      setContactTypes(types);
    } catch (error) {
      console.error('加载联系人类型失败', error);
    }
  };

  useEffect(() => {
    loadContacts();
    loadContactTypes();
  }, [currentPage, pageSize]);

  // 打开新建/编辑弹窗
  const handleOpenModal = (contact?: ContactResponse) => {
    if (contact) {
      setEditingContact(contact);
      form.setFieldsValue(contact);
    } else {
      setEditingContact(null);
      form.resetFields();
    }
    setModalVisible(true);
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingContact) {
        await updateContact(editingContact.id, values);
        message.success('联系人更新成功');
      } else {
        await createContact(values);
        message.success('联系人创建成功');
      }
      
      setModalVisible(false);
      loadContacts();
    } catch (error: any) {
      if (error.message) {
        message.error(error.message);
      }
    }
  };

  // 删除联系人
  const handleDelete = async (id: number) => {
    try {
      await deleteContact(id);
      message.success('联系人删除成功');
      loadContacts();
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 表格列定义
  const columns: ColumnsType<ContactResponse> = [
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      fixed: 'left',
      width: 120,
      render: (name: string) => (
        <Space>
          <UserOutlined />
          <strong>{name}</strong>
        </Space>
      )
    },
    {
      title: '职务',
      dataIndex: 'title',
      key: 'title',
      width: 150
    },
    {
      title: '机构',
      dataIndex: 'organization',
      key: 'organization',
      width: 200,
      ellipsis: true
    },
    {
      title: '类型',
      dataIndex: 'contact_type',
      key: 'contact_type',
      width: 120,
      render: (type: ContactType) => {
        const typeInfo = contactTypes.find(t => t.value === type);
        return typeInfo ? (
          <Tag color={typeInfo.color}>{typeInfo.label}</Tag>
        ) : type;
      }
    },
    {
      title: '主要电话',
      dataIndex: 'phone_primary',
      key: 'phone_primary',
      width: 150,
      render: (phone: string) => (
        <Space>
          <PhoneOutlined />
          <a href={`tel:${phone}`}>{phone}</a>
        </Space>
      )
    },
    {
      title: '备用电话',
      dataIndex: 'phone_secondary',
      key: 'phone_secondary',
      width: 150
    },
    {
      title: '可联系时间',
      dataIndex: 'available_hours',
      key: 'available_hours',
      width: 150
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      sorter: (a, b) => a.priority - b.priority
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, contact) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleOpenModal(contact)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除此联系人吗？"
            onConfirm={() => handleDelete(contact.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  const getTypeLabel = (value: string) => {
    const type = contactTypes.find(t => t.value === value);
    return type ? type.label : value;
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={2}>应急联系人列表</Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            新建联系人
          </Button>
        </div>

        <Table<ContactResponse>
          columns={columns}
          dataSource={contacts}
          rowKey="id"
          loading={loading}
          pagination={{
            current: currentPage,
            pageSize,
            total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setCurrentPage(page);
              setPageSize(pageSize);
            }
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 新建/编辑弹窗 */}
      <Modal
        title={editingContact ? '编辑联系人' : '新建联系人'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ priority: 0, is_active: true }}
        >
          <Form.Item
            name="name"
            label="姓名"
            rules={[{ required: true, message: '请输入姓名' }]}
          >
            <Input placeholder="请输入联系人姓名" />
          </Form.Item>

          <Form.Item
            name="title"
            label="职务/职称"
          >
            <Input placeholder="请输入职务/职称" />
          </Form.Item>

          <Form.Item
            name="organization"
            label="所属机构"
          >
            <Input placeholder="请输入所属机构" />
          </Form.Item>

          <Form.Item
            name="contact_type"
            label="联系人类型"
            rules={[{ required: true, message: '请选择联系人类型' }]}
          >
            <Select placeholder="请选择联系人类型">
              {contactTypes.map(type => (
                <Select.Option key={type.value} value={type.value}>
                  {type.label}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="phone_primary"
            label="主要电话"
            rules={[{ required: true, message: '请输入主要电话' }]}
          >
            <Input placeholder="请输入主要电话号码" />
          </Form.Item>

          <Form.Item
            name="phone_secondary"
            label="备用电话"
          >
            <Input placeholder="请输入备用电话号码" />
          </Form.Item>

          <Form.Item
            name="email"
            label="电子邮箱"
          >
            <Input placeholder="请输入电子邮箱" />
          </Form.Item>

          <Form.Item
            name="wechat"
            label="微信号"
          >
            <Input placeholder="请输入微信号" />
          </Form.Item>

          <Form.Item
            name="available_hours"
            label="可联系时间"
          >
            <Input placeholder="如：24 小时、工作日 9:00-17:00" />
          </Form.Item>

          <Form.Item
            name="priority"
            label="优先级"
            tooltip="数字越小优先级越高，紧急联系人建议设为 0"
          >
            <Input type="number" min={0} placeholder="请输入优先级" />
          </Form.Item>

          <Form.Item
            name="responsibilities"
            label="职责描述"
          >
            <TextArea rows={3} placeholder="请输入职责描述" />
          </Form.Item>

          <Form.Item
            name="notes"
            label="备注"
          >
            <TextArea rows={2} placeholder="请输入备注信息" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default EmergencyContacts;
