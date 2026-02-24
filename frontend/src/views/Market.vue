<template>
  <div class="market-page">
    <!-- 搜索栏 -->
    <div class="card">
      <el-input
        v-model="searchKeyword"
        placeholder="输入股票代码或名称搜索"
        class="search-input"
        @keyup.enter="handleSearch"
        clearable
      >
        <template #append>
          <el-button @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>

    <!-- 搜索结果 -->
    <div class="card" v-if="searchResults.length > 0">
      <div class="card-title">搜索结果</div>
      <el-table :data="searchResults" stripe @row-click="selectStock">
        <el-table-column prop="stock_code" label="股票代码" width="150" />
        <el-table-column prop="stock_name" label="股票名称" />
        <el-table-column prop="market" label="市场" width="100" />
      </el-table>
    </div>

    <!-- 当前股票信息 -->
    <div class="card" v-if="currentQuote">
      <div class="card-title">
        <span>{{ currentQuote.stock_name }} ({{ currentQuote.stock_code }})</span>
        <el-button type="primary" size="small" @click="goToTrade">
          交易
        </el-button>
      </div>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="quote-item">
            <div class="quote-label">最新价</div>
            <div class="quote-value" :class="currentQuote.change >= 0 ? 'amount-positive' : 'amount-negative'">
              {{ currentQuote.current_price.toFixed(3) }}
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="quote-item">
            <div class="quote-label">涨跌额</div>
            <div class="quote-value" :class="currentQuote.change >= 0 ? 'amount-positive' : 'amount-negative'">
              {{ currentQuote.change.toFixed(3) }}
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="quote-item">
            <div class="quote-label">涨跌幅</div>
            <div class="quote-value" :class="currentQuote.change_ratio >= 0 ? 'amount-positive' : 'amount-negative'">
              {{ (currentQuote.change_ratio * 100).toFixed(2) }}%
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="quote-item">
            <div class="quote-label">成交量</div>
            <div class="quote-value">{{ formatVolume(currentQuote.volume) }}</div>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 16px">
        <el-col :span="6">
          <div class="quote-item small">
            <div class="quote-label">今开</div>
            <div class="quote-value">{{ currentQuote.open_price.toFixed(3) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="quote-item small">
            <div class="quote-label">最高</div>
            <div class="quote-value amount-positive">{{ currentQuote.high_price.toFixed(3) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="quote-item small">
            <div class="quote-label">最低</div>
            <div class="quote-value amount-negative">{{ currentQuote.low_price.toFixed(3) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="quote-item small">
            <div class="quote-label">昨收</div>
            <div class="quote-value">{{ currentQuote.prev_close_price.toFixed(3) }}</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- K线图 -->
    <div class="card" v-if="currentQuote">
      <div class="card-title">K线图</div>
      <div ref="chartRef" class="chart-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useMarketStore } from '@/stores/market'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts'

const router = useRouter()
const marketStore = useMarketStore()
const { currentQuote, klineData, searchResults, loading } = storeToRefs(marketStore)

const searchKeyword = ref('')
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const handleSearch = async () => {
  if (searchKeyword.value) {
    await marketStore.searchStock(searchKeyword.value)
  }
}

const selectStock = async (row: any) => {
  await marketStore.fetchQuote(row.stock_code)
  await marketStore.fetchKline(row.stock_code)
  searchResults.value = []
}

const goToTrade = () => {
  if (currentQuote.value) {
    router.push({
      path: '/trade',
      query: { code: currentQuote.value.stock_code }
    })
  }
}

const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  }
  if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

const renderChart = () => {
  if (!chartRef.value || klineData.value.length === 0) return
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: klineData.value.map(k => k.timestamp.slice(0, 10))
    },
    yAxis: {
      type: 'value',
      scale: true
    },
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData.value.map(k => [k.open_price, k.close_price, k.low_price, k.high_price])
      }
    ]
  }
  
  chartInstance.setOption(option)
}

watch(klineData, () => {
  nextTick(() => {
    renderChart()
  })
})

onMounted(() => {
  // 加载默认股票
  marketStore.fetchQuote('HK.00700')
  marketStore.fetchKline('HK.00700')
})
</script>

<style lang="scss" scoped>
.market-page {
  .search-input {
    width: 400px;
  }
  
  .quote-item {
    text-align: center;
    
    .quote-label {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
    }
    
    .quote-value {
      font-size: 20px;
      font-weight: 600;
      
      &.small {
        font-size: 16px;
      }
    }
  }
  
  .chart-container {
    height: 400px;
  }
}
</style>
