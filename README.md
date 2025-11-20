# Learning Management System (LMS)

A full-stack Learning Management System built with React + TypeScript (frontend) and Flask + Python (backend).

## 📁 Project Structure

```
project/
│
├── frontend/                    # React + TypeScript Frontend
│   ├── src/                    # Source code
│   │   ├── components/         # React components
│   │   ├── config/             # Configuration files
│   │   ├── contexts/           # React contexts (Auth, LMS)
│   │   ├── hooks/              # Custom React hooks
│   │   ├── pages/              # Page components
│   │   ├── services/           # API service layer
│   │   ├── types/              # TypeScript type definitions
│   │   ├── utils/              # Utility functions
│   │   └── test/               # Frontend tests
│   ├── dist/                   # Build output (gitignored)
│   ├── node_modules/           # Dependencies (gitignored)
│   ├── package.json            # Frontend dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── vitest.config.ts        # Vitest test configuration
│   ├── tsconfig.json           # TypeScript configuration
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   └── eslint.config.js        # ESLint configuration
│
├── backend/                     # Flask + Python Backend
│   ├── routes/                 # API route handlers
│   │   ├── auth.py            # Authentication
│   │   ├── courses.py         # Course management
│   │   ├── assignments.py     # Assignments
│   │   ├── users.py           # User management
│   │   ├── ai.py              # AI features
│   │   ├── analytics.py       # Analytics
│   │   └── ...                # Other routes
│   ├── services/               # Business logic layer
│   ├── utils/                  # Utility functions
│   ├── tests/                  # Backend tests
│   ├── scripts/                # Utility scripts
│   │   ├── seeders/           # Database seeders
│   │   ├── generate_test_users.py
│   │   ├── reset_admin_password.py
│   │   └── token_cleanup.py
│   ├── uploads/                # User uploaded files
│   │   ├── assignments/       # Assignment submissions
│   │   ├── documents/         # Course documents
│   │   ├── thumbnails/        # Course thumbnails
│   │   └── videos/            # Video files
│   ├── logs/                   # Application logs
│   ├── app.py                  # Flask application
│   ├── run.py                  # Application entry point
│   ├── gunicorn_config.py      # Gunicorn configuration
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment template
│
├── .git/                       # Git repository
├── .kiro/                      # Kiro IDE settings
├── .vscode/                    # VS Code settings
├── .gitignore                  # Git ignore rules
├── deploy.sh                   # Deployment script
├── PROJECT_STRUCTURE.md        # Detailed structure documentation
└── README.md                   # This file
```

## 🚀 Getting Started

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173`

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python run.py
```

The backend API will run on `http://localhost:5000`

## 🔧 Environment Variables

1. Copy `.env.example` to `.env` in the backend directory
2. Configure your environment variables (MongoDB, JWT secret, etc.)

## 📦 Available Scripts

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

### Backend
- `python run.py` - Start Flask server
- `pytest` - Run backend tests

## 🌐 Deployment

Use `deploy.sh` for production deployment to your hosting platform.

## 🛠️ Tech Stack

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Supabase Client
- React Markdown

**Backend:**
- Flask
- MongoDB (PyMongo)
- JWT Authentication
- Google Generative AI
- Gunicorn
