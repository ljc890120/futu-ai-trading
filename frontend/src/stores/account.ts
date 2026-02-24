import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'

export const useAccountStore = defineStore('account', () => {
  // 状态
  const accountInfo = ref<any>(null)
  const positions = ref<any[]>([])
  const opendConnected = ref(false)
  const loading = ref(false)
  
  // 计算属性
  const totalAssets = computed(() => accountInfo.value?.total_assets || 0)
  const availableCash = computed(() => accountInfo.value?.available_cash || 0)
  const totalProfitLoss = computed(() => {
    return positions.value.reduce((sum, p) => sum + p.profit_loss, 0)
  })
  
  // 方法
  async function fetchAccountInfo() {
    try {
      loading.value = true
      accountInfo.value = await api.account.info()
    } catch (error) {
      console.error('获取账户信息失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  async function fetchPositions() {
    try {
      positions.value = await api.account.positions()
    } catch (error) {
      console.error('获取持仓列表失败:', error)
    }
  }
  
  async function fetchAccountStatus() {
    try {
      const status = await api.account.status()
      opendConnected.value = status.opend_connected
    } catch (error) {
      console.error('获取账户状态失败:', error)
      opendConnected.value = false
    }
  }
  
  async function refreshAll() {
    await Promise.all([
      fetchAccountInfo(),
      fetchPositions(),
      fetchAccountStatus()
    ])
  }
  
  return {
    // 状态
    accountInfo,
    positions,
    opendConnected,
    loading,
    // 计算属性
    totalAssets,
    availableCash,
    totalProfitLoss,
    // 方法
    fetchAccountInfo,
    fetchPositions,
    fetchAccountStatus,
    refreshAll
  }
})
