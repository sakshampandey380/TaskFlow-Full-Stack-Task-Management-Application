/**
 * TaskFlow - Application Main Entry Point
 * Orchestrates modules, keyboard shortcuts, modal triggers, and global event listeners.
 */

const App = {
  async init() {
    console.log("🚀 Initializing TaskFlow...");

    // 1. Initialize Theme (Light / Dark)
    UI.initTheme();

    // 2. Setup Global Listeners & Keyboard Shortcuts
    this.setupGlobalListeners();
    this.setupKeyboardShortcuts();

    // 3. Initialize Filters & UI Components
    Filters.init();
    await Tasks.init();

    // 4. Initialize Auth and verify session
    const isAuthed = await Auth.init();
    if (isAuthed) {
      await this.loadAppData();
    }
  },

  async loadAppData() {
    await Tasks.loadAll();
  },

  setupGlobalListeners() {
    // Theme Toggle Button
    const themeBtn = document.getElementById("themeToggleBtn");
    if (themeBtn) {
      themeBtn.addEventListener("click", () => UI.toggleTheme());
    }

    // Mobile Menu Button & Backdrop
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const sidebarBackdrop = document.getElementById("sidebarBackdrop");
    if (mobileMenuBtn) {
      mobileMenuBtn.addEventListener("click", () => UI.openMobileSidebar());
    }
    if (sidebarBackdrop) {
      sidebarBackdrop.addEventListener("click", () => UI.closeMobileSidebar());
    }

    // Add Task Buttons (Top Nav, Main View, and Mobile FAB)
    const addBtns = [
      document.getElementById("openAddTaskBtn"),
      document.getElementById("mobileFabBtn"),
      document.getElementById("sidebarAddTaskBtn")
    ];
    addBtns.forEach(btn => {
      if (btn) btn.addEventListener("click", () => Tasks.openCreateModal());
    });

    // Profile Dropdown Toggle
    const profileBtn = document.getElementById("userProfileBtn");
    const profileDropdown = document.getElementById("profileDropdown");
    if (profileBtn && profileDropdown) {
      profileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        if (!Auth.isAuthenticated()) {
          Auth.showAuthModal("login");
          return;
        }
        profileDropdown.classList.toggle("active");
      });

      document.addEventListener("click", (e) => {
        if (!profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
          profileDropdown.classList.remove("active");
        }
      });
    }

    // Modal Close Buttons (any element with [data-close-modal])
    document.querySelectorAll("[data-close-modal]").forEach(btn => {
      btn.addEventListener("click", () => {
        const modalId = btn.getAttribute("data-close-modal");
        UI.closeModal(modalId || null);
      });
    });

    // Click outside modal card to close
    document.querySelectorAll(".modal-overlay").forEach(overlay => {
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) {
          UI.closeModal(overlay.id);
        }
      });
    });

    // Seed Demo Data button inside user profile dropdown
    const seedDemoBtn = document.getElementById("seedDemoMenuBtn");
    if (seedDemoBtn) {
      seedDemoBtn.addEventListener("click", async () => {
        if (profileDropdown) profileDropdown.classList.remove("active");
        try {
          UI.showToast("Seeding Data", "Populating realistic sample tasks and categories...", "info");
          const resp = await API.seedDemoData();
          UI.showToast("Data Ready", resp.message || "Sample tasks loaded successfully! ✨", "success");
          await this.loadAppData();
        } catch (err) {
          UI.showToast("Seed Error", err.message, "error");
        }
      });
    }

    // New Category Modal Trigger & Form
    const openAddCategoryBtn = document.getElementById("openAddCategoryBtn");
    if (openAddCategoryBtn) {
      openAddCategoryBtn.addEventListener("click", () => {
        const form = document.getElementById("categoryForm");
        if (form) form.reset();
        UI.openModal("categoryModal");
      });
    }

    const categoryForm = document.getElementById("categoryForm");
    if (categoryForm) {
      categoryForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const nameInput = document.getElementById("categoryNameInput");
        const colorInput = document.getElementById("categoryColorInput");
        const nameVal = nameInput.value.trim();

        if (!nameVal) {
          UI.showToast("Validation Error", "Category name cannot be empty.", "warning");
          nameInput.focus();
          return;
        }

        try {
          await API.createCategory({
            name: nameVal,
            color: colorInput.value || "#4F46E5"
          });
          UI.closeModal("categoryModal");
          UI.showToast("Success", `Category "${nameVal}" created!`, "success");
          await this.loadAppData();
        } catch (err) {
          UI.showToast("Category Error", err.message, "error");
        }
      });
    }

    // Keyboard Shortcuts Dialog Trigger
    const shortcutsBtn = document.getElementById("shortcutsMenuBtn");
    if (shortcutsBtn) {
      shortcutsBtn.addEventListener("click", () => {
        if (profileDropdown) profileDropdown.classList.remove("active");
        UI.openModal("shortcutsModal");
      });
    }
  },

  setupKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
      const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : "";
      const isInputActive = activeTag === "input" || activeTag === "textarea" || activeTag === "select";

      // ESC: Close open modal or mobile sidebar
      if (e.key === "Escape") {
        if (UI.activeModal) {
          UI.closeModal();
          return;
        }
        UI.closeMobileSidebar();
      }

      // Ctrl + K or '/': Focus global search
      if ((e.ctrlKey && e.key.toLowerCase() === "k") || (e.key === "/" && !isInputActive)) {
        e.preventDefault();
        const searchInput = document.getElementById("globalSearchInput");
        if (searchInput) {
          searchInput.focus();
          searchInput.select();
        }
        return;
      }

      // 'c' or Ctrl + N: Open New Task Modal (only when not typing in form)
      if ((e.key.toLowerCase() === "c" && !isInputActive && !e.ctrlKey && !e.metaKey) || (e.ctrlKey && e.key.toLowerCase() === "n")) {
        e.preventDefault();
        if (Auth.isAuthenticated()) {
          Tasks.openCreateModal();
        }
      }

      // '?': Open Keyboard shortcuts
      if (e.key === "?" && !isInputActive) {
        e.preventDefault();
        UI.openModal("shortcutsModal");
      }
    });
  }
};

// Start application when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
