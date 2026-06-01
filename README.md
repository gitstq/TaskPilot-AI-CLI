<div align="center">

# 🎯 TaskPilot-CLI

**Lightweight Terminal AI Task Management Engine**

*轻量级终端AI智能任务管理引擎*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)]()
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🎉 Introduction

TaskPilot-CLI is a **zero-dependency**, AI-powered task management tool that runs entirely in your terminal. It combines natural language processing, intelligent priority calculation, and pomodoro time tracking to help you stay productive without leaving your command line.

### ✨ Key Features

- 🤖 **AI-Powered Priority** - Smart task prioritization based on content analysis
- 📝 **Natural Language Input** - Add tasks like "Finish report tomorrow high priority"
- 🍅 **Pomodoro Timer** - Built-in focus timer with statistics tracking
- 🎨 **Beautiful TUI** - Colorful terminal interface with ANSI support
- 💾 **SQLite Storage** - Local database with zero external dependencies
- 🔍 **Smart Search** - Full-text search across tasks
- 📊 **Productivity Stats** - Daily/weekly analytics and AI suggestions
- 🏷️ **Tag System** - Organize tasks with automatic tag extraction
- ⚡ **Lightning Fast** - Pure Python, no heavy frameworks

### 🚀 Quick Start

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/TaskPilot-AI-CLI.git
cd TaskPilot-AI-CLI

# Install
pip install -e .

# Or run directly
python -m taskpilot
```

#### Usage

```bash
# Launch interactive mode
taskpilot

# Add tasks with natural language
taskpilot add "Finish report tomorrow high priority"
taskpilot add "Buy milk today #personal"

# List pending tasks
taskpilot list

# Start pomodoro for a task
taskpilot pomodoro start task_abc123

# Show statistics
taskpilot stats
```

### 📖 Detailed Usage

#### Interactive Mode Commands

| Command | Description |
|---------|-------------|
| `add <text>` | Add task (supports natural language) |
| `list` | List pending tasks |
| `list all` | List all tasks |
| `done <id>` | Mark task as completed |
| `delete <id>` | Delete a task |
| `search <query>` | Search tasks |
| `start <id>` | Start pomodoro |
| `stop` | Stop pomodoro |
| `stats` | Show statistics |
| `suggest` | Get AI suggestion |
| `help` | Show help |

#### Natural Language Examples

```
> add Finish the quarterly report by Friday urgent
> add Buy groceries today #personal low priority
> add Call dentist tomorrow morning 30min
> add Review code #work high priority
```

### 💡 Design Philosophy

TaskPilot-CLI was designed with these principles:

1. **Zero Dependencies** - Uses only Python standard library
2. **Privacy First** - All data stored locally in SQLite
3. **AI-Enhanced** - Rule-based AI for priority calculation
4. **Developer-Friendly** - CLI-first, keyboard-driven workflow
5. **Cross-Platform** - Works on Linux, macOS, and Windows

### 📦 Project Structure

```
taskpilot/
├── __init__.py       # Package initialization
├── core.py           # Main controller
├── models.py         # Data models
├── database.py       # SQLite operations
├── ai_engine.py      # AI priority engine
├── pomodoro.py       # Timer implementation
├── tui.py            # Terminal UI
└── __main__.py       # Entry point
```

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🎉 项目介绍

TaskPilot-CLI 是一款**零外部依赖**、AI驱动的任务管理工具，完全在终端中运行。它结合自然语言处理、智能优先级计算和番茄工作法时间追踪，帮助您在命令行中保持高效。

### ✨ 核心特性

- 🤖 **AI智能优先级** - 基于内容分析的智能任务优先级排序
- 📝 **自然语言输入** - 像"明天前完成报告高优先级"这样添加任务
- 🍅 **番茄钟计时器** - 内置专注计时器，带统计追踪
- 🎨 **精美TUI** - 支持ANSI的彩色终端界面
- 💾 **SQLite存储** - 本地数据库，零外部依赖
- 🔍 **智能搜索** - 任务全文搜索
- 📊 **生产力统计** - 日/周分析和AI建议
- 🏷️ **标签系统** - 自动标签提取组织任务
- ⚡ **极速轻量** - 纯Python，无重型框架

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/TaskPilot-AI-CLI.git
cd TaskPilot-AI-CLI

# 安装
pip install -e .

# 或直接运行
python -m taskpilot
```

#### 使用

```bash
# 启动交互模式
taskpilot

# 使用自然语言添加任务
taskpilot add "明天前完成报告高优先级"
taskpilot add "今天买牛奶 #个人"

# 列出待办任务
taskpilot list

# 为任务启动番茄钟
taskpilot pomodoro start task_abc123

# 显示统计
taskpilot stats
```

### 📖 详细使用指南

#### 交互模式命令

