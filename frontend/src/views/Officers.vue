<script setup>
import { ref, computed, onMounted } from 'vue'
import { officerService } from '../services/api'

const officers = ref([])
const dutyTypes = ref([])
const loading = ref(true)
const error = ref(null)
const success = ref(null)

const showModal = ref(false)
const editingOfficer = ref(null)
const form = ref({ name: '', rank: '', position: '', department: '', phone: '', duty_types: [] })

const activeTab = ref('ทั้งหมด')

const ranks = ['นาย', 'นาง', 'นางสาว',
  'จ.ต.', 'จ.ต.หญิง', 'จ.ท.', 'จ.ท.หญิง', 'จ.อ.', 'จ.อ.หญิง',
  'พ.อ.ต.', 'พ.อ.ต.หญิง', 'พ.อ.ท.', 'พ.อ.ท.หญิง', 'พ.อ.อ.', 'พ.อ.อ.หญิง',
  'ร.ต.', 'ร.ต.หญิง', 'ร.ท.', 'ร.ท.หญิง', 'ร.อ.', 'ร.อ.หญิง',
  'น.ต.', 'น.ต.หญิง']

const departments = ['บก.ศซว.ทอ.', 'กมซ.ศซว.ทอ.', 'กวซ.ศซว.ทอ.', 'กบสซ.ศซว.ทอ.',]

const tabs = computed(() => ['ทั้งหมด', ...dutyTypes.value])

const dutyBadgePalette = [
  { background: '#e3f2fd', color: '#1565c0', borderColor: '#90caf9' },
  { background: '#e8f5e9', color: '#2e7d32', borderColor: '#a5d6a7' },
  { background: '#fff3e0', color: '#ef6c00', borderColor: '#ffcc80' },
  { background: '#f3e5f5', color: '#7b1fa2', borderColor: '#ce93d8' },
  { background: '#e0f2f1', color: '#00695c', borderColor: '#80cbc4' },
  { background: '#fbe9e7', color: '#d84315', borderColor: '#ffab91' },
  { background: '#f1f8e9', color: '#558b2f', borderColor: '#c5e1a5' },
  { background: '#ede7f6', color: '#4527a0', borderColor: '#b39ddb' },
]

function hashDuty(duty) {
  return [...duty].reduce((sum, ch) => sum + ch.charCodeAt(0), 0)
}

function dutyBadgeStyle(duty) {
  const idx = hashDuty(duty) % dutyBadgePalette.length
  return {
    background: dutyBadgePalette[idx].background,
    color: dutyBadgePalette[idx].color,
    border: `1px solid ${dutyBadgePalette[idx].borderColor}`,
  }
}

const filteredOfficers = computed(() => {
  if (activeTab.value === 'ทั้งหมด') return officers.value
  return officers.value.filter(o => (o.duty_types || []).includes(activeTab.value))
})

