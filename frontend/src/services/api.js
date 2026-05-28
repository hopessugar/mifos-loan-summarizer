import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 300000,
})

client.interceptors.response.use(
  res => res.data,
  err => Promise.reject({
    message: err.response?.data?.detail ?? err.message ?? 'Unexpected error',
    status: err.response?.status ?? 0,
  })
)

export const analyseContract = (payload) => client.post('/analyze', payload)
export const getLoanProducts = () => client.get('/loanproducts')
export const getHealth = () => client.get('/health')
export const getProviders = () => client.get('/providers')