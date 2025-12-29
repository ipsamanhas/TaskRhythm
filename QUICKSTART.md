# TaskRhythm - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Option 1: Automated Setup (Recommended)

#### On macOS/Linux:
```bash
cd TaskRhythm
./run.sh
```

#### On Windows:
```cmd
cd TaskRhythm
run.bat
```

The script will:
- Create a virtual environment
- Install all dependencies
- Start the server automatically

### Option 2: Manual Setup

1. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Run the server**
```bash
uvicorn app.main:app --reload
```

### Access the Application

Open your browser and go to: **http://localhost:8000**

## 📱 First Time Usage

### 1. Register an Account
- Click "Register here" on the landing page
- Choose a username and password
- You'll be logged in automatically

### 2. Define Your Energy Windows
- Go to **Energy Windows** from the dashboard
- Add at least 2-3 windows for different times of day
- Example:
  - Monday 9:00 AM - 11:00 AM → High Energy
  - Monday 2:00 PM - 4:00 PM → Medium Energy
  - Monday 8:00 PM - 9:00 PM → Low Energy

### 3. Add Your Tasks
- Go to **Tasks** from the dashboard
- Add your academic tasks with effort levels
- Example:
  - "Study for CMPUT 301 midterm" → High Effort, 120 minutes
  - "Read Chapter 5" → Medium Effort, 45 minutes
  - "Organize notes" → Low Effort, 30 minutes

### 4. Generate Your Schedule
- Go to **Schedule** from the dashboard
- Click **Generate Schedule**
- View your tasks matched to energy windows!

## 💡 Tips for Success

1. **Be Honest About Energy**: Don't force yourself into someone else's schedule
2. **Start Simple**: Add 3-5 energy windows to begin
3. **Adjust as Needed**: You can always modify windows and regenerate
4. **Use Effort Levels Wisely**:
   - High: Deep focus work (studying, writing, problem-solving)
   - Medium: Moderate tasks (reading, practice problems)
   - Low: Light work (organizing, reviewing, admin tasks)

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal to stop the server.

## 🆘 Troubleshooting

### Port Already in Use
If port 8000 is busy, run:
```bash
uvicorn app.main:app --reload --port 8001
```
Then access at: http://localhost:8001

### Dependencies Not Installing
Make sure you're in the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Database Issues
Delete the database and restart:
```bash
rm taskrhythm.db
# Restart the server - database will be recreated
```

## 📚 Need More Help?

See the full [README.md](README.md) for:
- Complete feature documentation
- API endpoints reference
- Architecture details
- Security information

---

**Remember**: Work with your energy, not against it! 💙

