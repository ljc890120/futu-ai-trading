<template>
  <div class="trade-page">
    <el-row :gutter="20">
      <!-- 左侧：下单区 -->
      <el-col :span="10">
        <div class="card">
          <div class="card-title">下单交易</div>
          
          <!-- 股票选择 -->
          <el-form :model="orderForm" label-width="80px">
            <el-form-item label="股票代码">
              <el-input
                v-model="orderForm.stock_code"
                placeholder="如：HK.00700"
                @change="handleStockCodeChange"
              />
            </el-form-item>
            
            <el-form-item label="股票名称">
              <el-input v-model="stockName" disabled />
            </el-form-item>
            
            <el-form-item label="当前价格">
              <el-input v-model="currentPrice" disabled>
                <template #append>HKD</template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="买卖方向">
              <el-radio-group v-model="orderForm.side">
                <el-radio-button value="BUY">买入</el-radio-button>
                <el-radio-button value="SELL">卖出</el-radio-button>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="订单类型">
              <el-select v-model="orderForm.order_type">
                <el-option label="限价单" value="LIMIT" />
                <el-option label="市价单" value="MARKET" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="价格" v-if="orderForm.order_type === 'LIMIT'">
              <el-input-number v-model="orderForm.price" :precision="3" :min="0" />
            </el-form-item>
            
            <el-form-item label="数量">
              <el-input-number v-model="orderForm.quantity" :min="1" :step="100" />
            </el-form-item>
            
            <el-form-item label="金额预估">
              <span class="amount-preview">{{ estimatedAmount }} HKD</span>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitOrder" :loading="submitting">
                确认下单
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
      
      <!-- 右侧：订单列表 -->
      <el-col :span="14">
        <div class="card">
          <div class="card-title">
            <span>今日订单</span>
            <el-button size="small" @click="refreshOrders">刷新</el-button>
          </div>
          
          <el-table :data="orders" stripe>
            <el-table-column prop="stock_code" label="股票代码" width="120" />
            <el-table-column prop="stock_name" label="股票名称" width="120" />
            <el-table-column prop="side" label="方向" width="80">
              <template #default="{ row }">
                <el-tag :type="row.side === 'BUY' ? 'success' : 'danger'" size="small">
                  {{ row.side === 'BUY' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="100" align="right">
              <template #default="{ row }">
                {{ row.price.toFixed(3) }}
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="100" align="right" />
            <el-table-column prop="filled_quantity" label="成交" width="80" align="right" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'SUBMITTED'"
                  type="danger"
                  size="small"
                  @click="handleCancelOrder(row.order_id)"
                >
                  撤单
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import { useMarketStore } from '@/stores/market'

const route = useRoute()
const marketStore = useMarketStore()

const orderForm = ref({
  stock_code: '',
  side: 'BUY',
  order_type: 'LIMIT',
  price: 0,
  quantity: 100
})

const stockName = ref('')
const currentPrice = ref(0)
const orders = ref<any[]>([])
const submitting = ref(false)

const estimatedAmount = computed(() => {
  const price = orderForm.value.order_type === 'MARKET' 
    ? currentPrice.value 
    : orderForm.value.price
  return (price * orderForm.value.quantity).toFixed(2)
})

const handleStockCodeChange = async () => {
  if (orderForm.value.stock_code) {
    try {
      const quote = await api.market.quote(orderForm.value.stock_code)
      stockName.value = quote.stock_name
      currentPrice.value = quote.current_price
      if (orderForm.value.price === 0) {
        orderForm.value.price = quote.current_price
      }
    } catch (error) {
      ElMessage.error('获取股票信息失败')
    }
  }
}

const submitOrder = async () => {
  if (!orderForm.value.stock_code) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认${orderForm.value.side === 'BUY' ? '买入' : '卖出'} ${stockName.value} ${orderForm.value.quantity}股，预估金额 ${estimatedAmount.value} HKD？`,
      '交易确认',
      { type: 'warning' }
    )
    
    submitting.value = true
    const result = await api.trade.createOrder(orderForm.value)
    ElMessage.success(`下单成功，订单号：${result.order_id}`)
    
    // 刷新订单列表
    await refreshOrders()
    
    // 重置表单
    orderForm.value.quantity = 100
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '下单失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleCancelOrder = async (orderId: string) => {
  try {
    await ElMessageBox.confirm('确认撤销该订单？', '撤单确认', { type: 'warning' })
    await api.trade.cancelOrder(orderId)
    ElMessage.success('撤单成功')
    await refreshOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '撤单失败')
    }
  }
}

const refreshOrders = async () => {
  try {
    orders.value = await api.trade.getOrders()
  } catch (error) {
    console.error('获取订单列表失败:', error)
  }
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    SUBMITTED: 'warning',
    FILLED: 'success',
    CANCELLED: 'info',
    REJECTED: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    SUBMITTED: '已提交',
    FILLED: '已成交',
    CANCELLED: '已撤单',
    REJECTED: '已拒绝'
  }
  return texts[status] || status
}

onMounted(async () => {
  // 检查URL参数
  const code = route.query.code as string
  if (code) {
    orderForm.value.stock_code = code
    await handleStockCodeChange()
  }
  
  // 加载订单列表
  await refreshOrders()
})
</script>

<style lang="scss" scoped>
.trade-page {
  .amount-preview {
    font-size: 18px;
    font-weight: 600;
    color: #409EFF;
  }
  
  .card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
