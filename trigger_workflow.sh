#!/bin/bash
# 定时触发 workflow 并保存格式化日志

# ========================
# 配置
# ========================
AGENTOS_HOST="${AGENTOS_HOST:-localhost}"
AGENTOS_PORT="${AGENTOS_PORT:-7777}"
WORKFLOW_ID="simple-newsletter-workflow"

USER_ID="asbeforekz@gmail.com"
INTERESTS="AI, quantum computing, space exploration"
SESSION_ID="scheduled_$(date +%s)"

# 日志目录和文件
LOG_DIR="/data/muskliu/mt/open_pulse/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/trigger_workflow_$(date +%F).log"

# ========================
# 健康检查
# ========================
echo "🔍 Checking AgentOS health..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$AGENTOS_HOST:$AGENTOS_PORT/health")

if [ "$STATUS" -ne 200 ]; then
    echo "❌ AgentOS is not running (HTTP $STATUS)"
    echo "   Please start it with: python agentos.py"
    exit 1
fi
echo "✅ AgentOS is running"
echo ""

# ========================
# 触发 Workflow（使用通知端点）
# ========================
echo "🚀 Triggering newsletter workflow..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "http://$AGENTOS_HOST:$AGENTOS_PORT/api/workflows/$WORKFLOW_ID/run-with-notification" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "message=Generate a newsletter about $INTERESTS" \
  --data-urlencode "user_id=$USER_ID" \
  --data-urlencode "session_id=$SESSION_ID")

# 分离响应体和状态码
HTTP_BODY=$(echo "$RESPONSE" | sed '$d')
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

# ========================
# 写入日志（格式化 JSON + 状态信息）
# ========================
{
echo "=== $(date "+%Y-%m-%d %H:%M:%S") ==="

# 格式化 JSON 输出
if command -v jq &> /dev/null; then
    echo "$HTTP_BODY" | jq '.'  # 使用 jq 格式化 JSON
else
    echo "$HTTP_BODY" | python3 -m json.tool  # 没有 jq 用 Python 格式化
fi

# 输出状态信息
if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 202 ]; then
    echo "✅ Workflow triggered successfully (HTTP $HTTP_CODE)"
    echo "📬 Notification will be sent to frontend when workflow completes"
    echo "   Open http://localhost:3000 to see the notification"
else
    echo "❌ Failed to trigger Workflow (HTTP $HTTP_CODE)"
fi

} >> "$LOG_FILE" 2>&1

# 同时输出到控制台
echo ""
echo "✅ Workflow triggered and logged to: $LOG_FILE"
echo "📬 Notification will appear in frontend when complete (~30-60s)"
echo "💡 Check backend logs for workflow progress"
