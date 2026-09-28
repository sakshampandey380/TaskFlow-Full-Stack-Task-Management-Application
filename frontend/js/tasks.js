/**
 * TaskFlow - Tasks Controller
 * Manages task CRUD operations, real-time checkbox completion syncing with MySQL,
 * optimistic UI updates, and statistics calculation.
 */

const Tasks = {
  items: [],
  categories: [],
  stats: null,
  activeTaskId: null,
  viewMode: "list", // 'list' or 'grid'

  async init() {
    this.viewMode = localStorage.getItem(CONFIG.STORAGE_KEYS.VIEW_MODE) || "list";
    this.applyViewMode(this.viewMode);
    this.setupEventListeners();
  },

  applyViewMode(mode) {
    this.viewMode = mode;
    localStorage.setItem(CONFIG.STORAGE_KEYS.VIEW_MODE, mode);
    const container = document.getElementById("tasksContainer");
    if (container) {
      if (mode === "grid") {
        container.classList.add("grid-view");
      } else {
        container.classList.remove("grid-view");
      }
    }

    const listBtn = document.getElementById("viewListBtn");
    const gridBtn = document.getElementById("viewGridBtn");
    if (listBtn && gridBtn) {
      listBtn.classList.toggle("active", mode === "list");
      gridBtn.classList.toggle("active", mode === "grid");
    }
  },

  /**
   * Load categories, tasks, and update dashboard statistics
   */
  async loadAll(filterParams = {}) {
    const container = document.getElementById("tasksContainer");
    if (container) UI.renderTaskSkeletons(container, 4);

    try {
      // Parallel fetch categories, tasks, and stats
      const [catsResp, tasksResp, statsResp] = await Promise.all([
        API.getCategories(),
        API.getTasks(filterParams),
        API.getStats()
      ]);

      if (catsResp && catsResp.data) {
        this.categories = catsResp.data;
        this.renderCategoriesSidebar(this.categories);
        this.populateCategoryDropdowns(this.categories);
      }

      if (tasksResp && tasksResp.data) {
        this.items = tasksResp.data;
        this.renderTasks(this.items);
      }

      if (statsResp && statsResp.data) {
        this.stats = statsResp.data;
        this.updateStatsUI(this.stats);
      }
    } catch (err) {
      if (container) {
        container.innerHTML = `
          <div class="empty-state">
            <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <h3 class="empty-state-title">Something went wrong</h3>
            <p class="empty-state-desc">${Utils.escapeHtml(err.message)}</p>
            <button class="btn btn-secondary" onclick="Tasks.loadAll()">Retry Loading</button>
          </div>
        `;
      }
    }
  },

  /**
   * Render task cards or rows
   */
  renderTasks(tasks) {
    const container = document.getElementById("tasksContainer");
    if (!container) return;

    if (!tasks || tasks.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <h3 class="empty-state-title">No tasks found</h3>
          <p class="empty-state-desc">Your task list is clear! Create your first task to start boosting productivity.</p>
          <button class="btn btn-primary" onclick="Tasks.openCreateModal()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            Create Task
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = tasks.map(task => this.generateTaskHtml(task)).join("");
  },

  generateTaskHtml(task) {
    const isCompleted = task.status === "completed";
    const priority = task.priority || "medium";
    const dueInfo = Utils.getRelativeDueDate(task.due_date, task.due_time);

    let dueBadgeHtml = "";
    if (dueInfo) {
      const cls = dueInfo.isOverdue ? "overdue" : (dueInfo.isToday ? "today" : "");
      dueBadgeHtml = `
        <span class="badge badge-due-date ${cls}" title="Due ${task.due_date}">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          ${dueInfo.text}
        </span>
      `;
    }

    let categoryBadgeHtml = "";
    if (task.category) {
      categoryBadgeHtml = `
        <span class="badge" style="background-color: ${task.category.color}15; color: ${task.category.color}; border: 1px solid ${task.category.color}30">
          <span class="category-dot" style="background-color: ${task.category.color}; width: 6px; height: 6px;"></span>
          ${Utils.escapeHtml(task.category.name)}
        </span>
      `;
    }

    let tagsHtml = "";
    if (task.tags && task.tags.length > 0) {
      tagsHtml = task.tags.map(t => `<span class="tag-pill">#${Utils.escapeHtml(t.name)}</span>`).join(" ");
    }

    const starClass = task.is_important ? "starred" : "";
    const starIcon = task.is_important
      ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="#F59E0B" stroke="#F59E0B" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`
      : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`;

    return `
      <div class="task-card ${isCompleted ? "completed" : ""}" id="task-card-${task.id}" data-id="${task.id}">
        <div class="task-checkbox-wrapper">
          <input 
            type="checkbox" 
            class="task-checkbox" 
            ${isCompleted ? "checked" : ""} 
            aria-label="Mark task as complete"
            onchange="Tasks.toggleComplete(${task.id}, this)"
          />
        </div>

        <div class="task-content">
          <div class="task-top-row">
            <h3 class="task-title">${Utils.escapeHtml(task.title)}</h3>
            <div class="task-actions">
              <button type="button" class="btn-icon-only star-btn ${starClass}" title="Toggle Star / Important" onclick="Tasks.toggleImportant(${task.id}, ${task.is_important ? "true" : "false"})">
                ${starIcon}
              </button>
              <button type="button" class="btn-icon-only" title="Edit Task" onclick="Tasks.openEditModal(${task.id})">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
              </button>
              <button type="button" class="btn-icon-only" title="Delete Task" onclick="Tasks.promptDelete(${task.id})">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
              </button>
            </div>
          </div>

          ${task.description ? `<p class="task-description">${Utils.escapeHtml(task.description)}</p>` : ""}

          <div class="task-meta-row">
            <span class="badge badge-priority-${priority}">
              ${priority}
            </span>
            ${categoryBadgeHtml}
            ${dueBadgeHtml}
            ${tagsHtml}
          </div>
        </div>
      </div>
    `;
  },

  /**
   * Toggle task completion with optimistic UI update and database synchronization
   */
  async toggleComplete(taskId, checkboxElem) {
    const card = document.getElementById(`task-card-${taskId}`);
    const isChecked = checkboxElem.checked;

    // Optimistic UI state
    if (card) {
      if (isChecked) {
        card.classList.add("completed");
      } else {
        card.classList.remove("completed");
      }
    }

    try {
      const resp = await API.toggleTaskComplete(taskId, isChecked);
      UI.showToast("Task Updated", isChecked ? "Task marked as completed! 🎉" : "Task marked as incomplete.", "success");

      // Refresh stats
      const statsResp = await API.getStats();
      if (statsResp && statsResp.data) {
        this.updateStatsUI(statsResp.data);
      }
    } catch (err) {
      // Revert optimistic UI on error
      if (card) {
        if (isChecked) {
          card.classList.remove("completed");
          checkboxElem.checked = false;
        } else {
          card.classList.add("completed");
          checkboxElem.checked = true;
        }
      }
      UI.showToast("Update Failed", err.message, "error");
    }
  },

  /**
   * Toggle Important / Star status
   */
  async toggleImportant(taskId, currentStatus) {
    try {
      await API.updateTask(taskId, { is_important: !currentStatus });
      UI.showToast("Task Updated", !currentStatus ? "Marked as Important" : "Removed from Important", "info");
      this.refreshCurrentView();
    } catch (err) {
      UI.showToast("Error", err.message, "error");
    }
  },

  /**
   * Update Dashboard Statistics Cards
   */
  updateStatsUI(stats) {
    this.stats = stats;
    const totalElem = document.getElementById("statTotalTasks");
    const completedElem = document.getElementById("statCompletedTasks");
    const pendingElem = document.getElementById("statPendingTasks");
    const overdueElem = document.getElementById("statOverdueTasks");
    const rateElem = document.getElementById("statCompletionRate");
    const circleBar = document.getElementById("statCircleBar");

    if (totalElem) totalElem.textContent = stats.total_tasks;
    if (completedElem) completedElem.textContent = stats.completed_tasks;
    if (pendingElem) pendingElem.textContent = stats.pending_tasks + stats.in_progress_tasks;
    if (overdueElem) overdueElem.textContent = stats.overdue_tasks;
    if (rateElem) rateElem.textContent = `${stats.completion_rate}%`;

    // Update circular gauge
    if (circleBar) {
      const radius = 20;
      const circumference = 2 * Math.PI * radius;
      const offset = circumference - (stats.completion_rate / 100) * circumference;
      circleBar.style.strokeDasharray = `${circumference} ${circumference}`;
      circleBar.style.strokeDashoffset = offset;
    }

    // Update Sidebar Navigation live counts
    this.updateSidebarCounts(stats);
  },

  updateSidebarCounts(stats) {
    const allCount = document.getElementById("countAllTasks");
    const todayCount = document.getElementById("countToday");
    const upcomingCount = document.getElementById("countUpcoming");
    const completedCount = document.getElementById("countCompleted");
    const importantCount = document.getElementById("countImportant");

    if (allCount) allCount.textContent = stats.total_tasks;
    if (todayCount) todayCount.textContent = stats.today_tasks;
    if (upcomingCount) upcomingCount.textContent = stats.upcoming_tasks;
    if (completedCount) completedCount.textContent = stats.completed_tasks;
    if (importantCount) importantCount.textContent = stats.important_tasks;
  },

  renderCategoriesSidebar(categories) {
    const listElem = document.getElementById("sidebarCategoriesList");
    if (!listElem) return;

    if (!categories || categories.length === 0) {
      listElem.innerHTML = `<li style="font-size: 0.8rem; color: var(--text-subtle); padding: 0.25rem 0.625rem;">No categories</li>`;
      return;
    }

    listElem.innerHTML = categories.map(cat => `
      <li>
        <button type="button" class="nav-item-btn category-nav-item" data-category-id="${cat.id}">
          <div class="nav-left">
            <span class="category-dot" style="background-color: ${cat.color || "#4F46E5"}"></span>
            <span>${Utils.escapeHtml(cat.name)}</span>
          </div>
          <span class="nav-counter">${cat.task_count || 0}</span>
        </button>
      </li>
    `).join("");

    // Attach click listeners to category items
    listElem.querySelectorAll(".category-nav-item").forEach(btn => {
      btn.addEventListener("click", () => {
        const catId = btn.getAttribute("data-category-id");
        if (window.Filters) {
          window.Filters.setCategoryFilter(parseInt(catId));
        }
      });
    });
  },

  populateCategoryDropdowns(categories) {
    const selectElems = [
      document.getElementById("taskCategory"),
      document.getElementById("filterCategory")
    ];

    selectElems.forEach(sel => {
      if (!sel) return;
      const isFilter = sel.id === "filterCategory";
      let html = isFilter ? `<option value="">All Categories</option>` : `<option value="">Select Category (Optional)</option>`;
      categories.forEach(cat => {
        html += `<option value="${cat.id}">${Utils.escapeHtml(cat.name)}</option>`;
      });
      sel.innerHTML = html;
    });
  },

  /* --- Task Form Open / Edit / Submit --- */
  openCreateModal() {
    this.activeTaskId = null;
    const form = document.getElementById("taskForm");
    if (form) form.reset();

    document.getElementById("taskModalTitle").textContent = "Create New Task";
    const submitBtn = document.getElementById("taskSubmitBtn");
    if (submitBtn) {
      submitBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
        <span>Save to Dashboard</span>
      `;
    }
    
    // Default priority & status
    const medRadio = document.querySelector('input[name="priority"][value="medium"]');
    if (medRadio) medRadio.checked = true;

    const pendingRadio = document.querySelector('input[name="status"][value="pending"]');
    if (pendingRadio) pendingRadio.checked = true;

    UI.openModal("taskModal");
  },

  async openEditModal(taskId) {
    this.activeTaskId = taskId;
    const form = document.getElementById("taskForm");
    if (form) form.reset();

    document.getElementById("taskModalTitle").textContent = "Edit Task";
    const submitBtn = document.getElementById("taskSubmitBtn");
    if (submitBtn) {
      submitBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
        <span>Save Changes</span>
      `;
    }

    try {
      const resp = await API.getTaskById(taskId);
      if (resp && resp.data) {
        const t = resp.data;
        document.getElementById("taskTitle").value = t.title || "";
        document.getElementById("taskDescription").value = t.description || "";
        
        // Priority
        const pRadio = document.querySelector(`input[name="priority"][value="${t.priority}"]`);
        if (pRadio) pRadio.checked = true;

        // Status
        const sRadio = document.querySelector(`input[name="status"][value="${t.status}"]`);
        if (sRadio) sRadio.checked = true;

        // Category
        if (t.category_id) {
          document.getElementById("taskCategory").value = t.category_id;
        }

        // Due date & time
        if (t.due_date) {
          document.getElementById("taskDueDate").value = t.due_date;
        }
        if (t.due_time) {
          document.getElementById("taskDueTime").value = t.due_time;
        }

        // Tags
        if (t.tags && t.tags.length > 0) {
          document.getElementById("taskTags").value = t.tags.map(tag => tag.name).join(", ");
        }

        // Important
        document.getElementById("taskImportant").checked = !!t.is_important;

        UI.openModal("taskModal");
      }
    } catch (err) {
      UI.showToast("Error", "Could not load task details: " + err.message, "error");
    }
  },

  async handleTaskFormSubmit(e) {
    e.preventDefault();
    const titleInput = document.getElementById("taskTitle");
    const titleError = document.getElementById("taskTitleError");

    if (!Validation.validateTaskForm(titleInput, titleError)) {
      return;
    }

    const priorityInput = document.querySelector('input[name="priority"]:checked');
    const statusInput = document.querySelector('input[name="status"]:checked');
    const catInput = document.getElementById("taskCategory");
    const descInput = document.getElementById("taskDescription");
    const dueDateInput = document.getElementById("taskDueDate");
    const dueTimeInput = document.getElementById("taskDueTime");
    const tagsInput = document.getElementById("taskTags");
    const importantInput = document.getElementById("taskImportant");
    const submitBtn = document.getElementById("taskSubmitBtn");

    const payload = {
      title: titleInput.value.trim(),
      description: descInput.value.trim() || null,
      priority: priorityInput ? priorityInput.value : "medium",
      status: statusInput ? statusInput.value : "pending",
      category_id: catInput.value ? parseInt(catInput.value) : null,
      due_date: dueDateInput.value || null,
      due_time: dueTimeInput.value || null,
      is_important: importantInput ? importantInput.checked : false,
      tags: tagsInput.value.split(",").map(t => t.trim()).filter(Boolean)
    };

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner"></span> Saving...`;

      if (this.activeTaskId) {
        await API.updateTask(this.activeTaskId, payload);
        UI.showToast("Success", "Task updated successfully! ✨", "success");
      } else {
        await API.createTask(payload);
        UI.showToast("Success", "Task created successfully! 🎉", "success");
      }

      UI.closeModal("taskModal");
      this.refreshCurrentView();
    } catch (err) {
      UI.showToast("Error", err.message, "error");
    } finally {
      submitBtn.disabled = false;
      const btnText = this.activeTaskId ? "Save Changes" : "Save to Dashboard";
      submitBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
        <span>${btnText}</span>
      `;
    }
  },

  /* --- Delete Confirmation Modal --- */
  promptDelete(taskId) {
    this.activeTaskId = taskId;
    UI.openModal("deleteConfirmModal");
  },

  async confirmDelete() {
    if (!this.activeTaskId) return;
    const confirmBtn = document.getElementById("confirmDeleteBtn");

    try {
      confirmBtn.disabled = true;
      confirmBtn.textContent = "Deleting...";

      await API.deleteTask(this.activeTaskId);
      UI.showToast("Deleted", "Task has been permanently removed.", "info");
      UI.closeModal("deleteConfirmModal");
      this.refreshCurrentView();
    } catch (err) {
      UI.showToast("Delete Failed", err.message, "error");
    } finally {
      confirmBtn.disabled = false;
      confirmBtn.textContent = "Delete Task";
      this.activeTaskId = null;
    }
  },

  refreshCurrentView() {
    if (window.Filters) {
      window.Filters.applyFilters();
    } else {
      this.loadAll();
    }
  },

  setupEventListeners() {
    const taskForm = document.getElementById("taskForm");
    if (taskForm) {
      taskForm.addEventListener("submit", (e) => this.handleTaskFormSubmit(e));
    }

    const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
    if (confirmDeleteBtn) {
      confirmDeleteBtn.addEventListener("click", () => this.confirmDelete());
    }

    const viewListBtn = document.getElementById("viewListBtn");
    const viewGridBtn = document.getElementById("viewGridBtn");
    if (viewListBtn) viewListBtn.addEventListener("click", () => this.applyViewMode("list"));
    if (viewGridBtn) viewGridBtn.addEventListener("click", () => this.applyViewMode("grid"));
  }
};
