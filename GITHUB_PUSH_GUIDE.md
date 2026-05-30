# 推送代码到 GitHub 指南

## GitHub 账号信息
- **用户名**: jwxys
- **仓库地址**: https://github.com/jwxys/breast-ai-system.git

---

## 方法一：使用 Personal Access Token（推荐）

### 第 1 步：创建 Personal Access Token

1. 访问：https://github.com/settings/tokens
2. 点击 **"Generate new token (classic)"**
3. 填写信息：
   - **Note**: `breast-ai-system-push`
   - **Expiration**: 选择 `90 days` 或 `No expiration`
4. 勾选权限：
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. 点击 **"Generate token"**
6. **重要**: 复制生成的 token（只会显示一次！）
   ```
   github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 第 2 步：使用 Token 推送

```bash
cd /workspace/breast-ai-system

# 使用 token 推送（将 YOUR_TOKEN 替换为实际 token）
git push -u origin master
# 当提示输入密码时，粘贴 token

# 或使用带 token 的 URL（不推荐，会显示在历史记录中）
git remote set-url origin https://jwxys:YOUR_TOKEN@github.com/jwxys/breast-ai-system.git
git push -u origin master
```

---

## 方法二：使用 SSH 密钥（更安全）

### 第 1 步：生成 SSH 密钥

```bash
# 生成新的 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"
# 连续按 3 次回车使用默认设置
```

### 第 2 步：添加 SSH 密钥到 GitHub

1. 查看公钥内容：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   复制输出的内容（以 `ssh-ed25519` 开头）

2. 访问：https://github.com/settings/keys
3. 点击 **"New SSH key"**
4. 填写：
   - **Title**: `breast-ai-system-key`
   - **Key**: 粘贴公钥内容
5. 点击 **"Add SSH key"**

### 第 3 步：切换到 SSH URL 并推送

```bash
cd /workspace/breast-ai-system

# 切换到 SSH URL
git remote set-url origin git@github.com:jwxys/breast-ai-system.git

# 测试连接
ssh -T git@github.com
# 应该看到：Hi jwxys! You've successfully authenticated

# 推送代码
git push -u origin master
```

---

## 方法三：使用 GitHub CLI（最简单）

### 第 1 步：安装 GitHub CLI

```bash
# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y

# 或直接下载
gh auth login
```

### 第 2 步：登录 GitHub

```bash
gh auth login
# 选择 GitHub.com
# 选择 HTTPS 或 SSH
# 按提示完成登录
```

### 第 3 步：推送代码

```bash
cd /workspace/breast-ai-system
git push -u origin master
```

---

## 推送成功后

### 在 GitHub 上查看代码

访问：https://github.com/jwxys/breast-ai-system

### 在 Windows 上克隆

```powershell
# 打开 PowerShell 或 Git Bash

# 创建目录
mkdir "F:\a_项目 a"
cd "F:\a_项目 a"

# 克隆仓库
git clone https://github.com/jwxys/breast-ai-system.git

# 或 SSH 方式
git clone git@github.com:jwxys/breast-ai-system.git
```

---

## 推荐：使用 Personal Access Token

**最快速度完成推送**：

1. 访问 https://github.com/settings/tokens
2. 创建 token（有效期 90 天）
3. 复制 token
4. 在终端执行：

```bash
cd /workspace/breast-ai-system
git push -u origin master
# Username: jwxys
# Password: [粘贴 token，不会显示]
```

---

## 需要帮助？

请从以下选项选择：

**A**: 我已创建 token，请帮我推送  
**B**: 我想使用 SSH 方式，请指导  
**C**: 我想使用 GitHub CLI  
**D**: 其他问题

---
