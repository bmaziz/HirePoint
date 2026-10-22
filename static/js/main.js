/* ==========================================================================
   HirePoint - Main Client-side Script
   Handles dropdowns, password toggles, tabs, and demo prefillers
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  // 1. User dropdown toggle in Navbar
  const userDropdown = document.querySelector('.user-dropdown');
  const userPill = document.querySelector('.user-pill');

  if (userPill && userDropdown) {
    userPill.addEventListener('click', function (e) {
      e.stopPropagation();
      userDropdown.classList.toggle('open');
    });

    document.addEventListener('click', function (e) {
      if (!userDropdown.contains(e.target)) {
        userDropdown.classList.remove('open');
      }
    });
  }

  // 2. Mobile navigation toggle
  const mobileToggle = document.querySelector('.mobile-toggle');
  const navbar = document.querySelector('.navbar');

  if (mobileToggle && navbar) {
    mobileToggle.addEventListener('click', function () {
      navbar.classList.toggle('mobile-nav-open');
    });
  }

  // 3. Password visibility toggle
  const toggleBtns = document.querySelectorAll('.password-toggle-btn');
  toggleBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input) {
        const isPassword = input.getAttribute('type') === 'password';
        input.setAttribute('type', isPassword ? 'text' : 'password');
        const icon = this.querySelector('i');
        if (icon) {
          icon.className = isPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
        }
      }
    });
  });

  // 4. Registration Role Tabs
  const roleTabButtons = document.querySelectorAll('.role-tab-btn');
  const rolePanels = document.querySelectorAll('.role-tab-panel');
  const targetRoleInputs = document.querySelectorAll('input[name="target_role"]');

  roleTabButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const role = this.getAttribute('data-role');

      // Update button styles
      roleTabButtons.forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      // Update panels
      rolePanels.forEach(panel => {
        if (panel.id === 'panel-' + role) {
          panel.classList.add('active');
        } else {
          panel.classList.remove('active');
        }
      });

      // Update hidden inputs
      targetRoleInputs.forEach(input => {
        input.value = role;
      });

      // Update URL query param without full page reload
      const url = new URL(window.location);
      url.searchParams.set('role', role);
      window.history.replaceState({}, '', url);
    });
  });

  // 5. Quick Demo Account Prefiller
  window.fillDemoAccount = function (username, password) {
    const identInput = document.getElementById('login-identifier');
    const passInput = document.getElementById('login-password');

    if (identInput && passInput) {
      identInput.value = username;
      passInput.value = password;

      // Visual feedback
      identInput.style.borderColor = 'var(--primary)';
      passInput.style.borderColor = 'var(--primary)';

      // Auto submit or focus
      passInput.focus();
    }
  };

  // 6. Alert dismiss buttons
  const alertCloses = document.querySelectorAll('.alert-close');
  alertCloses.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const alert = this.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });

  // Auto-dismiss success messages after 6 seconds
  const successAlerts = document.querySelectorAll('.alert-success');
  successAlerts.forEach(function (alert) {
    setTimeout(function () {
      if (alert && alert.parentElement) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 250);
      }
    }, 6000);
  });
});
