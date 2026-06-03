# 乳腺超声 AI 诊断系统 - 安装指南

## 系统要求

- **Python**: 3.13 或更高版本
- **操作系统**: Linux / macOS / Windows 10+
- **内存**: 最低 8GB，推荐 16GB+
- **存储**: 至少 10GB 可用空间
- **GPU** (可选): NVIDIA GPU with CUDA 11.8+

---

## 快速开始 (5 分钟)

### 1. 从 GitHub 克隆项目

```bash
git clone https://github.com/jwxys/breast-ai-system.git
cd breast-ai-system
```

### 2. 设置虚拟环境

**Linux/macOS**:
```bash
chmod +x setup_env.sh
./setup_env.sh
```

**Windows PowerShell**:
```powershell
.\setup_env.ps1
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和 API Keys
```

### 4. 启动服务

```bash
# Linux/macOS
./quickstart.sh

# Windows
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

访问：http://localhost:8005

---

## 详细安装步骤

### 步骤 1: 安装 Python 3.13

#### Ubuntu/Debian
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev
```

#### macOS (Homebrew)
```bash
brew install python@3.13
```

#### Windows
从官网下载：https://www.python.org/downloads/release/python-3130/

安装时勾选 "Add Python to PATH"

### 步骤 2: 验证安装

```bash
python3.13 --version
# 应显示：Python 3.13.x
```

### 步骤 3: 克隆项目

```bash
git clone https://github.com/jwxys/breast-ai-system.git
cd breast-ai-system
```

### 步骤 4: 创建虚拟环境

```bash
# 方法 1: 使用自动脚本 (推荐)
./setup_env.sh

# 方法 2: 手动创建
python3.13 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
.\venv\Scripts\Activate.ps1  # Windows

# 升级 pip
pip install --upgrade pip
```

### 步骤 5: 安装依赖

```bash
# 方法 1: 使用 requirements.txt
pip install -r requirements.txt

# 方法 2: 使用 pyproject.toml
pip install -e .
```

### 步骤 6: 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必需的环境变量：

```ini
# 数据库
DATABASE_URL=mysql+asyncmy://user:password@localhost:3306/breast_ai_db

# AI API Keys (可选)
KIMI_API_KEY=sk-...
TONGYI_API_KEY=sk-...

# JWT Secret (生产环境必须修改)
SECRET_KEY=your-secret-key-here
```

### 步骤 7: 初始化数据库 (可选)

```bash
# 如果需要使用数据库
python scripts/init_db.py
```

### 步骤 8: 启动服务

```bash
# 开发模式 (自动重载)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload

# 生产模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --workers 4
```

---

## 依赖包说明

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| fastapi | >=0.115.0 | Web API 框架 |
| uvicorn | >=0.30.0 | ASGI 服务器 |
| sqlalchemy | >=2.0.30 | ORM 框架 |
| torch | >=2.4.0 | 深度学习框架 |
| numpy | >=1.26.0 | 数值计算 |
| opencv-python | >=4.10.0 | 图像处理 |
| pydantic | >=2.8.0 | 数据验证 |

### 可选依赖

**开发环境**:
```bash
pip install -e ".[dev]"
```

**文档构建**:
```bash
pip install -e ".[docs]"
```

---

## 常见问题

### Q1: Python 版本不兼容

**错误**: `Requires Python >=3.13`

**解决**:
```bash
# 检查 Python 版本
python --version

# 安装 Python 3.13
# Ubuntu: sudo apt install python3.13
# macOS: brew install python@3.13
# Windows: 从 python.org 下载
```

### Q2: 虚拟环境激活失败

**Linux/macOS**:
```bash
source venv/bin/activate
```

**Windows**:
```powershell
.\venv\Scripts\Activate.ps1

# 如果提示权限问题，执行:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q3: PyTorch 安装失败

**GPU 版本** (NVIDIA):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**CPU 版本**:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Q4: OpenCV 导入错误

```bash
# 卸载冲突的包
pip uninstall opencv-python opencv-contrib-python
# 重新安装 headless 版本
pip install opencv-python-headless
```

### Q5: 数据库连接失败

检查 MySQL 是否运行：
```bash
# 启动 MySQL
sudo systemctl start mysql

# 创建数据库
mysql -u root -p
CREATE DATABASE breast_ai_db CHARACTER SET utf8mb4;
```

---

## 验证安装

运行测试脚本：

```bash
# 检查核心包
python -c "
import fastapi
import torch
import numpy as np
import cv2
print('✓ 所有核心依赖安装成功')
print(f'  FastAPI: {fastapi.__version__}')
print(f'  PyTorch: {torch.__version__}')
print(f'  NumPy: {np.__version__}')
print(f'  OpenCV: {cv2.__version__}')
"

# 启动服务并访问 API 文档
# http://localhost:8005/docs
```

---

## 更新项目

```bash
# 拉取最新代码
git pull origin main

# 重新安装依赖
pip install -r requirements.txt --upgrade

# 重启服务
pkill -f uvicorn
python -m uvicorn app.main:app --reload
```

---

## 卸载

```bash
# 停用虚拟环境
deactivate

# 删除虚拟环境
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# 删除项目
cd ..
rm -rf breast-ai-system  # Linux/macOS
rmdir /s breast-ai-system  # Windows
```

---

## 获取更多帮助

- **文档**: https://github.com/jwxys/breast-ai-system/wiki
- **Issues**: https://github.com/jwxys/breast-ai-system/issues
- **讨论**: https://github.com/jwxys/breast-ai-system/discussions

**版本**: v3.1.0  
**更新日期**: 2026-06-03
