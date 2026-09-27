# TaskFlow — Production-Ready Full-Stack Task & Productivity Management

> A high-performance, modern SaaS-style productivity application engineered with a **FastAPI (Python)** backend, **MySQL / MariaDB (XAMPP)** relational persistence, and a responsive **Vanilla HTML5 / Modern CSS / JavaScript** frontend.

![TaskFlow Logo](frontend/assets/favicon.svg)

---

## 🌟 Overview

**TaskFlow** is designed from the ground up to reflect modern productivity dashboards like Linear, Todoist, and Notion. It goes far beyond typical toy CRUD tutorials by featuring:

- Real-time task progress computation and statistics tracking
- Full user authentication with **JWT** and **bcrypt** password hashing
- Relational data modeling with foreign keys, many-to-many tag relationships, and cascade behaviors
- Instant optimistic UI checkbox updates synchronized directly to MySQL
- Keyboard shortcuts for rapid power-user productivity (`Ctrl+K`, `C`, `Esc`, `?`)
- Seamless Light / Dark theme system with persistent storage
- Interactive, accessible modals adhering to modern web accessibility principles

---

## 🛠 Tech Stack

| Domain | Technology | Details |
| :--- | :--- | :--- |
| **Backend** | **Python 3.11+ / FastAPI** | High performance asynchronous REST API with Pydantic v2 schemas and validation |
| **Database** | **MySQL (InnoDB) via XAMPP** | Database: `todo-application` with UTF-8 (`utf8mb4_unicode_ci`) encoding |
| **ORM** | **SQLAlchemy 2.0 + PyMySQL** | Connection pooling, relational mappings, cascades, indexes |
| **Authentication** | **JWT (python-jose) + bcrypt** | Secure Bearer authorization header with salted hashing |
| **Frontend** | **HTML5, CSS3, Vanilla JS** | Modular architecture, design tokens, zero-build-step requirement |
| **Testing** | **unittest & FastAPI TestClient** | Automated integration tests for auth, CRUD, validation, 404s, stats |

---

## 📁 Project Architecture

```text
QSkills - Task -1/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application, CORS, static mounts, exception handlers
│   │   ├── config.py            # Pydantic BaseSettings (.env reader)
│   │   ├── database.py          # SQLAlchemy engine, session maker, get_db dependency
│   │   ├── auth/
│   │   │   ├── security.py      # bcrypt hashing and JWT token generator
│   │   │   └── deps.py          # get_current_user dependency
│   │   ├── models/              # SQLAlchemy relational models
│   │   │   ├── user.py          # users table
│   │   │   ├── task.py          # tasks table
│   │   │   ├── category.py      # categories table
│   │   │   ├── tag.py           # tags and task_tags association table
│   │   │   ├── reminder.py      # task_reminders table
│   │   │   └── settings.py      # user_settings table
│   │   ├── schemas/             # Pydantic validation schemas
│   │   │   ├── common.py        # Generic APIResponse envelope
│   │   │   ├── user.py          # UserRegister, UserLogin, UserOut
│   │   │   ├── task.py          # TaskCreate, TaskUpdate, TaskOut
│   │   │   ├── category.py      # Category schemas
│   │   │   ├── tag.py           # Tag schemas
│   │   │   └── stats.py         # TaskStatsOut schema
│   │   ├── routes/              # Modular API routers
│   │   │   ├── auth.py          # /api/auth (register, login, me, logout)
│   │   │   ├── tasks.py         # /api/tasks (CRUD, toggle-complete, stats, seed-demo)
│   │   │   ├── categories.py    # /api/categories (CRUD)
│   │   │   ├── tags.py          # /api/tags
│   │   │   └── settings.py      # /api/settings
│   │   └── services/            # Business logic
│   │       ├── task_service.py  # Filtering, searching, sorting, stats calculation
│   │       └── seed_service.py  # Realistic demo tasks and category seed generator
│   ├── tests/
│   │   └── test_api.py          # Comprehensive automated integration test suite
│   ├── seed_data.py             # CLI database seeding script
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Configuration template
│
├── frontend/
│   ├── index.html               # Semantic, accessible HTML5 dashboard
│   ├── css/
│   │   ├── style.css            # CSS variables, typography, reset, layout, dark theme
│   │   ├── components.css       # Buttons, cards, modals, toasts, skeletons, dropdowns
│   │   └── responsive.css       # Tablet and mobile optimizations, drawer, mobile FAB
│   ├── js/
│   │   ├── config.js            # Configuration & endpoints
│   │   ├── utils.js             # Date helpers, XSS sanitization, debounce
│   │   ├── api.js               # Centralized REST API client
│   │   ├── validation.js        # Client-side form input validation
│   │   ├── ui.js                # Toast system, theme toggling, modal controls
│   │   ├── auth.js              # Session state, login/register modal
│   │   ├── tasks.js             # Task card rendering, toggle complete, optimistic UI
│   │   ├── filters.js           # Navigation tabs, search bar, dropdown filters
│   │   └── app.js               # App bootstrap and keyboard shortcuts
│   └── assets/
│       └── favicon.svg          # Modern SVG icon
│
├── schema.sql                   # MySQL database creation script
├── seed_data.py                 # Root seed data script
├── run.py                       # Unified server launcher
├── requirements.txt             # Root dependencies
├── .env.example                 # Root environment template
└── README.md                    # Documentation
```

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.11)
- **MySQL / MariaDB via XAMPP** (Listening on `localhost:3306`)

