# 乳腺 AI 辅助诊断系统

中西医结合乳腺癌超声 AI 辅助诊断系统

## 技术栈

### 后端
- **框架**: FastAPI + Pydantic v2
- **数据库**: PostgreSQL 14
- **缓存**: Redis 7
- **ORM**: SQLAlchemy 2.0 (Async)
- **认证**: JWT + OAuth2
- **对象存储**: MinIO

### 前端
- **框架**: React 18 + TypeScript
- **UI 库**: Ant Design 5
- **路由**: React Router v6
- **状态管理**: Zustand
- **HTTP 客户端**: Axios
- **图表**: ECharts
- **构建工具**: Vite

### AI 推理
- **框架**: PyTorch 2.0 + PyTorch Lightning
- **模型**: PBS-Net / DFMFI / HXM-Net

### 部署
- **容器**: Docker + Docker Compose
- **编排**: Kubernetes (生产环境)
- **CI/CD**: GitHub Actions

## 快速开始

### 环境要求
- Docker 20+
- Docker Compose 2.0+
- Node.js 18+
- Python 3.11+

### 开发环境启动

```bash
# 克隆项目
git clone <repository-url>
cd breast-ai-system

# 启动所有服务
docker-compose up -d

# 或使用 make
make dev

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:5173 | React 开发服务器 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| PostgreSQL | localhost:5432 | 数据库 |
| Redis | localhost:6379 | 缓存 |
| MinIO | http://localhost:9000 | 对象存储 (Console: 9001) |

### 数据库初始化

```bash
# 进入后端容器
docker-compose exec backend /bin/bash

# 执行初始化脚本
python scripts/init_db.py
```

### 测试数据

```bash
# 生成测试数据
python scripts/generate_test_data.py
```

## 项目结构

```
breast-ai-system/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/v1/         # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 入口
│   ├── tests/              # 测试
│   └── requirements.txt
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/           # API 封装
│   │   ├── components/    # 组件
│   │   ├── pages/         # 页面
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   ├── styles/        # 样式
│   │   ├── utils/         # 工具函数
│   │   ├── App.tsx        # 根组件
│   │   ├── main.tsx       # 入口
│   │   └── vite-env.d.ts
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml      # Docker 编排
├── Makefile               # 快捷命令
└── README.md
```

## 核心功能

### 1. 患者管理
- 患者基本信息录入
- 中医体质辨识
- 中医证型分类
- 风险等级评估

### 2. 超声检查
- 图像上传与存储
- 扫描质控评分
- BI-RADS 特征提取
- 病灶分割与标注

### 3. AI 诊断
- 病灶分割 (PBS-Net)
- 多切面特征融合 (DFMFI)
- 多模态融合诊断 (HXM-Net)
- 良恶性预测

### 4. 随访管理
- 随访计划生成
- 失访预警
- 生存分析

### 5. 治疗管理
- 治疗方案推荐
- 分子分型预测
- 疗效评估

### 6. 知识库
- 中医证治知识库
- 诊疗指南
- 文献检索

## API 认证

使用 JWT Token 进行认证：

```bash
# 获取 Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 使用 Token
curl http://localhost:8000/api/v1/patients \
  -H "Authorization: Bearer <token>"
```

## 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 开发规范

### 代码风格
- 后端：遵循 PEP 8，使用 Black 格式化
- 前端：使用 ESLint + Prettier

### Git 提交规范
```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式化
refactor: 重构
test: 测试
chore: 构建/工具链
```

## 许可证

专有软件 - 仅供授权医疗机构使用

## 联系方式

技术支持：support@breast-ai.com
