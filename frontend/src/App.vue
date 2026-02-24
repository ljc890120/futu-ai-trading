<template>
  <el-config-provider :locale="zhCn">
    <el-container class="app-container">
      <!-- 侧边栏 -->
      <el-aside width="220px" class="app-aside">
        <div class="logo">
          <el-icon><TrendCharts /></el-icon>
          <span>富途交易系统</span>
        </div>
        <el-menu
          :default-active="currentRoute"
          router
          background-color="#1d1e1f"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/account">
            <el-icon><Wallet /></el-icon>
            <span>账户管理</span>
          </el-menu-item>
          <el-menu-item index="/market">
            <el-icon><TrendCharts /></el-icon>
            <span>行情中心</span>
          </el-menu-item>
          <el-menu-item index="/trade">
            <el-icon><ShoppingCart /></el-icon>
            <span>交易下单</span>
          </el-menu-item>
          <el-menu-item index="/strategy">
            <el-icon><Setting /></el-icon>
            <span>策略配置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部栏 -->
        <el-header class="app-header">
          <div class="header-left">
            <span class="page-title">{{ pageTitle }}</span>
          </div>
          <div class="header-right">
            <el-tag :type="opendConnected ? 'success' : 'danger'" size="small">
              OpenD: {{ opendConnected ? '已连接' : '未连接' }}
            </el-tag>
          </div>
        </el-header>

        <!-- 内容区 -->
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { useAccountStore } from '@/stores/account'

const route = useRoute()
const accountStore = useAccountStore()

const currentRoute = computed(() => route.path)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/': '系统概览',
    '/account': '账户管理',
    '/market': '行情中心',
    '/trade': '交易下单',
    '/strategy': '策略配置'
  }
  return titles[route.path] || '富途交易系统'
})

const opendConnected = computed(() => accountStore.opendConnected)

onMounted(async () => {
  await accountStore.fetchAccountStatus()
})
</script>

<style lang="scss" scoped>
.app-container {
  height: 100vh;
}

.app-aside {
  background-color: #1d1e1f;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    border-bottom: 1px solid #2d2e2f;
    
    .el-icon {
      font-size: 24px;
      margin-right: 8px;
      color: #409EFF;
    }
  }
  
  .el-menu {
    border-right: none;
  }
}

.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .header-left {
    .page-title {
      font-size: 18px;
      font-weight: 500;
      color: #303133;
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}

.app-main {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
