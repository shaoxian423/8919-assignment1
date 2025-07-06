# 🛡️ CST8919 Lab 1: Flask + Auth0 Secure Login

This project is a Flask web application integrated with Auth0 for secure authentication. It supports user login, logout, and a protected route that only authenticated users can access.

---

## 🎥 Demo Video 222

[**Watch my demo on YouTube**](https://www.youtube.com/watch?v=ERFhrtObAuc)


## ✅ Features

- 🔐 Login and logout via Auth0
- 🔒 `/protected` route accessible only to logged-in users
- 📄 Displays user name and email on protected page
- 🌐 Secure token/session handling with Flask + Authlib

---

## 🧠 How It Works

| Route        | Description                              |
|--------------|------------------------------------------|
| `/`          | Home page with login button              |
| `/login`     | Redirects to Auth0 login page            |
| `/callback`  | Handles Auth0 redirect and sets session  |
| `/logout`    | Logs out from Auth0 and clears session   |
| `/protected` | Protected page with user info (requires login) |

---

## ⚙️ Setup Instructions

### 0. signed up for Auth0
https://auth0.com/docs

login and set up a application ,choose python and download code zip

### 1. Clone the repo

```bash
git clone https://github.com/shaoxian423/8919lab1.git
cd 8919lab1
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```


(See `.env.example` for reference)

---

### 4 ▶️ Run the app

```bash
python server.py
```

Open browser to: [http://localhost:3000](http://localhost:3000)

---

### 5 🔐 Protected Route

Access [http://localhost:3000/protected](http://localhost:3000/protected)

- ✔ If logged in → see name + email
- ❌ If not logged in → redirected to Auth0 login

---


## 📝 Notes

- Do NOT commit `.env` to GitHub!
- `.env.example` is safe to share
- Ideal for deploying secure Flask apps with Auth0

---

© 2025 Shaoxian Duan · CST8919 Lab 1
