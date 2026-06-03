/**
 * 患者管理模块 - 主页面
 * 
 * 显示患者列表和提供操作入口
 */

import React, { useState, useEffect } from 'react';
import { Table, Button, Space } from 'antd';
import { UserAddOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { patientAPI } from './api';

/**
 * 患者数据类型
 */
interface Patient {
  id: string;        // 患者 ID
  name: string;      // 姓名
  age: number;       // 年龄
  gender: string;    // 性别
  phone?: string;    // 电话 (可选)
}

/**
 * 患者列表页面组件
 */
const PatientList: React.FC = () => {
  // 状态：患者列表数据
  const [patients, setPatients] = useState<Patient[]>([]);
  
  // 状态：加载状态
  const [loading, setLoading] = useState(false);
  
  // 状态：分页信息
  const [pagination, setPagination] = useState({
    current: 1,      // 当前页
    pageSize: 10,    // 每页数量
    total: 0,        // 总数
  });


  /**
   * 加载患者列表数据
   * 
   * @param page - 页码
   */
  const loadPatients = async (page: number = 1) => {
    setLoading(true);
    try {
      const response = await patientAPI.getList({
        skip: (page - 1) * pagination.pageSize,
        limit: pagination.pageSize,
      });
      setPatients(response.data);
      setPagination(prev => ({ ...prev, current: page }));
    } catch (error) {
      console.error('加载患者列表失败:', error);
    } finally {
      setLoading(false);
    }
  };


  /**
   * 组件挂载时加载数据
   */
  useEffect(() => {
    loadPatients();
  }, []);


  /**
   * 表格列定义
   */
  const columns = [
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '年龄',
      dataIndex: 'age',
      key: 'age',
      sorter: (a: Patient, b: Patient) => a.age - b.age,  // 年龄排序
    },
    {
      title: '性别',
      dataIndex: 'gender',
      key: 'gender',
      filters: [                                       // 性别筛选
        { text: '男', value: '男' },
        { text: '女', value: '女' },
      ],
      onFilter: (value: any, record: Patient) => record.gender === value,
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Patient) => (           // 操作按钮
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Button icon={<DeleteOutlined />} danger onClick={() => handleDelete(record)} />
        </Space>
      ),
    },
  ];


  /**
   * 编辑患者
   * 
   * @param patient - 患者数据
   */
  const handleEdit = (patient: Patient) => {
    console.log('编辑患者:', patient);
    // TODO: 打开编辑对话框
  };


  /**
   * 删除患者
   * 
   * @param patient - 患者数据
   */
  const handleDelete = async (patient: Patient) => {
    if (!confirm(`确定删除患者 "${patient.name}" 吗？`)) return;
    
    try {
      await patientAPI.delete(patient.id);
      loadPatients(pagination.current);  // 重新加载
      message.success('删除成功');
    } catch (error) {
      message.error('删除失败');
    }
  };


  return (
    <div className="patient-list">
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<UserAddOutlined />} onClick={() => handleAdd()}>
          新建患者
        </Button>
      </div>
      
      <Table
        columns={columns}              // 列定义
        dataSource={patients}          // 数据源
        loading={loading}              // 加载状态
        pagination={pagination}        // 分页配置
        onChange={(pag) => loadPatients(pag.current)}  // 分页变化
        rowKey="id"                    // 行键
      />
    </div>
  );
};


export default PatientList;
