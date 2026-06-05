# 乳腺 AI 辅助诊断系统

AI-powered breast cancer diagnosis assistance system

## 🚀 快速开始

```bash
# 安装后端依赖
pip install -r requirements.txt --break-system-packages

# 安装前端依赖
cd frontend && npm install

# 启动服务
./scripts/run.sh
```

访问 http://localhost:3000

## 📁 项目结构

```
.
├── app/                    # 后端服务 (FastAPI)
├── frontend/               # 前端应用 (React + TypeScript)
├── docs/                   # 项目文档
│   ├── guides/            # 使用指南
│   ├── api/               # API 文档
│   ├── architecture/      # 架构设计
│   └── changelog/         # 更新日志
├── scripts/                # 工具脚本
│   ├── setup/             # 安装脚本
│   ├── deploy/            # 部署脚本
│   └── utils/             # 工具脚本
└── config/                 # 配置文件
```

## 📖 文档导航

| 文档 | 路径 | 说明 |
|------|------|------|
| 安装指南 | `docs/guides/INSTALL.md` | 详细安装步骤 |
| 开发指南 | `docs/guides/DEVELOPMENT.md` | 开发环境配置 |
| 功能说明 | `docs/FEATURES_SUMMARY.md` | 功能列表 |
| API 文档 | `docs/api/` | API 接口说明 |
| 架构设计 | `docs/architecture/` | 系统架构 |

## 🔧 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端页面 | http://localhost:3000 | React 应用 |
| 后端 API | http://localhost:8005 | FastAPI 服务 |
| API 文档 | http://localhost:8005/api/docs | Swagger UI |

## 📦 技术栈

**后端**:
- Python 3.11+
- FastAPI
- SQLAlchemy + asyncmy
- PyTorch

**前端**:
- React 18
- TypeScript
- Vite
- Ant Design

## 📄 许可证

MIT License

---

**v3.3.0** | 2026-06-05
