import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api'

export const useMarketStore = defineStore('market', () => {
  // 状态
  const currentQuote = ref<any>(null)
  const klineData = ref<any[]>([])
  const searchResults = ref<any[]>([])
  const watchList = ref<string[]>(['HK.00700', 'HK.09988', 'US.AAPL'])
  const watchListQuotes = ref<Record<string, any>>({})
  const loading = ref(false)
  
  // 方法
  async function fetchQuote(stockCode: string) {
    try {
      loading.value = true
      currentQuote.value = await api.market.quote(stockCode)
    } catch (error) {
      console.error('获取行情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  async function fetchKline(stockCode: string, params?: any) {
    try {
      loading.value = true
      klineData.value = await api.market.kline(stockCode, params)
    } catch (error) {
      console.error('获取K线数据失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  async function searchStock(keyword: string) {
    try {
      searchResults.value = await api.market.search(keyword)
    } catch (error) {
      console.error('搜索股票失败:', error)
    }
  }
  
  async function fetchWatchListQuotes() {
    const quotes: Record<string, any> = {}
    for (const code of watchList.value) {
      try {
        quotes[code] = await api.market.quote(code)
      } catch (error) {
        console.error(`获取 ${code} 行情失败:`, error)
      }
    }
    watchListQuotes.value = quotes
  }
  
  function addToWatchList(stockCode: string) {
    if (!watchList.value.includes(stockCode)) {
      watchList.value.push(stockCode)
    }
  }
  
  function removeFromWatchList(stockCode: string) {
    const index = watchList.value.indexOf(stockCode)
    if (index > -1) {
      watchList.value.splice(index, 1)
    }
  }
  
  return {
    // 状态
    currentQuote,
    klineData,
    searchResults,
    watchList,
    watchListQuotes,
    loading,
    // 方法
    fetchQuote,
    fetchKline,
    searchStock,
    fetchWatchListQuotes,
    addToWatchList,
    removeFromWatchList
  }
})
