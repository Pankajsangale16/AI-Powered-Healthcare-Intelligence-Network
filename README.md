# 🩺 AI-Powered Healthcare Intelligence Network

> **Modern Full-Stack Healthcare Intelligence Platform: React 19 Frontend + Django 5 REST Backend with PWA and Mobile-First Chrome Android Support.**

---

## 📌 Architecture Overview

The system migrates the original Streamlit application into a modern, decoupled production architecture:

```
├── backend/                       # Django 5 + Django REST Framework API
│   ├── apps/
│   │   ├── core/                  # Singleton model loaders & standardized exception handlers
│   │   ├── disease/               # Disease prediction & symptoms autocomplete
│   │   ├── drugs/                 # 9,720-drug catalog & cosine similarity recommendation
│   │   ├── heart/                 # 22-feature BRFSS heart risk & SHAP attribution
│   │   └── chatbot/               # Medibot RAG LLM endpoint with SSE streaming
│   ├── config/                    # Django settings, URLs, ASGI/WSGI
│   └── tests/                     # 17 comprehensive pytest parity test cases
├── frontend/                      # React 19 + Vite + TypeScript Frontend
│   ├── src/
│   │   ├── components/            # Design system (Navbar, BottomNav, Stepper, TagInput, Modal)
│   │   ├── pages/                 # Home, Disease, Drugs, Heart, Medibot, NotFound
│   │   ├── lib/                   # API client (VITE_API_URL, timeouts, SSE streaming)
│   │   └── context/               # Dark/Light theme provider with system detection
│   └── public/                    # PWA icons (192, 512 maskable) & manifest
├── legacy/                        # Untouched backup of original Streamlit pages
├── data/                          # Medical datasets (CSVs, reference dictionaries)
├── models/                        # Pre-trained ML models (.pkl, .joblib)
└── vectorstore/                   # FAISS vector database for clinical RAG
```

---

## 🚀 Key Modules & Endpoints

| Module | Route / Endpoint | Description |
|---|---|---|
| **Health** | `GET /api/v1/health/` | API status & Groq configuration check |
| **Disease Prediction** | `POST /api/v1/disease/predict/`<br>`GET /api/v1/disease/symptoms/`<br>`GET /api/v1/disease/search/?q=` | Random Forest classification on 132 symptoms + precautions, medications, diet, and workouts |
| **Drug Recommendation** | `GET /api/v1/drugs/?q=&page=`<br>`POST /api/v1/drugs/recommend/` | Paginated search across 9,720 medicines & NLP cosine similarity recommendations |
| **Heart Risk** | `GET /api/v1/heart/options/`<br>`POST /api/v1/heart/assess/` | EasyEnsemble + SHAP attribution across 22 CDC BRFSS lifestyle & clinical indicators |
| **Medibot AI** | `POST /api/v1/chat/` | Clinical health education assistant with LangChain + FAISS + Groq and SSE streaming |

---

## 💻 Quick Start & Step-by-Step Run Commands

Follow these steps to run both the Django backend and React frontend.

---

### Step 1: Backend Setup (Django REST Framework)

Open a terminal in the root directory: `d:\Project\AI-Powered-Healthcare-Intelligence-Network`

#### On Windows (PowerShell):
```powershell
# 1. Activate the virtual environment
# If PowerShell gives a script execution policy error, run:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\venv\Scripts\Activate.ps1

# 2. (First-time only) Apply database migrations
python backend\manage.py migrate

# 3. (Optional) Run automated test suite to verify ML model parity
pytest -v backend

# 4. Start the Django backend server on port 8000
python backend\manage.py runserver 0.0.0.0:8000
```
> **Tip:** You can also run directly without activating:  
> `.\venv\Scripts\python.exe backend\manage.py runserver 0.0.0.0:8000`

#### On Windows (Command Prompt - CMD):
```cmd
venv\Scripts\activate.bat
python backend\manage.py migrate
python backend\manage.py runserver 0.0.0.0:8000
```

#### On Linux / macOS (Bash):
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Apply database migrations
python backend/manage.py migrate

# 3. Run test suite
pytest -v backend

# 4. Start backend server
python backend/manage.py runserver 0.0.0.0:8000
```

*Backend will be running at:* `http://localhost:8000/api/v1/health/`

---

### Step 2: Frontend Setup (React + Vite + TypeScript PWA)

Open a **second terminal** and navigate to the `frontend` directory:

```bash
cd frontend

# 1. (First-time only) Install node dependencies
npm install

# 2. Start the development server with local network access enabled
npm run dev -- --host 0.0.0.0 --port 5173
```

*Frontend will be running at:* `http://localhost:5173/`

---

### Step 3: Accessing the Application

- **On Desktop:** Open [http://localhost:5173/](http://localhost:5173/) in Chrome, Edge, or Brave.
- **On Mobile (Android Chrome):** Open `http://<YOUR_PC_IP>:5173/` on the same Wi-Fi network, or use USB debugging:
  ```bash
  adb reverse tcp:5173 tcp:5173
  adb reverse tcp:8000 tcp:8000
  ```
  Then open `http://localhost:5173/` directly on your mobile device.


---

## 📱 Testing on a Real Android Phone over LAN

To test the mobile experience on a real Android device (Chrome Android) connected to the same Wi-Fi network:

### Option A: Local Network IP
1. Find your computer's local IP address (`ipconfig` on Windows or `ifconfig` on Linux/macOS, e.g., `192.168.1.50`).
2. Update `frontend/.env`:
   ```env
   VITE_API_URL=http://<YOUR_LOCAL_IP>:8000/api/v1
   ```
3. Restart frontend: `npm run dev -- --host 0.0.0.0`
4. On your Android phone, open Chrome and navigate to `http://<YOUR_LOCAL_IP>:5173`.
5. Tap **Add to Home screen** in Chrome to install the PWA.

### Option B: Android Debug Bridge (`adb reverse`) over USB
```bash
# Connect Android phone with USB Debugging enabled
adb reverse tcp:5173 tcp:5173
adb reverse tcp:8000 tcp:8000
```
Then navigate to `http://localhost:5173` directly on your Android phone's Chrome browser!

---

## 🧪 Automated Testing

To run the verification test suite comparing API outputs with original Streamlit algorithms:

```powershell
pytest -v backend
```

---

## 🐳 Docker Deployment

> **Prerequisite:** [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) must be installed and running.

Run both frontend and backend using Docker Compose:

```bash
docker compose up --build
```
*(Or `docker-compose up --build` if using legacy Compose v1)*

To run in the background (detached):
```bash
docker compose up -d --build
```

To stop containers:
```bash
docker compose down
```

---

## ⚖️ Legal & Medical Disclaimer

*This platform is intended solely for educational and clinical decision support demonstration. It is not a substitute for professional medical diagnosis or clinical treatment.*

