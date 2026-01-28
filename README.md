# 🤖❓ AI CHATBOT Web App

**Author:** OBI IKECHUKWU
**Student ID:** 23CE034397
**Course:** Computer Science

---

## 🚀 Live Demo

**Live App:** [https://obi-ikechukwu-23ce034397-ai-app.onrender.com](https://obi-23ce034397-ai-chatbot-web-app.onrender.com/)


*(Note: This application is hosted on Render. If the site is idle, it may take 30-60 seconds to spin up the server on the first load.)*

---

## 📖 Project Overview

This project is a chatbot web app. The application provides a seamless bridge between a user-friendly web interface and an external Large Language Model (LLM).

Unlike standard implementations using ChatGPT, this system utilizes the **Google Gemini API** to process natural language questions. The app captures user input, queries the AI backend, logs the interaction in a persistent database, and returns the feedback to the user in real-time.

## ✨ Key Features

* **Universal Query Interface:** Accepts any text-based question from the user via a clean `index.html` interface.
* **External AI Integration:** Communicates with the Google Gemini Pro model for intelligent response generation.
* **Persistent Interaction Logging:** Every question and its corresponding AI feedback is stored in a **SQLite/PostgreSQL** database for history and audit purposes.
* **Asynchronous Processing:** Uses JavaScript `fetch` to ensure the UI doesn't freeze while waiting for the AI response.
* **Mobile-Responsive Design:** Styled with CSS to ensure the interface works on both desktop and mobile devices.

---

## 🔧 Technology Stack

### Back-End

* **Python 3.x:** Core logic and API integration.
* **Flask:** Lightweight WSGI web framework.
* **Google Generative AI SDK:** To interface with the Gemini-1.5-Flash model.

### Front-End

* **HTML5/CSS3:** Structure and styling.
* **JavaScript (Vanilla):** For handling asynchronous API calls to the Flask backend.

### Database

* **SQLite:** Local relational database for storing user names, questions, and AI feedback.
* **SQLAlchemy:** ORM used for database management.

---

## 📂 Project Structure

Following the required assignment structure:

```bash
OBI_IKECHUKWU_23CE034397_AI_QUERY_APP/
│
├── app.py                 # Backend logic, API routes, and DB management
├── model.py               # Logic for AI API connection and configuration
├── requirements.txt       # Dependencies (Flask, google-generativeai, etc.)
├── queries.db             # SQLite database containing logs of interactions
├── link_to_my_web_app.txt # Text file containing the Render hosting link
├── .env                   # Environment variables (API Keys - Excluded from Git)
├── .gitignore             # To prevent sensitive data leakage
│
├── static/
│   └── style.css          # Custom styling for the web interface
│
└── templates/
    └── index.html         # Main web interface (Accepts input and shows feedback)

```

---

## ⚙️ Setup and Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/your-repo-name.git

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Configure API Key:**
Create a `.env` file and add your Google AI API Key:
```text
GEMINI_API_KEY=your_api_key_here

```


4. **Run the application:**
```bash
python app.py

```

## 📬 Contact

**Student email:** iobi.2301688@stu.cu.edu.ng



