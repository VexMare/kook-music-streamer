# 🎵 KOOK Music Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![KOOK API](https://img.shields.io/badge/KOOK-API-green.svg)](https://developer.kookapp.cn/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Audio-orange.svg)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An intelligent music playback bot based on KOOK API, supporting NetEase Cloud Music search and playlist playback

## ✨ Features

- 🎤 **Single Track Search & Play** - Search by song name or artist, quickly find target music
- 📀 **Playlist Batch Playback** - Support NetEase Cloud Music playlist links, one-click playback
- 🔄 **Real-time URL Fetching** - Get latest links during playback to avoid link expiration
- 🎧 **High-Quality Audio** - FFmpeg-based audio processing supporting multiple formats
- ⏭️ **Playback Control** - Skip, stop, view playlist and other control functions
- 📊 **Detailed Statistics** - Playback success rate, song information and detailed statistics
- 🎯 **Intelligent Error Handling** - Comprehensive exception handling and user-friendly error messages

## 🚀 Quick Start

### Requirements

- Python 3.8+
- FFmpeg
- KOOK Bot Token

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/your-username/KOOK_Audio.git
cd KOOK_Audio/Main
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configuration**
Edit `config.py` file:
```python
# Configuration file for global parameters
ffmpeg_path = "D:/GitHub/KOOK_Audio/Main/ffmpeg/bin/ffmpeg.exe"  # FFmpeg path
bot_token = "your_bot_token_here"  # Your KOOK bot token

# Music API configuration
music_api_base = "https://1304404172-f3na0r58ws.ap-beijing.tencentscf.com"  # Music API address
```

4. **Run Bot**
```bash
python kookvoice_bot.py
```

## 📖 Usage Guide

### Basic Commands

| Command | Function | Example |
|---------|----------|---------|
| `/加入` | Join voice channel | `/加入` |
| `/wy` | Search and play single track | `/wy 九万字` |
| `/wygd` | Play playlist | `/wygd [playlist_link]` |
| `/跳过` | Skip current song | `/跳过` |
| `/停止` | Stop playback | `/停止` |
| `/进度` | View playback progress | `/进度` |
| `/跳转` | Jump to specific time | `/跳转 30` |
| `/清空列表` | Clear playlist | `/清空列表` |
| `/帮助` | View help information | `/帮助` |

### Usage Examples

#### Play Single Track
```
/wy 九万字
```
The bot will search for "九万字" and add it to the playback queue.

#### Play Playlist
```
/wygd https://music.163.com/playlist?id=947835566
```
The bot will fetch all songs from the playlist and add them to the playback queue.

#### Playback Control
```
/跳过          # Skip current song
/停止          # Stop playback
/进度          # View playback progress
/跳转 30       # Jump to 30 seconds
/清空列表      # Clear playlist
```

## 🏗️ Project Structure

```
KOOK_Audio/
├── Main/                          # Main program directory
│   ├── kookvoice_bot.py          # Main bot program
│   ├── config.py                 # Configuration file
│   ├── requirements.txt          # Dependencies list
│   ├── README.md                 # Project documentation
│   ├── kookvoice/                # Core voice module
│   │   ├── __init__.py
│   │   ├── kookvoice.py          # Voice playback core
│   │   └── requestor.py          # API request handling
│   ├── ffmpeg/                   # FFmpeg tools
│   │   └── bin/
│   │       ├── ffmpeg.exe
│   │       ├── ffplay.exe
│   │       └── ffprobe.exe
│   ├── test_files/               # Test files directory
│   │   ├── test_playlist_realtime.py
│   │   ├── test_playlist_final.py
│   │   └── 歌单实时获取URL功能总结.md
│   └── 项目文件说明.txt          # Detailed file description
├── Kook_Dos/                     # KOOK API documentation
└── build/                        # Build output directory
```

## 🔧 Technical Features

