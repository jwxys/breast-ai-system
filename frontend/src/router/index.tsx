import { createHashRouter } from 'react-router-dom';
import { AppLayout } from '@/components/common';
import Dashboard from '@/pages/Dashboard';
import PatientList from '@/pages/Patient/List';
import VisitList from '@/pages/Visit/List';
import UltrasoundExam from '@/pages/Ultrasound';
import AIDiagnosis from '@/pages/Diagnosis';
import TreatmentList from '@/pages/Treatment';
import KnowledgeBase from '@/pages/Knowledge';
import DataManagement from '@/pages/DataManagement';
import Login from '@/pages/Login';
import AIInquiryPage from '@/pages/Inquiry';
import MedicalCopilotPage from '@/pages/Copilot';
import ImagingTCMPage from '@/pages/ImagingTCM';

export const router = createHashRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'patient',
        children: [
          {
            index: true,
            element: <PatientList />,
          },
          {
            path: 'create',
            element: <div>新建患者 (页面开发中...)</div>,
          },
          {
            path: ':id',
            element: <div>患者详情 (页面开发中...)</div>,
          },
          {
            path: ':id/edit',
            element: <div>编辑患者 (页面开发中...)</div>,
          },
        ],
      },
      {
        path: 'visit',
        children: [
          {
            index: true,
            element: <VisitList />,
          },
          {
            path: 'create',
            element: <div>新建随访 (页面开发中...)</div>,
          },
        ],
      },
      {
        path: 'ultrasound',
        children: [
          {
            index: true,
            element: <UltrasoundExam />,
          },
          {
            path: ':id/tcm-analysis',
            element: <ImagingTCMPage />,
          },
        ],
      },
      {
        path: 'diagnosis',
        children: [
          {
            index: true,
            element: <AIDiagnosis />,
          },
          {
            path: 'create',
            element: <div>新建诊断 (页面开发中...)</div>,
          },
        ],
      },
      {
        path: 'treatment',
        children: [
          {
            index: true,
            element: <TreatmentList />,
          },
        ],
      },
      {
        path: 'knowledge',
        children: [
          {
            index: true,
            element: <KnowledgeBase />,
          },
          {
            path: ':id',
            element: <div>文章详情 (页面开发中...)</div>,
          },
        ],
      },
      {
        path: 'data',
        children: [
          {
            index: true,
            element: <DataManagement />,
          },
        ],
      },
      {
        path: 'inquiry',
        element: <AIInquiryPage />,
      },
      {
        path: 'copilot',
        element: <MedicalCopilotPage />,
      },
      {
        path: 'settings',
        element: <div>系统设置 (页面开发中...)</div>,
      },
    ],
  },
]);
