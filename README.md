# xuexitong-cli

一个用 Python 写的超星学习通命令行工具。

直接调移动端和网页端接口，不用开浏览器，内存占用不到 20MB。适合扔在 Linux 服务器、树莓派或者后台跑，也可以通过 `--json` 参数给自动化脚本或 AI Agent 调用。

## 主要功能

- **扫码/Cookie 登录**：调 passport2 接口生成二维码终端轮询，或者直接塞进浏览器 Cookie，自动存到 `~/.xuexitong_session.json`。
- **原速刷课**：逆向视频心跳包算法（MD5 + 盐值），严格按真实时长每 30 秒上报一次，不搞暴力倍速和伪造秒刷，避免被后台离线审计清零。
- **AI 做题**：不接任何付费题库和公众号卡密。抓取测验题目直接发给 DeepSeek（用自己的 API Key），支持单选、多选、判断题。
- **签到**：支持普通签到、手势、定位签到（自定义经纬度）、签到码、二维码签到。
- **一键全自动**：提供了一个脚本把“查课 -> 刷视频 -> 答题 -> 提交 -> 下一节”串起来跑。

## 安装

只要 Python 3.8+ 和 requests：

```bash
git clone https://github.com/cuic19053-hue/xuexitong-cli.git
cd xuexitong-cli
pip install requests
```

## 常用命令

直接运行 `./bin/xuexitong`，或者软链接到你的 `PATH`。

### 1. 登录

```bash
# 扫码登录（终端轮询，手机打开学习通扫码）
./bin/xuexitong auth --poll

# 或者直接用浏览器抓出来的 Cookie 登录
./bin/xuexitong auth --cookie "UID=xxx; _d=xxx; vc3=xxx"

# 检查当前登录状态
./bin/xuexitong auth --status

# 退出登录
./bin/xuexitong auth --logout
```

### 2. 查课与章节

```bash
# 列出在修课程
./bin/xuexitong course --list

# 查指定课程的章节和任务点
./bin/xuexitong course --chapters <COURSE_ID> --clazz-id <CLAZZ_ID>
```

### 3. 刷视频

```bash
# 单次发包测试（测试连通性）
./bin/xuexitong play --clazz-id 12345 --job-id 67890 --object-id obj_xxx --duration 300 --simulate

# 正常挂机（按视频长度原速跑，每 30 秒发一次心跳）
./bin/xuexitong play --clazz-id 12345 --job-id 67890 --object-id obj_xxx --duration 1800
```

### 4. 答测验

配置好 DeepSeek API Key（没有题库，现场用大模型做题）：

```bash
export DEEPSEEK_API_KEY="sk-your-key"

# 传入考卷 JSON 直接解题
./bin/xuexitong quiz --solve '{"questions":[{"id":1,"type":"单选题","question":"下列选项属于清洁能源的是","options":[{"letter":"A","text":"煤炭"},{"letter":"B","text":"太阳能"}]}]}'
```

### 5. 课堂签到

```bash
# 查看当前班级是否有正在进行的签到
./bin/xuexitong sign --list --course-id <COURSE_ID> --clazz-id <CLAZZ_ID>

# 普通 / 手势签到
./bin/xuexitong sign --active-id <ACTIVE_ID>

# 定位签到（随便填经纬度和地址名）
./bin/xuexitong sign --active-id <ACTIVE_ID> --type location --address "教学楼301" --lat 34.757975 --lng 113.665412

# 签到码签到
./bin/xuexitong sign --active-id <ACTIVE_ID> --type code --code 1234
```

### 6. 一键自动跑

全自动跑完选课、看视频、写作业：

```bash
export DEEPSEEK_API_KEY="sk-your-key"
./bin/auto_run.py
```

### 7. 给脚本 / Agent 调用

所有命令加 `--json` 都会输出纯 JSON：

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

## 免责声明

代码仅供协议分析和学习交流，别拿去搞破坏或商用。跑脚本引起的任何后果自负。

## License

MIT
