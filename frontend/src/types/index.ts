export interface User {
  id: string;
  username: string;
  email?: string;
  role?: string;
}

export interface Patient {
  id: string;
  name: string;
  age?: number;
  gender?: string;
  phone?: string;
}

export interface ApiResponse<T = any> {
  code: number;
  data: T;
  message?: string;
}