### Core Tech Stack
- **Python 3.8+** - Primary development language
- **KOOK API** - Bot API interface
- **FFmpeg** - Audio processing and streaming
- **asyncio** - Asynchronous programming framework
- **requests** - HTTP request library
- **aiohttp** - Asynchronous HTTP client

### Technical Highlights
- **Asynchronous Architecture** - High-performance async processing based on asyncio
- **Real-time URL Fetching** - Avoid music link expiration issues
- **Intelligent Error Handling** - Comprehensive exception handling and recovery
- **Modular Design** - Clear code structure, easy to maintain
- **Configuration Management** - Flexible configuration file system
- **Thread Safety** - Multi-threaded playback processing, supports concurrent operations

## 📊 Feature Demo

### Playlist Playback
```
✅ Playlist added to queue
🎵 Playlist: 悪尒夢喜欢的音乐
📊 Total tracks: 204
✅ Successfully fetched: 204 track info
❌ Failed to fetch: 0 tracks
📈 Success rate: 100.0%
🔄 Real-time URL fetching during playback
```

### Single Track Search
```
✅ Music added successfully
九万字 - 黄诗扶 added to playback queue
```

### Playback Control
```
🎵 Currently playing: 九万字 - 黄诗扶
⏱️ Playback progress: 1:23 / 3:45
📊 Playlist: 3 tracks
```

## 🛠️ Development Guide

### Environment Setup
1. Ensure Python environment is properly installed
2. Download and configure FFmpeg
3. Get KOOK bot token
4. Install project dependencies

### Code Structure
- `kookvoice_bot.py` - Main program entry, handles user commands
- `kookvoice/kookvoice.py` - Core playback logic
- `config.py` - Global configuration management
- `test_files/` - Test and debug files

### Extension Development
The project uses modular design, making it easy to add new features:
- Add new music source support
- Add playback control functions
- Extend statistics functionality
- Optimize user experience

## 🔍 Core Features Explained

### Real-time URL Fetching Mechanism
To avoid music link expiration issues, we implemented a real-time URL fetching mechanism:

1. **Playlist Processing**: Only fetch basic song information (ID, name, artist)
2. **Create Markers**: Generate special format song markers
3. **Real-time Fetching**: Get latest playback links during playback

### Intelligent Error Handling
- **API Response Validation**: Check status codes and JSON format
- **Network Exception Handling**: Timeout, connection errors, etc.
- **Playback Exception Recovery**: Automatically skip unplayable songs
- **User-friendly Prompts**: Clear error message display

### Playback Control Features
- **Playlist Management**: Support add, delete, clear operations
- **Playback State Control**: Play, pause, stop, skip
- **Progress Control**: View progress, jump to time
- **Multi-server Support**: Support multiple KOOK servers simultaneously

## 🤝 Contributing

We welcome Issue submissions and Pull Requests to improve the project!

### How to Contribute
1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Issue Reporting
If you encounter problems or have suggestions, please:
1. Check the [Issues](../../issues) page
2. Create a new Issue
3. Describe the problem and reproduction steps in detail

## 📝 Changelog

### v1.0.0 (2025-08-30)
- ✨ Implement basic music playback functionality
- 🎵 Support NetEase Cloud Music search
- 📀 Support playlist playback functionality
- 🔄 Implement real-time URL fetching mechanism
- 🛠️ Improve error handling and logging system
- 🎯 Optimize playback control features
- 📊 Add detailed statistics information

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [KOOK Developer Platform](https://developer.kookapp.cn/) - Provides bot API
- [NetEase Cloud Music API](https://music.163.com/) - Music resource support
- [FFmpeg](https://ffmpeg.org/) - Audio processing tools

## 📞 Contact

- Project Homepage: [GitHub Repository](https://github.com/your-username/KOOK_Audio)
- Issue Feedback: [Issues](../../issues)
- Email: your-email@example.com

---

⭐ If this project helps you, please give it a star!
