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
# 触发 Workflow
# ========================
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "http://$AGENTOS_HOST:$AGENTOS_PORT/workflows/$WORKFLOW_ID/runs" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "message=Generate a newsletter about $INTERESTS" \
  --data-urlencode "user_id=$USER_ID" \
  --data-urlencode "session_id=$SESSION_ID" \
  --data-urlencode "stream=false")

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
    RUN_ID=$(echo "$HTTP_BODY" | jq -r '.run_id' 2>/dev/null)
    if [ "$RUN_ID" != "null" ] && [ -n "$RUN_ID" ]; then
        echo "📋 Run ID: $RUN_ID"
        echo "💡 Check status at: http://$AGENTOS_HOST:$AGENTOS_PORT/workflows/$WORKFLOW_ID/runs/$RUN_ID"
    fi
else
    echo "❌ Failed to trigger Workflow (HTTP $HTTP_CODE)"
fi

} >> "$LOG_FILE" 2>&1
