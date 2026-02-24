import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 封装请求方法
export const request = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return service.get(url, config)
  },
  
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.post(url, data, config)
  },
  
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.put(url, data, config)
  },
  
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return service.delete(url, config)
  }
}

// API接口定义
export const api = {
  // 账户相关
  account: {
    info: () => request.get('/account/info'),
    positions: () => request.get('/account/positions'),
    status: () => request.get('/account/status')
  },
  
  // 行情相关
  market: {
    quote: (stockCode: string) => request.get(`/market/quote/${stockCode}`),
    kline: (stockCode: string, params?: any) => request.get(`/market/kline/${stockCode}`, { params }),
    search: (keyword: string) => request.get('/market/search', { params: { keyword } })
  },
  
  // 交易相关
  trade: {
    createOrder: (data: any) => request.post('/trade/order', data),
    cancelOrder: (orderId: string) => request.delete(`/trade/order/${orderId}`),
    getOrders: (status?: string) => request.get('/trade/orders', { params: { status } }),
    getOrder: (orderId: string) => request.get(`/trade/order/${orderId}`)
  }
}

export default service
