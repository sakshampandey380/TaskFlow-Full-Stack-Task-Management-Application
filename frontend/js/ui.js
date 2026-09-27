/**
 * TaskFlow - UI Manager
 * Toast notifications, Theme toggling, Modal controls, and Skeleton loading.
 */

const UI = {
  activeModal: null,

  /**
   * Initialize theme from localStorage or system preference
   */
  initTheme() {
    const savedTheme = localStorage.getItem(CONFIG.STORAGE_KEYS.THEME) || "light";
    this.setTheme(savedTheme);
  },

  /**
   * Set theme ('light' or 'dark') and persist
   */
  setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(CONFIG.STORAGE_KEYS.THEME, theme);

    const themeToggleBtn = document.getElementById("themeToggleBtn");
    if (themeToggleBtn) {
      themeToggleBtn.innerHTML = theme === "dark" 
        ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`
        : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
      themeToggleBtn.setAttribute("title", theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode");
    }
  },

  toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    this.setTheme(next);

    // If authenticated, sync with backend settings silently
    if (API.getToken()) {
      API.updateSettings({ theme: next }).catch(() => {});
    }
  },

  /**
   * Display accessible toast message
   * @param {string} title
   * @param {string} message
   * @param {'success'|'error'|'warning'|'info'} type
   * @param {number} duration ms
   */
  showToast(title, message = "", type = "info", duration = 3500) {
    let container = document.getElementById("toastContainer");
    if (!container) {
      container = document.createElement("div");
      container.id = "toastContainer";
      container.className = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let iconSvg = "";
    if (type === "success") {
      iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    } else if (type === "error") {
      iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
    } else if (type === "warning") {
      iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
    } else {
      iconSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
    }

    toast.innerHTML = `
      <div class="toast-icon">${iconSvg}</div>
      <div class="toast-content">
        <div class="toast-title">${Utils.escapeHtml(title)}</div>
        ${message ? `<div class="toast-message">${Utils.escapeHtml(message)}</div>` : ""}
      </div>
      <button type="button" class="toast-close" aria-label="Close notification">&times;</button>
    `;

    container.appendChild(toast);

    // Trigger entrance animation
    requestAnimationFrame(() => {
      toast.classList.add("show");
    });

    const removeToast = () => {
      toast.classList.remove("show");
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    };

    toast.querySelector(".toast-close").addEventListener("click", removeToast);
    setTimeout(removeToast, duration);
  },

  /**
   * Open Modal dialog with accessible focus management
   */
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.add("active");
    this.activeModal = modal;
    document.body.style.overflow = "hidden";

    // Auto-focus first input or primary button
    setTimeout(() => {
      const focusable = modal.querySelector("input:not([type=hidden]), textarea, select, button.btn-primary");
      if (focusable) focusable.focus();
    }, 50);
  },

  /**
   * Close Modal dialog
   */
  closeModal(modalId = null) {
    const modal = modalId ? document.getElementById(modalId) : this.activeModal;
    if (!modal) return;

    modal.classList.remove("active");
    if (this.activeModal === modal) {
      this.activeModal = null;
    }
    document.body.style.overflow = "";
  },

  /**
   * Mobile Sidebar Drawer Controls
   */
  openMobileSidebar() {
    const sidebar = document.getElementById("appSidebar");
    const backdrop = document.getElementById("sidebarBackdrop");
    if (sidebar) sidebar.classList.add("open");
    if (backdrop) backdrop.classList.add("active");
  },

  closeMobileSidebar() {
    const sidebar = document.getElementById("appSidebar");
    const backdrop = document.getElementById("sidebarBackdrop");
    if (sidebar) sidebar.classList.remove("open");
    if (backdrop) backdrop.classList.remove("active");
  },

  /**
   * Render loading skeleton cards
   */
  renderTaskSkeletons(container, count = 5) {
    let skeletonsHtml = "";
    for (let i = 0; i < count; i++) {
      skeletonsHtml += `
        <div class="skeleton-card">
          <div class="skeleton" style="width: 22px; height: 22px; border-radius: 6px;"></div>
          <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
            <div class="skeleton" style="width: ${50 + Math.floor(Math.random() * 35)}%; height: 16px;"></div>
            <div class="skeleton" style="width: 80%; height: 12px;"></div>
            <div style="display: flex; gap: 8px; margin-top: 4px;">
              <div class="skeleton" style="width: 60px; height: 18px; border-radius: 99px;"></div>
              <div class="skeleton" style="width: 70px; height: 18px; border-radius: 99px;"></div>
            </div>
          </div>
        </div>
      `;
    }
    container.innerHTML = skeletonsHtml;
  }
};
