# 🤖 Human Emotion Detection Web App

**Author:** OBI IKECHUKWU
**Student ID:** 23CE034397
**Course:** Computer Science

---

## 🚀 Live Demo

* **Live App:** [https://emotion-detection-app-htbi.onrender.com](https://emotion-detection-app-htbi.onrender.com)
* **Database Logs:** [https://emotion-detection-app-htbi.onrender.com/view-logs-secret](https://emotion-detection-app-htbi.onrender.com/view-logs-secret)

*(Note: The app is hosted on Render's free tier. It may take 30-60 seconds to wake up on the first load.)*

---

## 📖 Project Overview

This project is a full-stack web application designed to detect and classify human emotions from facial images using Artificial Intelligence.

The application allows users to upload an image of a face. The system then processes the image using the `deepface` library (powered by TensorFlow/Keras), identifies the dominant emotion (e.g., happy, sad, angry), and displays the result. It also features a persistent cloud database that logs every analysis for record-keeping.

## ✨ Key Features

* **AI Emotion Analysis:** Accurately classifies faces into 7 emotion categories: Angry, Disgust, Fear, Happy, Sad, Surprise, and Neutral.
* **User-Friendly Interface:** Simple web interface for uploading images and viewing results.
* **Persistent Cloud Database:** Integrates with **Neon (PostgreSQL)** to save analysis logs (User Name, Image Name, Result) permanently, ensuring data survives server restarts.
* **Smart Memory Management:** Optimized to run on low-memory environments (512MB RAM) by using the `opencv` backend and lazy-loading the AI model.
* **Admin Dashboard:** Includes a secure "secret" route to view the history of all analyses performed on the app.

---

## 🔧 Technology Stack

### Back-End
* **Python 3.10:** Core programming language.
* **Flask:** Micro-web framework for handling requests and routing.
* **Gunicorn:** Production WSGI server for reliable deployment.

### AI & Machine Learning
* **DeepFace:** A lightweight face recognition and facial attribute analysis framework.
* **TensorFlow / Keras:** The underlying deep learning engine.
* **OpenCV:** Used as the lightweight face detector backend.

### Database
* **PostgreSQL:** Robust relational database system.
* **Neon:** Serverless Postgres platform for cloud hosting.
* **SQLAlchemy:** Python ORM for database interactions.

### Deployment
* **Render:** Cloud platform for hosting the web service.
* **Git & GitHub:** Version control and CI/CD (Continuous Deployment).

---

## 📂 Project Structure

```bash
OBI_IKECHUKWU_23CE034397_EMOTION_DETECTION_WEB_APP/
│
├── app.py              # Main application entry point (Routes & DB Setup)
├── model.py            # AI Logic: Contains the analyze_emotion() function
├── requirements.txt    # List of python dependencies
├── .gitignore          # Files to exclude from Git
│
├── static/
│   └── uploads/        # Directory for temporary image storage
│
└── templates/
    ├── index.html      # Homepage (Upload Form)
    ├── result.html     # Result Display Page
    └── logs.html       # Database Log Viewer Page

```

---

## ⚙️ Local Installation & Setup

Follow these steps to run the project on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/Killua2026/OBI_IKECHUKWU_23CE034397_EMOTION_DETECTION_WEB_APP.git](https://github.com/Killua2026/OBI_IKECHUKWU_23CE034397_EMOTION_DETECTION_WEB_APP.git)
cd OBI_IKECHUKWU_23CE034397_EMOTION_DETECTION_WEB_APP

```

### 2. Create a Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Run the Application

```bash
python app.py

```

*The app will automatically create a local `database.db` (SQLite) file for testing if a cloud database URL is not found.*

### 5. Access the App

Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 🛠 Troubleshooting & Optimization

This project implements specific optimizations to handle heavy AI models on free-tier cloud servers:

1. **Memory Crash (Error 139):**
* **Issue:** The `deepface` library loads heavy TensorFlow weights that exceed the 512MB RAM limit on Render.
* **Solution:** I implemented "Lazy Loading." The model is imported inside the `analyze_emotion()` function, not at the top of the file. I also switched the detector backend to `opencv` instead of `retinaface` to save memory.


2. **Worker Timeout:**
* **Issue:** The model takes >30 seconds to load initially, causing Gunicorn to kill the worker.
* **Solution:** The deployment command includes `--timeout 120` to allow sufficient start-up time.



---

## 📬 Contact

**Student email:** iobi.2301688@stu.cu.edu.ng



