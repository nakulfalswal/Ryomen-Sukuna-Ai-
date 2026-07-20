<div align="center">

```

██████╗ ██████╗ ██████╗ ███████╗███████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝
██████╔╝██████╔╝██████╔╝█████╗  ███████╗███████╗
██╔═══╝ ██╔═══╝ ██╔══██╗██╔══╝  ╚════██║╚════██║
██║     ██║     ██║  ██║███████╗███████║███████║
╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
```


# Ryomen-Sukuna-Ai-


<div align="center">


![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)


</div>

---


## 📖 About

<div align="center">

---

## ✨ Features

- ✅ **Mention-based chat** — ping the bot and it responds in character
- ✅ **Multiple built-in personas** — Sukuna, Luffy, Doraemon and more
- ✅ **Per-server custom personas** — admins can set a server-specific persona with `/update_persona`
- ✅ **Long-term memory** — summarizes who you are and what your server is like, persisted in SQLite across restarts
- ✅ **Smart prompt assembly** — every reply is built as `Persona → Server Memory → User Memory → Recent Messages → Your Message`

---

## 🛠️ Tech Stack

**Languages**: `Python`

**Frameworks**: `Flask`

**Tools**: `pip/poetry`

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+

### Installation

```bash
**1. Clone**
```bash
git clone https://github.com/lukan-lawslaf/Ryomen-Sukuna-Ai-
cd Ryomen-Sukuna-Ai-
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create a `.env` file**
```env
DISCORD_TOKEN=your_discord_bot_token
HF_TOKEN=your_huggingface_token
```

| Variable | Where to get it |
|---|---|
| `DISCORD_TOKEN` | [Discord Developer Portal](https://discord.com/developers/applications) → Your App → Bot |
| `HF_TOKEN` | [Hugging Face](https://huggingface.co/settings/tokens) — needs Inference API access |

**4. Run**
```bash
python main.py
```

`bot_data.db` is created automatically and stores all personas and memories.

---
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---



---
<div align="center">

**Made with ❤️ by [lukan-lawslaf](https://github.com/lukan-lawslaf)**

⭐ Star this repo if you found it helpful!

</div>