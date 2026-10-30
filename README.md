# xuexitong-cli

超星学习通命令行工具：免浏览器挂机刷课、DeepSeek 辅助做题，支持普通/手势/定位/签到码签到。

## 安装

```bash
git clone https://github.com/cuic19053-hue/xuexitong-cli.git
cd xuexitong-cli
pip install requests
```

## 功能与用法速查

直接执行 `./bin/xuexitong` 使用各子命令，或运行 `./bin/auto_run.py` 进行全自动托管。

---

### 1. 刷课核心命令

#### 方式 A：全自动刷课（推荐）
自动扫描在修课程、列出章节、逐节按真实时钟挂完视频：

```bash
# 仅自动刷视频
./bin/auto_run.py

# 自动刷视频 + 顺便自动写作业做题（需配置 DeepSeek Key）
export DEEPSEEK_API_KEY="sk-your-key"
./bin/auto_run.py
```

#### 方式 B：手动刷指定视频任务点
按实际视频时长每 30 秒上报一次合规心跳：

```bash
# 正常挂机播放（例如总时长 1800 秒的视频）
./bin/xuexitong play --clazz-id <班级ID> --job-id <任务点ID> --object-id <视频ID> --duration 1800

# 单次发包测试（测试连通性，不实际挂机）
./bin/xuexitong play --clazz-id <班级ID> --job-id <任务点ID> --object-id <视频ID> --duration 300 --simulate
```

---

### 2. 登录与账号

```bash
# 扫码登录（终端显示二维码链接并轮询，手机打开学习通扫码确认）
./bin/xuexitong auth --poll

# 用浏览器已有 Cookie 登录
./bin/xuexitong auth --cookie "UID=xxx; _d=xxx; vc3=xxx"

# 查看当前登录状态与用户信息
./bin/xuexitong auth --status

# 退出登录并清除本地 Session
./bin/xuexitong auth --logout
```

---

### 3. 查课程与章节

```bash
# 列出已选课程（获取 course_id 和 clazz_id）
./bin/xuexitong course --list

# 查看某门课的章节目录与任务点
./bin/xuexitong course --chapters <COURSE_ID> --clazz-id <CLAZZ_ID>
```

---

### 4. 章节测验与作业答题

调用 DeepSeek API 做题（支持单选、多选、判断题，自动对抗乱码混淆）：

```bash
export DEEPSEEK_API_KEY="sk-your-key"

./bin/xuexitong quiz --solve '{"questions":[{"id":1,"type":"单选题","question":"题目内容","options":[{"letter":"A","text":"选项1"},{"letter":"B","text":"选项2"}]}]}'
```

---

### 5. 课堂签到

```bash
# 查看当前班级是否有正在进行的签到活动
./bin/xuexitong sign --list --course-id <COURSE_ID> --clazz-id <CLAZZ_ID>

# 普通 / 手势签到
./bin/xuexitong sign --active-id <ACTIVE_ID>

# 位置签到（支持自定义地址和经纬度）
./bin/xuexitong sign --active-id <ACTIVE_ID> --type location --address "教学楼301" --lat 34.757975 --lng 113.665412

# 签到码签到（填 4 位数字）
./bin/xuexitong sign --active-id <ACTIVE_ID> --type code --code 1234
```

---

### 6. JSON 模式（供脚本 / Agent 调用）

所有命令均支持追加 `--json` 参数，返回结构化 JSON：

```bash
./bin/xuexitong auth --status --json
./bin/xuexitong course --list --json
```

## License

MIT
