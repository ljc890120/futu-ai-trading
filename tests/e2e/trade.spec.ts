import { test, expect } from '@playwright/test'

test.describe('交易下单页面', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/trade')
  })

  test('应该显示下单表单', async ({ page }) => {
    // 检查页面标题
    await expect(page.locator('.card-title').first()).toContainText('下单交易')
    
    // 检查表单元素
    await expect(page.locator('text=股票代码')).toBeVisible()
    await expect(page.locator('text=买卖方向')).toBeVisible()
    await expect(page.locator('text=订单类型')).toBeVisible()
  })

  test('买卖方向选择器应该正常工作', async ({ page }) => {
    // 检查默认选中买入
    const buyButton = page.locator('.el-radio-button:has-text("买入")')
    await expect(buyButton).toHaveClass(/is-active/)
    
    // 点击卖出
    const sellButton = page.locator('.el-radio-button:has-text("卖出")')
    await sellButton.click()
    await expect(sellButton).toHaveClass(/is-active/)
  })

  test('输入股票代码应该能获取股票信息', async ({ page }) => {
    const codeInput = page.locator('input[placeholder="如：HK.00700"]')
    await codeInput.fill('HK.00700')
    await codeInput.blur()
    
    // 等待API响应
    await page.waitForTimeout(1000)
    
    // 应该显示股票名称
    const nameInput = page.locator('.el-input:has-text("股票名称") input').first()
    await expect(nameInput).not.toBeEmpty()
  })

  test('应该显示订单列表', async ({ page }) => {
    // 检查订单列表标题
    await expect(page.locator('.card-title:has-text("今日订单")')).toBeVisible()
    
    // 检查表格存在
    await expect(page.locator('.el-table')).toBeVisible()
  })

  test('确认下单按钮应该存在', async ({ page }) => {
    const submitButton = page.locator('.el-button:has-text("确认下单")')
    await expect(submitButton).toBeVisible()
    await expect(submitButton).toBeEnabled()
  })
})

test.describe('行情页面跳转到交易', () => {
  test('从行情页面点击交易按钮应跳转到交易页面并预填代码', async ({ page }) => {
    await page.goto('/market')
    
    // 等待页面加载
    await page.waitForTimeout(2000)
    
    // 如果有交易按钮，点击
    const tradeButton = page.locator('.card-title .el-button:has-text("交易")')
    if (await tradeButton.isVisible()) {
      await tradeButton.click()
      
      // 应该跳转到交易页面
      await expect(page).toHaveURL(/\/trade/)
      
      // 股票代码应该预填
      const codeInput = page.locator('input[placeholder="如：HK.00700"]')
      await expect(codeInput).not.toBeEmpty()
    }
  })
})
