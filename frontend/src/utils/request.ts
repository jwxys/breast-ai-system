import axios from 'axios';
import type { AxiosRequestConfig, AxiosResponse } from 'axios';

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

export default request;
