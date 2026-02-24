<template>
  <div class="home-page">
    <!-- 概览卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <div class="card stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
            <el-icon><Wallet /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">总资产</div>
            <div class="stat-value">{{ formatMoney(accountStore.totalAssets) }}</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="card stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%)">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">可用资金</div>
            <div class="stat-value">{{ formatMoney(accountStore.availableCash) }}</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="card stat-card">
          <div class="stat-icon" :style="profitLossStyle">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">持仓盈亏</div>
            <div class="stat-value" :class="profitLossClass">
              {{ formatMoney(accountStore.totalProfitLoss) }}
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="card stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
            <el-icon><Collection /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">持仓数量</div>
            <div class="stat-value">{{ accountStore.positions.length }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 持仓列表 -->
    <div class="card">
      <div class="card-title">持仓列表</div>
      <el-table :data="accountStore.positions" stripe>
        <el-table-column prop="stock_code" label="股票代码" width="120" />
        <el-table-column prop="stock_name" label="股票名称" width="150" />
        <el-table-column prop="quantity" label="持有数量" width="100" align="right" />
        <el-table-column prop="cost_price" label="成本价" width="100" align="right">
          <template #default="{ row }">
            {{ row.cost_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="现价" width="100" align="right">
          <template #default="{ row }">
            {{ row.current_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="market_value" label="市值" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.market_value) }}
          </template>
        </el-table-column>
        <el-table-column prop="profit_loss" label="盈亏" width="120" align="right">
          <template #default="{ row }">
            <span :class="row.profit_loss >= 0 ? 'amount-positive' : 'amount-negative'">
              {{ formatMoney(row.profit_loss) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_loss_ratio" label="收益率" align="right">
          <template #default="{ row }">
            <span :class="row.profit_loss_ratio >= 0 ? 'amount-positive' : 'amount-negative'">
              {{ (row.profit_loss_ratio * 100).toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 系统状态 -->
    <div class="card">
      <div class="card-title">系统状态</div>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="OpenD状态">
          <el-tag :type="accountStore.opendConnected ? 'success' : 'danger'">
            {{ accountStore.opendConnected ? '已连接' : '未连接' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="账户状态">
          <el-tag type="success">正常</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="系统版本">v0.1.0</el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAccountStore } from '@/stores/account'

const accountStore = useAccountStore()

const formatMoney = (value: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'HKD',
    minimumFractionDigits: 2
  }).format(value)
}

const profitLossClass = computed(() => {
  return accountStore.totalProfitLoss >= 0 ? 'amount-positive' : 'amount-negative'
})

const profitLossStyle = computed(() => {
  if (accountStore.totalProfitLoss >= 0) {
    return 'background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%)'
  }
  return 'background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
})

onMounted(() => {
  accountStore.refreshAll()
})
</script>

<style lang="scss" scoped>
.home-page {
  .stat-card {
    display: flex;
    align-items: center;
    padding: 24px;
    
    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;
      
      .el-icon {
        font-size: 28px;
        color: #fff;
      }
    }
    
    .stat-content {
      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 8px;
      }
      
      .stat-value {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }
    }
  }
}
</style>
