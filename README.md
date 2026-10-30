# xuexitong-cli

超星学习通命令行工具。

## 安装

```bash
git clone https://github.com/cuic19053-hue/xuexitong-cli.git
cd xuexitong-cli
pip install requests
```

## 功能与用法

直接执行 `./bin/xuexitong` 使用各子命令。

### 1. 登录与账号

```bash
# 扫码登录（终端显示二维码链接并轮询，手机打开学习通扫码）
./bin/xuexitong auth --poll

# 用浏览器已有 Cookie 登录
./bin/xuexitong auth --cookie "UID=xxx; _d=xxx; vc3=xxx"

# 查看当前登录状态
./bin/xuexitong auth --status

# 退出登录
./bin/xuexitong auth --logout
```

### 2. 查课程与章节

```bash
# 列出已选课程（输出 course_id 和 clazz_id）
./bin/xuexitong course --list

# 查看某门课的章节目录
./bin/xuexitong course --chapters <COURSE_ID> --clazz-id <CLAZZ_ID>
```

### 3. 刷视频

按实际视频时长每 30 秒上报一次心跳：

```bash
# 正常挂机播放
./bin/xuexitong play --clazz-id <CLAZZ_ID> --job-id <JOB_ID> --object-id <OBJECT_ID> --duration 1800

# 单次发包测试（测试连通性，不挂机）
./bin/xuexitong play --clazz-id <CLAZZ_ID> --job-id <JOB_ID> --object-id <OBJECT_ID> --duration 300 --simulate
```

### 4. 章节测验答题

调用 DeepSeek API 做题（单选、多选、判断题）：

```bash
export DEEPSEEK_API_KEY="sk-your-key"

./bin/xuexitong quiz --solve '{"questions":[{"id":1,"type":"单选题","question":"题目内容","options":[{"letter":"A","text":"选项1"},{"letter":"B","text":"选项2"}]}]}'
```

### 5. 课堂签到

```bash
# 查看当前班级是否有正在进行的签到
./bin/xuexitong sign --list --course-id <COURSE_ID> --clazz-id <CLAZZ_ID>

# 普通 / 手势签到
./bin/xuexitong sign --active-id <ACTIVE_ID>

# 位置签到（支持自定义地址和经纬度）
./bin/xuexitong sign --active-id <ACTIVE_ID> --type location --address "教学楼301" --lat 34.757975 --lng 113.665412

# 签到码签到
./bin/xuexitong sign --active-id <ACTIVE_ID> --type code --code 1234
```

### 6. 一键自动跑

自动按顺序执行：查课 -> 看视频 -> 做作业 -> 提交 -> 下一节。

```bash
export DEEPSEEK_API_KEY="sk-your-key"
./bin/auto_run.py
```

### 7. JSON 模式

所有命令均支持追加 `--json` 参数，返回结构化 JSON，方便脚本或 Agent 二次处理：

```bash
./bin/xuexitong auth --status --json
./bin/xuexitong course --list --json
```

## License

MIT
