# NeuraBot 🤖

<div align="center">

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-magenta.svg)](https://github.com/ultralytics/ultralytics)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The Next-Generation AI Farming Assistant for Metin2**

NeuraBot is a fully autonomous bot that combines **Computer Vision (YOLOv8)** with **Kernel-Level Input Simulation** to farm Metin Stones safely and efficiently. Unlike traditional pixel-bots, NeuraBot *sees* the game world.

[Features](#features) •
[Installation](#installation) •
[Usage](#usage) •
[Disclaimer](#disclaimer)

</div>

---

---

<a id="features"></a>
## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **🧠 AI Vision** | Uses **YOLOv8** to detect Metin stones with human-like accuracy. Optimized for **Yongan, Joan, and Pyungmoo** maps (`village1.pt`). |
| **🛡️ Smart Bypass** | Operates at the **Kernel Level** using the Interception Driver to simulate hardware mouse/keyboard events, bypassing standard protections. |
| **🧭 Intelligent Navigation** | Uses momentum-based movement and visual hashing to detect obstacles and unstick itself automatically. |
| **⚡ Auto-Loot** | Automatically collects drops (`Z` key) immediately after destroying a target. |
| **🖥️ Modern GUI** | Features a sleek, dark-mode interface built with **CustomTkinter** for a premium user experience. |
| **👻 Background Mode** | Can continue farming even when the game window is not in focus (must remain visible on screen). |

<a id="installation"></a>
## 🛠️ Installation

### Prerequisites
- **OS:** Windows 10/11
- **Python:** 3.11 (Strictly recommended for Torch compatibility)
- **Driver:** Interception Driver (Required for input simulation)

### Quick Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/mfcan10/metin2-neurabot.git
    cd metin2-neurabot
    ```

2.  **Install Interception Driver**
    *   Right-click `install_driver.ps1` and select **"Run with PowerShell"**.
    *   *Restart your computer after installation!*

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

<a id="usage"></a>
## 🎮 Usage

1.  **Run as Administrator (Critical)**
    ```powershell
    run_gui.bat
    ```
    *Or run `python gui_app.py`*

2.  **Select Game Window**
    *   Open your Metin2 Client.
    *   In the bot, click **"Refresh Windows"** and select the game window from the list.

3.  **Start Farming**
    *   Click **START BOT**. The status will change to `SEARCHING`.
    *   *Tip: Press `End` key to emergency stop.*

## 📂 Project Structure

```
neurabot/
├── gui_app.py         # 🖥️ Main GUI Application
├── bot_logic.py       # 🧠 Core AI & State Machine
├── cinput.py          # ⌨️ Low-level Input Wrapper
├── install_driver.ps1 # 🔌 Driver Installer Script
├── models/            # 🤖 YOLO Models
│   └── village1.pt    #    (Trained for Village 1)
├── interception.dll   # ⚙️ Driver Library
└── requirements.txt   # 📦 Dependencies
```

<a id="disclaimer"></a>
## ⚠️ Disclaimer

> [!WARNING]
> This software is for **educational purposes only**.
> Using automation tools in online games may violate the Terms of Service and result in account bans.
> The developer is not responsible for any consequences arising from the use of this software. Use at your own risk.

---

<div align="center">
Made with ❤️ by MFC
</div>
