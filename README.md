# xuexitong-cli

超星学习通命令行工具：免浏览器挂机刷课、DeepSeek 辅助做题，支持普通/手势/定位/签到码签到。已原生适配 **Windows / macOS / Linux** 全系统。

---

## 跨平台一键运行（最简单）

无需先去查一堆复杂的子命令，根据你的电脑系统直接双击或执行启动脚本即可：

### 🪟 Windows 用户
1. 下载/解压本项目；
2. 双击打开 **`start.bat`** 脚本；
3. 脚本会自动检查 Python 环境与依赖，并弹出菜单选择是否一键自动登录 + 刷课做题。

### 🍎 macOS / 🐧 Linux 用户
打开终端进入目录，直接执行一键脚本：
```bash
chmod +x start.sh
./start.sh
```

---

## 基础环境要求

- Python 3.8 或更高版本
- 轻量网络依赖 `requests`

```bash
pip install requests
```

---

## 命令行用法速查 (CLI Reference)

如果你喜欢直接在终端中敲命令或通过脚本调度：

### 1. 全自动一键巡航（推荐）
自动检测登录（未登录自动弹出二维码并轮询等待） -> 自动拉取全部在修课程 -> 逐节挂视频 -> DeepSeek 自动做作业：

```bash
# Windows
python bin\auto_run.py

# macOS / Linux
./bin/auto_run.py
```
> 如需同时自动解答作业，运行前先配置环境变量：
> - Windows (CMD): `set DEEPSEEK_API_KEY=sk-your-key`
> - Windows (PowerShell): `$env:DEEPSEEK_API_KEY="sk-your-key"`
> - macOS / Linux: `export DEEPSEEK_API_KEY="sk-your-key"`

---

### 2. 账号与登录 (`auth`)

```bash
# 扫码登录（终端生成二维码并在系统浏览器自动打开，实时轮询状态）
./bin/xuexitong auth --poll

# 浏览器已登录的 Cookie 直接导入
./bin/xuexitong auth --cookie "UID=xxx; _d=xxx; vc3=xxx"

# 查看当前登录状态与用户信息
./bin/xuexitong auth --status

# 退出登录并清除本地凭据
./bin/xuexitong auth --logout
```

---

### 3. 课程与章节查询 (`course`)

```bash
# 列出已选课程列表（获取 course_id 和 clazz_id）
./bin/xuexitong course --list

# 查看某门课的章节结构与任务点
./bin/xuexitong course --chapters <COURSE_ID> --clazz-id <CLAZZ_ID>
```

---

### 4. 视频任务点原速挂机 (`play`)

严格按照物理时钟每 30 秒步进一次合规心跳，绝非违规秒刷：

```bash
# 正常原速挂机（例如 1800 秒的视频）
./bin/xuexitong play --clazz-id <班级ID> --job-id <任务点ID> --object-id <视频ID> --duration 1800

# 单次连通性发包测试（不进行持久挂机）
./bin/xuexitong play --clazz-id <班级ID> --job-id <任务点ID> --object-id <视频ID> --duration 300 --simulate
```

---

### 5. 章节测验与作业 AI 答题 (`quiz`)

```bash
./bin/xuexitong quiz --solve '{"questions":[{"id":1,"type":"单选题","question":"题目内容","options":[{"letter":"A","text":"选项1"},{"letter":"B","text":"选项2"}]}]}'
```

---

### 6. 班级全模式签到 (`sign`)

```bash
# 查看当前班级是否有正在进行的签到活动
./bin/xuexitong sign --list --course-id <COURSE_ID> --clazz-id <CLAZZ_ID>

# 普通 / 手势签到
./bin/xuexitong sign --active-id <ACTIVE_ID>

# 位置 / GPS 签到（可指定经纬度和地址名）
./bin/xuexitong sign --active-id <ACTIVE_ID> --type location --address "教学楼301" --lat 34.757975 --lng 113.665412

# 签到码签到（输入 4 位数字）
./bin/xuexitong sign --active-id <ACTIVE_ID> --type code --code 1234
```

---

### 7. JSON 模式（供脚本 / Agent 二次调用）

所有命令后均可加上 `--json` 获取标准结构化输出：

```bash
./bin/xuexitong auth --status --json
./bin/xuexitong course --list --json
```

## License

MIT