| 命令 | 描述 |
|------|------|
| `add <文本>` | 添加任务（支持自然语言） |
| `list` | 列出待办任务 |
| `list all` | 列出所有任务 |
| `done <id>` | 标记任务完成 |
| `delete <id>` | 删除任务 |
| `search <查询>` | 搜索任务 |
| `start <id>` | 启动番茄钟 |
| `stop` | 停止番茄钟 |
| `stats` | 显示统计 |
| `suggest` | 获取AI建议 |
| `help` | 显示帮助 |

#### 自然语言示例

```
> add 周五前完成季度报告 紧急
> add 今天买杂货 #个人 低优先级
> add 明天上午给牙医打电话 30分钟
> add 审查代码 #工作 高优先级
```

### 💡 设计理念

TaskPilot-CLI 遵循以下设计原则：

1. **零依赖** - 仅使用Python标准库
2. **隐私优先** - 所有数据本地SQLite存储
3. **AI增强** - 基于规则的AI优先级计算
4. **开发者友好** - CLI优先，键盘驱动工作流
5. **跨平台** - 支持Linux、macOS和Windows

### 📦 项目结构

```
taskpilot/
├── __init__.py       # 包初始化
├── core.py           # 主控制器
├── models.py         # 数据模型
├── database.py       # SQLite操作
├── ai_engine.py      # AI优先级引擎
├── pomodoro.py       # 计时器实现
├── tui.py            # 终端UI
└── __main__.py       # 入口点
```

### 🤝 贡献指南

欢迎贡献！请随时提交Pull Request。

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

### 📄 开源协议

本项目采用MIT协议 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🎉 專案介紹

TaskPilot-CLI 是一款**零外部依賴**、AI驅動的任務管理工具，完全在終端機中運行。它結合自然語言處理、智能優先級計算和番茄工作法時間追蹤，幫助您在命令列中保持高效。

### ✨ 核心特性

- 🤖 **AI智能優先級** - 基於內容分析的智能任務優先級排序
- 📝 **自然語言輸入** - 像"明天前完成報告高優先級"這樣添加任務
- 🍅 **番茄鐘計時器** - 內建專注計時器，帶統計追蹤
- 🎨 **精美TUI** - 支援ANSI的彩色終端介面
- 💾 **SQLite儲存** - 本地資料庫，零外部依賴
- 🔍 **智能搜尋** - 任務全文搜尋
- 📊 **生產力統計** - 日/週分析和AI建議
- 🏷️ **標籤系統** - 自動標籤提取組織任務
- ⚡ **極速輕量** - 純Python，無重型框架

### 🚀 快速開始

#### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/TaskPilot-AI-CLI.git
cd TaskPilot-AI-CLI

# 安裝
pip install -e .

# 或直接運行
python -m taskpilot
```

#### 使用

```bash
# 啟動互動模式
taskpilot

# 使用自然語言添加任務
taskpilot add "明天前完成報告高優先級"
taskpilot add "今天買牛奶 #個人"

# 列出待辦任務
taskpilot list

# 為任務啟動番茄鐘
taskpilot pomodoro start task_abc123

# 顯示統計
taskpilot stats
```

### 📖 詳細使用指南

#### 互動模式命令

| 命令 | 描述 |
|------|------|
| `add <文字>` | 添加任務（支援自然語言） |
| `list` | 列出待辦任務 |
| `list all` | 列出所有任務 |
| `done <id>` | 標記任務完成 |
| `delete <id>` | 刪除任務 |
| `search <查詢>` | 搜尋任務 |
| `start <id>` | 啟動番茄鐘 |
| `stop` | 停止番茄鐘 |
| `stats` | 顯示統計 |
| `suggest` | 獲取AI建議 |
| `help` | 顯示幫助 |

#### 自然語言範例

```
> add 週五前完成季度報告 緊急
> add 今天買雜貨 #個人 低優先級
> add 明天上午給牙醫打電話 30分鐘
> add 審查代碼 #工作 高優先級
```

### 💡 設計理念

TaskPilot-CLI 遵循以下設計原則：

1. **零依賴** - 僅使用Python標準庫
2. **隱私優先** - 所有資料本地SQLite儲存
3. **AI增強** - 基於規則的AI優先級計算
4. **開發者友好** - CLI優先，鍵盤驅動工作流
5. **跨平台** - 支援Linux、macOS和Windows

### 📦 專案結構

```
taskpilot/
├── __init__.py       # 套件初始化
├── core.py           # 主控制器
├── models.py         # 資料模型
├── database.py       # SQLite操作
├── ai_engine.py      # AI優先級引擎
├── pomodoro.py       # 計時器實現
├── tui.py            # 終端UI
└── __main__.py       # 入口點
```

### 🤝 貢獻指南

歡迎貢獻！請隨時提交Pull Request。

1. Fork倉庫
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟Pull Request

### 📄 開源協議

本專案採用MIT協議 - 詳見 [LICENSE](LICENSE) 檔案。

---

<div align="center">

Made with ❤️ by TaskPilot Team

</div>
