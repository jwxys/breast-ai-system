# 前端 TypeScript 错误修复指南

## 错误分类统计

总错误数：~165 个

### 按类型分类

| 错误类型 | 数量 | 优先级 | 说明 |
|---------|------|--------|------|
| TS6133 | ~40 | 低 | 未使用的变量/导入 |
| TS2305 | ~30 | 高 | 模块无导出 |
| TS2307 | ~25 | 高 | 模块找不到 |
| TS2303 | ~20 | 中 | 循环导入 |
| TS2724 | ~15 | 中 | 图标不存在 |
| TS6196 | ~10 | 低 | 类型声明未使用 |
| 其他 | ~25 | 中 | 各种类型错误 |

## 关键修复项

### 1. 已修复 - 图标导入错误
```diff
- import { AiOutlined } from '@ant-design/icons';
+ import { ApiOutlined } from '@ant-design/icons';

- import { PrintOutlined } from '@ant-design/icons';
+ import { PrinterOutlined } from '@ant-design/icons';
```

### 2. 已修复 - 导出语句
```diff
// dashboard/index.ts
- export { default } from './index';
- export { default as Dashboard } from './index';
+ export { default as Dashboard } from './index';

// copilot/index.ts
- export { default as MedicalCopilotPage } from './index';
+ export { default as MedicalCopilotPage } from './index';
```

### 3. 待修复 - 缺失的类型定义

#### three.js 相关
```bash
npm install three @types/three --save
```

#### react-signature-canvas
```bash
npm install react-signature-canvas @types/react-signature-canvas --save
```

### 4. 待修复 - 未使用的导入

批量清理命令：
```bash
# 使用 ESLint 自动清理
npx eslint src/ --fix
```

## 修复优先级

### P0 - 阻止编译的错误
- [x] 图标导入错误 (AiOutlined → ApiOutlined)
- [x] 导出语句循环
- [ ] 缺失的模块导出

### P1 - 影响功能的错误
- [ ] three.js 类型定义
- [ ] react-signature-canvas 类型
- [ ] API 模块路径

### P2 - 代码质量警告
- [ ] 未使用的变量
- [ ] 未使用的导入
- [ ] 类型隐式 any

## 下一步行动

1. 安装缺失的依赖
2. 修复模块路径
3. 清理未使用代码
4. 完善类型定义

---

**状态**: 进行中  
**最后更新**: 2026-06-05
