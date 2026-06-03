# 前端开发说明

## 快速开始

```bash
# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev

# 3. 访问 http://localhost:3000
```

## 开发命令

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 生产构建 |
| `npm run preview` | 预览生产构建 |
| `npm run lint` | 代码检查 |

## 项目结构

```
src/
├── api/          # API 调用
├── components/   # UI 组件
├── pages/        # 页面组件
├── hooks/        # 自定义 Hooks
├── utils/        # 工具函数
├── types/        # TypeScript 类型
├── styles/       # 样式文件
└── main.tsx      # 入口文件
```

## 技术栈

- React 18
- TypeScript
- Ant Design 5
- Vite 4
- React Router 6
- React Query

## 注意事项

1. **本地开发不需要 Docker**，只需要 Node.js
2. 后端 API 通过 Vite 代理转发
3. 使用淘宝镜像加速 npm 安装

## 故障排查

1. **删除 node_modules 重装**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **清除缓存**:
   ```bash
   npm cache clean --force
   ```

3. **重启服务器**:
   按 Ctrl+C 停止，然后重新 `npm run dev`
