# Xuexitong CLI (学习通终端逆向与 AI 自动化工具)

<p align="center">
  <b>纯协议逆向 · 原速安全守护 · DeepSeek AI 答题推理 · 班级多模式签到 · AI Agent 友好</b>
</p>

---

## 📖 项目简介

这是一个基于**超星学习通网络协议逆向 + 现代终端 CLI + 接入 DeepSeek 大模型推理**的轻量级自动化工具。

彻底摆脱庞大臃肿的浏览器环境与容易失效的前端 DOM 依赖，内存占用从传统浏览器的几百 MB 降低到 **< 20MB**。专为 Linux 服务器后台常驻、无头环境挂机以及 AI Agent（如 Claude / Codex / 智能助手）通过命令行调度而设计。

> ⚠️ **声明**：本项目仅供计算机网络协议逆向、自动化测试及学术研究学习使用，请勿用于违反校纪校规或任何商业非法用途。

---

## 🌟 核心特性

- **脱离浏览器**：直接模拟超星移动端与 PC 端通讯协议，极省系统资源。
- **真物理时间心跳**：坚决摒弃暴力倍速和伪造发包，内部时钟严格按照真实物理时间步进上报，日志时序真实，确保账号安全。
- **Passport2 逆向扫码与 Cookie 快速导入**：
  - 终端一键生成最新 `getauthstatus/v2` 协议二维码或实时轮询。
  - 支持浏览器抓包 Cookie 一键粘贴登录，持久化至 `~/.xuexitong_session.json`。
- **DeepSeek AI 实时推理做题**：
  - 彻底抛弃传统付费题库与公众号卡密体系。
  - 自动对抗网页防复制乱码与特殊字符混淆，整卷打包调用大模型现场语义分析。
- **全类型班级签到**：
  - 覆盖普通签到、手势签到、定位签到（自定义经纬度/教室名）、签到码签到与二维码扫码签到。
- **AI Agent 原生友好**：
  - 全局命令支持 `--json` 输出，标准结构化数据，无缝作为 Function Calling / Tool 喂给智能体。

---

## 🛠️ 安装与准备

项目纯 Python 编写，仅依赖标准库和 `requests`：

```bash
git clone <your-repo-url>
cd xuexitong-cli

# 安装依赖
pip install requests
```

---

## 🚀 命令指南

可以直接通过可执行入口运行：`./bin/xuexitong <command> [options]`

### 1. 登录与身份管理 (`auth`)
```bash
# 检查当前登录状态
./bin/xuexitong auth --status

# 终端获取扫码二维码图片链接
./bin/xuexitong auth --qrcode

# 持续轮询等待手机学习通扫码确认
./bin/xuexitong auth --poll

# 通过浏览器复制的 Cookie 快速登录
./bin/xuexitong auth --cookie "UID=123456; _d=xxx; vc3=yyy"

# 退出登录并清除本地凭据
./bin/xuexitong auth --logout
```

### 2. 课程与章节查询 (`course`)
```bash
# 列出当前账号下所有在修课程
./bin/xuexitong course --list

# 查看指定课程的章节树与任务点结构
./bin/xuexitong course --chapters <COURSE_ID> --clazz-id <CLAZZ_ID>
```

### 3. 原速视频心跳守护 (`play`)
```bash
# 模拟单次心跳测试（测试通信连通性）
./bin/xuexitong play --clazz-id 12345 --job-id 67890 --object-id obj_xxx --duration 300 --simulate

# 原速守护挂机（内部时钟按 30s 步进安全上报）
./bin/xuexitong play --clazz-id 12345 --job-id 67890 --object-id obj_xxx --duration 1800
```

### 4. 章节测验与作业 AI 答题 (`quiz`)
```bash
# 设置 DeepSeek API Key
export DEEPSEEK_API_KEY="sk-xxxxxxxx"

# 输入题目 JSON 进行推理解答
./bin/xuexitong quiz --solve '{"questions":[{"id":1,"type":"单选题","question":"下列选项中属于清洁能源的是","options":[{"letter":"A","text":"煤炭"},{"letter":"B","text":"太阳能"}]}]}'
```

### 5. 课堂签到打卡 (`sign`)
```bash
# 查询当前班级是否有正在进行的签到活动
./bin/xuexitong sign --list --course-id <COURSE_ID> --clazz-id <CLAZZ_ID>

# 普通签到 / 手势签到
./bin/xuexitong sign --active-id <ACTIVE_ID>

# 位置/GPS 签到（可自定义经纬度与地址）
./bin/xuexitong sign --active-id <ACTIVE_ID> --type location --address "教学楼301" --lat 34.757975 --lng 113.665412

# 签到码签到
./bin/xuexitong sign --active-id <ACTIVE_ID> --type code --code 1234
```

### 6. 一键全自动托管管家
如果你希望全自动跑完全套流程，运行预置的 Agent 串联脚本：
```bash
export DEEPSEEK_API_KEY="sk-xxxxxxxx"
./bin/auto_run.py
```

---

## 🤖 供 AI Agent 消费（JSON 模式）

所有命令都可以加上 `--json` 选项，例如：
```bash
./bin/xuexitong auth --status --json
./bin/xuexitong course --list --json
```
返回严格 JSON 数据流，便于接入 LangChain、AutoGPT 或自定义 MCP Server。

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源。
