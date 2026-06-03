import request from '@/utils/request';

export interface ContactResponse {
  id: number;
  name: string;
  title?: string;
  organization?: string;
  contact_type: ContactType;
  phone_primary: string;
  phone_secondary?: string;
  email?: string;
  wechat?: string;
  address?: string;
  responsibilities?: string;
  available_hours?: string;
  priority: number;
  is_active: boolean;
  notes?: string;
  created_by?: number;
  created_at: string;
  updated_at: string;
}

export type ContactType = 'emergency' | 'medical' | 'admin' | 'technical' | 'ethics' | 'other';

export interface ContactListParams {
  contact_type?: ContactType;
  is_active?: boolean;
  skip?: number;
  limit?: number;
}

export interface ContactListResponse {
  items: ContactResponse[];
  total: number;
  skip: number;
  limit: number;
}

export interface ContactCreateData {
  name: string;
  title?: string;
  organization?: string;
  contact_type: ContactType;
  phone_primary: string;
  phone_secondary?: string;
  email?: string;
  wechat?: string;
  address?: string;
  responsibilities?: string;
  available_hours?: string;
  priority?: number;
  is_active?: boolean;
  notes?: string;
}

/**
 * 获取联系人列表
 */
export const getContactList = async (params?: ContactListParams): Promise<ContactListResponse> => {
  return request('/api/v1/emergency-contacts', {
    method: 'GET',
    params
  });
};

/**
 * 获取联系人详情
 */
export const getContact = async (id: number): Promise<ContactResponse> => {
  return request(`/api/v1/emergency-contacts/${id}`, {
    method: 'GET'
  });
};

/**
 * 创建联系人
 */
export const createContact = async (data: ContactCreateData): Promise<ContactResponse> => {
  return request('/api/v1/emergency-contacts', {
    method: 'POST',
    data
  });
};

/**
 * 更新联系人
 */
export const updateContact = async (id: number, data: Partial<ContactCreateData>): Promise<ContactResponse> => {
  return request(`/api/v1/emergency-contacts/${id}`, {
    method: 'PUT',
    data
  });
};

/**
 * 删除联系人
 */
export const deleteContact = async (id: number): Promise<void> => {
  return request(`/api/v1/emergency-contacts/${id}`, {
    method: 'DELETE'
  });
};

/**
 * 获取联系人类型列表
 */
export const getContactTypes = async (): Promise<{ value: string; label: string; color: string }[]> => {
  return request('/api/v1/emergency-contacts/types', {
    method: 'GET'
  });
};

/**
 * 获取快速访问联系人
 */
export const getQuickAccessContacts = async (): Promise<ContactResponse[]> => {
  return request('/api/v1/emergency-contacts/quick-access', {
    method: 'GET'
  });
};
