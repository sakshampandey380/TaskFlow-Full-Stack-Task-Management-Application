/**
 * TaskFlow - Authentication Manager
 * Handles login, registration, demo auto-fill, session validation, and logout.
 */

const Auth = {
  user: null,

  isAuthenticated() {
    return !!API.getToken();
  },

  async init() {
    this.setupEventListeners();

    const token = API.getToken();
    if (token) {
      try {
        const resp = await API.getMe();
        if (resp && resp.data) {
          this.user = resp.data;
          this.updateUserUI(this.user);
          return true;
        }
      } catch (err) {
        console.warn("Session expired or invalid token:", err.message);
        API.setToken(null);
      }
    }

    // If no authenticated session, show Auth Modal or offer demo login
    this.showAuthModal("login");
    return false;
  },

  updateUserUI(user) {
    const avatarElem = document.getElementById("userAvatar");
    const nameElem = document.getElementById("userNameLabel");
    const emailElem = document.getElementById("dropdownUserEmail");
    const profileDropdown = document.getElementById("profileDropdownWrapper");

    if (user) {
      if (avatarElem) avatarElem.textContent = Utils.getInitials(user.name);
      if (nameElem) nameElem.textContent = user.name;
      if (emailElem) emailElem.textContent = user.email;
      if (profileDropdown) profileDropdown.style.display = "block";
    } else {
      if (avatarElem) avatarElem.textContent = "?";
      if (nameElem) nameElem.textContent = "Sign In";
      if (emailElem) emailElem.textContent = "";
    }
  },

  showAuthModal(mode = "login") {
    const authModal = document.getElementById("authModal");
    if (!authModal) return;

    this.setAuthMode(mode);
    UI.openModal("authModal");
  },

  setAuthMode(mode) {
    const isLogin = mode === "login";
    document.getElementById("authTitle").textContent = isLogin ? "Welcome to TaskFlow" : "Create your Account";
    document.getElementById("authSubtitle").textContent = isLogin 
      ? "Sign in to manage and streamline your daily productivity" 
      : "Start organizing your tasks with modern productivity tools";

    const nameGroup = document.getElementById("authNameGroup");
    if (nameGroup) nameGroup.style.display = isLogin ? "none" : "block";

    const submitBtn = document.getElementById("authSubmitBtn");
    if (submitBtn) submitBtn.textContent = isLogin ? "Sign In" : "Create Account";

    const toggleText = document.getElementById("authToggleText");
    const toggleBtn = document.getElementById("authToggleModeBtn");
    if (toggleText && toggleBtn) {
      toggleText.textContent = isLogin ? "Don't have an account?" : "Already have an account?";
      toggleBtn.textContent = isLogin ? "Register now" : "Sign in";
      toggleBtn.setAttribute("data-mode", isLogin ? "register" : "login");
    }
  },

  async handleFormSubmit(e) {
    e.preventDefault();
    const toggleBtn = document.getElementById("authToggleModeBtn");
    const mode = toggleBtn.getAttribute("data-mode") === "register" ? "login" : "register";

    const emailInput = document.getElementById("authEmail");
    const passInput = document.getElementById("authPassword");
    const nameInput = document.getElementById("authName");

    const emailError = document.getElementById("authEmailError");
    const passError = document.getElementById("authPasswordError");
    const nameError = document.getElementById("authNameError");

    const submitBtn = document.getElementById("authSubmitBtn");

    if (mode === "login") {
      if (!Validation.validateLoginForm({ emailInput, emailError, passInput, passError })) {
        return;
      }
    } else {
      if (!Validation.validateRegisterForm({ nameInput, nameError, emailInput, emailError, passInput, passError })) {
        return;
      }
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner"></span> Processing...`;

      let resp;
      if (mode === "login") {
        resp = await API.login(emailInput.value.trim(), passInput.value);
      } else {
        resp = await API.register(nameInput.value.trim(), emailInput.value.trim(), passInput.value);
      }

      if (resp && resp.data && resp.data.access_token) {
        API.setToken(resp.data.access_token);
        this.user = resp.data.user;
        this.updateUserUI(this.user);
        UI.closeModal("authModal");
        UI.showToast("Success", resp.message || `Welcome to TaskFlow, ${this.user.name}!`, "success");

        // Reload app data
        if (window.App && typeof window.App.loadAppData === "function") {
          window.App.loadAppData();
        }
      }
    } catch (err) {
      UI.showToast("Authentication Failed", err.message, "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = mode === "login" ? "Sign In" : "Create Account";
    }
  },

  async loginWithDemo() {
    const emailInput = document.getElementById("authEmail");
    const passInput = document.getElementById("authPassword");
    if (emailInput && passInput) {
      emailInput.value = CONFIG.DEMO_CREDENTIALS.email;
      passInput.value = CONFIG.DEMO_CREDENTIALS.password;
    }

    const submitBtn = document.getElementById("authSubmitBtn");
    try {
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner"></span> Logging in...`;
      }
      const resp = await API.login(CONFIG.DEMO_CREDENTIALS.email, CONFIG.DEMO_CREDENTIALS.password);
      if (resp && resp.data && resp.data.access_token) {
        API.setToken(resp.data.access_token);
        this.user = resp.data.user;
        this.updateUserUI(this.user);
        UI.closeModal("authModal");
        UI.showToast("Demo Loaded", `Signed in as ${this.user.name}`, "success");
        if (window.App && typeof window.App.loadAppData === "function") {
          window.App.loadAppData();
        }
      }
    } catch (err) {
      UI.showToast("Demo Error", err.message, "error");
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Sign In";
      }
    }
  },

  logout() {
    API.setToken(null);
    this.user = null;
    this.updateUserUI(null);
    UI.showToast("Signed Out", "You have been successfully logged out.", "info");
    this.showAuthModal("login");
  },

  handleSessionExpired() {
    UI.showToast("Session Expired", "Your session has expired. Please sign in again.", "warning");
    this.showAuthModal("login");
  },

  setupEventListeners() {
    const authForm = document.getElementById("authForm");
    if (authForm) {
      authForm.addEventListener("submit", (e) => this.handleFormSubmit(e));
    }

    const toggleModeBtn = document.getElementById("authToggleModeBtn");
    if (toggleModeBtn) {
      toggleModeBtn.addEventListener("click", () => {
        const targetMode = toggleModeBtn.getAttribute("data-mode");
        this.setAuthMode(targetMode);
      });
    }

    const demoLoginBtn = document.getElementById("demoLoginBtn");
    if (demoLoginBtn) {
      demoLoginBtn.addEventListener("click", () => this.loginWithDemo());
    }

    const logoutBtn = document.getElementById("logoutMenuBtn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => this.logout());
    }
  }
};
