<template>
  <div class="strategy-page">
    <el-alert
      title="策略功能开发中"
      type="info"
      description="策略配置、自动交易、风控管理等功能正在开发中，敬请期待！"
      show-icon
      :closable="false"
      style="margin-bottom: 20px"
    />

    <!-- 策略列表 -->
    <div class="card">
      <div class="card-title">
        <span>策略列表</span>
        <el-button type="primary" size="small" @click="showCreateDialog = true">
          新建策略
        </el-button>
      </div>
      
      <el-empty description="暂无策略" v-if="strategies.length === 0">
        <el-button type="primary" @click="showCreateDialog = true">创建第一个策略</el-button>
      </el-empty>
      
      <el-table :data="strategies" stripe v-else>
        <el-table-column prop="name" label="策略名称" />
        <el-table-column prop="type" label="策略类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="toggleStrategy(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="profit" label="累计收益" width="150" align="right">
          <template #default="{ row }">
            <span :class="row.profit >= 0 ? 'amount-positive' : 'amount-negative'">
              {{ row.profit >= 0 ? '+' : '' }}{{ row.profit.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="editStrategy(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteStrategy(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 风控设置 -->
    <div class="card">
      <div class="card-title">风控设置</div>
      <el-form :model="riskSettings" label-width="120px">
        <el-form-item label="单笔最大金额">
          <el-input-number v-model="riskSettings.maxOrderAmount" :min="0" />
          <span style="margin-left: 8px">HKD</span>
        </el-form-item>
        <el-form-item label="每日最大亏损">
          <el-input-number v-model="riskSettings.maxDailyLoss" :min="0" />
          <span style="margin-left: 8px">HKD</span>
        </el-form-item>
        <el-form-item label="止损比例">
          <el-input-number v-model="riskSettings.stopLossRatio" :min="0" :max="100" />
          <span style="margin-left: 8px">%</span>
        </el-form-item>
        <el-form-item label="止盈比例">
          <el-input-number v-model="riskSettings.takeProfitRatio" :min="0" :max="100" />
          <span style="margin-left: 8px">%</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveRiskSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 创建策略对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建策略" width="500px">
      <el-form :model="newStrategy" label-width="100px">
        <el-form-item label="策略名称">
          <el-input v-model="newStrategy.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-select v-model="newStrategy.type">
            <el-option label="均线策略" value="MA" />
            <el-option label="MACD策略" value="MACD" />
            <el-option label="网格交易" value="GRID" />
            <el-option label="定投策略" value="DCA" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标股票">
          <el-input v-model="newStrategy.stock_code" placeholder="如：HK.00700" />
        </el-form-item>
        <el-form-item label="初始资金">
          <el-input-number v-model="newStrategy.capital" :min="10000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createStrategy">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const strategies = ref<any[]>([])

const riskSettings = reactive({
  maxOrderAmount: 50000,
  maxDailyLoss: 5000,
  stopLossRatio: 5,
  takeProfitRatio: 10
})

const showCreateDialog = ref(false)
const newStrategy = reactive({
  name: '',
  type: 'MA',
  stock_code: '',
  capital: 50000
})

const toggleStrategy = (strategy: any) => {
  ElMessage.success(`策略 ${strategy.name} ${strategy.enabled ? '已启用' : '已停用'}`)
}

const editStrategy = (strategy: any) => {
  ElMessage.info('策略编辑功能开发中')
}

const deleteStrategy = (strategy: any) => {
  ElMessage.info('策略删除功能开发中')
}

const saveRiskSettings = () => {
  ElMessage.success('风控设置已保存')
}

const createStrategy = () => {
  if (!newStrategy.name || !newStrategy.stock_code) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  strategies.value.push({
    id: Date.now(),
    ...newStrategy,
    enabled: false,
    profit: 0
  })
  
  showCreateDialog.value = false
  ElMessage.success('策略创建成功')
  
  // 重置表单
  newStrategy.name = ''
  newStrategy.stock_code = ''
}
</script>

<style lang="scss" scoped>
.strategy-page {
  .card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
