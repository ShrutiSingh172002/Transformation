// Toggle dropdown
const userIcon = document.getElementById("userIcon");
const userDropdown = document.getElementById("userDropdown");

userIcon.addEventListener("click", () => {
  userDropdown.style.display =
    userDropdown.style.display === "flex" ? "none" : "flex";
});

// Modal login
const loginBtn = document.getElementById("loginBtn");
const logoutBtn = document.getElementById("logoutBtn");
const loginModal = document.getElementById("loginModal");
const closeModal = document.getElementById("closeModal");

loginBtn.addEventListener("click", (e) => {
  e.preventDefault();
  loginModal.style.display = "flex";
  userDropdown.style.display = "none";
});

closeModal.addEventListener("click", () => {
  loginModal.style.display = "none";
});

// Simulate login
document.getElementById("loginForm").addEventListener("submit", function (e) {
  e.preventDefault();
  loginModal.style.display = "none";
  loginBtn.style.display = "none";
  logoutBtn.style.display = "block";
});

// Simulate logout
logoutBtn.addEventListener("click", (e) => {
  e.preventDefault();
  loginBtn.style.display = "block";
  logoutBtn.style.display = "none";
});
