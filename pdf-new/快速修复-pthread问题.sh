#!/bin/bash
# 快速修复 pthread_create 权限问题

echo "========================================"
echo "快速修复 - OpenBLAS pthread 权限问题"
echo "========================================"
echo ""

echo "问题: pthread_create failed: Operation not permitted"
echo "原因: 统信系统Docker安全策略限制"
echo "解决: 添加 --security-opt seccomp=unconfined"
echo ""

echo "[1/3] 停止当前容器..."
sudo docker stop pdf-editor
echo "[✓] 已停止"
echo ""

echo "[2/3] 删除当前容器..."
sudo docker rm pdf-editor
echo "[✓] 已删除"
echo ""

echo "[3/3] 使用修复的安全策略重新创建容器..."
echo ""
echo "添加的修复:"
echo "  • --security-opt seccomp=unconfined  (放宽系统调用限制)"
echo "  • -e OPENBLAS_NUM_THREADS=1          (限制OpenBLAS线程数)"
echo ""

sudo docker run -d \
  --name pdf-editor \
  -p 5000:5000 \
  -v ~/pdf-editor/processed:/app/processed \
  -e TZ=Asia/Shanghai \
  -e OPENBLAS_NUM_THREADS=1 \
  --security-opt seccomp=unconfined \
  --restart unless-stopped \
  pdf-editor:arm64

if [ $? -eq 0 ]; then
    echo "[✓] 容器已重新创建"
    echo ""
    
    echo "等待应用启动（30秒）..."
    sleep 30
    
    echo ""
    echo "========================================"
    echo "修复完成！"
    echo "========================================"
    echo ""
    
    # 检查日志
    echo "检查应用状态..."
    if sudo docker logs pdf-editor 2>&1 | grep -q "PDF编辑工具"; then
        echo "[✓] 应用已成功启动！"
        echo ""
        echo "🎉 问题已解决！"
        echo ""
        echo "访问地址: http://localhost:5000"
        echo ""
        
        # 测试连接
        if curl -s http://localhost:5000 > /dev/null 2>&1; then
            echo "[✓] 连接测试成功"
        else
            echo "[提示] 如无法访问，请再等待10-20秒"
        fi
    else
        echo "[注意] 应用可能还在启动..."
        echo ""
        echo "查看实时日志:"
        echo "  sudo docker logs -f pdf-editor"
        echo ""
        echo "如果看到 'PDF编辑工具 v1.4 已启动'，说明成功了"
    fi
    
    echo ""
    echo "完整日志（最后20行）:"
    echo "----------------------------------------"
    sudo docker logs --tail 20 pdf-editor
    echo "----------------------------------------"
    
else
    echo "[✗] 容器创建失败"
    echo ""
    echo "请查看错误信息并重试"
    exit 1
fi

echo ""
echo "========================================"
echo "提示"
echo "========================================"
echo ""
echo "• 这个修复已包含开机自启配置"
echo "• 系统重启后容器会自动运行"
echo "• 数据保存在 ~/pdf-editor/processed"
echo ""

