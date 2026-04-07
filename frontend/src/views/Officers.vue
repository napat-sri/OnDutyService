<script setup>
import { ref, onMounted } from 'vue'
import { officerService } from '../services/api'

const officers = ref([])
const loading = ref(true)
const error = ref(null)
const success = ref(null)

const showModal = ref(false)
const editingOfficer = ref(null)
const form = ref({ name: '', rank: '', position: '', department: '', phone: '' })

const ranks = ['นาย', 'นาง', 'นางสาว',
  'จ.ต.', 'จ.ต.หญิง', 'จ.ท.', 'จ.ท.หญิง', 'จ.อ.', 'จ.อ.หญิง',
  'พ.อ.ต.', 'พ.อ.ต.หญิง', 'พ.อ.ท.', 'พ.อ.ท.หญิง', 'พ.อ.อ.', 'พ.อ.อ.หญิง',
  'ร.ต.', 'ร.ต.หญิง', 'ร.ท.', 'ร.ท.หญิง', 'ร.อ.', 'ร.อ.หญิง',
  'น.ต.', 'น.ต.หญิง']

const departments = ['บก.ศซว.ทอ.', 'กมซ.ศซว.ทอ.', 'กวซ.ศซว.ทอ.', 'กบสซ.ศซว.ทอ.',]

async function loadOfficers() {
  try {
    loading.value = true
    const res = await officerService.list()
    officers.value = res.data
  } catch (e) {
    error.value = 'ไม่สามารถโหลดข้อมูลเจ้าหน้าที่ได้'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingOfficer.value = null
  form.value = { name: '', rank: '', position: '', department: '', phone: '' }
  showModal.value = true
}

function openEdit(officer) {
  editingOfficer.value = officer
  form.value = { ...officer }
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

    <div class="card">
      <div v-if="loading" class="text-center text-muted">กำลังโหลด...</div>
      <div v-else-if="officers.length === 0" class="text-center text-muted" style="padding:2rem">
        ยังไม่มีเจ้าหน้าที่ในระบบ คลิก "เพิ่มเจ้าหน้าที่" เพื่อเริ่มต้น
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
              <th>เบอร์โทร</th>
              <th>จัดการ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(officer, idx) in officers" :key="officer._id">
              <td>{{ idx + 1 }}</td>
              <td>{{ officer.rank }}</td>
              <td><strong>{{ officer.name }}</strong></td>
              <td>{{ officer.position }}</td>
              <td>{{ officer.department || '-' }}</td>
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
