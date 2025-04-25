import { createRouter, createWebHistory } from 'vue-router'
import SentimentDashboard from '../components/SentimentDashboard.vue'

const router = createRouter({
  history: createWebHistory(), 
  routes: [
    {
      path: '/',
      name: 'home',
      component: SentimentDashboard,
    }
  ],
})

export default router