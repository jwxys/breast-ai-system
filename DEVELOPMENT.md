# 开发指南

## 🚀 快速启动

```bash
./run.sh
```

## 📁 项目结构

```
.
├── app/          # 后端 (FastAPI)
├── frontend/     # 前端 (React)
└── ai_chat/      # AI 服务
```

## 🔧 配置

编辑 `app/.env`:
```
KIMI_API_KEY=sk-xxx
QWEN_API_KEY=sk-xxx
```

## 📝 访问地址

- 前端：http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档：http://localhost:8000/api/docs

## 💻 开发模式

**单独启动后端**:
```bash
cd app
python -m uvicorn main:app --reload
```

**单独启动前端**:
```bash
cd frontend
npm run dev
```
