/**
 * 智能问诊 API 封装
 */
import { request } from '@/utils/request';
import type { CollectedInfo, ChatState } from '@/pages/Inquiry/IntelligentInquiryPage';

export interface ChatRequest {
  session_id: string;
  message: string;
  patient_id?: number;
}

export interface ChatResponse {
  response: string;
  follow_up_questions: string[];
  collected_info: CollectedInfo;
  completeness: number;
  is_complete: boolean;
  risk_assessment?: {
    level: '低危' | '中危' | '高危';
    score: number;
    factors: string[];
    recommendation: string;
  };
  next_step: string;
}

export interface ChatReport {
  chief_complaint: string;
  present_illness: string;
  patient_info: any;
  symptoms: Array<{
    name: string;
    severity?: number;
    duration?: string;
  }>;
  medical_history: any;
  family_history: any;
  risk_assessment?: string;
  completeness: number;
}

/**
 * 发送问诊消息
 */
export const sendChatMessage = async (
  requestId: ChatRequest
): Promise<ChatResponse> => {
  return request({
    url: '/api/v1/symptom-chat/chat',
    method: 'post',
    data: requestId,
  });
};

/**
 * 获取问诊报告
 */
export const getChatReport = async (sessionId: string): Promise<{ report: ChatReport }> => {
  return request({
    url: `/api/v1/symptom-chat/session/${sessionId}/report`,
    method: 'get',
  });
};

/**
 * 结束问诊会话
 */
export const endChatSession = async (sessionId: string): Promise<{ message: string }> => {
  return request({
    url: `/api/v1/symptom-chat/session/${sessionId}`,
    method: 'delete',
  });
};

/**
 * 保存问诊记录到患者档案
 */
export const saveChatToPatient = async (
  sessionId: string,
  patientId: number
): Promise<{ message: string; patient_id: number }> => {
  return request({
    url: `/api/v1/symptom-chat/session/${sessionId}/save-to-patient/${patientId}`,
    method: 'post',
  });
};
