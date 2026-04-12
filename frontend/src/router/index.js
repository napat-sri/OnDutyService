import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Officers from '../views/Officers.vue'
import Schedule from '../views/Schedule.vue'
import Exchanges from '../views/Exchanges.vue'
import PersonnelManager from '../views/PersonnelManager.vue'

const routes = [
  { path: '/', component: Dashboard, name: 'dashboard' },
  { path: '/officers', component: Officers, name: 'officers' },
  { path: '/schedule', component: Schedule, name: 'schedule' },
  { path: '/exchanges', component: Exchanges, name: 'exchanges' },
  { path: '/personnel', component: PersonnelManager, name: 'personnel' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
