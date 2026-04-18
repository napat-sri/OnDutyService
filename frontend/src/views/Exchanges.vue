<script setup>
import { ref, onMounted } from 'vue'
import { exchangeService, officerService, scheduleService } from '../services/api'

const exchanges = ref([])
const officers = ref([])
const loading = ref(true)
const error = ref(null)
const success = ref(null)

const showModal = ref(false)
const form = ref({
  request_type: 'exchange',
  requester_id: '',
  requester_date: '',
  target_id: '',
  target_date: '',
  reason: '',
})

const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1

const requesterDuties = ref([])
const targetDuties = ref([])

const requestTypeLabels = {
  exchange: 'แลกเวร',
  represent: 'แทนเวร',
}

const statusLabels = {
  pending: 'รอดำเนินการ',
  approved: 'อนุมัติแล้ว',
  rejected: 'ปฏิเสธแล้ว',
}

const statusClass = {
  pending: 'badge-pending',
  approved: 'badge-approved',
  rejected: 'badge-rejected',
}

async function loadData() {
  try {
    loading.value = true
    const [exchRes, offRes] = await Promise.all([
      exchangeService.list(),
      officerService.list(),
    ])
    exchanges.value = exchRes.data
    officers.value = offRes.data
  } catch (e) {
    error.value = 'ไม่สามารถโหลดข้อมูลได้'
  } finally {
    loading.value = false
  }
}

async function loadDutiesForOfficer(officerId, year, month, target) {
  try {
    const res = await scheduleService.get(year, month)
    const entries = res.data.entries.filter(e => e.officer_id === officerId)
    if (target === 'requester') requesterDuties.value = entries
    else targetDuties.value = entries
  } catch {
    if (target === 'requester') requesterDuties.value = []
    else targetDuties.value = []
  }
}

async function onRequesterChange() {
  form.value.requester_date = ''
  if (form.value.requester_id) {
    await loadDutiesForOfficer(form.value.requester_id, currentYear, currentMonth, 'requester')
  }
}

async function onTargetChange() {
  form.value.target_date = ''
  if (form.value.target_id) {
    await loadDutiesForOfficer(form.value.target_id, currentYear, currentMonth, 'target')
  }
}

function openCreate(type = 'exchange') {
  form.value = {
    request_type: type,
    requester_id: '',
    requester_date: '',
    target_id: '',
    target_date: '',
    reason: '',
  }
  requesterDuties.value = []
  targetDuties.value = []
  showModal.value = true
}

function closeModal() { showModal.value = false }

function getOfficerName(id) {
  const o = officers.value.find(x => x._id === id)
  return o ? `${o.rank} ${o.name}` : id
}

