// Function to set the theme
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  
  // Update button icon
  const themeIcon = document.getElementById('theme-icon');
  if (themeIcon) {
    themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
  }
  
  // Update background image
  updateBackgroundImage(theme);
  
  // Update logo
  updateLogo(theme);
}

// Function to update background image based on theme
function updateBackgroundImage(theme) {
  const body = document.body;
  if (theme === 'dark') {
    body.style.backgroundImage = "url('/static/bg-dark.png')";
  } else {
    body.style.backgroundImage = "url('/static/bg.png')";
  }
  body.style.backgroundSize = 'cover';
  body.style.backgroundPosition = 'center';
  body.style.backgroundRepeat = 'no-repeat';
  body.style.backgroundAttachment = 'fixed';
}

// Function to update logo based on theme
function updateLogo(theme) {
  const logoImg = document.getElementById('theme-logo');
  if (logoImg) {
    if (theme === 'dark') {
      logoImg.src = '/static/logo-dark.png';
    } else {
      logoImg.src = '/static/logo.png';
    }
  }
}

// Function to toggle between themes
function toggleTheme() {
  const currentTheme = localStorage.getItem('theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  setTheme(newTheme);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
  // Get stored theme or default to light
  const savedTheme = localStorage.getItem('theme') || 'light';
  setTheme(savedTheme);
  
  // Add theme toggle button if it doesn't exist
  if (!document.querySelector('.theme-switcher')) {
    const themeSwitcher = document.createElement('div');
    themeSwitcher.className = 'theme-switcher';
    themeSwitcher.innerHTML = `
      <button class="theme-toggle" onclick="toggleTheme()">
        <span id="theme-icon">${savedTheme === 'dark' ? '☀️' : '🌙'}</span>
      </button>
    `;
    document.body.appendChild(themeSwitcher);
  }
});