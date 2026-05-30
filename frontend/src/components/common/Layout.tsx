import { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Badge, theme } from 'antd';
import {
  HomeOutlined,
  UserOutlined,
  CalendarOutlined,
  FileImageOutlined,
  FileTextOutlined,
  MedicineBoxOutlined,
  BookOutlined,
  SettingOutlined,
  LogoutOutlined,
  BellOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = Layout;

export const AppLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const menuItems: MenuProps['items'] = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/patient',
      icon: <UserOutlined />,
      label: '患者管理',
    },
    {
      key: '/visit',
      icon: <CalendarOutlined />,
      label: '随访管理',
    },
    {
      key: '/ultrasound',
      icon: <FileImageOutlined />,
      label: '超声检查',
    },
    {
      key: '/ultrasound-tcm',
      icon: <ExperimentOutlined />,
      label: '影像 - 中医分析',
    },
    {
      key: '/diagnosis',
      icon: <FileTextOutlined />,
      label: '诊断管理',
    },
    {
      key: '/treatment',
      icon: <MedicineBoxOutlined />,
      label: '治疗管理',
    },
    {
      key: '/knowledge',
      icon: <BookOutlined />,
      label: '知识库',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => {
        // TODO: 实现退出登录
        navigate('/login');
      },
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 侧边栏 */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
        width={256}
      >
        <div
          style={{
            height: 64,
            margin: collapsed ? 'auto' : '16px',
            background: 'rgba(255, 255, 255, 0.2)',
            borderRadius: borderRadiusLG,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: collapsed ? 0 : 18,
            fontWeight: 600,
            overflow: 'hidden',
          }}
        >
          {collapsed ? '🏥' : '乳腺 AI 系统'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => {
            if (key === '/ultrasound-tcm') {
              // 跳转到第一个超声检查的中医分析页面
              navigate('/ultrasound/1/tcm-analysis');
            } else {
              navigate(key);
            }
          }}
        />
      </Sider>

      <Layout>
        {/* 头部 */}
        <Header
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h2 style={{ margin: 0, fontSize: 18 }}>
            {menuItems.find((item) => item?.key === location.pathname)?.label || '乳腺 AI 辅助诊断系统'}
          </h2>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {/* 通知 */}
            <Badge count={5} size="small">
              <BellOutlined style={{ fontSize: 20, cursor: 'pointer' }} />
            </Badge>

            {/* 用户信息 */}
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                {!collapsed && <span>王伟 医生</span>}
              </div>
            </Dropdown>
          </div>
        </Header>

        {/* 内容区 */}
        <Content
          style={{
            margin: 24,
            padding: 24,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            minHeight: 280,
            overflow: 'auto',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