async function submitExchange() {
  try {
    error.value = null
    const requester = officers.value.find(o => o._id === form.value.requester_id)
    const target = officers.value.find(o => o._id === form.value.target_id)
    if (!requester || !target) return

    await exchangeService.create({
      request_type: form.value.request_type,
      requester_id: requester._id,
      requester_name: `${requester.rank} ${requester.name}`,
      requester_date: form.value.requester_date,
      target_id: target._id,
      target_name: `${target.rank} ${target.name}`,
      target_date: form.value.request_type === 'exchange' ? form.value.target_date : null,
      reason: form.value.reason,
    })
    success.value = form.value.request_type === 'represent'
      ? 'ส่งคำขอคนแทนเวรสำเร็จ'
      : 'ส่งคำขอเปลี่ยนเวรสำเร็จ'
    closeModal()
    await loadData()
    setTimeout(() => (success.value = null), 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'เกิดข้อผิดพลาด'
  }
}

async function approveExchange(id) {
  if (!confirm('ยืนยันการอนุมัติคำขอนี้?')) return
  try {
    const item = exchanges.value.find(x => x._id === id)
    await exchangeService.updateStatus(id, 'approved', '')
    success.value = item?.request_type === 'represent'
      ? 'อนุมัติคำขอสำเร็จ ระบบจะมอบหมายเวรให้ผู้แทนโดยไม่สลับเวร'
      : 'อนุมัติคำขอสำเร็จ ระบบจะสลับเวรในตารางโดยอัตโนมัติ'
    await loadData()
    setTimeout(() => (success.value = null), 4000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'เกิดข้อผิดพลาด'
  }
}

async function rejectExchange(id) {
  const note = prompt('เหตุผลที่ปฏิเสธ (ถ้ามี):') ?? ''
  try {
    await exchangeService.updateStatus(id, 'rejected', note)
    success.value = 'ปฏิเสธคำขอสำเร็จ'
    await loadData()
    setTimeout(() => (success.value = null), 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'เกิดข้อผิดพลาด'
  }
}

async function deleteExchange(id) {
  if (!confirm('ยืนยันการลบคำขอนี้?')) return
  try {
    await exchangeService.delete(id)
    success.value = 'ลบคำขอสำเร็จ'
    await loadData()
    setTimeout(() => (success.value = null), 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'เกิดข้อผิดพลาด'
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('th-TH', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(loadData)
</script>

<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">🔄 คำขอเปลี่ยนเวร</h1>
      <div class="flex gap-2">
        <button class="btn btn-primary" @click="openCreate('exchange')">+ ขอแลกเวร</button>
        <button class="btn btn-secondary" @click="openCreate('represent')">+ ขอคนแทนเวร</button>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div class="card">
      <div v-if="loading" class="text-center text-muted">กำลังโหลด...</div>
      <div v-else-if="exchanges.length === 0" class="text-center text-muted" style="padding:2rem">
        ยังไม่มีคำขอเปลี่ยนเวร
      </div>
      <div v-else class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>ผู้ขอ</th>
              <!-- <th>ประเภท</th> -->
              <th>วันที่ขอ</th>
              <th>สลับกับ</th>
              <th>วันที่สลับ</th>
              <!-- <th>เหตุผล</th> -->
              <th>สถานะ</th>
              <th>จัดการ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(exch, idx) in exchanges" :key="exch._id">
              <td>{{ idx + 1 }}</td>
              <td><strong>{{ exch.requester_name }}</strong></td>
              <!-- <td>{{ requestTypeLabels[exch.request_type || 'exchange'] }}</td> -->
              <td>{{ formatDate(exch.requester_date) }}</td>
              <td>{{ exch.target_name }}</td>
              <td>{{ exch.request_type === 'represent' ? '-' : formatDate(exch.target_date) }}</td>
              <!-- <td>{{ exch.reason || '-' }}</td> -->
              <td>
                <span class="badge" :class="statusClass[exch.status]">
                  {{ statusLabels[exch.status] }}
                </span>
                <div v-if="exch.admin_note" class="text-muted" style="font-size:0.78rem;margin-top:2px">
                  หมายเหตุ: {{ exch.admin_note }}
                </div>
              </td>
              <td>
                <div class="flex gap-2">
                  <template v-if="exch.status === 'pending'">
                    <button class="btn btn-success btn-sm" @click="approveExchange(exch._id)">✅ อนุมัติ</button>
                    <button class="btn btn-danger btn-sm" @click="rejectExchange(exch._id)">❌ ปฏิเสธ</button>
                  </template>
                  <button class="btn btn-secondary btn-sm" @click="deleteExchange(exch._id)">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Exchange Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ form.request_type === 'represent' ? '👥 ขอคนแทนเวร' : '🔄 ขอแลกเวร' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="alert alert-info">
          ระบบจะค้นหาเวรของเดือนปัจจุบัน ({{ currentMonth }}/{{ currentYear }}) สำหรับแต่ละเจ้าหน้าที่
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem">
          <!-- Requester -->
          <div>
            <h4 style="margin-bottom:0.5rem;color:#1565c0">ผู้ขอเปลี่ยน</h4>
            <div class="form-group">
              <label>เจ้าหน้าที่ *</label>
              <select v-model="form.requester_id" @change="onRequesterChange">
                <option value="">-- เลือก --</option>
                <option v-for="o in officers" :key="o._id" :value="o._id">
                  {{ o.rank }} {{ o.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>วันที่ขอสลับ *</label>
              <select v-model="form.requester_date" :disabled="!requesterDuties.length">
                <option value="">{{ requesterDuties.length ? '-- เลือกวัน --' : 'ไม่พบเวรในเดือนนี้' }}</option>
                <option v-for="d in requesterDuties" :key="d.date" :value="d.date">{{ d.date }}</option>
              </select>
              <div v-if="form.requester_id && !requesterDuties.length" class="text-muted mt-1" style="font-size:0.8rem">
                เจ้าหน้าที่นี้ไม่มีเวรในเดือนปัจจุบัน หรือยังไม่ได้จัดตาราง
              </div>
            </div>
          </div>

          <!-- Target -->
          <div>
            <h4 style="margin-bottom:0.5rem;color:#2e7d32">
              {{ form.request_type === 'represent' ? 'เปลี่ยนเป็น' : 'ขอสลับกับ' }}
            </h4>
            <div class="form-group">
              <label>เจ้าหน้าที่ *</label>
              <select v-model="form.target_id" @change="onTargetChange">
                <option value="">-- เลือก --</option>
                <option v-for="o in officers.filter(x => x._id !== form.requester_id)" :key="o._id" :value="o._id">
                  {{ o.rank }} {{ o.name }}
                </option>
              </select>
            </div>
            <div v-if="form.request_type === 'exchange'" class="form-group">
              <label>วันที่ขอสลับ *</label>
              <select v-model="form.target_date" :disabled="!targetDuties.length">
                <option value="">{{ targetDuties.length ? '-- เลือกวัน --' : 'ไม่พบเวรในเดือนนี้' }}</option>
                <option v-for="d in targetDuties" :key="d.date" :value="d.date">{{ d.date }}</option>
              </select>
              <div v-if="form.target_id && !targetDuties.length" class="text-muted mt-1" style="font-size:0.8rem">
                เจ้าหน้าที่นี้ไม่มีเวรในเดือนปัจจุบัน หรือยังไม่ได้จัดตาราง
              </div>
            </div>
            <div v-else class="text-muted mt-1" style="font-size:0.8rem">
              ผู้แทนเวรจะถูกมอบหมายให้รับเวรในวันที่ผู้ขอ โดยไม่มีการสลับเวรกลับ
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>เหตุผล</label>
          <textarea v-model="form.reason" rows="2" placeholder="ระบุเหตุผลในการขอเปลี่ยนเวร (ถ้ามี)"></textarea>
        </div>

        <div class="flex gap-2 mt-2">
          <button class="btn btn-primary" @click="submitExchange"
            :disabled="!form.requester_id || !form.requester_date || !form.target_id || (form.request_type === 'exchange' && !form.target_date)">
            📤 ส่งคำขอ
          </button>
          <button class="btn btn-secondary" @click="closeModal">ยกเลิก</button>
        </div>
      </div>
    </div>
  </div>
</template>