### 2. Database Initialization
Ensure your XAMPP MySQL module is started.

Import the provided schema into MySQL:
```bash
mysql -u root -p < schema.sql
```
*(Or in phpMyAdmin, import `schema.sql` into the `todo-application` database).*

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` configuration:
```ini
PROJECT_NAME="TaskFlow"
VERSION="1.0.0"
API_V1_PREFIX="/api"
DATABASE_URL="mysql+pymysql://root:@localhost:3306/todo-application?charset=utf8mb4"
SECRET_KEY="taskflow_super_secret_production_key_change_in_real_deployment_64char"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 5. Seed Realistic Sample Data
Populate demo user, categories (Work, Personal, Study, Projects), and sample tasks:
```bash
python seed_data.py
```
**Demo Account Credentials:**
- **Email:** `demo@taskflow.dev`
- **Password:** `Password123!`

---

## 🚀 Running the Application

### Single Command Launcher (Serves Frontend & Backend Together):
```bash
python run.py
```
This boots the FastAPI application via Uvicorn on `http://localhost:8000/`.

- **Web Dashboard:** [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Automated Tests

Run the backend integration test suite:
```bash
python backend/tests/test_api.py
```
Tests cover:
- User registration and duplicate check
- JWT authentication and bad credentials rejection
- Fetching authenticated profile (`/api/auth/me`)
- Task creation with priority, tags, categories, and due dates
- Task search and filtering by query string
- Updating task title and priority
- Toggling task completion (persists in DB, updates `completed_at`)
- Calculation of live dashboard statistics
- Backend 422 validation errors
- 401 Unauthorized protection on private endpoints
- 404 Not Found handling
- Permanent task deletion

---

## 📡 REST API Reference

All responses return a uniform JSON envelope:
```json
{
  "success": true,
  "message": "Operation description",
  "data": { ... }
}
```

### Authentication (`/api/auth`)
- `POST /api/auth/register` — Create account, seeds defaults, returns JWT
- `POST /api/auth/login` — Login with email/password, returns JWT
- `GET  /api/auth/me` — Get authenticated user details *(Bearer token required)*
- `POST /api/auth/logout` — Logout user session

### Tasks (`/api/tasks`)
- `GET    /api/tasks` — List tasks *(Params: `search`, `status`, `priority`, `category_id`, `is_important`, `due_filter`, `sort_by`, `order`)*
- `GET    /api/tasks/stats` — Live statistics: total, completed, pending, overdue, completion rate %, priority and category breakdowns
- `POST   /api/tasks` — Create task with title, description, priority, category, due date/time, tags
- `GET    /api/tasks/{task_id}` — Get single task details
- `PUT    /api/tasks/{task_id}` — Update task details
- `PATCH  /api/tasks/{task_id}/complete` — Toggle or explicitly set task completion
- `DELETE /api/tasks/{task_id}` — Permanently delete task
- `POST   /api/tasks/seed-demo` — Populate sample tasks on-demand

### Categories (`/api/categories`)
- `GET    /api/categories` — List user categories with task counts
- `POST   /api/categories` — Create category with custom color & icon
- `PUT    /api/categories/{id}` — Update category
- `DELETE /api/categories/{id}` — Delete category *(tasks set to NULL)*

### User Settings (`/api/settings`)
- `GET /api/settings` — Get user preferences (theme, default priority)
- `PUT /api/settings` — Update preferences

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| <kbd>Ctrl</kbd> + <kbd>K</kbd> or <kbd>/</kbd> | Focus global search bar |
| <kbd>C</kbd> or <kbd>Ctrl</kbd> + <kbd>N</kbd> | Open **New Task** modal |
| <kbd>Esc</kbd> | Dismiss active modal or mobile drawer |
| <kbd>?</kbd> | Open Keyboard Shortcuts reference |

---

## 📸 Screenshots & UI Showcase

```
+----------------------------------------------------------------------------------------------------+
|  [Logo] TaskFlow      [ Search tasks, categories, #tags... (Ctrl+K) ]      [🌙] [🔔] [AM Alex M. ▾] |
+-----------------------+----------------------------------------------------------------------------+
|  VIEWS                |  All Tasks                                                  [+ Add Task]   |
|  • All Tasks       8  |  Organize, track progress, and accomplish goals seamlessly.                |
|  • Today           2  +----------------------------------------------------------------------------+
|  • Upcoming        4  | [TOTAL: 8]   [COMPLETED: 2]   [PENDING: 5]   [OVERDUE: 0]   [RATE: 25.0% ⭘] |
|  • Important       4  +----------------------------------------------------------------------------+
|  • Completed       2  | Filters: [All Statuses ▾] [All Priorities ▾] [All Categories ▾] [Sort ▾]   |
|                       +----------------------------------------------------------------------------+
|  CATEGORIES       [+] | [✓] Build FastAPI JWT authentication API              [URGENT] [Projects]  |
|  • Work            2  |     Implemented password hashing with bcrypt          Due Yesterday        |
|  • Personal        1  |     #backend #security                                [Edit] [Delete]      |
|  • Study           3  | -------------------------------------------------------------------------- |
|  • Projects        2  | [ ] Design responsive dashboard UI in TaskFlow        [HIGH]   [Work]      |
|                       |     Craft modern SaaS layout with sidebar & cards     Due Today            |
|  [+ Add New Task]     |     #frontend #ui #responsive                         [Edit] [Delete]      |
+-----------------------+----------------------------------------------------------------------------+
```

---

## 🛡 Security & Best Practices

1. **SQL Injection Prevention:** Uses SQLAlchemy parameterized queries and ORM object graphs.
2. **Password Security:** Salted hashes using **bcrypt**; raw passwords are never logged or stored.
3. **User Isolation:** All database queries strictly scope to `user_id = current_user.id`.
4. **Input Sanitization:** Frontend escapes HTML before rendering user strings; Pydantic strictly validates all JSON bodies.
5. **CORS Hardening:** Configurable allowed origins in `.env`.
6. **Graceful Fallbacks:** Connection pool pre-ping handles database connection drops seamlessly.

---

## 🔮 Future Enhancements

- WebSockets for real-time collaboration across multiple devices
- Email reminders via background Celery or APScheduler workers using `task_reminders`
- Drag-and-drop Kanban view option alongside List and Grid views
- Subtasks / checklists hierarchy inside tasks

---

## 📄 License
MIT License. Built with ❤️ for high-performance productivity.
