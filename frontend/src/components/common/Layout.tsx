/**
 * 增强的布局组件
 * 
 * 优化内容:
 * - 响应式侧边栏
 * - Breadcrumb 导航
 * - 用户菜单
 * - 通知系统
 * - 暗黑模式切换
 */

import { useState, useEffect } from 'react';
import { Layout, Menu, Avatar, Dropdown, Badge, Button, Drawer, Space, Breadcrumb, theme } from 'antd';
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
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  MoonOutlined,
  SunOutlined,
  DashboardOutlined,
  AiOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import type { MenuProps } from 'antd';
import './Layout.css';

const { Header, Sider, Content } = Layout;

export const AppLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = theme.useToken();

  // 检测屏幕尺寸
  useEffect(() => {
    const checkScreen = () => {
      if (window.innerWidth < 768) {
        setCollapsed(true);
      }
    };
    checkScreen();
    window.addEventListener('resize', checkScreen);
    return () => window.removeEventListener('resize', checkScreen);
  }, []);

  // 暗黑模式切换
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  }, [darkMode]);

  // 菜单配置
  const menuItems: MenuProps['items'] = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘', },
    { type: 'divider' },
    { key: '/patient', icon: <UserOutlined />, label: '患者管理', },
    { key: '/visit', icon: <CalendarOutlined />, label: '随访管理', },
    { type: 'divider' },
    { key: '/ultrasound', icon: <FileImageOutlined />, label: '超声检查', },
    { key: '/diagnosis', icon: <FileTextOutlined />, label: '诊断管理', },
    { type: 'divider' },
    { key: '/treatment', icon: <MedicineBoxOutlined />, label: '治疗方案', },
    { key: '/knowledge', icon: <BookOutlined />, label: '知识库', },
    { key: '/copilot', icon: <AiOutlined />, label: 'AI 助手', },
    { type: 'divider' },
    { key: '/settings', icon: <SettingOutlined />, label: '系统设置', },
  ];

  // 用户菜单
  const userMenu: MenuProps['items'] = [
    { key: 'profile', icon: <UserOutlined />, label: '个人中心', },
    { key: 'settings', icon: <SettingOutlined />, label: '账户设置', },
    { type: 'divider' },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true, },
  ];

  // 面包屑导航
  const getBreadcrumbItems = () => {
    const path = location.pathname;
    const items = [{ title: <HomeOutlined />, href: '/dashboard' }];
    
    const currentMenu = menuItems.find(item => item?.key === path);
    if (currentMenu) {
      items.push({ title: String(currentMenu.label) });
    }
    
    return items;
  };

  return (
    <Layout className="app-layout" style={{ minHeight: '100vh' }}>
      {/* 侧边栏 - 桌面端 */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        breakpoint="lg"
        className="app-sider"
        width={256}
      >
        <div className="logo">
          {collapsed ? '🏥' : <span>🏥 乳腺 AI 诊断系统</span>}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>

      {/* 移动端侧边栏 */}
      <Drawer
        placement="left"
        onClose={() => setMobileOpen(false)}
        open={mobileOpen}
        className="mobile-drawer"
        bodyStyle={{ padding: 0 }}
      >
        <div className="logo" style={{ padding: 16 }}>🏥 乳腺 AI 诊断系统</div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => {
            navigate(key);
            setMobileOpen(false);
          }}
        />
      </Drawer>

      <Layout>
        {/* 顶部导航 */}
        <Header className="app-header" style={{ padding: '0 16px' }}>
          <div className="header-left">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => {
                if (window.innerWidth < 768) {
                  setMobileOpen(true);
                } else {
                  setCollapsed(!collapsed);
                }
              }}
              className="trigger"
            />
            <Breadcrumb items={getBreadcrumbItems()} />
          </div>
          
          <div className="header-right">
            {/* 通知 */}
            <Badge count={3} size="small">
              <Button type="text" icon={<BellOutlined />} />
            </Badge>

            {/* 暗黑模式切换 */}
            <Button
              type="text"
              icon={darkMode ? <SunOutlined /> : <MoonOutlined />}
              onClick={() => setDarkMode(!darkMode)}
            />

            {/* 用户菜单 */}
            <Dropdown menu={{ items: userMenu }} placement="bottomRight">
              <Avatar
                style={{ backgroundColor: token.colorPrimary, cursor: 'pointer' }}
                icon={<UserOutlined />}
                size="default"
              />
            </Dropdown>
          </div>
        </Header>

        {/* 内容区域 */}
        <Content className="app-content">
          <div className="content-wrapper">
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};