async function loadOfficers() {
  try {
    loading.value = true
    const [offRes, dtRes] = await Promise.all([
      officerService.list(),
      officerService.listDutyTypes(),
    ])
    officers.value = offRes.data
    dutyTypes.value = dtRes.data
  } catch (e) {
    error.value = 'ไม่สามารถโหลดข้อมูลเจ้าหน้าที่ได้'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingOfficer.value = null
  form.value = { name: '', rank: '', position: '', department: '', phone: '', duty_types: [] }
  showModal.value = true
}

function openEdit(officer) {
  editingOfficer.value = officer
  form.value = { ...officer, duty_types: [...(officer.duty_types || [])] }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingOfficer.value = null
}

async function saveOfficer() {
  try {
    error.value = null
    if (editingOfficer.value) {
      await officerService.update(editingOfficer.value._id, form.value)
      success.value = 'แก้ไขข้อมูลเจ้าหน้าที่สำเร็จ'
    } else {
      await officerService.create(form.value)
      success.value = 'เพิ่มเจ้าหน้าที่สำเร็จ'
    }
    closeModal()
    await loadOfficers()
    setTimeout(() => (success.value = null), 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'เกิดข้อผิดพลาด'
  }
}

async function deleteOfficer(officer) {
  if (!confirm(`ยืนยันการลบ ${officer.name}?`)) return
  try {
    await officerService.delete(officer._id)
    success.value = 'ลบเจ้าหน้าที่สำเร็จ'
    await loadOfficers()
    setTimeout(() => (success.value = null), 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'เกิดข้อผิดพลาด'
  }
}

onMounted(loadOfficers)
</script>

<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">👮 เจ้าหน้าที่</h1>
      <button class="btn btn-primary" @click="openCreate">+ เพิ่มเจ้าหน้าที่</button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <!-- Duty type tabs -->
    <div class="duty-tabs">
      <button v-for="tab in tabs" :key="tab" class="duty-tab" :class="{ active: activeTab === tab }"
        @click="activeTab = tab">
        {{ tab }}
        <span class="tab-count">
          {{
            tab === 'ทั้งหมด'
              ? officers.length
              : officers.filter(o => (o.duty_types || []).includes(tab)).length
          }}
        </span>
      </button>
    </div>

    <div class="card">
      <div v-if="loading" class="text-center text-muted">กำลังโหลด...</div>
      <div v-else-if="filteredOfficers.length === 0" class="text-center text-muted" style="padding:2rem">
        ไม่มีเจ้าหน้าที่ในหน้านี้
      </div>
      <div v-else class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>ยศ</th>
              <th>ชื่อ</th>
              <th>ตำแหน่ง</th>
              <th>สังกัด</th>
              <th>หน้าที่เวร</th>
              <th>เบอร์โทร</th>
              <th>จัดการ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(officer, idx) in filteredOfficers" :key="officer._id">
              <td>{{ idx + 1 }}</td>
              <td>{{ officer.rank }}</td>
              <td><strong>{{ officer.name }}</strong></td>
              <td>{{ officer.position }}</td>
              <td>{{ officer.department || '-' }}</td>
              <td>
                <div class="duty-badges">
                  <span v-for="dt in (officer.duty_types || [])" :key="dt" class="duty-badge"
                    :style="dutyBadgeStyle(dt)">{{ dt }}</span>
                  <span v-if="!(officer.duty_types || []).length" class="text-muted">-</span>
                </div>
              </td>
              <td>{{ officer.phone || '-' }}</td>
              <td>
                <div class="flex gap-2">
                  <button class="btn btn-secondary btn-sm" @click="openEdit(officer)">✏️ แก้ไข</button>
                  <button class="btn btn-danger btn-sm" @click="deleteOfficer(officer)">🗑️ ลบ</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingOfficer ? '✏️ แก้ไขเจ้าหน้าที่' : '➕ เพิ่มเจ้าหน้าที่' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <form @submit.prevent="saveOfficer">
          <div class="form-group">
            <label>ยศ *</label>
            <select v-model="form.rank" required>
              <option value="">-- เลือกยศ --</option>
              <option v-for="r in ranks" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>ชื่อ-นามสกุล *</label>
            <input type="text" v-model="form.name" required placeholder="เช่น สมชาย ใจดี" />
          </div>
          <div class="form-group">
            <label>ตำแหน่ง (ตัวย่อ) *</label>
            <input type="text" v-model="form.position" required placeholder="เช่น นปซ.ผสพซ.2 กวซ.ศซว.ทอ." />
          </div>
          <div class="form-group">
            <label>สังกัด *</label>
            <select v-model="form.department" required>
              <option value="">-- เลือกสังกัด --</option>
              <option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>หน้าที่เวร</label>
            <div class="checkbox-group">
              <label v-for="dt in dutyTypes" :key="dt" class="checkbox-label">
                <input type="checkbox" :value="dt" v-model="form.duty_types" />
                {{ dt }}
              </label>
            </div>
          </div>
          <div class="form-group">
            <label>เบอร์โทรศัพท์</label>
            <input type="text" v-model="form.phone" placeholder="เช่น 081-234-5678" />
          </div>
          <div class="flex gap-2 mt-2">
            <button type="submit" class="btn btn-primary">💾 บันทึก</button>
            <button type="button" class="btn btn-secondary" @click="closeModal">ยกเลิก</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
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

.duty-tab:hover {
  border-color: #3949ab;
  color: #1a237e;
}

.duty-tab.active {
  background: #3949ab;
  border-color: #3949ab;
  color: white;
}

.tab-count {
  background: rgba(255, 255, 255, 0.3);
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

.duty-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.duty-badge {
  border: 1px solid transparent;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 0.75rem;
  white-space: nowrap;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}
</style>
