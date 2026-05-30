import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import PatientList from './pages/Patient/List';
import PatientDetail from './pages/Patient/Detail';
import PatientCreate from './pages/Patient/Create';
import VisitList from './pages/Visit/List';
import VisitForm from './pages/Visit/Form';
import UltrasoundUpload from './pages/Ultrasound/Upload';
import UltrasoundAnalysis from './pages/Ultrasound/Analysis';
import DiagnosisForm from './pages/Diagnosis/Form';
import TreatmentPlan from './pages/Treatment/Plan';
import KnowledgeBase from './pages/Knowledge';
import Settings from './pages/Settings';
import LoginPage from './pages/Login';
import { useAuth } from './hooks/useAuth';

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>加载中...</div>;
  }

  return (
    <Routes>
      {/* 登录页 */}
      <Route path="/login" element={!user ? <LoginPage /> : <Navigate to="/" />} />

      {/* 主应用 */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        
        {/* 患者管理 */}
        <Route path="patient">
          <Route index element={<PatientList />} />
          <Route path=":id" element={<PatientDetail />} />
          <Route path="create" element={<PatientCreate />} />
        </Route>

        {/* 随访管理 */}
        <Route path="visit">
          <Route index element={<VisitList />} />
          <Route path=":id" element={<VisitForm />} />
        </Route>

        {/* 超声检查 */}
        <Route path="ultrasound">
          <Route path="upload" element={<UltrasoundUpload />} />
          <Route path="analysis/:id" element={<UltrasoundAnalysis />} />
        </Route>

        {/* 诊断管理 */}
        <Route path="diagnosis">
          <Route path=":lesionId" element={<DiagnosisForm />} />
        </Route>

        {/* 治疗管理 */}
        <Route path="treatment">
          <Route path="plan/:diagnosisId" element={<TreatmentPlan />} />
        </Route>

        {/* 知识库 */}
        <Route path="knowledge" element={<KnowledgeBase />} />

        {/* 系统设置 */}
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
