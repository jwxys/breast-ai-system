"""
危急值预警服务

支持：
- 危急值识别
- 预警通知
- 质控提醒
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AlertLevel(str, Enum):
    """预警级别"""
    LOW = "low"          # 低优先级
    MEDIUM = "medium"    # 中优先级
    HIGH = "high"        # 高优先级
    CRITICAL = "critical"  # 危急


@dataclass
class Alert:
    """预警记录"""
    patient_id: int
    patient_name: str
    alert_type: str
    alert_level: AlertLevel
    alert_message: str
    created_at: datetime
    action_required: str
    assigned_to: Optional[int] = None


class AlertService:
    """
    危急值预警服务
    
    功能：
    1. 危急值识别
    2. 预警生成
    3. 通知发送
    4. 质控跟踪
    """
    
    def __init__(self):
        self.alert_rules = self._load_alert_rules()
    
    def _load_alert_rules(self) -> Dict:
        """加载预警规则"""
        return {
            "birads_5": {
                "level": AlertLevel.HIGH,
                "message": "BI-RADS 5 类 - 高度提示恶性",
                "action": "48 小时内安排穿刺活检或手术"
            },
            "rapid_growth": {
                "level": AlertLevel.HIGH,
                "message": "病灶快速增大",
                "action": "建议尽快进一步检查"
            },
            "new_calcification": {
                "level": AlertLevel.MEDIUM,
                "message": "新发微小钙化",
                "action": "建议短期随访或活检"
            },
            "overdue_followup": {
                "level": AlertLevel.MEDIUM,
                "message": "随访逾期",
                "action": "尽快联系患者安排随访"
            },
            "discordant_results": {
                "level": AlertLevel.HIGH,
                "message": "影像与病理结果不一致",
                "action": "请上级医师会诊或重新评估"
            },
            "triple_negative": {
                "level": AlertLevel.HIGH,
                "message": "三阴性乳腺癌",
                "action": "建议多学科会诊 (MDT)"
            },
        }
    
    def check_and_create_alerts(
        self,
        patient_id: int,
        patient_name: str,
        diagnosis_data: Dict
    ) -> List[Alert]:
        """
        检查并生成预警
        
        Args:
            patient_id: 患者 ID
            patient_name: 患者姓名
            diagnosis_data: 诊断数据
        
        Returns:
            List[Alert]: 预警列表
        """
        alerts = []
        
        # BI-RADS 5 类
        if diagnosis_data.get("birads_category") == "5":
            alerts.append(self._create_alert(
                patient_id, patient_name,
                "birads_5",
                self.alert_rules["birads_5"]
            ))
        
        # 三阴性
        if diagnosis_data.get("molecular_subtype") == "Basal-like":
            alerts.append(self._create_alert(
                patient_id, patient_name,
                "triple_negative",
                self.alert_rules["triple_negative"]
            ))
        
        # 快速生长
        if diagnosis_data.get("growth_rate", 0) > 2.0:  # 倍增时间<6 个月
            alerts.append(self._create_alert(
                patient_id, patient_name,
                "rapid_growth",
                self.alert_rules["rapid_growth"]
            ))
        
        # 影像病理不一致
        if self._is_discordant(diagnosis_data):
            alerts.append(self._create_alert(
                patient_id, patient_name,
                "discordant_results",
                self.alert_rules["discordant_results"]
            ))
        
        return alerts
    
    def _create_alert(
        self,
        patient_id: int,
        patient_name: str,
        alert_type: str,
        rule: Dict
    ) -> Alert:
        """创建预警"""
        return Alert(
            patient_id=patient_id,
            patient_name=patient_name,
            alert_type=alert_type,
            alert_level=rule["level"],
            alert_message=rule["message"],
            created_at=datetime.utcnow(),
            action_required=rule["action"]
        )
    
    def _is_discordant(self, diagnosis_data: Dict) -> bool:
        """检查影像与病理是否不一致"""
        birads = diagnosis_data.get("birads_category", "")
        pathology = diagnosis_data.get("pathology_type", "")
        
        # BI-RADS 2-3 但病理恶性
        if birads in ["2", "3"] and pathology and "恶性" in pathology:
            return True
        
        # BI-RADS 5 但病理良性
        if birads == "5" and pathology and "良性" in pathology:
            return True
        
        return False
    
    def get_alert_statistics(self, days: int = 30) -> Dict:
        """
        获取预警统计
        
        Args:
            days: 统计天数
        
        Returns:
            Dict: 统计信息
        """
        # 示例返回
        return {
            "total_alerts": 0,
            "by_level": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "by_type": {},
            "resolved_rate": 0.0,
            "avg_response_time_hours": 0.0
        }
