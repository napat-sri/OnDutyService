<script setup>
import { ref, computed, onMounted } from 'vue'
import { scheduleService, officerService } from '../services/api'

const schedules = ref([])
const officers = ref([])
const loading = ref(false)
const error = ref(null)
const success = ref(null)

const selectedYear = ref(new Date().getFullYear())
const selectedMonth = ref(new Date().getMonth() + 1)
const currentSchedule = ref(null)
const loadingSchedule = ref(false)

const showAddEntryModal = ref(false)
const entryForm = ref({ officer_id: '', date: '' })

const months = [
  { value: 1, label: 'มกราคม' }, { value: 2, label: 'กุมภาพันธ์' },
  { value: 3, label: 'มีนาคม' }, { value: 4, label: 'เมษายน' },
  { value: 5, label: 'พฤษภาคม' }, { value: 6, label: 'มิถุนายน' },
  { value: 7, label: 'กรกฎาคม' }, { value: 8, label: 'สิงหาคม' },
  { value: 9, label: 'กันยายน' }, { value: 10, label: 'ตุลาคม' },
  { value: 11, label: 'พฤศจิกายน' }, { value: 12, label: 'ธันวาคม' },
]

const years = computed(() => {
  const y = new Date().getFullYear()
  return [y - 1, y, y + 1]
})

const calendarDays = computed(() => {
  if (!selectedYear.value || !selectedMonth.value) return []
  const days = []
  const daysInMonth = new Date(selectedYear.value, selectedMonth.value, 0).getDate()
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const entries = currentSchedule.value?.entries?.filter(e => e.date === dateStr) || []
    days.push({ day: d, dateStr, entries })
  }
  return days
})

const selectedOfficer = computed(() => {
  return officers.value.find(o => o._id === entryForm.value.officer_id)
})

async function loadSchedule() {
  loadingSchedule.value = true
  error.value = null
  try {
    const res = await scheduleService.get(selectedYear.value, selectedMonth.value)
    currentSchedule.value = res.data
  } catch (e) {
    if (e.response?.status === 404) {
      currentSchedule.value = null
    } else {
      error.value = 'เกิดข้อผิดพลาดในการโหลดข้อมูล'
    }
  } finally {
    loadingSchedule.value = false
  }
}

