#!/bin/bash
set -e

echo "============================================"
echo "Breast AI System - systemd 服务安装"
echo "============================================"

BACKEND_SERVICE="/workspace/breast-ai-system/deploy/systemd/breast-ai-backend.service"
FRONTEND_SERVICE="/workspace/breast-ai-system/deploy/systemd/breast-ai-frontend.service"

# 复制服务文件到 systemd 目录
echo "正在安装后端服务..."
cp "$BACKEND_SERVICE" /etc/systemd/system/
systemctl daemon-reload
systemctl enable breast-ai-backend.service

echo "正在安装前端服务..."
cp "$FRONTEND_SERVICE" /etc/systemd/system/
systemctl daemon-reload
systemctl enable breast-ai-frontend.service

echo ""
echo "✅ 服务安装完成"
echo ""
echo "常用命令:"
echo "  systemctl start breast-ai-backend.service    # 启动后端"
echo "  systemctl stop breast-ai-backend.service     # 停止后端"
echo "  systemctl restart breast-ai-backend.service  # 重启后端"
echo "  systemctl status breast-ai-backend.service   # 查看状态"
echo ""
echo "  journalctl -u breast-ai-backend.service -f   # 查看日志"
echo ""
