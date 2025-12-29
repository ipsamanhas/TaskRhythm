# TaskRhythm

> Work with your energy, not against it

TaskRhythm is a human-centered productivity web application that helps students schedule academic tasks based on their natural energy levels instead of rigid time blocks, reducing burnout and guilt while improving productivity.

## 🌟 Features

- **Energy-Based Scheduling**: Define your daily energy windows (high, medium, low) to match your natural rhythm
- **Smart Task Assignment**: Automatically assigns tasks to appropriate energy windows using deterministic logic
- **Compassionate Design**: Guilt-free, non-judgmental interface with supportive messaging
- **No Tracking**: No surveillance or productivity metrics—just support for your natural patterns
- **Academic Focus**: Built specifically for students managing coursework and deadlines

## 🎯 Core Concept

Instead of forcing yourself to work on demanding tasks when your energy is low, TaskRhythm:

1. **Lets you define your energy windows** - When do you feel most alert? When do you need rest?
2. **Labels tasks by effort level** - High effort (deep work), medium effort (moderate focus), or low effort (routine tasks)
3. **Automatically matches tasks to windows** - High-effort tasks go to high-energy windows
4. **Prioritizes your wellbeing** - Flexible, compassionate, and judgment-free

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**

```bash
cd TaskRhythm
```

2. **Create a virtual environment** (recommended)

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**

```bash
cd backend
pip install -r requirements.txt
```

### Running the Application

1. **Start the FastAPI server**

```bash
# From the backend directory
uvicorn app.main:app --reload
```

2. **Open your browser**

Navigate to: `http://localhost:8000`

3. **Create an account**

- Click "Register here" on the landing page
- Enter your username, email, and password
- You'll be automatically logged in

## 📖 How to Use

### Step 1: Define Your Energy Windows

1. Navigate to **Energy Windows** from the dashboard
2. Add windows for different times of day and days of week
3. Label each window with your expected energy level:
   - 🔥 **High**: Alert, focused, ready for deep work
   - ⚡ **Medium**: Steady energy, good for moderate tasks
   - 🌙 **Low**: Need rest or can only handle light tasks

**Example Energy Windows:**

- Monday 9:00 AM - 11:00 AM: High Energy
- Monday 2:00 PM - 4:00 PM: Medium Energy
- Monday 8:00 PM - 9:00 PM: Low Energy

### Step 2: Add Your Tasks

1. Navigate to **Tasks** from the dashboard
2. Add your academic tasks with:
   - **Title**: Brief description (e.g., "Study for CMPUT 301 midterm")
   - **Effort Level**: High, Medium, or Low
   - **Duration**: Estimated time in minutes (optional)
   - **Deadline**: Due date (optional)

**Effort Level Guide:**

- **High**: Complex problem-solving, deep research, writing essays, learning new concepts
- **Medium**: Practice problems, reading assignments, note-taking, group work
- **Low**: Reviewing notes, organizing files, light reading, administrative tasks

### Step 3: Generate Your Schedule

1. Navigate to **Schedule** from the dashboard
2. Click **Generate Schedule**
3. TaskRhythm will automatically assign tasks to matching energy windows
4. View your personalized schedule organized by energy windows

### Step 4: Work at Your Best

- Follow your schedule and work during your natural energy peaks
- Mark tasks as complete when done
- Add new tasks and regenerate the schedule as needed

## 🏗️ Project Structure

```
TaskRhythm/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic validation schemas
│   │   ├── auth.py              # Authentication utilities
│   │   ├── scheduler.py         # Core scheduling algorithm
│   │   └── routers/             # API route handlers
│   │       ├── auth.py          # Authentication routes
│   │       ├── energy.py        # Energy windows CRUD
│   │       ├── tasks.py         # Tasks CRUD
│   │       └── schedule.py      # Schedule generation
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── energy_windows.html
│   │   ├── tasks.html
│   │   └── schedule.html
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── main.js
│   └── requirements.txt
├── taskrhythm.db                # SQLite database (created on first run)
└── README.md
```

## 🔧 Technical Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Templates**: Jinja2 (server-rendered HTML)
- **Authentication**: Session-based with secure cookies
- **Styling**: Custom CSS with responsive design
- **Validation**: Pydantic v2

## 🧠 Scheduling Algorithm

The scheduling algorithm uses deterministic effort-energy mapping:

1. **Priority Mapping**:
   - High-effort tasks → High-energy windows (fallback: medium)
   - Medium-effort tasks → Medium-energy windows (fallback: high or low)
   - Low-effort tasks → Low-energy windows (fallback: medium or high)

2. **Sorting**:
   - Tasks with deadlines are prioritized
   - Within deadline groups, tasks are sorted by effort level
   - Earlier tasks are scheduled first

3. **Capacity Management**:
   - Each window has a duration calculated from start/end times
   - Tasks are assigned only if the window has sufficient remaining capacity
   - Already-assigned tasks reduce available capacity

4. **Graceful Degradation**:
   - If no perfect match exists, the algorithm tries the next-best energy level
   - Unscheduled tasks are clearly shown with helpful messaging

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `GET /auth/logout` - Logout
- `GET /auth/me` - Get current user

### Energy Windows
- `GET /energy` - Energy windows page
- `GET /energy/windows` - List energy windows (JSON)
- `POST /energy/windows` - Create energy window
- `POST /energy/windows/{id}/delete` - Delete energy window

### Tasks
- `GET /tasks` - Tasks page
- `GET /tasks/list` - List tasks (JSON)
- `POST /tasks/create` - Create task
- `POST /tasks/{id}/complete` - Toggle completion
- `POST /tasks/{id}/delete` - Delete task

### Schedule
- `GET /schedule` - Schedule view page
- `POST /schedule/generate` - Run scheduling algorithm
- `POST /schedule/clear` - Clear all assignments

## 🛡️ Security

- Passwords are hashed using bcrypt
- Session-based authentication with signed cookies
- CSRF protection via session middleware
- Input validation using Pydantic schemas
- SQL injection protection via SQLAlchemy ORM

## 🎨 Design Philosophy

TaskRhythm is built on principles of **compassionate computing**:

- **No Guilt**: No productivity tracking, no judgment, no shame
- **Autonomy**: You control your schedule and energy definitions
- **Flexibility**: Easy to adjust and reschedule as life happens
- **Support**: Helpful messaging that empowers rather than pressures
- **Human-Centered**: Technology that adapts to you, not the other way around

## 🚧 Known Limitations (MVP)

- Energy windows are defined weekly (not flexible across dates)
- No task dependencies or subtasks
- Schedule is regenerated fresh each time (doesn't preserve manual adjustments)
- Single-user sessions (no concurrent user handling optimization)
- No mobile app (web-only)

## 🔮 Future Enhancements

Potential features for future versions:

- Drag-and-drop schedule editing
- Recurring tasks
- Task templates for common academic work
- Energy level tracking to improve window definitions
- Integration with calendar apps
- Multi-week view
- Task notes and attachments
- Study break reminders

## 🤝 Contributing

This is an MVP built for educational purposes. Contributions, suggestions, and feedback are welcome!

## 📄 License

This project is open source and available for educational and personal use.

## 🙏 Acknowledgments

Built with care for students who are tired of productivity systems that make them feel guilty for being human.

---

**Remember**: Your energy ebbs and flows. That's natural. TaskRhythm helps you work *with* that rhythm, not against it. 💙