async function createSchedule() {
  try {
    const res = await scheduleService.create({
      year: selectedYear.value,
      month: selectedMonth.value,
      entries: [],
    })
    currentSchedule.value = res.data
    success.value = 'สร้างตารางเวรสำเร็จ'
    setTimeout(() => (success.value = null), 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'เกิดข้อผิดพลาด'
  }
}

function openAddEntry(dateStr) {
  entryForm.value = { officer_id: '', date: dateStr }
  showAddEntryModal.value = true
}

async function addEntry() {
  if (!entryForm.value.officer_id || !entryForm.value.date) return
  const officer = officers.value.find(o => o._id === entryForm.value.officer_id)
  if (!officer) return
  const newEntry = {
    officer_id: officer._id,
    officer_name: `${officer.rank} ${officer.name}`,
    date: entryForm.value.date,
  }
  const updatedEntries = [...(currentSchedule.value.entries || []), newEntry]
  try {
    const res = await scheduleService.update(selectedYear.value, selectedMonth.value, {
      entries: updatedEntries,
    })
    currentSchedule.value = res.data
    showAddEntryModal.value = false
    success.value = 'เพิ่มเวรสำเร็จ'
    setTimeout(() => (success.value = null), 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'เกิดข้อผิดพลาด'
  }
}

async function removeEntry(dateStr, officerId) {
  if (!confirm('ยืนยันการลบเวรนี้?')) return
  const updatedEntries = currentSchedule.value.entries.filter(
    e => !(e.date === dateStr && e.officer_id === officerId)
  )
  try {
    const res = await scheduleService.update(selectedYear.value, selectedMonth.value, {
      entries: updatedEntries,
    })
    currentSchedule.value = res.data
    success.value = 'ลบเวรสำเร็จ'
    setTimeout(() => (success.value = null), 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'เกิดข้อผิดพลาด'
  }
}

const dayNames = ['อา', 'จ', 'อ', 'พ', 'พฤ', 'ศ', 'ส']

function getWeekday(dateStr) {
  return new Date(dateStr + 'T00:00:00').getDay()
}

onMounted(async () => {
  const [offRes] = await Promise.all([officerService.list()])
  officers.value = offRes.data
  await loadSchedule()
})
</script>

<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">📅 ตารางเวร</h1>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <!-- Controls -->
    <div class="card" style="margin-bottom:1.5rem">
      <div class="controls">
        <div class="form-group" style="margin:0">
          <label>ปี</label>
          <select v-model="selectedYear" @change="loadSchedule">
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div class="form-group" style="margin:0">
          <label>เดือน</label>
          <select v-model="selectedMonth" @change="loadSchedule">
            <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="loadSchedule" style="align-self:flex-end">🔍 ค้นหา</button>
      </div>
    </div>

    <!-- No schedule yet -->
    <div v-if="!loadingSchedule && !currentSchedule" class="card text-center" style="padding:3rem">
      <div style="font-size:3rem;margin-bottom:1rem">📅</div>
      <div style="font-size:1.1rem;margin-bottom:1rem;color:#546e7a">
        ยังไม่มีตารางเวรสำหรับเดือน {{ months.find(m => m.value === selectedMonth)?.label }} {{ selectedYear }}
      </div>
      <button class="btn btn-primary" @click="createSchedule">+ สร้างตารางเวร</button>
    </div>

    <!-- Loading -->
    <div v-else-if="loadingSchedule" class="card text-center text-muted">กำลังโหลด...</div>

    <!-- Calendar -->
    <div v-else class="card">
      <div class="calendar-header">
        <h2 style="font-size:1.2rem;color:#1a237e">
          📅 {{ months.find(m => m.value === selectedMonth)?.label }} {{ selectedYear }}
        </h2>
      </div>
      <div class="calendar-grid">
        <div v-for="day in dayNames" :key="day" class="cal-day-header">{{ day }}</div>
        <!-- empty cells for first week offset -->
        <div v-for="i in getWeekday(calendarDays[0]?.dateStr)" :key="'empty-'+i" class="cal-cell empty"></div>
        <div
          v-for="dayObj in calendarDays"
          :key="dayObj.dateStr"
          class="cal-cell"
          :class="{ today: dayObj.dateStr === new Date().toISOString().split('T')[0] }"
        >
          <div class="cal-day-num">{{ dayObj.day }}</div>
          <div class="cal-entries">
            <div
              v-for="entry in dayObj.entries"
              :key="entry.officer_id"
              class="cal-entry"
              :title="entry.officer_name"
            >
              <span>👮 {{ entry.officer_name }}</span>
              <button class="entry-remove" @click="removeEntry(dayObj.dateStr, entry.officer_id)" title="ลบ">✕</button>
            </div>
          </div>
          <button class="add-entry-btn" @click="openAddEntry(dayObj.dateStr)" title="เพิ่มเวร">+</button>
        </div>
      </div>
    </div>

    <!-- Add Entry Modal -->
    <div v-if="showAddEntryModal" class="modal-overlay" @click.self="showAddEntryModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>➕ เพิ่มเวร - {{ entryForm.date }}</h3>
          <button class="close-btn" @click="showAddEntryModal = false">✕</button>
        </div>
        <div class="form-group">
          <label>เลือกเจ้าหน้าที่</label>
          <select v-model="entryForm.officer_id">
            <option value="">-- เลือกเจ้าหน้าที่ --</option>
            <option v-for="o in officers" :key="o._id" :value="o._id">
              {{ o.rank }} {{ o.name }} ({{ o.badge_number }})
            </option>
          </select>
        </div>
        <div class="flex gap-2 mt-2">
          <button class="btn btn-primary" @click="addEntry" :disabled="!entryForm.officer_id">💾 เพิ่มเวร</button>
          <button class="btn btn-secondary" @click="showAddEntryModal = false">ยกเลิก</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.controls { display: flex; gap: 1.5rem; align-items: flex-end; flex-wrap: wrap; }
.controls .form-group { min-width: 140px; }

.calendar-header { margin-bottom: 1rem; }

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.cal-day-header {
  text-align: center;
  font-weight: 700;
  font-size: 0.85rem;
  color: #546e7a;
  padding: 0.5rem;
  background: #e8eaf6;
  border-radius: 4px;
}

.cal-cell {
  min-height: 90px;
  border: 1px solid #e8eaf6;
  border-radius: 8px;
  padding: 4px;
  position: relative;
  background: white;
  transition: background 0.15s;
}

.cal-cell.empty { background: transparent; border: none; }
.cal-cell.today { border-color: #3949ab; background: #f0f4ff; }

.cal-day-num {
  font-weight: 600;
  font-size: 0.85rem;
  color: #37474f;
  margin-bottom: 4px;
}

.today .cal-day-num {
  background: #3949ab;
  color: white;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
}

.cal-entries { display: flex; flex-direction: column; gap: 2px; }

.cal-entry {
  background: #e3f2fd;
  color: #1565c0;
  border-radius: 4px;
  padding: 2px 4px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2px;
  overflow: hidden;
}

.cal-entry span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }

.entry-remove {
  background: none;
  border: none;
  color: #ef5350;
  cursor: pointer;
  font-size: 0.65rem;
  padding: 0;
  line-height: 1;
  flex-shrink: 0;
}

.add-entry-btn {
  position: absolute;
  bottom: 3px;
  right: 3px;
  background: none;
  border: 1px dashed #90a4ae;
  color: #90a4ae;
  border-radius: 4px;
  width: 18px;
  height: 18px;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: all 0.15s;
}

.add-entry-btn:hover { background: #e8eaf6; color: #1a237e; border-color: #1a237e; }
</style>
