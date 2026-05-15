# 👟 Cephas Ok Shoes: AI-Powered Retail Agent

An intelligent, agentic commerce solution designed to bridge the gap between casual WhatsApp shoppers and a structured inventory system. This bot automates customer inquiries, shoe inventory management, and debt tracking using state-of-the-art AI.

---

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092e20.svg?style=for-the-badge&logo=django&logoColor=white)
![Google Gemini](https://img.shields.io/badge/google%20gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Twilio](https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=Twilio&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Cloudflare](https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&logo=Cloudflare&logoColor=white)
![Termux](https://img.shields.io/badge/termux-000000?style=for-the-badge&logo=termux&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)

---

## 🌟 Key Features

* **Structured Database**: Robust relational schema managing `Shoes`, `Customers`, `Orders`, and `ShoeRequests` for full business traceability.
* **Admin Interface**: A comprehensive business dashboard with real-time CRUD (Create, Read, Update, Delete) implementation for inventory control.
* **Natural Language Search**: "Do you have size 45 male canvas?" triggers a database lookup and returns real-time results.
* **Automatic Media Delivery**: Dynamically generates Absolute URIs to send shoe photos directly to the user's WhatsApp.
* **Automated Marketing**: Integrated **APScheduler** that sends randomized health and shoe-care tips to the entire customer base every 5 days.
* **Competing Order Logic**: Smart handling of "Pending" vs "Picked Up" states, automatically notifying other interested customers when a specific pair is sold.
* **Balance Tracking**: Customers can check their debt status instantly based on their unique phone identifier.
* **Smart Preferences**: Detects and saves preferred language (English, Pidgin, Yoruba) and sizing history for personalized service.

---

## 🚀 Getting Started

### 1. Clone & Install
```bash
git clone [https://github.com/marviecephas/cephasokshoes.git](https://github.com/marviecephas/cephasokshoes.git)
cd cephasokshoes
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file in the root directory:

```plaintext
GEMINI_API_KEY=your_gemini_key
TWILIO_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_auth_token
```

### 3. Initialize & Run
```bash
python manage.py migrate
python manage.py runserver
```

### 4. Tunneling
In a new Termux session, run:

```bash
cloudflared tunnel --url [http://127.0.0.1:8000](http://127.0.0.1:8000)
```

## 📜 License

This project is licensed under the **MIT License**.  
Copyright (c) 2026 **Marvellous Cephas**.

See the [LICENSE](LICENSE) file for the full legal text.

