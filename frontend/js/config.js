/**
 * TaskFlow - Configuration & Constants
 */
const CONFIG = {
  // Determine API base URL dynamically: if served directly via FastAPI on :8000, use /api;
  // if served via Live Server on :5500 or Apache, point to http://localhost:8000/api
  API_BASE_URL: (window.location.port === "8000") 
    ? "/api" 
    : "http://localhost:8000/api",

  STORAGE_KEYS: {
    AUTH_TOKEN: "taskflow_jwt_token",
    USER_DATA: "taskflow_user_data",
    THEME: "taskflow_theme_preference",
    VIEW_MODE: "taskflow_view_mode", // 'list' | 'grid'
  },

  PRIORITIES: {
    low: { label: "Low", color: "#64748B", bg: "rgba(100, 116, 139, 0.12)" },
    medium: { label: "Medium", color: "#3B82F6", bg: "rgba(59, 130, 246, 0.12)" },
    high: { label: "High", color: "#F97316", bg: "rgba(249, 115, 22, 0.12)" },
    urgent: { label: "Urgent", color: "#EF4444", bg: "rgba(239, 68, 68, 0.12)" }
  },

  STATUSES: {
    pending: { label: "Pending", color: "#F59E0B" },
    in_progress: { label: "In Progress", color: "#8B5CF6" },
    completed: { label: "Completed", color: "#10B981" }
  },

  DEMO_CREDENTIALS: {
    email: "demo@taskflow.dev",
    password: "Password123!"
  }
};
