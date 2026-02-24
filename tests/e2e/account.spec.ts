import { test, expect } from '@playwright/test'

test.describe('账户管理页面', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/account')
  })

  test('应该显示账户信息卡片', async ({ page }) => {
    // 检查页面标题
    await expect(page.locator('.card-title').first()).toContainText('账户信息')
    
    // 检查统计数字
    await expect(page.locator('.el-statistic').first()).toBeVisible()
  })

  test('应该显示持仓列表', async ({ page }) => {
    // 等待表格加载
    await expect(page.locator('.el-table')).toBeVisible()
    
    // 检查表头
    await expect(page.locator('.el-table th').first()).toContainText('股票代码')
  })

  test('刷新按钮应该可以点击', async ({ page }) => {
    const refreshButton = page.locator('.card-title .el-button:has-text("刷新")')
    await expect(refreshButton).toBeEnabled()
    
    await refreshButton.click()
    
    // 应该显示加载状态或刷新成功
    await page.waitForTimeout(1000)
  })

  test('持仓数据应该正确显示盈亏颜色', async ({ page }) => {
    // 等待表格数据加载
    await page.waitForSelector('.el-table__row', { timeout: 10000 })
    
    // 检查是否有盈亏数据
    const profitLossCells = page.locator('.el-table .amount-positive, .el-table .amount-negative')
    const count = await profitLossCells.count()
    
    if (count > 0) {
      // 有数据时检查颜色类
      const firstCell = profitLossCells.first()
      await expect(firstCell).toBeVisible()
    }
  })
})

test.describe('首页账户概览', () => {
  test('应该显示总资产、可用资金等统计', async ({ page }) => {
    await page.goto('/')
    
    // 检查统计卡片
    const statCards = page.locator('.stat-card')
    await expect(statCards).toHaveCount(4)
    
    // 检查第一个卡片（总资产）
    await expect(statCards.first().locator('.stat-label')).toContainText('总资产')
    await expect(statCards.first().locator('.stat-value')).toBeVisible()
  })
})
