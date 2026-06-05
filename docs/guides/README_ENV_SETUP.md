# 环境配置快速参考

## 🚀 5 分钟快速开始

```bash
# 1. 克隆项目
git clone https://github.com/jwxys/breast-ai-system.git
cd breast-ai-system

# 2. 设置环境 (选择对应系统)
./setup_env.sh           # Linux/macOS
.\setup_env.ps1          # Windows

# 3. 配置环境变量
cp .env.example .env

# 4. 启动服务
./quickstart.sh          # Linux/macOS
.\venv\Scripts\Activate.ps1 && python -m uvicorn app.main:app --reload  # Windows
```

访问：http://localhost:8005

---

## 📋 命令速查表

| 操作 | 命令 |
|------|------|
| 创建虚拟环境 | `./setup_env.sh` |
| 激活虚拟环境 | `source venv/bin/activate` |
| 退出虚拟环境 | `deactivate` |
| 安装依赖 | `pip install -r requirements.txt` |
| 启动服务 | `python -m uvicorn app.main:app --reload` |
| 查看帮助 | `http://localhost:8005/docs` |

---

## ⚙️ 环境变量说明

```ini
# 必需配置
DATABASE_URL=mysql+asyncmy://user:pass@localhost:3306/db
SECRET_KEY=your-secret-key

# 可选配置 (AI 功能)
KIMI_API_KEY=sk-...
TONGYI_API_KEY=sk-...
```

---

## 🔧 常见问题

**Q: Python 版本不匹配？**  
A: 需要 Python 3.13+, 检查：`python --version`

**Q: 虚拟环境激活失败？**  
A: Windows 执行 `Set-ExecutionPolicy RemoteSigned`

**Q: 端口被占用？**  
A: 修改端口：`--port 8006`

---

**完整文档**: [INSTALL.md](./INSTALL.md)
