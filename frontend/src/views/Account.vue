<template>
  <div class="account-page">
    <!-- 账户选择 -->
    <div class="card account-selector">
      <div class="card-title">
        <span>账户选择</span>
        <el-tag :type="opendConnected ? 'success' : 'danger'" size="small">
          OpenD: {{ opendConnected ? '已连接' : '未连接' }}
        </el-tag>
      </div>
      <el-row :gutter="20" align="middle">
        <el-col :span="16">
          <el-select v-model="currentAccountId" placeholder="选择账户" @change="handleAccountChange" style="width: 100%">
            <el-option
              v-for="acc in accounts"
              :key="acc.acc_id"
              :label="getAccountLabel(acc)"
              :value="acc.acc_id"
              :disabled="acc.acc_status !== 'ACTIVE'"
            >
              <div class="account-option">
                <div class="account-main">
                  <span class="account-card-num">{{ acc.uni_card_num || acc.acc_id }}</span>
                  <el-tag size="small" :type="acc.trd_env === 'SIMULATE' ? 'warning' : 'primary'" style="margin-left: 8px">
                    {{ acc.trd_env === 'SIMULATE' ? '模拟' : '真实' }}
                  </el-tag>
                  <el-tag size="small" :type="acc.acc_status === 'ACTIVE' ? 'success' : 'info'" style="margin-left: 4px">
                    {{ acc.acc_status === 'ACTIVE' ? '活跃' : '禁用' }}
                  </el-tag>
                </div>
                <div class="account-detail">
                  <span v-if="acc.acc_type" class="detail-item">类型: {{ acc.acc_type }}</span>
                  <span v-if="acc.trdmarket_auth" class="detail-item">市场: {{ acc.trdmarket_auth }}</span>
                  <span v-if="acc.security_firm" class="detail-item">券商: {{ acc.security_firm }}</span>
                  <span v-if="acc.acc_role" class="detail-item">角色: {{ acc.acc_role }}</span>
                </div>
              </div>
            </el-option>
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-button type="primary" @click="refreshAll" :loading="loading">
            刷新数据
          </el-button>
        </el-col>
      </el-row>
      <!-- 当前选中账户详情 -->
      <div v-if="currentAccount" class="current-account-info">
        <el-descriptions :column="4" border size="small">
          <el-descriptions-item label="账户卡号">{{ currentAccount.uni_card_num || currentAccount.acc_id }}</el-descriptions-item>
          <el-descriptions-item label="账户ID">{{ currentAccount.acc_id }}</el-descriptions-item>
          <el-descriptions-item label="账户类型">{{ currentAccount.acc_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="交易市场">{{ currentAccount.trdmarket_auth || '-' }}</el-descriptions-item>
          <el-descriptions-item label="券商">{{ currentAccount.security_firm || '-' }}</el-descriptions-item>
          <el-descriptions-item label="角色">{{ currentAccount.acc_role || '-' }}</el-descriptions-item>
          <el-descriptions-item label="业务卡号">{{ currentAccount.card_num || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentAccount.acc_status === 'ACTIVE' ? 'success' : 'danger'" size="small">
              {{ currentAccount.acc_status === 'ACTIVE' ? '正常' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>

    <!-- 账户信息卡片 -->
    <div class="card">
      <div class="card-title">
        <span>账户信息</span>
        <el-tag v-if="accountInfo?.acc_id" type="info" size="small">
          ID: {{ accountInfo.acc_id }}
        </el-tag>
      </div>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="总资产" :value="accountInfo?.total_assets || 0" :precision="2">
            <template #suffix>HKD</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="持仓市值" :value="accountInfo?.market_value || 0" :precision="2">
            <template #suffix>HKD</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="可用资金" :value="accountInfo?.available_cash || 0" :precision="2">
            <template #suffix>HKD</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="现金" :value="accountInfo?.cash || 0" :precision="2">
            <template #suffix>HKD</template>
          </el-statistic>
        </el-col>
      </el-row>
    </div>

    <!-- 持仓明细 -->
    <div class="card">
      <div class="card-title">
        <span>持仓明细 (共 {{ positions.length }} 只)</span>
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
                ({{ row.profit_loss_ratio.toFixed(2) }}%)
              </span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useAccountStore } from '@/stores/account'
import { storeToRefs } from 'pinia'

const accountStore = useAccountStore()
const { accountInfo, positions, accounts, currentAccountId, opendConnected, loading } = storeToRefs(accountStore)

// 当前选中的账户对象
const currentAccount = computed(() => {
  return accounts.value.find(a => a.acc_id === currentAccountId.value)
})

// 获取账户显示标签
const getAccountLabel = (acc: any) => {
  const cardNum = acc.uni_card_num || acc.acc_id
  const env = acc.trd_env === 'SIMULATE' ? '模拟' : '真实'
  const status = acc.acc_status === 'ACTIVE' ? '' : '(禁用)'
  return `${cardNum} (${env}) ${status}`
}

const handleAccountChange = async (accId: string) => {
  await accountStore.switchAccount(accId)
}

const refreshAll = async () => {
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

  .account-selector {
    margin-bottom: 16px;
  }

  .account-option {
    width: 100%;
    
    .account-main {
      display: flex;
      align-items: center;
      
      .account-card-num {
        font-weight: 500;
        font-size: 14px;
      }
    }
    
    .account-detail {
      margin-top: 4px;
      font-size: 12px;
      color: #909399;
      
      .detail-item {
        margin-right: 16px;
      }
    }
  }

  .current-account-info {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #ebeef5;
  }

  .amount-positive {
    color: #67c23a;
  }

  .amount-negative {
    color: #f56c6c;
  }
}
</style>
