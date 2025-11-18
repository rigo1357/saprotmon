// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // URL gốc của FastAPI server
  timeout: 15000, // 15s để tránh treo request nếu backend không phản hồi
});

// "Bộ lọc" (Interceptor) này sẽ tự động thêm token vào header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('Yêu cầu quá thời gian chờ:', error.message);
    }
    // Xử lý lỗi 401 - Unauthorized
    if (error.response?.status === 401) {
      // Chỉ logout nếu không phải đang ở trang login
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('access_token');
      }
    }
    // Xử lý lỗi response không hợp lệ
    if (error.response && typeof error.response.data === 'string') {
      try {
        error.response.data = JSON.parse(error.response.data);
      } catch (e) {
        // Nếu không parse được, giữ nguyên
      }
    }
    return Promise.reject(error);
  }
);

export default api;