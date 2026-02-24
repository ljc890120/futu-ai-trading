<template>
  <div class="account-page">
    <!-- 账户信息卡片 -->
    <div class="card">
      <div class="card-title">账户信息</div>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="总资产" :value="accountInfo?.total_assets || 0" :precision="2">
            <template #suffix>HKD</template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="持仓市值" :value="accountInfo?.market_value || 0" :precision="2">
            <template #suffix>HKD</template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="可用资金" :value="accountInfo?.available_cash || 0" :precision="2">
            <template #suffix>HKD</template>
          </el-statistic>
        </el-col>
      </el-row>
    </div>

    <!-- 持仓明细 -->
    <div class="card">
      <div class="card-title">
        <span>持仓明细</span>
        <el-button type="primary" size="small" @click="refreshPositions" :loading="loading">
          刷新
        </el-button>
      </div>
      <el-table :data="positions" stripe>
        <el-table-column prop="stock_code" label="股票代码" width="120" />
        <el-table-column prop="stock_name" label="股票名称" width="150" />
        <el-table-column prop="quantity" label="持有数量" width="100" align="right" />
        <el-table-column prop="available_quantity" label="可卖数量" width="100" align="right" />
        <el-table-column prop="cost_price" label="成本价" width="100" align="right">
          <template #default="{ row }">
            {{ row.cost_price.toFixed(3) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="现价" width="100" align="right">
          <template #default="{ row }">
            {{ row.current_price.toFixed(3) }}
          </template>
        </el-table-column>
        <el-table-column prop="market_value" label="市值" width="120" align="right">
          <template #default="{ row }">
            {{ row.market_value.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="盈亏" align="right">
          <template #default="{ row }">
            <div>
              <span :class="row.profit_loss >= 0 ? 'amount-positive' : 'amount-negative'">
                {{ row.profit_loss.toFixed(2) }}
              </span>
              <span :class="row.profit_loss_ratio >= 0 ? 'amount-positive' : 'amount-negative'" style="margin-left: 8px">
                ({{ (row.profit_loss_ratio * 100).toFixed(2) }}%)
              </span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAccountStore } from '@/stores/account'
import { storeToRefs } from 'pinia'

const accountStore = useAccountStore()
const { accountInfo, positions, loading } = storeToRefs(accountStore)

const refreshPositions = async () => {
  await accountStore.refreshAll()
}

onMounted(() => {
  accountStore.refreshAll()
})
</script>

<style lang="scss" scoped>
.account-page {
  .card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
