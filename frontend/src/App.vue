<script setup>
import { RouterView, RouterLink } from 'vue-router'
</script>

<template>
  <div class="app">
    <nav class="navbar">
      <div class="navbar-brand">
        <span class="brand-icon">🛡️</span>
        <span class="brand-name">OnDutyService</span>
        <span class="brand-sub">ระบบจัดการเวรรักษาการณ์</span>
      </div>
      <ul class="nav-links">
        <li><RouterLink to="/" exact-active-class="active">หน้าหลัก</RouterLink></li>
        <li><RouterLink to="/officers" active-class="active">เจ้าหน้าที่</RouterLink></li>
        <li><RouterLink to="/schedule" active-class="active">ตารางเวร</RouterLink></li>
        <li><RouterLink to="/exchanges" active-class="active">ขอเปลี่ยนเวร</RouterLink></li>
      </ul>
    </nav>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
  color: white;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  gap: 3rem;
  height: 64px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: white;
}

.brand-icon { font-size: 1.6rem; }
.brand-name { font-size: 1.2rem; font-weight: 700; }
.brand-sub { font-size: 0.75rem; opacity: 0.8; }

.nav-links {
  display: flex;
  list-style: none;
  gap: 0.5rem;
  margin: 0;
  padding: 0;
}

.nav-links a {
  color: rgba(255,255,255,0.85);
  text-decoration: none;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  transition: background 0.2s;
  font-size: 0.95rem;
}

.nav-links a:hover,
.nav-links a.active {
  background: rgba(255,255,255,0.2);
  color: white;
}

.main-content {
  flex: 1;
  padding: 2rem;
  background: #f4f6fb;
}
</style>

