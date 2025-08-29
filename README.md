# 🎵 KOOK音乐机器人

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![KOOK API](https://img.shields.io/badge/KOOK-API-green.svg)](https://developer.kookapp.cn/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Audio-orange.svg)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 基于KOOK API开发的智能音乐播放机器人，支持网易云音乐搜索、歌单播放等功能

## ✨ 主要功能

- 🎤 **单曲搜索播放** - 支持歌名、歌手搜索，快速找到目标音乐
- 📀 **歌单批量播放** - 支持网易云音乐歌单链接，一键播放整个歌单
- 🔄 **实时URL获取** - 播放时实时获取最新链接，避免链接失效问题
- 🎧 **高质量音频** - 基于FFmpeg的音频处理，支持多种音频格式
- ⏭️ **播放控制** - 支持跳过、停止、查看播放列表等控制功能
- 📊 **详细统计** - 提供播放成功率、歌曲信息等详细统计
- 🎯 **智能错误处理** - 完善的异常处理和用户友好的错误提示

## 🚀 快速开始

### 环境要求

- Python 3.8+
- FFmpeg
- KOOK机器人Token

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/KOOK_Audio.git
cd KOOK_Audio/Main
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置设置**
编辑 `config.py` 文件：
```python
# 配置文件，存放全局参数
ffmpeg_path = "D:/GitHub/KOOK_Audio/Main/ffmpeg/bin/ffmpeg.exe"  # FFmpeg路径
bot_token = "your_bot_token_here"  # 你的KOOK机器人Token

# 音乐API配置
music_api_base = "https://1304404172-f3na0r58ws.ap-beijing.tencentscf.com"  # 音乐API地址
```

4. **运行机器人**
```bash
python kookvoice_bot.py
```

## 📖 使用指南

### 基础命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `/加入` | 加入语音频道 | `/加入` |
| `/wy` | 搜索并播放单曲 | `/wy 九万字` |
| `/wygd` | 播放歌单 | `/wygd [歌单链接]` |
| `/跳过` | 跳过当前歌曲 | `/跳过` |
| `/停止` | 停止播放 | `/停止` |
| `/进度` | 查看播放进度 | `/进度` |
| `/跳转` | 跳转到指定时间 | `/跳转 30` |
| `/清空列表` | 清空播放列表 | `/清空列表` |
| `/帮助` | 查看帮助信息 | `/帮助` |

### 使用示例

#### 播放单曲
```
/wy 九万字
```
机器人会搜索"九万字"并添加到播放队列。

#### 播放歌单
```
/wygd https://music.163.com/playlist?id=947835566
```
机器人会获取歌单中的所有歌曲并添加到播放队列。

#### 播放控制
```
/跳过          # 跳过当前歌曲
/停止          # 停止播放
/进度          # 查看播放进度
/跳转 30       # 跳转到30秒
/清空列表      # 清空播放列表
```

## 🏗️ 项目结构

```
KOOK_Audio/
├── Main/                          # 主程序目录
│   ├── kookvoice_bot.py          # 主机器人程序
│   ├── config.py                 # 配置文件
│   ├── requirements.txt          # 依赖列表
│   ├── README.md                 # 项目说明
│   ├── kookvoice/                # 核心语音模块
│   │   ├── __init__.py
│   │   ├── kookvoice.py          # 语音播放核心
│   │   └── requestor.py          # API请求处理
│   ├── ffmpeg/                   # FFmpeg工具
│   │   └── bin/
│   │       ├── ffmpeg.exe
│   │       ├── ffplay.exe
│   │       └── ffprobe.exe
│   ├── test_files/               # 测试文件目录
│   │   ├── test_playlist_realtime.py
│   │   ├── test_playlist_final.py
│   │   └── 歌单实时获取URL功能总结.md
│   └── 项目文件说明.txt          # 详细文件说明
├── Kook_Dos/                     # KOOK API文档
└── build/                        # 构建输出目录
```

## 🔧 技术特性

### 核心技术栈
- **Python 3.8+** - 主要开发语言
- **KOOK API** - 机器人API接口
- **FFmpeg** - 音频处理和流媒体
- **asyncio** - 异步编程框架
- **requests** - HTTP请求库
- **aiohttp** - 异步HTTP客户端

### 技术亮点
- **异步架构** - 基于asyncio的高性能异步处理
- **实时URL获取** - 避免音乐链接失效问题
- **智能错误处理** - 完善的异常处理和恢复机制
- **模块化设计** - 清晰的代码结构，易于维护
- **配置管理** - 灵活的配置文件系统
- **线程安全** - 多线程播放处理，支持并发操作

## 📊 功能演示

### 歌单播放功能
```
✅ 歌单已加入播放队列
🎵 歌单: 悪尒夢喜欢的音乐
📊 总歌曲数: 204 首
✅ 成功获取: 204 首歌曲信息
❌ 获取失败: 0 首
📈 成功率: 100.0%
🔄 播放时将实时获取最新链接
```

### 单曲搜索功能
```
✅ 添加音乐成功
九万字 - 黄诗扶 已加入播放队列
```

### 播放控制功能
```
🎵 当前播放: 九万字 - 黄诗扶
⏱️ 播放进度: 1:23 / 3:45
📊 播放列表: 3 首歌曲
```

## 🛠️ 开发指南

### 环境搭建
1. 确保Python环境正确安装
2. 下载并配置FFmpeg
3. 获取KOOK机器人Token
4. 安装项目依赖

### 代码结构
- `kookvoice_bot.py` - 主程序入口，处理用户命令
- `kookvoice/kookvoice.py` - 核心播放逻辑
- `config.py` - 全局配置管理
- `test_files/` - 测试和调试文件

### 扩展开发
项目采用模块化设计，可以轻松添加新功能：
- 新增音乐源支持
- 添加播放控制功能
- 扩展统计功能
- 优化用户体验

## 🔍 核心功能详解

### 实时URL获取机制
为了避免音乐链接失效的问题，我们实现了实时URL获取机制：

1. **歌单处理**：只获取歌曲基本信息（ID、歌名、歌手）
2. **创建标记**：生成特殊格式的歌曲标记
3. **实时获取**：播放时实时获取最新播放链接

### 智能错误处理
- **API响应验证**：检查状态码和JSON格式
- **网络异常处理**：超时、连接错误等
- **播放异常恢复**：自动跳过无法播放的歌曲
- **用户友好提示**：清晰的错误信息展示

### 播放控制功能
- **播放队列管理**：支持添加、删除、清空操作
- **播放状态控制**：播放、暂停、停止、跳过
- **进度控制**：查看进度、跳转时间
- **多服务器支持**：支持多个KOOK服务器同时使用

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

### 贡献方式
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 问题反馈
如果您遇到问题或有建议，请：
1. 查看 [Issues](../../issues) 页面
2. 创建新的 Issue
3. 详细描述问题和复现步骤

## 📝 更新日志

### v1.0.0 (2025-08-30)
- ✨ 实现基础音乐播放功能
- 🎵 支持网易云音乐搜索
- 📀 支持歌单播放功能
- 🔄 实现实时URL获取机制
- 🛠️ 完善错误处理和日志系统
- 🎯 优化播放控制功能
- 📊 添加详细统计信息

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [KOOK开发者平台](https://developer.kookapp.cn/) - 提供机器人API
- [网易云音乐API](https://music.163.com/) - 音乐资源支持
- [FFmpeg](https://ffmpeg.org/) - 音频处理工具

## 📞 联系方式

- 项目主页：[GitHub Repository](https://github.com/VexMare/kook-music-streamer)
- 邮箱：chixiaotao@foxmail.com

---

⭐ 如果这个项目对您有帮助，请给它一个星标！
