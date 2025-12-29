# TaskRhythm

TaskRhythm is a human-centered productivity web application that helps students schedule academic tasks based on their natural energy levels rather than rigid time blocks. By aligning work with energy rhythms, TaskRhythm aims to reduce burnout and guilt while supporting sustainable productivity.

## 🌟 Features

- **Energy-Based Scheduling**: Define your daily energy windows (high, medium, low) to match your natural rhythm
- **Smart Task Assignment**: Automatically assigns tasks to appropriate energy windows using deterministic logic
- **Compassionate Design**: Guilt-free, non-judgmental interface with supportive messaging
- **Privacy-First Design**: No surveillance, productivity scoring, or behavioral analytics—only the data required to generate schedules
- **Academic Focus**: Built specifically for students managing coursework and deadlines

## 🎯 Core Concept

Instead of forcing yourself to work on demanding tasks when your energy is low, TaskRhythm:

1. **Lets you define your energy windows** - When do you feel most alert? When do you need rest?
2. **Labels tasks by effort level** - High effort (deep work), medium effort (moderate focus), or low effort (routine tasks)
3. **Automatically matches tasks to windows** - High-effort tasks go to high-energy windows
4. **Prioritizes your wellbeing** - Flexible, compassionate, and judgment-free


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

