import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'

export const useAccountStore = defineStore('account', () => {
  // 状态
  const accountInfo = ref<any>(null)
  const positions = ref<any[]>([])
  const accounts = ref<any[]>([])
  const currentAccountId = ref<string>('')
  const opendConnected = ref(false)
  const tradeEnabled = ref(false)
  const loading = ref(false)

  // 计算属性
  const totalAssets = computed(() => accountInfo.value?.total_assets || 0)
  const availableCash = computed(() => accountInfo.value?.available_cash || 0)
  const totalProfitLoss = computed(() => {
    return positions.value.reduce((sum, p) => sum + p.profit_loss, 0)
  })
  const currentAccount = computed(() => {
    return accounts.value.find(a => a.acc_id === currentAccountId.value)
  })

  // 方法
  async function fetchAccountList() {
    try {
      accounts.value = await api.account.list()
      // 默认选择第一个活跃账户
      const activeAccount = accounts.value.find(a => a.acc_status === 'ACTIVE')
      if (activeAccount && !currentAccountId.value) {
        currentAccountId.value = activeAccount.acc_id
      }
    } catch (error) {
      console.error('获取账户列表失败:', error)
    }
  }

  async function fetchAccountInfo() {
    try {
      loading.value = true
      accountInfo.value = await api.account.info(currentAccountId.value || undefined)
    } catch (error) {
      console.error('获取账户信息失败:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchPositions() {
    try {
      positions.value = await api.account.positions(currentAccountId.value || undefined)
    } catch (error) {
      console.error('获取持仓列表失败:', error)
    }
  }

  async function fetchAccountStatus() {
    try {
      const status = await api.account.status()
      opendConnected.value = status.opend_connected
      tradeEnabled.value = status.trade_enabled
      if (status.accounts && status.accounts.length > 0) {
        accounts.value = status.accounts
        if (!currentAccountId.value) {
          const activeAccount = accounts.value.find(a => a.acc_status === 'ACTIVE')
          if (activeAccount) {
            currentAccountId.value = activeAccount.acc_id
          }
        }
      }
    } catch (error) {
      console.error('获取账户状态失败:', error)
      opendConnected.value = false
    }
  }

  async function switchAccount(accId: string) {
    currentAccountId.value = accId
    await refreshAll()
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
    accounts,
    currentAccountId,
    opendConnected,
    tradeEnabled,
    loading,
    // 计算属性
    totalAssets,
    availableCash,
    totalProfitLoss,
    currentAccount,
    // 方法
    fetchAccountList,
    fetchAccountInfo,
    fetchPositions,
    fetchAccountStatus,
    switchAccount,
    refreshAll
  }
})
