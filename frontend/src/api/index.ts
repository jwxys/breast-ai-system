import apiClient from './request';
import type { Patient, PatientCreate, PatientUpdate, PatientListParams } from '@/types/patient';

/**
 * 患者管理 API
 */
export const patientApi = {
  /** 获取患者列表 */
  async getList(params: PatientListParams) {
    return apiClient.get('/api/v1/patient', { params });
  },

  /** 获取患者详情 */
  async getById(id: number) {
    return apiClient.get(`/api/v1/patient/${id}`);
  },

  /** 创建患者 */
  async create(data: PatientCreate) {
    return apiClient.post('/api/v1/patient', data);
  },

  /** 更新患者 */
  async update(id: number, data: PatientUpdate) {
    return apiClient.put(`/api/v1/patient/${id}`, data);
  },

  /** 删除患者 */
  async delete(id: number) {
    return apiClient.delete(`/api/v1/patient/${id}`);
  },

  /** 获取患者统计 */
  async getStats() {
    return apiClient.get('/api/v1/patient/stats');
  },
};

/**
 * 认证 API
 */
export const authApi = {
  /** 用户登录 */
  async login(username: string, password: string) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    return apiClient.post('/api/v1/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },

  /** 获取当前用户信息 */
  async getCurrentUser() {
    return apiClient.get('/api/v1/auth/me');
  },

  /** 退出登录 */
  logout() {
    localStorage.removeItem('token');
  },
};

/**
 * 随访管理 API
 */
export const visitApi = {
  async getList(params: any) {
    return apiClient.get('/api/v1/visit', { params });
  },

  async getById(id: number) {
    return apiClient.get(`/api/v1/visit/${id}`);
  },

  async create(data: any) {
    return apiClient.post('/api/v1/visit', data);
  },

  async update(id: number, data: any) {
    return apiClient.put(`/api/v1/visit/${id}`, data);
  },
};

/**
 * 超声检查 API
 */
export const ultrasoundApi = {
  async upload(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.post('/api/v1/ultrasound/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  async annotate(data: any) {
    return apiClient.post('/api/v1/ultrasound/annotate', data);
  },

  async getById(id: number) {
    return apiClient.get(`/api/v1/ultrasound/${id}`);
  },
};

/**
 * 诊断管理 API
 */
export const diagnosisApi = {
  async getList(params: any) {
    return apiClient.get('/api/v1/diagnosis', { params });
  },

  async create(data: any) {
    return apiClient.post('/api/v1/diagnosis', data);
  },

  /** 中医证型识别 */
  async recognizeZhengType(data: any) {
    return apiClient.post('/api/v1/diagnosis/zheng-type', data);
  },

  /** AI 辅助诊断 */
  async aiDiagnosis(data: any) {
    return apiClient.post('/api/v1/diagnosis/ai', data);
  },
};

/**
 * 治疗管理 API
 */
export const treatmentApi = {
  async getList(params: any) {
    return apiClient.get('/api/v1/treatment', { params });
  },

  async create(data: any) {
    return apiClient.post('/api/v1/treatment', data);
  },

  /** 治疗方案推荐 */
  async recommend(data: any) {
    return apiClient.post('/api/v1/treatment/recommend', data);
  },
};
