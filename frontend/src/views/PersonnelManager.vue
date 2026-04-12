<script setup>
import { ref, computed, onMounted } from 'vue'
import { officerService, absenceService } from '../services/api'

const officers = ref([])
const dutyTypes = ref([])
const absences = ref([])
const loading = ref(true)
const error = ref(null)
const success = ref(null)

const selectedYear = ref(new Date().getFullYear())
const selectedMonth = ref(new Date().getMonth() + 1)

const activeTab = ref('')

const showModal = ref(false)
const editingAbsence = ref(null)
const form = ref({ officer_id: '', start_date: '', end_date: '', reason: '' })

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

const daysInMonth = computed(() => {
  const count = new Date(selectedYear.value, selectedMonth.value, 0).getDate()
  const days = []
  for (let d = 1; d <= count; d++) {
    const dateStr = `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({ day: d, dateStr, weekday: new Date(selectedYear.value, selectedMonth.value - 1, d).getDay() })
  }
  return days
})

// Today's date in local time as YYYY-MM-DD
const todayStr = computed(() => {
  const t = new Date()
  return `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, '0')}-${String(t.getDate()).padStart(2, '0')}`
})

// Absence lookup map: `${officerId}:${dateStr}` -> absence object
const absenceLookup = computed(() => {
  const map = {}
  for (const a of absences.value) {
    // Iterate all days of the absence range
    const start = new Date(a.start_date + 'T00:00:00')
    const end = new Date(a.end_date + 'T00:00:00')
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      const key = `${a.officer_id}:${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      map[key] = a
    }
  }
  return map
})

function getAbsenceForDate(officerId, dateStr) {
  return absenceLookup.value[`${officerId}:${dateStr}`]
}

const filteredOfficers = computed(() => {
  if (!activeTab.value) return officers.value
  return officers.value.filter(o => (o.duty_types || []).includes(activeTab.value))
})

async function loadAbsences() {
  const res = await absenceService.list(selectedYear.value, selectedMonth.value)
  absences.value = res.data
}

async function loadData() {
  loading.value = true
  error.value = null
  try {
    const [offRes, dtRes] = await Promise.all([
      officerService.list(),
      officerService.listDutyTypes(),
    ])
    officers.value = offRes.data
    dutyTypes.value = dtRes.data
    if (!activeTab.value && dtRes.data.length > 0) {
      activeTab.value = dtRes.data[0]
    }
    await loadAbsences()
  } catch (e) {
    error.value = 'ไม่สามารถโหลดข้อมูลได้'
  } finally {
    loading.value = false
  }
}

function openAddAbsence(officerId, dateStr) {
  editingAbsence.value = null
  form.value = { officer_id: officerId, start_date: dateStr, end_date: dateStr, reason: '' }
  showModal.value = true
}

