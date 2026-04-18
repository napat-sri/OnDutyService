<script setup>
import { ref, onMounted } from 'vue'
import { officerService, scheduleService, exchangeService } from '../services/api'
import { formatThaiDate, formatThaiYear, toIsoDateString } from '../utils/thaiDate'
import { RouterLink } from 'vue-router'

const stats = ref({ officers: 0, schedules: 0, pendingExchanges: 0 })
const loading = ref(true)
const currentDate = new Date()
const currentYear = currentDate.getFullYear()
const currentMonth = currentDate.getMonth() + 1

const dutyToday = ref([])

const monthNames = [
  'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
  'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
]

onMounted(async () => {
  try {
    const [officersRes, schedulesRes, exchangesRes] = await Promise.all([
      officerService.list(),
      scheduleService.list(),
      exchangeService.list(),
    ])
    stats.value.officers = officersRes.data.length
    stats.value.schedules = schedulesRes.data.length
    stats.value.pendingExchanges = exchangesRes.data.filter(e => e.status === 'pending').length

    // Get today's duty
    const todayStr = toIsoDateString(currentDate)
    try {
      const schedRes = await scheduleService.get(currentYear, currentMonth)
      dutyToday.value = schedRes.data.entries.filter(e => e.date === todayStr)
    } catch {
      dutyToday.value = []
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">🏠 หน้าหลัก</h1>
      <span class="text-muted">{{ formatThaiDate(currentDate, {
        weekday: 'long', year: 'numeric', month: 'long', day:
          'numeric' }) }}</span>
    </div>

    <div v-if="loading" class="text-center text-muted mt-2">กำลังโหลด...</div>
    <div v-else>
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👮</div>
          <div class="stat-value">{{ stats.officers }}</div>
          <div class="stat-label">เจ้าหน้าที่ทั้งหมด</div>
          <RouterLink to="/officers" class="stat-link">จัดการเจ้าหน้าที่ →</RouterLink>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <div class="stat-value">{{ stats.schedules }}</div>
          <div class="stat-label">ตารางเวรที่บันทึก</div>
          <RouterLink to="/schedule" class="stat-link">ดูตารางเวร →</RouterLink>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🔄</div>
          <div class="stat-value">{{ stats.pendingExchanges }}</div>
          <div class="stat-label">คำขอเปลี่ยนเวรรอดำเนินการ</div>
          <RouterLink to="/exchanges" class="stat-link">จัดการคำขอ →</RouterLink>
        </div>
      </div>

      <!-- Today's duty -->
      <div class="card mt-2">
        <h2 class="section-title">🗓️ เวรวันนี้ - {{ monthNames[currentMonth - 1] }} {{ formatThaiYear(currentYear) }}
        </h2>
        <div v-if="dutyToday.length === 0" class="text-muted text-center mt-1">
          ยังไม่มีข้อมูลเวรสำหรับวันนี้
        </div>
        <div v-else class="duty-list">
          <div v-for="entry in dutyToday" :key="entry.officer_id" class="duty-item">
            <span class="duty-icon" v-if="entry.officer_duty == 'นายทหารเวร'">🧑‍✈️</span>
            <span class="duty-icon" v-else-if="entry.officer_duty == 'นายทหารเวร (หญิง)'">👮‍♀️</span>
            <span class="duty-icon" v-else-if="entry.officer_duty == 'เสมียนเวร'">📋</span>
            <span class="duty-icon" v-else-if="entry.officer_duty == 'เวรประชาสัมพันธ์'">📢</span>
            <span class="duty-icon" v-else>📌</span>
            <div>
              <div class="duty-name">{{ entry.officer_name }}</div>
              <div class="text-muted" style="font-size:0.85rem">{{ formatThaiDate(entry.date) }}</div>
              <div class="text-muted" style="font-size:0.85rem">{{ entry.officer_duty }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick links -->
      <div class="card mt-2">
        <h2 class="section-title">⚡ เมนูด่วน</h2>
        <div class="quick-links">
          <RouterLink to="/officers" class="quick-link">
            <span class="ql-icon">👮</span>
            <span>เพิ่มเจ้าหน้าที่</span>
          </RouterLink>
          <RouterLink to="/schedule" class="quick-link">
            <span class="ql-icon">📅</span>
            <span>จัดตารางเวร</span>
          </RouterLink>
          <RouterLink to="/exchanges" class="quick-link">
            <span class="ql-icon">🔄</span>
            <span>ขอเปลี่ยนเวร</span>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 0.75rem;
  text-align: center;
  box-shadow: 0 2px 12px rgba(26, 35, 126, 0.08);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1a237e;
}

.stat-label {
  font-size: 0.8rem;
  color: #546e7a;
  margin-top: 0.25rem;
}

.stat-link {
  display: block;
  margin-top: 0.75rem;
  color: #3949ab;
  font-size: 0.85rem;
  text-decoration: none;
}

.stat-link:hover {
  text-decoration: underline;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1a237e;
}

.duty-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.duty-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8f9ff;
  border-radius: 8px;
}

.duty-icon {
  font-size: 1.5rem;
}

.duty-name {
  font-weight: 600;
}

.quick-links {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.quick-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-radius: 10px;
  background: #e8eaf6;
  color: #1a237e;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
  min-width: 120px;
}

.quick-link:hover {
  background: #c5cae9;
  transform: translateY(-1px);
}

.ql-icon {
  font-size: 1.8rem;
}
</style>
