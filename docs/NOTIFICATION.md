# Newsletter 通知功能

## 功能说明

当使用 `trigger_workflow.sh` 脚本生成 Newsletter 时，前端会自动弹出通知卡片，显示生成的内容和封面图片。

## 使用方法

### 1. 启动服务

```bash
# 启动后端
python agentos.py

# 启动前端（新终端）
cd agent-ui
pnpm dev
```

### 2. 触发 Newsletter 生成

```bash
./trigger_workflow.sh
```

### 3. 查看通知

- 打开浏览器访问 http://localhost:3000
- 等待 30-60 秒
- 右下角会弹出通知卡片
- 点击 "View Full Newsletter" 查看完整内容
- 点击 "Dismiss" 关闭通知

## 定时任务配置

使用 crontab 设置定时生成：

```bash
crontab -e

# 每天早上 8 点生成
0 8 * * * /data/muskliu/mt/open_pulse/trigger_workflow.sh
```

## 技术实现

### 后端

- **通知端点**: `/api/workflows/{workflow_id}/run-with-notification`
- **SSE 流**: `/api/notifications/stream`
- **统计信息**: `/api/notifications/stats`

### 前端

- **SSE 连接**: `useNotificationStream` Hook
- **通知卡片**: `NewsletterNotificationCard` 组件
- **模态框**: `NewsletterModal` 组件

### 工作流程

1. `trigger_workflow.sh` 调用通知端点
2. 后端追踪 workflow 运行状态
3. Workflow 完成后提取封面图和内容
4. 通过 SSE 推送通知到前端
5. 前端显示通知卡片

## 故障排查

### 通知没有弹出

1. 检查后端是否运行：`curl http://localhost:7777/health`
2. 检查 SSE 连接：浏览器控制台应显示 "Notification stream connected"
3. 检查通知状态：`curl http://localhost:7777/api/notifications/stats`

### 图片不显示

1. 检查图片是否生成：`ls -lh static/images/`
2. 检查 Google Gemini API Key 是否配置
3. 查看浏览器控制台错误信息

## 日志

所有触发记录保存在：`logs/trigger_workflow_YYYY-MM-DD.log`

