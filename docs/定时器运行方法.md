📅 新闻简报调度器指南

本指南介绍了如何使用 Open Pulse 的灵活新闻简报调度器。

🎯 概览

调度器支持三种模式：
	1.	开发模式 - 用于测试的快速间隔（每 2 分钟一次）
	2.	生产模式 - 每天在指定时间运行（例如上午 8:00）
	3.	一次性模式 - 延时后运行一次（快速测试用）

🚀 快速开始

1. 先测试工作流

在使用调度器之前，先手动测试工作流：

# 运行所有测试
python test_workflow.py

# 运行特定测试
python test_workflow.py 1  # 基本执行
python test_workflow.py 2  # 流式执行
python test_workflow.py 3  # 后台执行
python test_workflow.py 4  # 多用户执行

2. 配置调度器

编辑 .env 文件：

# 开发模式（每 2 分钟运行一次）
SCHEDULER_MODE=development

# 生产模式（每天早上 8 点）
SCHEDULER_MODE=production
NEWSLETTER_GENERATION_HOUR=8
NEWSLETTER_GENERATION_MINUTE=0

# 一次性模式（2 分钟后运行）
SCHEDULER_MODE=once

3. 运行调度器

python scheduler.py

📖 详细用法

开发模式

非常适合测试！每 2 分钟运行一次。

# 在 .env 文件中
SCHEDULER_MODE=development

# 启动
python scheduler.py

输出示例：

🔧 在开发模式下启动调度器
   间隔: 每 2 分钟
   首次运行: 2025-10-02 14:32:00
✅ 调度器已在开发模式启动

生产模式

适合真实部署。每天在指定时间运行。

# 在 .env 文件中
SCHEDULER_MODE=production
NEWSLETTER_GENERATION_HOUR=8
NEWSLETTER_GENERATION_MINUTE=0

# 启动
python scheduler.py

输出示例：

🚀 在生产模式下启动调度器
   时间表: 每天 08:00
✅ 调度器已在生产模式启动

一次性模式

延时后运行一次。非常适合快速测试。

# 在 .env 文件中
SCHEDULER_MODE=once

# 启动
python scheduler.py

输出示例：

⏰ 安排一次性执行
   运行时间: 2025-10-02 14:32:00
   (2 分钟后)
✅ 一次性任务已调度

🔧 高级用法

程序化控制

你也可以通过代码控制调度器：

from scheduler import NewsletterScheduler

scheduler = NewsletterScheduler()

# 开发模式，自定义间隔
scheduler.start_development_mode(interval_minutes=5)

# 生产模式，自定义时间
scheduler.start_production_mode(hour=9, minute=30)

# 一次性模式，自定义延时
scheduler.start_once_after_delay(delay_minutes=1)

# 修改现有任务
scheduler.modify_schedule(interval_minutes=10)

# 获取状态
status = scheduler.get_status()
print(status)

# 停止调度器
scheduler.stop()

手动触发

为某个用户生成简报：

import asyncio
from scheduler import NewsletterScheduler

scheduler = NewsletterScheduler()

# 为单用户生成简报
result = asyncio.run(
    scheduler.generate_newsletter_for_user(
        user_id="user_123",
        interests="人工智能与机器学习"
    )
)

print(result)

📊 监控

检查调度器状态

from scheduler import NewsletterScheduler

scheduler = NewsletterScheduler()
scheduler.start_development_mode()

# 获取状态
status = scheduler.get_status()
print(f"运行中: {status['running']}")
print(f"任务: {status['jobs']}")
print(f"运行中的工作流: {status['running_workflows']}")

查看日志

调度器会打印详细日志：

📰 每日新闻简报生成开始
   时间: 2025-10-02T14:30:00

🚀 开始为用户 test_user_1 生成简报
✅ 已开始生成简报：test_user_1
   运行 ID: abc123...
   ⏳ 等待完成... (5s)
   ⏳ 等待完成... (10s)
   
✅ 简报生成完成：test_user_1

✅ 每日新闻简报生成完成
   总用户数: 1
   成功: 1
   失败: 0

🎛️ 配置选项

环境变量

变量	描述	默认值	示例
SCHEDULER_MODE	调度器模式	development	production
NEWSLETTER_GENERATION_HOUR	每日生成小时	8	9
NEWSLETTER_GENERATION_MINUTE	每日生成分钟	0	30

调度器参数

# 开发模式
scheduler.start_development_mode(
    interval_minutes=2  # 每 N 分钟运行一次
)

# 生产模式
scheduler.start_production_mode(
    hour=8,    # 小时 (0-23)
    minute=0   # 分钟 (0-59)
)

# 一次性模式
scheduler.start_once_after_delay(
    delay_minutes=2  # 延迟分钟数
)

🐛 故障排查

调度器不运行

问题: 调度器启动但不执行任务
解决办法:
	1.	检查调度器状态：status = scheduler.get_status()
	2.	确认下次运行时间在未来
	3.	检查日志错误

工作流超时

问题: 新闻简报生成时间过长
解决办法:
	1.	增加 scheduler.py 中的 max_wait（默认 300 秒）
	2.	检查 API 速率限制
	3.	减少研究范围

多次执行

问题: 任务意外运行多次
解决办法:
	1.	添加任务时使用 replace_existing=True
	2.	检查是否有重复任务 ID
	3.	停止并重启调度器

📝 最佳实践

开发环境
	1.	使用短间隔（1-2 分钟）快速迭代
	2.	先用单用户测试，再扩展
	3.	密切监控日志，发现错误
	4.	先跑 test_workflow.py 再跑调度器

生产环境
	1.	选择低峰时间（如凌晨 2-4 点）避免速率限制
	2.	对用户间执行加限流
	3.	建立监控与告警
	4.	用后台执行 避免阻塞
	5.	结果存数据库 便于后续查询

测试环境
	1.	用一次性模式 快速测试
	2.	测试不同用户画像
	3.	验证简报质量 再自动化
	4.	检查多用户时的内存使用

🔗 与 AgentOS 集成

调度器可以集成到 AgentOS，通过 API 控制：

# 在 agentos.py
from scheduler import NewsletterScheduler

scheduler = NewsletterScheduler()

@app.on_event("startup")
async def startup_event():
    # AgentOS 启动时启动调度器
    mode = os.getenv("SCHEDULER_MODE", "development")
    if mode == "development":
        scheduler.start_development_mode()
    else:
        scheduler.start_production_mode()

@app.on_event("shutdown")
async def shutdown_event():
    # AgentOS 关闭时停止调度器
    scheduler.stop()

# 添加手动触发的 API 接口
@app.post("/generate-newsletter")
async def generate_newsletter(user_id: str):
    result = await scheduler.generate_newsletter_for_user(user_id)
    return result

📚 下一步
	1.	✅ 用 test_workflow.py 测试工作流
	2.	✅ 在 .env 配置调度器
	3.	✅ 以开发模式运行调度器
	4.	✅ 验证新闻简报质量
	5.	✅ 切换到生产模式
	6.	🚀 部署并监控！

🆘 需要帮助？
	•	检查日志获取详细错误信息
	•	在 AgentOS UI 中查看工作流执行情况
	•	用 test_workflow.py 测试单个组件
	•	根据需要调整时间和间隔

祝调度愉快！🎉

、