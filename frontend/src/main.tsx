/**
 * 乳腺 AI 辅助诊断系统 - 前端入口
 * 
 * 基于 React 18 + TypeScript + Vite
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider } from 'antd';          // Ant Design 配置
import zhCN from 'antd/locale/zh_CN';           // 中文语言包
import { RouterProvider } from 'react-router-dom';
import { router } from './router';              // 路由配置
import './styles/global.css';                   // 全局样式


// 创建应用根节点
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* Ant Design 全局配置 */}
    <ConfigProvider locale={zhCN}>
      {/* 路由提供者 */}
      <RouterProvider router={router} />
    </ConfigProvider>
  </React.StrictMode>
);
