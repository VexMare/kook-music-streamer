# kook-music-streamer 使用说明 & 搭建说明（纯小白版）

---

## 一、项目简介

kook-music-streamer 是一个为 KOOK（开黑啦）语音频道打造的音乐点歌机器人，支持网易云音乐单曲和歌单一键推流。你可以通过 KOOK 聊天指令让机器人自动播放你想听的歌。

---

## 二、环境准备

### 1. 安装 Python

- 打开[Python 官网](https://www.python.org/downloads/)，下载并安装 Python 3.8 或更高版本。
- 安装时**务必勾选“Add Python to PATH”**，否则后续命令行无法识别 python。

### 2. 安装依赖包

- 按下 `Win + R`，输入 `cmd`，回车，打开命令提示符。
- 进入你的项目文件夹（假设在 D:\GitHub_Test\kook-music-streamer）：
  ```bash
  cd /d D:\GitHub_Test\kook-music-streamer
  ```
- 安装依赖（复制下面命令到命令行回车）：
  ```bash
  pip install aiohttp khl.py flask
  ```

### 3. 安装 ffmpeg

- 访问 [ffmpeg 官网](https://ffmpeg.org/download.html) 下载 Windows 版本。
- 解压后，记住 `ffmpeg.exe` 的路径（如 `F:/ffmpeg/bin/ffmpeg.exe`）。
- **建议将 ffmpeg.exe 所在目录添加到系统环境变量**，不会也没关系，后面可以在配置文件里写死路径。

---

## 三、配置机器人

### 1. 获取 KOOK 机器人 Token

- 登录 KOOK 官网，创建你的机器人，获取机器人的 Token。
- 记下你的服务器ID（guild_id）和语音频道ID（voice_channel_id），可在 KOOK 频道右键复制。

### 2. 配置 config.py

- 打开项目根目录下的 `config.py` 文件，填入你的 ffmpeg 路径和机器人 token，例如：

  ```python
  ffmpeg_path = "F:/ffmpeg/bin/ffmpeg.exe"  # 你的ffmpeg路径
  bot_token = "你的KOOK机器人token"
  ```

---

## 四、启动机器人

- 在命令行输入：
  ```bash
  python kookvoice_bot.py
  ```
- 看到类似“KOOK 机器人启动中...”字样，说明启动成功。

---

## 五、KOOK 频道内使用指令

1. **让机器人进入语音频道**
   ```
   /join
   ```
   机器人会自动加入你当前所在的语音频道。

2. **点歌（单曲/直链）**
   ```
   /播放 歌名
   ```
   或
   ```
   /播放 歌曲直链
   ```

3. **批量点歌（网易云歌单）**
   ```
   /歌单 歌单链接
   ```
   例如：
   ```
   /歌单 https://music.163.com/playlist?id=947835566
   ```
   机器人会自动获取歌单所有歌曲并依次播放。

4. **跳过当前歌曲**
   ```
   /跳过
   ```

5. **停止播放**
   ```
   /停止
   ```

6. **查看播放队列**
   ```
   /列表
   ```

7. **跳转到指定秒数**
   ```
   /跳转 60
   ```
   跳到第60秒。

---

## 六、常见问题

- **命令行提示 python 不是内部命令？**  
  说明 Python 没装好或没加到环境变量，重装并勾选“Add Python to PATH”。

- **ffmpeg 报错或找不到？**  
  检查 config.py 里的 ffmpeg_path 是否写对，或将 ffmpeg.exe 所在目录加到系统环境变量。

- **机器人没反应？**  
  检查 bot_token 是否正确，机器人是否已加入服务器，是否有语音频道权限。

---

## 七、进阶用法

- 支持批量播放网易云歌单，支持自定义开发。
- 所有配置集中在 config.py，便于统一管理。

---

如有更多问题，欢迎在 KOOK 群或 GitHub 提问！

---

**祝你使用愉快，点歌无忧！**
