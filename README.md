<div align="center">

# 🎫 TicketBot

**Interactive Discord Support Ticket System with Dynamic Dropdown Categories**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/discord.py-v2.0+-5865F2.svg)](https://github.com/Rapptz/discord.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, streamlined support ticket bot built with custom select menus, category selection, and automated private channel setup.

[Features](#-features) • [Ticket Topics](#-ticket-topics) • [Commands](#-commands) • [Installation](#-installation) • [Author](#-author)

</div>


## ✨ Features

- 📌 **Panel Deployment:** Easily publish a support panel using `/ticket_panel`.
- 📋 **Dropdown Menu Selection:** Users choose their specific issue topic directly from a clean Discord Select Menu.
- 🔒 **Private Support Channel:** Instantly provisions a private channel pinging the ticket owner and staff.
- 🔒 **One-Click Close:** Close and manage tickets effortlessly with an interactive button.


## 📑 Ticket Topics Included

When a user opens a ticket, they can choose from the following pre-configured options:
- 👥 **Issues with other members / Staff**
- 💡 **Server idea**
- 🛠️ **Problem with channels / roles**
- 🤝 **Partnership / Collab**
- 📝 **Staff Team application**


## 🛠️ Commands & Components

| Command / Component | Description |
| :--- | :--- |
| `/ticket_panel` | Posts the support ticket panel in the designated channel. |
| **`🎫 Open Ticket`** | Button that triggers the ticket creation flow. |
| **`Select the topic...`** | Dropdown menu allowing users to specify their ticket reason. |
| **`🔒 Close Ticket`** | Action button to close and archive the ongoing ticket. |


## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone [https://github.com/bikiogirl/TicketBot.git](https://github.com/bikiogirl/TicketBot.git)
cd TicketBot
