import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '系统概览' }
  },
  {
    path: '/account',
    name: 'Account',
    component: () => import('@/views/Account.vue'),
    meta: { title: '账户管理' }
  },
  {
    path: '/market',
    name: 'Market',
    component: () => import('@/views/Market.vue'),
    meta: { title: '行情中心' }
  },
  {
    path: '/trade',
    name: 'Trade',
    component: () => import('@/views/Trade.vue'),
    meta: { title: '交易下单' }
  },
  {
    path: '/strategy',
    name: 'Strategy',
    component: () => import('@/views/Strategy.vue'),
    meta: { title: '策略配置' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || '富途交易系统'} - 富途股票交易管理系统`
  next()
})

export default router
