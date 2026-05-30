# 问题跟踪与修复记录

**创建时间**: 2026-05-28 23:43  
**测试版本**: v1.0.0  
**测试人员**: AI Coding Assistant (角色模拟)

---

## 🔴 严重问题 (已修复)

### ISSUE-001: Report 模型缺少关系定义
- **发现时间**: 2026-05-28 23:35
- **严重性**: 高 (阻碍登录)
- **现象**: 登录时数据库报错 `Mapper 'Mapper[Report(report)]' has no property 'patient'`
- **根本原因**: Report 模型缺少与 Patient/Visit/Diagnosis 的 relationship 定义
- **修复内容**:
  - `backend/app/models/data_management.py` - Report 类添加:
    ```python
    patient = relationship("Patient", back_populates="reports")
    visit = relationship("Visit", back_populates="reports")
    diagnosis = relationship("Diagnosis", back_populates="reports")
    ```
  - `backend/app/models/visit.py` - 添加:
    ```python
    reports = relationship("Report", back_populates="visit")
    ```
  - `backend/app/models/diagnosis.py` - 添加:
    ```python
    reports = relationship("Report", back_populates="diagnosis")
    ```
- **修复状态**: ✅ 已完成
- **验证结果**: 登录功能正常

---

### ISSUE-002: PatientResponse Schema 字段验证错误
- **发现时间**: 2026-05-28 23:36
- **严重性**: 高 (影响患者查询)
- **现象**: 创建患者时返回 500 错误，`age` 字段验证失败
- **根本原因**: PatientResponse 中 `age` 定义为必填 int，但数据库中可能为 NULL
- **修复内容**:
  - `backend/app/schemas/patient.py`:
    ```python
    # 修复前
    age: int
    
    # 修复后
    age: Optional[int]
    ```
- **修复状态**: ✅ 已完成
- **验证结果**: 待验证

---

## 🟡 中等问题 (需修复)

### ISSUE-003: 性别字段格式不匹配
- **发现时间**: 2026-05-28 23:36
- **严重性**: 中
- **现象**: 创建患者返回 422 错误
- **原因**: Schema 要求 gender 为 `^[MF]$` (M 或 F)，测试使用 `female`
- **解决方案**: 
  - 前端/测试中使用正确格式：`M` (男) / `F` (女)
  - 或修改 schema 支持更灵活格式
- **影响**: 前端表单需要限制输入为 M/F

---

### ISSUE-004: Schema 字段命名不一致
- **发现时间**: 2026-05-28 23:36
- **严重性**: 中
- **现象**: 创建患者 API 要求 `birth_date`，但模型使用 `date_of_birth`
- **原因**: Schema 和 Model 字段名不一致
- **解决方案**:
  - 统一字段命名
  - 或在 Schema 中使用 `alias` 映射
- **修复建议**:
  ```python
  # 方案 1: Schema 中使用 alias
  birth_date: date = Field(..., alias="date_of_birth")
  
  # 方案 2: 修改 Schema 字段名
  date_of_birth: date
  ```

---

## 🟢 体验优化 (建议)

### ISSUE-005: 登录 Token 用户信息不完整
- **发现时间**: 2026-05-28 23:37
- **严重性**: 低
- **现象**: 登录返回的 user 对象为空
- **原因**: Token response 未包含完整的 user 信息
- **建议**: 在 login API 返回中包含完整的用户信息
  ```python
  return {
      "access_token": token,
      "token_type": "bearer",
      "user": {
          "id": user.id,
          "username": user.username,
          "role": user.role.code
      }
  }
  ```

---

## 📋 测试覆盖情况

| 模块 | 测试用例 | 通过 | 失败 | 通过率 |
|------|---------|------|------|--------|
| 认证 | 1 | 1 | 0 | 100% |
| 患者管理 | 2 | 0 | 2 (已修复) | 待验证 |
| 知识库 | 1 | 1 | 0 | 100% |
| 数据管理 | 4 | 2 | 2 | 50% |
| 系统健康 | 1 | 1 | 0 | 100% |
| **总计** | **9** | **5** | **4** | **56%** |

---

## 🔄 待验证修复

1. **ISSUE-001**: Report 关系定义 - 待完整测试验证
2. **ISSUE-002**: PatientResponse age 字段 - 待完整测试验证

---

## ✅ 功能正常模块

| 模块 | 功能 | 状态 |
|------|------|------|
| 认证 | 用户登录 | ✅ 正常 |
| 知识库 | 文章查询 | ✅ 正常 |
| 数据管理 | 模型权重查询 | ✅ 正常 |
| 数据管理 | 推理记录查询 | ✅ 正常 |
| 系统 | 健康检查 | ✅ 正常 |

---

## 📝 后续改进建议

1. **Schema 统一性**: 建立 Schema 命名规范，避免字段名不一致
2. **错误处理**: 完善 API 错误信息，便于调试
3. **单元测试**: 为关键 API 添加单元测试
4. **集成测试**: 建立完整的集成测试流程
5. **文档完善**: 更新 API 文档，标明字段格式要求

---

**下次测试时间**: 修复后进行回归测试  
**预计通过率**: 修复后应达到 90% 以上
