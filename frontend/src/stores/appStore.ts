import { create } from 'zustand';
import { authApi, patientApi } from '@/api';
import type { User, Patient, PatientStats } from '@/types';

interface AppState {
  // 用户状态
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  
  // 患者数据
  patients: Patient[];
  patientStats: PatientStats | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchPatients: (params?: any) => Promise<void>;
  fetchPatientStats: () => Promise<void>;
  createPatient: (data: any) => Promise<Patient>;
  updatePatient: (id: number, data: any) => Promise<void>;
  deletePatient: (id: number) => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  // 初始状态
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  patients: [],
  patientStats: null,
  loading: false,
  error: null,
  
  // 登录
  login: async (username: string, password: string) => {
    set({ loading: true, error: null });
    try {
      const response = await authApi.login(username, password);
      const token = response.access_token;
      
      localStorage.setItem('token', token);
      
      const userInfo = await authApi.getCurrentUser();
      
      set({
        token,
        user: userInfo,
        isAuthenticated: true,
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.message || '登录失败',
        loading: false,
      });
      throw error;
    }
  },
  
  // 退出登录
  logout: () => {
    localStorage.removeItem('token');
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  },
  
  // 获取患者列表
  fetchPatients: async (params) => {
    set({ loading: true, error: null });
    try {
      const response = await patientApi.getList(params || {});
      set({
        patients: response.data || [],
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.message || '获取患者列表失败',
        loading: false,
      });
    }
  },
  
  // 获取患者统计
  fetchPatientStats: async () => {
    try {
      const response = await patientApi.getStats();
      set({
        patientStats: response.data,
      });
    } catch (error) {
      console.error('获取统计数据失败:', error);
    }
  },
  
  // 创建患者
  createPatient: async (data) => {
    const response = await patientApi.create(data);
    set((state) => ({
      patients: [...state.patients, response.data],
    }));
    return response.data;
  },
  
  // 更新患者
  updatePatient: async (id, data) => {
    await patientApi.update(id, data);
    set((state) => ({
      patients: state.patients.map((p) =>
        p.id === id ? { ...p, ...data } : p
      ),
    }));
  },
  
  // 删除患者
  deletePatient: async (id) => {
    await patientApi.delete(id);
    set((state) => ({
      patients: state.patients.filter((p) => p.id !== id),
    }));
  },
}));
