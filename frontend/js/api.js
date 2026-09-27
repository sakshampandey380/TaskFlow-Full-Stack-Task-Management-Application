/**
 * TaskFlow - Centralized REST API Client
 * Handles HTTP requests, JWT token authorization, and unified error handling.
 */

const API = {
  getToken() {
    return localStorage.getItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
  },

  setToken(token) {
    if (token) {
      localStorage.setItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN, token);
    } else {
      localStorage.removeItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
    }
  },

  /**
   * Generic request executor
   */
  async request(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const token = this.getToken();

    const headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(options.headers || {})
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      let jsonResult = null;
      const text = await response.text();
      if (text) {
        try {
          jsonResult = JSON.parse(text);
        } catch {
          jsonResult = { message: text };
        }
      }

      if (!response.ok) {
        // Handle 401 Unauthorized: token expired or missing
        if (response.status === 401 && !endpoint.includes("/auth/login") && !endpoint.includes("/auth/register")) {
          this.setToken(null);
          if (window.Auth && typeof window.Auth.handleSessionExpired === "function") {
            window.Auth.handleSessionExpired();
          }
        }

        const errorMessage = (jsonResult && jsonResult.message) 
          ? jsonResult.message 
          : `Server returned HTTP ${response.status}: ${response.statusText}`;

        const error = new Error(errorMessage);
        error.status = response.status;
        error.data = jsonResult;
        throw error;
      }

      return jsonResult;
    } catch (err) {
      // Network failure or offline
      if (!err.status) {
        err.message = "Unable to connect to the TaskFlow server. Please check your network or verify the backend is running.";
      }
      throw err;
    }
  },

  /* --- Auth APIs --- */
  async register(name, email, password) {
    return this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password })
    });
  },

  async login(email, password) {
    return this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  },

  async getMe() {
    return this.request("/auth/me", { method: "GET" });
  },

  /* --- Task APIs --- */
  async getTasks(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== "") {
        query.append(key, val);
      }
    });
    const queryString = query.toString() ? `?${query.toString()}` : "";
    return this.request(`/tasks${queryString}`, { method: "GET" });
  },

  async getTaskById(taskId) {
    return this.request(`/tasks/${taskId}`, { method: "GET" });
  },

  async createTask(taskData) {
    return this.request("/tasks", {
      method: "POST",
      body: JSON.stringify(taskData)
    });
  },

  async updateTask(taskId, taskData) {
    return this.request(`/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(taskData)
    });
  },

  async toggleTaskComplete(taskId, completed = null) {
    const payload = completed !== null ? { completed } : {};
    return this.request(`/tasks/${taskId}/complete`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  },

  async deleteTask(taskId) {
    return this.request(`/tasks/${taskId}`, {
      method: "DELETE"
    });
  },

  async getStats() {
    return this.request("/tasks/stats", { method: "GET" });
  },

  async seedDemoData() {
    return this.request("/tasks/seed-demo", { method: "POST" });
  },

  /* --- Categories APIs --- */
  async getCategories() {
    return this.request("/categories", { method: "GET" });
  },

  async createCategory(categoryData) {
    return this.request("/categories", {
      method: "POST",
      body: JSON.stringify(categoryData)
    });
  },

  /* --- Settings APIs --- */
  async getSettings() {
    return this.request("/settings", { method: "GET" });
  },

  async updateSettings(settingsData) {
    return this.request("/settings", {
      method: "PUT",
      body: JSON.stringify(settingsData)
    });
  }
};
