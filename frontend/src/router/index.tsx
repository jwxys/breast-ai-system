/**
 * 应用路由配置
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import App from '../App';

// 页面组件
import Dashboard from '../dashboard';
import PatientList from '../patient';
import DiagnosisList from '../diagnosis';
import DiagnosisDetail from '../diagnosis/detail';
import DiagnosisCreate from '../diagnosis/create';
import StatisticsDashboard from '../statistics/dashboard';
import Copilot from '../copilot';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      // 默认跳转
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      
      // 仪表盘
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      
      // 患者管理
      {
        path: 'patient',
        element: <PatientList />,
      },
      
      // 诊断管理
      {
        path: 'diagnosis',
        children: [
          {
            index: true,
            element: <DiagnosisList />,
          },
          {
            path: ':id',
            element: <DiagnosisDetail />,
          },
          {
            path: 'create',
            element: <DiagnosisCreate />,
          },
          {
            path: ':id/edit',
            element: <DiagnosisCreate />,
          },
        ],
      },
      
      // 统计看板
      {
        path: 'statistics',
        element: <StatisticsDashboard />,
      },
      
      // AI 助手
      {
        path: 'copilot',
        element: <Copilot />,
      },
    ],
  },
]);

export default router;
