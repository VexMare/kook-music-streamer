<p align="center">
  <a href="https://github.com/NightmaresNightmares/kook-music-streamer" target="_blank"><img src="https://img.shields.io/badge/GitHub-开源项目-black?logo=github" alt="GitHub"></a>
  &nbsp;
  <a href="https://www.douyin.com/user/MS4wLjABAAAADKa8egW-VGLmOg0sqjN-9Vf8wFZRfJwPpzVerdVKzlQ4WK_NvSLjSj3tzdUXfq-k?from_tab_name=main" target="_blank"><img src="https://img.shields.io/badge/抖音-短视频平台-ff69b4?logo=tiktok" alt="抖音"></a>
  &nbsp;
  <a href="https://space.bilibili.com/365374856" target="_blank"><img src="https://img.shields.io/badge/哔哩哔哩-Bilibili-00A1D6?logo=bilibili" alt="Bilibili"></a>
</p>

<p align="center">
  <a href="https://github.com/NightmaresNightmares/kook-music-streamer" target="_blank">GitHub 开源地址</a> |
  <a href="https://www.douyin.com/user/MS4wLjABAAAADKa8egW-VGLmOg0sqjN-9Vf8wFZRfJwPpzVerdVKzlQ4WK_NvSLjSj3tzdUXfq-k?from_tab_name=main" target="_blank">抖音</a> |
  <a href="https://space.bilibili.com/365374856" target="_blank">哔哩哔哩</a>
</p>

# 🎵 kook-music-streamer

---

## 📝 项目简介

kook-music-streamer 是为 KOOK（开黑啦）语音频道打造的音乐点歌机器人，支持网易云音乐单曲和歌单一键推流。你可以通过 KOOK 聊天指令让机器人自动播放你想听的歌。

---

## 🚀 快速开始

### 1. 解压程序包

解压后你会看到如下文件结构（示例）：

```
kook-music-streamer/
  ├─ kookvoice_bot.exe
  ├─ config.py
  ├─ ffmpeg/
  │    └─ ffmpeg.exe
  ├─ list.txt
  └─ ...
```

### 2. 配置机器人信息

- 用文本编辑器打开 `config.py`，只需填写两项内容：

  ```python
  ffmpeg_path = "ffmpeg/ffmpeg.exe"  # 保持默认即可
  bot_token = "你的KOOK机器人token"   # 必须填写你自己的token
  ```
- 如何获取 token？请在 KOOK 官网创建机器人，获取 token，并记下服务器ID和语音频道ID。

### 3. 免安装，开箱即用

无需安装 Python、依赖或配置环境变量，程序包已自带 ffmpeg，直接用 exe 文件即可。

---

## ▶️ 启动机器人

- **直接双击 `kookvoice_bot.exe`**
- 首次运行会弹出命令行窗口，看到“KOOK 机器人启动中...”即为成功。

---

## 💬 KOOK 频道内指令

| 指令                | 作用说明                                   |
|---------------------|--------------------------------------------|
| `/加入`             | 让机器人进入你的语音频道                   |
| `/wy 歌名`          | 网易云点歌（如 `/wy 晴天`），也可直链      |
| `/wygd 歌单链接`    | 播放网易云歌单（如 `/wygd 歌单链接`）      |
| `/跳过`             | 跳过当前歌曲                               |
| `/停止`             | 停止播放                                   |
| `/清空列表`         | 清空播放队列                               |
| `/跳转 秒数`        | 跳转到指定秒数（如 `/跳转 60`）            |
| `/帮助`             | 查看指令说明                               |

---

## ❓ 常见问题

- ⚠️ **机器人无法启动？**  
  检查 `config.py` 是否正确填写，ffmpeg 路径和 token 是否有效。

- ⚠️ **KOOK 频道无响应？**  
  检查机器人是否已加入服务器，是否有语音频道权限，token 是否正确。

- ⚠️ **ffmpeg 报错？**  
  保证 `ffmpeg/ffmpeg.exe` 文件存在，路径填写无误。

---

## 🆕 更新日志

<details>
<summary><b>点击展开历史版本</b></summary>

### v1.2.0
- 🗑️ 新增 `/清空列表` 指令，可一键清空播放队列
- 🛠️ 优化网易云歌单批量点歌体验，支持大歌单分批处理
- 🐞 修复部分情况下机器人无法自动进入语音频道的问题

### v1.1.0
- ⏩ 支持 `/跳转 秒数` 指令，播放中可快速定位到指定时间
- 💡 增强错误提示，常见问题自动反馈到频道

### v1.0.0
- 🎶 支持网易云单曲点歌、歌单批量播放
- 🔑 支持 `/加入`、`/wy`、`/wygd`、`/跳过`、`/停止` 等基础指令
- 📦 免安装绿色版，内置 ffmpeg，开箱即用

</details>

---

## 📢 其他说明

- 本程序为免安装绿色版，无需 Python 环境和依赖，解压即用。
- 如需自定义开发或遇到问题，请联系作者或访问项目 GitHub。

---

<p align="center"><b>🎉 祝你使用愉快，点歌无忧！🎉</b></p> 
