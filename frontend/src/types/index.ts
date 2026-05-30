/**
 * 患者类型定义
 */
export interface Patient {
  id: number;
  patient_no: string;
  name: string;
  gender: 'F' | 'M';
  birth_date: string;
  age: number;
  phone?: string;
  email?: string;
  constitution?: string;
  constitution_score?: number;
  zheng_type?: string;
  zheng_severity?: string;
  risk_level?: 'low' | 'medium' | 'high' | 'very_high';
  risk_score?: number;
  created_at: string;
  updated_at: string;
}

export interface PatientCreate {
  name: string;
  gender: 'F' | 'M';
  birth_date: string;
  phone?: string;
  email?: string;
  constitution?: string;
  zheng_type?: string;
}

export interface PatientUpdate {
  name?: string;
  phone?: string;
  email?: string;
  constitution?: string;
  zheng_type?: string;
  risk_level?: string;
}

export interface PatientListParams {
  page?: number;
  page_size?: number;
  name?: string;
  patient_no?: string;
  constitution?: string;
  risk_level?: string;
}

export interface PatientStats {
  total: number;
  high_risk_count: number;
  constitution_distribution: Record<string, number>;
  risk_level_distribution: Record<string, number>;
}

/**
 * 随访类型定义
 */
export interface Visit {
  id: number;
  patient_id: number;
  visit_no: string;
  visit_date: string;
  visit_type: string;
  chief_complaint?: string;
  birads_category?: string;
  created_at: string;
  patient?: Patient;
}

export interface VisitCreate {
  patient_id: number;
  visit_date: string;
  visit_type: string;
  chief_complaint?: string;
}

/**
 * 超声检查类型定义
 */
export interface Ultrasound {
  id: number;
  visit_id: number;
  image_no: string;
  image_path: string;
  image_type: string;
  quality_score?: number;
  ai_score?: number;
  ai_prediction?: string;
  created_at: string;
}

/**
 * 诊断类型定义
 */
export interface Diagnosis {
  id: number;
  lesion_id: number;
  diagnosis_no: string;
  diagnosis_type: string;
  diagnosis_date: string;
  malignancy?: string;
  status: string;
  created_at: string;
}

/**
 * 治疗类型定义
 */
export interface Treatment {
  id: number;
  diagnosis_id: number;
  treatment_no: string;
  treatment_type: string;
  status: string;
  created_at: string;
}

/**
 * 通用响应类型
 */
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: number;
  username: string;
  role?: string;
}
