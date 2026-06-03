# 前端模块化开发指南

**版本**: v3.0  
**更新日期**: 2026-06-02

---

## 📚 目录

1. [模块化结构](#模块化结构)
2. [快速开始](#快速开始)
3. [开发规范](#开发规范)
4. [最佳实践](#最佳实践)

---

## 🏗️ 模块化结构

### 目录组织

```
src/
├── features/          # 功能模块（核心）
│   ├── auth/         # 认证模块
│   │   ├── index.ts        # 模块导出
│   │   ├── index.tsx       # 页面组件
│   │   ├── index.css       # 样式
│   │   ├── components/     # 模块组件
│   │   ├── hooks/          # 模块 Hooks
│   │   ├── api/            # 模块 API
│   │   ├── types/          # 模块类型
│   │   └── utils/          # 模块工具
│   ├── patient/      # 患者管理
│   └── ...           # 其他模块
├── components/        # 通用组件
├── hooks/            # 通用 Hooks
├── api/              # 通用 API
├── utils/            # 通用工具
├── types/            # 通用类型
└── router/           # 路由配置
```

### 16 个功能模块

| 模块 | 路径 | 功能 |
|------|------|------|
| auth | `features/auth/` | 登录认证 |
| dashboard | `features/dashboard/` | 首页仪表盘 |
| patient | `features/patient/` | 患者管理 |
| visit | `features/visit/` | 随访管理 |
| ultrasound | `features/ultrasound/` | 超声检查 |
| diagnosis | `features/diagnosis/` | AI 诊断 |
| treatment | `features/treatment/` | 治疗管理 |
| knowledge | `features/knowledge/` | 知识库 |
| inquiry | `features/inquiry/` | 智能问诊 |
| copilot | `features/copilot/` | AI 医学助手 |
| imaging-tcm | `features/imaging-tcm/` | 影像中医 |
| breast-3d | `features/breast-3d/` | 3D 重建 |
| data | `features/data/` | 数据管理 |
| settings | `features/settings/` | 系统设置 |
| emergency | `features/emergency/` | 紧急联系人 |
| consent | `features/consent/` | 知情同意 |

---

## 🚀 快速开始

### 添加新功能模块

#### 步骤 1: 创建模块目录

```bash
# 在 features 目录创建新模块
mkdir -p src/features/my-feature/{components,hooks,api,types,utils}
```

#### 步骤 2: 创建页面组件

```tsx
// src/features/my-feature/index.tsx
import React from 'react';

const MyFeaturePage: React.FC = () => {
  return (
    <div>
      <h1>我的功能</h1>
      <p>功能开发中...</p>
    </div>
  );
};

export default MyFeaturePage;
```

#### 步骤 3: 创建模块导出

```ts
// src/features/my-feature/index.ts
// 模块导出文件
export { default as MyFeaturePage } from './index';

// 导出样式
import './index.css';
```

#### 步骤 4: 添加到路由

```tsx
// src/router/index.tsx
import { MyFeaturePage } from '@/features/my-feature';

export const router = createHashRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        path: 'my-feature',
        element: <MyFeaturePage />,
      },
    ],
  },
]);
```

---

## 📖 开发规范

### 导入规范

#### ✅ 推荐方式

```tsx
// 命名导入（推荐）
import { PatientList } from '@/features/patient';
import { useAuth } from '@/features/auth';

// 统一导入
import { patient, auth } from '@/features';
```

#### ❌ 不推荐

```tsx
// 避免相对路径
import PatientList from '../../features/patient/index';

// 避免深层导入
import { PatientList } from '@/features/patient/pages/Patient/List';
```

### 文件命名

- **页面组件**: 使用 PascalCase，如 `PatientList.tsx`
- **工具函数**: 使用 camelCase，如 `formatDate.ts`
- **样式文件**: 跟随组件文件，如 `index.css`
- **导出文件**: 统一使用 `index.ts`

### 目录结构

每个模块内部结构：

```
my-feature/
├── index.ts          # 模块导出（必需）
├── index.tsx         # 主页面（可选）
├── index.css         # 样式（可选）
├── components/       # 模块组件（可选）
├── hooks/            # 模块 Hooks（可选）
├── api/              # 模块 API（可选）
├── types/            # 模块类型（可选）
└── utils/            # 模块工具（可选）
```

---

## 🎯 最佳实践

### 1. 模块内聚

每个模块应包含其所有相关代码：

```
features/patient/
├── components/       # 患者专用组件
│   ├── PatientCard.tsx
│   └── PatientForm.tsx
├── hooks/            # 患者专用 Hooks
│   └── usePatient.ts
├── api/              # 患者相关 API
│   └── patientAPI.ts
└── types/            # 患者类型定义
    └── patient.types.ts
```

### 2. 共享代码

跨模块共享的代码放在顶层：

```
components/    # 通用 UI 组件
hooks/         # 通用 Hooks
api/           # Axios 实例、通用 API
utils/         # 通用工具函数
types/         # 全局类型
```

### 3. 类型定义

优先在模块内定义类型：

```ts
// features/patient/types/index.ts
export interface Patient {
  id: string;
  name: string;
  age?: number;
}

// 使用
import { Patient } from '@/features/patient/types';
```

### 4. 样式管理

- 模块样式放在模块目录内
- 全局样式在 `styles/` 目录
- 使用 CSS Modules 或 SCSS

```ts
// 导入模块样式
import './index.css';

// 导入 SCSS
import styles from './component.module.scss';
```

---

## 🔧 常用模式

### 模式 1: 创建模块组件

```tsx
// features/patient/components/PatientCard.tsx
import React from 'react';
import { Card } from 'antd';
import { Patient } from '../types';

interface PatientCardProps {
  patient: Patient;
  onSelect?: (patient: Patient) => void;
}

export const PatientCard: React.FC<PatientCardProps> = ({ 
  patient, 
  onSelect 
}) => {
  return (
    <Card onClick={() => onSelect?.(patient)}>
      <h3>{patient.name}</h3>
      <p>{patient.age}岁</p>
    </Card>
  );
};
```

### 模式 2: 创建模块 Hook

```ts
// features/patient/hooks/usePatient.ts
import { useQuery } from '@tanstack/react-query';
import { patientAPI } from '../api';

export const usePatient = (id: string) => {
  return useQuery({
    queryKey: ['patient', id],
    queryFn: () => patientAPI.getPatient(id),
  });
};
```

### 模式 3: 创建模块 API

```ts
// features/patient/api/index.ts
import request from '@/utils/request';

export const patientAPI = {
  // 获取患者列表
  getPatientList: () => request.get('/patients'),
  
  // 获取患者详情
  getPatient: (id: string) => request.get(`/patients/${id}`),
  
  // 创建患者
  createPatient: (data: any) => request.post('/patients', data),
};
```

### 模式 4: 导出模块

```ts
// features/patient/index.ts
// 页面组件
export { default as PatientList } from './List';
export { default as PatientDetail } from './Detail';
export { default as PatientCreate } from './Create';

// 组件
export { PatientCard } from './components/PatientCard';
export { PatientForm } from './components/PatientForm';

// Hooks
export { usePatient } from './hooks/usePatient';

// API
export { patientAPI } from './api';

// 类型
export type { Patient } from './types';

// 样式
import './index.css';
```

---

## 📋 任务清单

### 新建功能模块

- [ ] 创建模块目录结构
- [ ] 编写页面组件
- [ ] 创建模块导出文件
- [ ] 添加路由配置
- [ ] 编写 API 调用（如需要）
- [ ] 编写类型定义（如需要）
- [ ] 添加样式文件

### 修改现有模块

- [ ] 确保模块导出文件更新
- [ ] 检查是否有 Breaking Changes
- [ ] 更新相关文档

---

## 🎓 学习资源

- [React 官方文档](https://react.dev/)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)
- [Vite 文档](https://vitejs.dev/)
- [React Router 文档](https://reactrouter.com/)

---

**Happy Coding!** 🚀
