/**
 * TaskFlow - Filters, Search, and Navigation Controller
 * Coordinates sidebar navigation tabs, global search, status/priority/category filters, and sorting.
 */

const Filters = {
  activeNav: "all", // 'all' | 'today' | 'upcoming' | 'completed' | 'important' | 'category'
  searchQuery: "",
  statusFilter: "",
  priorityFilter: "",
  categoryFilter: null,
  sortBy: "newest",
  order: "desc",

  init() {
    this.setupNavigation();
    this.setupSearch();
    this.setupDropdowns();
  },

  setupNavigation() {
    const navButtons = document.querySelectorAll(".sidebar-main-nav .nav-item-btn");
    navButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        navButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        const target = btn.getAttribute("data-nav");
        this.setNavigation(target);

        // Close mobile drawer on item selection
        UI.closeMobileSidebar();
      });
    });
  },

  setNavigation(navTarget) {
    this.activeNav = navTarget;
    this.categoryFilter = null; // Clear category filter if changing main tab

    // Update View Title
    const titleMap = {
      dashboard: "Dashboard Overview",
      all: "All Tasks",
      today: "Today's Tasks",
      upcoming: "Upcoming Tasks",
      completed: "Completed Tasks",
      important: "Important Tasks"
    };

    const viewTitle = document.getElementById("viewTitle");
    if (viewTitle) viewTitle.textContent = titleMap[navTarget] || "Tasks";

    this.applyFilters();
  },

  setCategoryFilter(categoryId) {
    this.activeNav = "category";
    this.categoryFilter = categoryId;

    // Deselect main nav buttons
    document.querySelectorAll(".sidebar-main-nav .nav-item-btn").forEach(b => b.classList.remove("active"));

    // Find category name
    const cat = Tasks.categories.find(c => c.id === categoryId);
    const viewTitle = document.getElementById("viewTitle");
    if (viewTitle && cat) {
      viewTitle.textContent = `Category: ${cat.name}`;
    }

    // Sync dropdown
    const catSelect = document.getElementById("filterCategory");
    if (catSelect) catSelect.value = categoryId;

    UI.closeMobileSidebar();
    this.applyFilters();
  },

  setupSearch() {
    const searchInput = document.getElementById("globalSearchInput");
    if (!searchInput) return;

    searchInput.addEventListener(
      "input",
      Utils.debounce((e) => {
        this.searchQuery = e.target.value.trim();
        this.applyFilters();
      }, 300)
    );
  },

  setupDropdowns() {
    const statusSelect = document.getElementById("filterStatus");
    const prioritySelect = document.getElementById("filterPriority");
    const categorySelect = document.getElementById("filterCategory");
    const sortSelect = document.getElementById("sortBySelect");

    if (statusSelect) {
      statusSelect.addEventListener("change", (e) => {
        this.statusFilter = e.target.value;
        this.applyFilters();
      });
    }

    if (prioritySelect) {
      prioritySelect.addEventListener("change", (e) => {
        this.priorityFilter = e.target.value;
        this.applyFilters();
      });
    }

    if (categorySelect) {
      categorySelect.addEventListener("change", (e) => {
        this.categoryFilter = e.target.value ? parseInt(e.target.value) : null;
        this.applyFilters();
      });
    }

    if (sortSelect) {
      sortSelect.addEventListener("change", (e) => {
        const val = e.target.value;
        if (val === "oldest") {
          this.sortBy = "oldest";
          this.order = "asc";
        } else if (val === "due_date") {
          this.sortBy = "due_date";
          this.order = "asc";
        } else if (val === "priority") {
          this.sortBy = "priority";
          this.order = "desc";
        } else if (val === "title") {
          this.sortBy = "title";
          this.order = "asc";
        } else {
          this.sortBy = "newest";
          this.order = "desc";
        }
        this.applyFilters();
      });
    }
  },

  /**
   * Aggregate active criteria into query params and trigger API reload
   */
  applyFilters() {
    const params = {
      sort_by: this.sortBy,
      order: this.order
    };

    if (this.searchQuery) {
      params.search = this.searchQuery;
    }

    // Navigation filters
    if (this.activeNav === "today") {
      params.due_filter = "today";
    } else if (this.activeNav === "upcoming") {
      params.due_filter = "upcoming";
    } else if (this.activeNav === "completed") {
      params.status = "completed";
    } else if (this.activeNav === "important") {
      params.is_important = true;
    }

    // Status filter dropdown (overrides navigation status if specified)
    if (this.statusFilter) {
      params.status = this.statusFilter;
    }

    // Priority filter
    if (this.priorityFilter) {
      params.priority = this.priorityFilter;
    }

    // Category filter
    if (this.categoryFilter) {
      params.category_id = this.categoryFilter;
    }

    Tasks.loadAll(params);
  },

  resetAllFilters() {
    this.searchQuery = "";
    this.statusFilter = "";
    this.priorityFilter = "";
    this.categoryFilter = null;
    this.sortBy = "newest";
    this.order = "desc";

    const searchInput = document.getElementById("globalSearchInput");
    if (searchInput) searchInput.value = "";

    const statusSelect = document.getElementById("filterStatus");
    if (statusSelect) statusSelect.value = "";

    const prioritySelect = document.getElementById("filterPriority");
    if (prioritySelect) prioritySelect.value = "";

    const catSelect = document.getElementById("filterCategory");
    if (catSelect) catSelect.value = "";

    const sortSelect = document.getElementById("sortBySelect");
    if (sortSelect) sortSelect.value = "newest";

    this.setNavigation("all");
  }
};
