# 开发指南

## 开发环境配置

### 1. 安装依赖

```bash
# 后端
pip install -r requirements.txt

# 前端
cd frontend && npm install
```

### 2. 配置环境变量

编辑 `.env` 和 `frontend/.env` 文件

### 3. 启动开发服务器

```bash
./scripts/run.sh
```

## 代码规范

### 后端 (Python)
- 遵循 PEP 8
- 类型注解 (Type Hints)
- 中文注释

### 前端 (TypeScript)
- ESLint + Prettier
- React Hooks 规范
- 中文注释

## 提交规范

```bash
# 格式
<type>(<scope>): <subject>

# 示例
feat(diagnosis): 添加 AI 辅助诊断功能
fix(types): 修复 TypeScript 语法错误
```

## 测试

```bash
# 后端测试
pytest

# 前端测试
cd frontend && npm run test
```

---

**返回**: [安装指南](INSTALL.md) | [文档索引](../README.md)
