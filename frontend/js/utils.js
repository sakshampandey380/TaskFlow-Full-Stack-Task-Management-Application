/**
 * TaskFlow - Utility Functions
 * Date formatting, XSS sanitization, Debounce, Relative time
 */

const Utils = {
  /**
   * Escape HTML to prevent XSS injection in dynamic text
   */
  escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  },

  /**
   * Format ISO date string into readable text (e.g. "Oct 12, 2026")
   */
  formatDate(dateStr) {
    if (!dateStr) return "";
    try {
      const parts = dateStr.split("-");
      if (parts.length === 3) {
        const d = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
        return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
      }
      return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    } catch {
      return dateStr;
    }
  },

  /**
   * Calculate human friendly relative due date ("Due Today", "Tomorrow", "Overdue by 2d", etc.)
   */
  getRelativeDueDate(dateStr, timeStr) {
    if (!dateStr) return null;

    try {
      const parts = dateStr.split("-");
      const targetDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
      
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

      const diffTime = targetDate.getTime() - today.getTime();
      const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

      let formattedTime = "";
      if (timeStr) {
        const [h, m] = timeStr.split(":");
        const hour = parseInt(h);
        const ampm = hour >= 12 ? "PM" : "AM";
        const hour12 = hour % 12 || 12;
        formattedTime = ` at ${hour12}:${m} ${ampm}`;
      }

      if (diffDays === 0) {
        return { text: `Today${formattedTime}`, isToday: true, isOverdue: false };
      } else if (diffDays === 1) {
        return { text: `Tomorrow${formattedTime}`, isToday: false, isOverdue: false };
      } else if (diffDays === -1) {
        return { text: `Yesterday (Overdue)`, isToday: false, isOverdue: true };
      } else if (diffDays < -1) {
        return { text: `Overdue by ${Math.abs(diffDays)}d`, isToday: false, isOverdue: true };
      } else if (diffDays <= 7) {
        return { text: `In ${diffDays} days`, isToday: false, isOverdue: false };
      } else {
        return { text: Utils.formatDate(dateStr) + formattedTime, isToday: false, isOverdue: false };
      }
    } catch (e) {
      return { text: dateStr, isToday: false, isOverdue: false };
    }
  },

  /**
   * Debounce helper for instant smooth search input
   */
  debounce(func, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  },

  /**
   * Extract initials from user name (e.g. "Alex Morgan" -> "AM")
   */
  getInitials(name) {
    if (!name) return "U";
    const parts = name.trim().split(" ");
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return parts[0].substring(0, 2).toUpperCase();
  }
};