function openEditAbsence(absence) {
  editingAbsence.value = absence
  form.value = {
    officer_id: absence.officer_id,
    start_date: absence.start_date,
    end_date: absence.end_date,
    reason: absence.reason,
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingAbsence.value = null
}

async function saveAbsence() {
  try {
    error.value = null
    if (editingAbsence.value) {
      await absenceService.update(editingAbsence.value._id, {
        start_date: form.value.start_date,
        end_date: form.value.end_date,
        reason: form.value.reason,
      })
      success.value = 'แก้ไขข้อมูลสำเร็จ'
    } else {
      await absenceService.create(form.value)
      success.value = 'บันทึกข้อมูลสำเร็จ'
    }
    closeModal()
    await loadAbsences()
    setTimeout(() => (success.value = null), 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'เกิดข้อผิดพลาด'
  }
}

async function deleteAbsence(absence, event) {
  event.stopPropagation()
  if (!confirm('ยืนยันการลบข้อมูลการลา/ไม่พร้อมปฏิบัติหน้าที่?')) return
  try {
    await absenceService.delete(absence._id)
    success.value = 'ลบสำเร็จ'
    await loadAbsences()
    setTimeout(() => (success.value = null), 3000)
  } catch (e) {
    error.value = 'เกิดข้อผิดพลาด'
  }
}

const dayNames = ['อา', 'จ', 'อ', 'พ', 'พฤ', 'ศ', 'ส']

// Absence list for the selected month (sorted by officer, then date)
const absenceList = computed(() => {
  const officerIds = new Set(filteredOfficers.value.map(o => o._id))
  return absences.value
    .filter(a => officerIds.has(a.officer_id))
    .sort((a, b) => a.start_date.localeCompare(b.start_date))
})

onMounted(loadData)
</script>

<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">📊 จำหน่ายเวร</h1>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <!-- Month / Year selector -->
    <div class="card" style="margin-bottom:1rem">
      <div class="controls">
        <div class="form-group" style="margin:0">
          <label>ปี</label>
          <select v-model="selectedYear" @change="loadAbsences">
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div class="form-group" style="margin:0">
          <label>เดือน</label>
          <select v-model="selectedMonth" @change="loadAbsences">
            <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="loadAbsences" style="align-self:flex-end">🔍 ค้นหา</button>
      </div>
    </div>

    <!-- Duty type tabs -->
    <div class="duty-tabs">
      <button
        v-for="dt in dutyTypes"
        :key="dt"
        class="duty-tab"
        :class="{ active: activeTab === dt }"
        @click="activeTab = dt"
      >
        {{ dt }}
        <span class="tab-count">
          {{ officers.filter(o => (o.duty_types || []).includes(dt)).length }}
        </span>
      </button>
    </div>

    <div v-if="loading" class="card text-center text-muted">กำลังโหลด...</div>
    <div v-else-if="filteredOfficers.length === 0" class="card text-center text-muted" style="padding:2rem">
      ไม่มีเจ้าหน้าที่ในหน้านี้
    </div>
    <div v-else>
      <!-- Gantt Chart -->
      <div class="card" style="padding:0;overflow:hidden">
        <div class="gantt-header-row">
          <span class="gantt-title">
            {{ months.find(m => m.value === selectedMonth)?.label }} {{ selectedYear }}
          </span>
          <span class="gantt-legend">
            <span class="legend-dot available"></span> พร้อม
            <span class="legend-dot absent"></span> ไม่พร้อม
            <span class="legend-dot weekend"></span> วันหยุด
          </span>
        </div>
        <div class="gantt-scroll">
          <table class="gantt-table">
            <thead>
              <tr>
                <th class="gantt-officer-col">ยศ-ชื่อ สกุล</th>
                <th
                  v-for="d in daysInMonth"
                  :key="d.dateStr"
                  class="gantt-day-col"
                  :class="{ weekend: d.weekday === 0 || d.weekday === 6 }"
                >
                  <div class="day-num">{{ d.day }}</div>
                  <div class="day-name">{{ dayNames[d.weekday] }}</div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="officer in filteredOfficers" :key="officer._id">
                <td class="gantt-officer-cell">
                  <div class="officer-name-wrap">
                    <span class="officer-rank">{{ officer.rank }}</span>
                    <span class="officer-name">{{ officer.name }}</span>
                  </div>
                </td>
                <td
                  v-for="d in daysInMonth"
                  :key="d.dateStr"
                  class="gantt-cell"
                  :class="{
                    'weekend': d.weekday === 0 || d.weekday === 6,
                    'absent': !!getAbsenceForDate(officer._id, d.dateStr),
                    'today': d.dateStr === todayStr,
                  }"
                  :title="getAbsenceForDate(officer._id, d.dateStr)?.reason"
                  @click="
                    getAbsenceForDate(officer._id, d.dateStr)
                      ? openEditAbsence(getAbsenceForDate(officer._id, d.dateStr))
                      : openAddAbsence(officer._id, d.dateStr)
                  "
                >
                  <span
                    v-if="getAbsenceForDate(officer._id, d.dateStr)"
                    class="absent-dot"
                    :title="getAbsenceForDate(officer._id, d.dateStr).reason"
                  >✕</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Absence List for the month -->
      <div class="card" style="margin-top:1.5rem">
        <h2 class="section-title">📋 รายชื่อจำหน่าย</h2>
        <div v-if="absenceList.length === 0" class="text-center text-muted" style="padding:1.5rem">
          ไม่มีรายการสำหรับเดือนนี้
        </div>
        <div v-else class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>ยศ-ชื่อ สกุล</th>
                <th>วันที่เริ่ม</th>
                <th>วันที่สิ้นสุด</th>
                <th>เหตุผล</th>
                <th>จัดการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(absence, idx) in absenceList" :key="absence._id">
                <td>{{ idx + 1 }}</td>
                <td>{{ absence.officer_name || absence.officer_id }}</td>
                <td>{{ absence.start_date }}</td>
                <td>{{ absence.end_date }}</td>
                <td>{{ absence.reason }}</td>
                <td>
                  <div class="flex gap-2">
                    <button class="btn btn-secondary btn-sm" @click="openEditAbsence(absence)">✏️ แก้ไข</button>
                    <button class="btn btn-danger btn-sm" @click="deleteAbsence(absence, $event)">🗑️ ลบ</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add / Edit Absence Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingAbsence ? '✏️ แก้ไขข้อมูล' : '➕ เพิ่มข้อมูลไม่พร้อม' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <form @submit.prevent="saveAbsence">
          <div class="form-group">
            <label>เจ้าหน้าที่</label>
            <select v-model="form.officer_id" required :disabled="!!editingAbsence">
              <option value="">-- เลือกเจ้าหน้าที่ --</option>
              <option v-for="o in filteredOfficers" :key="o._id" :value="o._id">
                {{ o.rank }} {{ o.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>วันที่เริ่มต้น *</label>
            <input type="date" v-model="form.start_date" required />
          </div>
          <div class="form-group">
            <label>วันที่สิ้นสุด *</label>
            <input type="date" v-model="form.end_date" required :min="form.start_date" />
          </div>
          <div class="form-group">
            <label>เหตุผล *</label>
            <input
              type="text"
              v-model="form.reason"
              required
              placeholder="เช่น ราชการ, ศึกษา"
            />
          </div>
          <div class="flex gap-2 mt-2">
            <button type="submit" class="btn btn-primary" :disabled="!form.officer_id || !form.start_date || !form.end_date || !form.reason">
              💾 บันทึก
            </button>
            <button type="button" class="btn btn-secondary" @click="closeModal">ยกเลิก</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.controls { display: flex; gap: 1.5rem; align-items: flex-end; flex-wrap: wrap; }
.controls .form-group { min-width: 140px; }

.duty-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.duty-tab {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  border: 2px solid #c5cae9;
  background: white;
  color: #546e7a;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.duty-tab:hover { border-color: #3949ab; color: #1a237e; }

.duty-tab.active {
  background: #3949ab;
  border-color: #3949ab;
  color: white;
}

.tab-count {
  background: rgba(255,255,255,0.3);
  border-radius: 10px;
  padding: 0 0.4rem;
  font-size: 0.75rem;
  min-width: 20px;
  text-align: center;
}

.duty-tab:not(.active) .tab-count {
  background: #e8eaf6;
  color: #3949ab;
}

/* Gantt */
.gantt-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #e8eaf6;
  border-bottom: 1px solid #c5cae9;
}

.gantt-title { font-weight: 700; color: #1a237e; font-size: 1rem; }

.gantt-legend {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.82rem;
  color: #546e7a;
}

.legend-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 3px;
  margin-right: 2px;
}

.legend-dot.available { background: #e8f5e9; border: 1px solid #a5d6a7; }
.legend-dot.absent { background: #ffcdd2; border: 1px solid #ef9a9a; }
.legend-dot.weekend { background: #f5f5f5; border: 1px solid #e0e0e0; }

.gantt-scroll {
  overflow-x: auto;
}

.gantt-table {
  border-collapse: collapse;
  min-width: 100%;
  font-size: 0.82rem;
}

.gantt-table thead th {
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  padding: 4px 2px;
  text-align: center;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 1;
}

.gantt-officer-col {
  min-width: 180px;
  max-width: 220px;
  text-align: left !important;
  padding-left: 10px !important;
  position: sticky;
  left: 0;
  z-index: 2;
  background: #f5f5f5 !important;
}

.gantt-day-col {
  min-width: 32px;
  width: 32px;
}

.gantt-day-col.weekend { background: #fafafa !important; color: #b0bec5; }

.day-num { font-weight: 700; font-size: 0.78rem; color: #37474f; }
.day-name { font-size: 0.65rem; color: #90a4ae; }

.gantt-officer-cell {
  border: 1px solid #e0e0e0;
  padding: 4px 8px;
  background: white;
  position: sticky;
  left: 0;
  z-index: 1;
  min-width: 180px;
  max-width: 220px;
}

.officer-name-wrap {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.officer-rank { font-size: 0.7rem; color: #78909c; }
.officer-name { font-weight: 600; color: #1a237e; }

.gantt-cell {
  border: 1px solid #e8eaf6;
  text-align: center;
  cursor: pointer;
  height: 36px;
  width: 32px;
  background: #f9fff9;
  transition: background 0.1s;
  vertical-align: middle;
}

.gantt-cell:hover { background: #e3f2fd !important; }
.gantt-cell.weekend { background: #f9f9f9; }
.gantt-cell.absent { background: #ffcdd2; }
.gantt-cell.absent:hover { background: #ef9a9a !important; }
.gantt-cell.today { outline: 2px solid #3949ab; outline-offset: -2px; }

.absent-dot {
  font-size: 0.65rem;
  color: #c62828;
  font-weight: 700;
  line-height: 1;
}

.section-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: #1a237e; }

td {
  padding: 0.75rem 0 0.75rem 0;
}
</style>
