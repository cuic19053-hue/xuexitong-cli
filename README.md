# Xuexitong CLI (学习通终端逆向与 AI 自动化工具)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/AI%20Model-DeepSeek-purple.svg" alt="DeepSeek Supported">
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg" alt="Platform">
</p>

<p align="center">
  <b>纯协议逆向 · 极低资源消耗 · 真物理时钟心跳 · DeepSeek 现场解题 · 全类型签到 · AI Agent 友好</b>
</p>

---

## 📖 项目简介

`xuexitong-cli` 是一个针对超星学习通网络协议进行逆向封装的现代命令行终端工具。

项目彻底摒弃了传统方案对庞大浏览器（Chrome/Edge）、油猴扩展（Tampermonkey）以及脆弱 DOM 结构的依赖，将内存占用从几百兆大幅压降至 **< 20MB**。它既适合在无桌面环境的 Linux 服务器/容器中后台静默挂机，也通过全量 `--json` 接口为 **AI Agent（Claude / Codex / AutoGPT / 个人助理）** 提供了开箱即用的自动化工具调用底座。

> ⚠️ **免责声明**：本项目仅供计算机网络协议逆向、API 自动化测试与大模型工具集成之学术交流使用。严禁用于非法代刷、破坏系统公平性或商业牟利行为。使用者需自行遵守平台用户协议与相关法律法规。

---

## ✨ 核心特性

- 🚀 **脱离浏览器，轻量高效**：直接组装并校验超星 HTTP/HTTPS 业务协议，零 DOM 渲染，零内存负担。
- 🛡️ **真物理时钟心跳守护**：坚决不搞暴力倍速与违规秒刷，内部时钟严格按照视频实际时长按 30 秒步进平滑上报，保证服务器端时序日志完整合规。
- 🔑 **Passport2 扫码与凭据持久化**：
  - 逆向对接最新的 `passport2.chaoxing.com/getauthstatus/v2` 二维码轮询协议，终端直接生成二维码。
  - 支持浏览器一键提取 Cookie 注入，凭据自动安全持久化至本地 `~/.xuexitong_session.json`。
- 🧠 **DeepSeek AI 实时现场解题**：
  - 彻底抛弃第三方灰产题库与公众号卡密充值体系。
  - 自动对抗学习通防复制乱码与混淆字符，考卷结构化打包直连 DeepSeek 大模型现场语义推理，支持单选、多选、判断题。
- 📍 **全类型班级签到打卡**：
  - 覆盖普通签到、手势签到、定位/GPS 签到（可指定经纬度与教学楼名称）、签到码签到与二维码扫码签到。
- 🤖 **AI Agent 规范接口**：
  - 每一个子命令均支持 `--json` 输出标准 JSON 数据，可直接作为 Function Calling / MCP (Model Context Protocol) 供给大模型自主决策调用。

---

## 📦 项目结构

```
xuexitong-cli/
├── bin/
│   ├── xuexitong                  # 主 CLI 可执行入口
│   └── auto_run.py                # 全自动巡航领航脚本 (Agent 调度闭环)
├── xuexitong_cli/
│   ├── crypto.py                  # 逆向核心：学习通多媒体心跳 enc 签名算法 (MD5+盐值计算)
│   ├── session.py                 # 会话凭据持久化与有效性校验
│   ├── auth.py                    # Passport2 扫码登录与鉴权协议
│   ├── api.py                     # 核心业务接口：课程列表、章节树、视频心跳上报
│   ├── ai_solver.py               # DeepSeek 大模型现场解题器
│   ├── sign.py                    # 班级全类型签到引擎 (定位/码签/手势)
│   ├── upload.py                  # 超星云盘与大作业附件上传引擎
│   └── cli.py                     # 终端交互参数解析与分发
├── tests/
│   ├── test_cli.py                # 核心加密与 Session 测试
│   └── test_sign.py               # 签到模块单元测试
├── setup.py                       # Python 模块打包定义
├── LICENSE                        # MIT 开源协议
└── README.md                      # 项目说明文档
```

---

## 🛠️ 安装说明

项目纯 Python 打造，无需复杂系统依赖：

```bash
git clone https://github.com/cuic19053-hue/xuexitong-cli.git
cd xuexitong-cli

# 安装轻量 HTTP 依赖
pip install requests
```

---

## 💻 使用指南

可以直接使用可执行文件 `./bin/xuexitong`，也可以将其软链接至系统 `PATH`。

### 1. 登录认证 (`auth`)

```bash
# 检查当前登录状态
./bin/xuexitong auth --status

# 终端获取扫码二维码图片链接
./bin/xuexitong auth --qrcode

# 持续轮询等待手机学习通扫码确认 (推荐)
./bin/xuexitong auth --poll

# 或者直接导入已有的浏览器 Cookie 字符串
./bin/xuexitong auth --cookie "UID=123456; _d=xxx; vc3=yyy"

# 退出登录并清除本地凭据
./bin/xuexitong auth --logout
```

### 2. 课程与章节查询 (`course`)

```bash
# 列出账号下所有正在修读的课程
./bin/xuexitong course --list

# 查看指定课程的全部章节结构与任务点
./bin/xuexitong course --chapters <COURSE_ID> --clazz-id <CLAZZ_ID>
```

### 3. 视频心跳原速守护 (`play`)

```bash
# 单次模拟心跳发包测试 (测试网络连通性)
./bin/xuexitong play --clazz-id 12345 --job-id 67890 --object-id obj_xxx --duration 300 --simulate

# 正常后台原速守护挂机 (严格物理时钟按 30 秒步进上报)
./bin/xuexitong play --clazz-id 12345 --job-id 67890 --object-id obj_xxx --duration 1800
```

### 4. 章节测验与作业 AI 答题 (`quiz`)

```bash
# 配置你的 DeepSeek API Key
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"

# 传入考卷 JSON 题目，自动推理解答
./bin/xuexitong quiz --solve '{"questions":[{"id":1,"type":"单选题","question":"下列选项中属于清洁能源的是","options":[{"letter":"A","text":"煤炭"},{"letter":"B","text":"太阳能"}]}]}'
```

### 5. 班级全模式签到打卡 (`sign`)

```bash
# 查询当前班级是否有正在进行的签到活动
./bin/xuexitong sign --list --course-id <COURSE_ID> --clazz-id <CLAZZ_ID>

# 普通签到 / 手势签到
./bin/xuexitong sign --active-id <ACTIVE_ID>

# 定位 / GPS 签到 (可自定义经纬度与教室名称)
./bin/xuexitong sign --active-id <ACTIVE_ID> --type location --address "1号教学楼302" --lat 34.757975 --lng 113.665412

# 签到码签到 (如老师口头告知的 4 位数)
./bin/xuexitong sign --active-id <ACTIVE_ID> --type code --code 1234
```

### 6. 一键全自动无人值守巡航 (`auto_run`)

如果希望一条命令搞定全套流程，直接运行巡航管家：
```bash
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
./bin/auto_run.py
```
> **流程闭环**：校验登录 ➔ 智能选课 ➔ 拉取小节 ➔ 原速心跳视频 ➔ 识别测验 ➔ DeepSeek 推理 ➔ 自动提交 ➔ 推进下一节。

---

## 🤖 供 AI Agent 消费（JSON 模式）

所有命令后均可追加 `--json` 参数，输出纯净的结构化数据，供 AI 智能体直接消费：

```bash
$ ./bin/xuexitong auth --status --json
{
  "logged_in": true,
  "user_info": {
    "name": "张三",
    "uid": "12345678"
  },
  "cookies_present": true
}
```

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 协议开源。
