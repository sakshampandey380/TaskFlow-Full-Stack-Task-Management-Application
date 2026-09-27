/**
 * TaskFlow - Form Validation Module
 * Client-side validation ensuring instant user feedback before making API requests.
 */

const Validation = {
  /**
   * Show inline field error message
   */
  showError(inputElem, errorElem, message) {
    if (inputElem) {
      inputElem.style.borderColor = "var(--priority-urgent)";
    }
    if (errorElem) {
      errorElem.textContent = message;
      errorElem.classList.add("visible");
    }
  },

  /**
   * Clear inline field error message
   */
  clearError(inputElem, errorElem) {
    if (inputElem) {
      inputElem.style.borderColor = "";
    }
    if (errorElem) {
      errorElem.textContent = "";
      errorElem.classList.remove("visible");
    }
  },

  /**
   * Validate Task Form Inputs
   */
  validateTaskForm(titleInput, titleErrorElem) {
    this.clearError(titleInput, titleErrorElem);
    const titleVal = titleInput.value.trim();

    if (!titleVal) {
      this.showError(titleInput, titleErrorElem, "Task title is required.");
      titleInput.focus();
      return false;
    }

    if (titleVal.length > 255) {
      this.showError(titleInput, titleErrorElem, "Task title cannot exceed 255 characters.");
      titleInput.focus();
      return false;
    }

    return true;
  },

  /**
   * Validate User Registration Form
   */
  validateRegisterForm({ nameInput, nameError, emailInput, emailError, passInput, passError }) {
    let isValid = true;

    this.clearError(nameInput, nameError);
    this.clearError(emailInput, emailError);
    this.clearError(passInput, passError);

    // Validate Name
    const nameVal = nameInput.value.trim();
    if (!nameVal || nameVal.length < 2) {
      this.showError(nameInput, nameError, "Please enter your name (at least 2 characters).");
      isValid = false;
    }

    // Validate Email
    const emailVal = emailInput.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailVal || !emailRegex.test(emailVal)) {
      this.showError(emailInput, emailError, "Please enter a valid email address.");
      isValid = false;
    }

    // Validate Password
    const passVal = passInput.value;
    if (!passVal || passVal.length < 6) {
      this.showError(passInput, passError, "Password must be at least 6 characters long.");
      isValid = false;
    }

    return isValid;
  },

  /**
   * Validate User Login Form
   */
  validateLoginForm({ emailInput, emailError, passInput, passError }) {
    let isValid = true;
    this.clearError(emailInput, emailError);
    this.clearError(passInput, passError);

    const emailVal = emailInput.value.trim();
    if (!emailVal) {
      this.showError(emailInput, emailError, "Email is required.");
      isValid = false;
    }

    const passVal = passInput.value;
    if (!passVal) {
      this.showError(passInput, passError, "Password is required.");
      isValid = false;
    }

    return isValid;
  }
};
