import axios from 'axios';

// Create axios instance
const apiClient = axios.create({
    baseURL: '/',
    timeout: 120000, // 2 minutes for long-running tasks
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor
apiClient.interceptors.response.use(
    (response) => {
        return response.data;
    },
    (error) => {
        // Handle 401 Unauthorized - redirect to login
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

// API Methods
export const api = {
    // Authentication
    signup: async (username, email, password) => {
        return apiClient.post('/auth/signup', { username, email, password });
    },

    login: async (username, password) => {
        return apiClient.post('/auth/login', { username, password });
    },

    logout: async () => {
        return apiClient.post('/auth/logout');
    },

    getCurrentUser: async () => {
        return apiClient.get('/auth/me');
    },

    // Tasks
    executeTask: async (task, context = null) => {
        return apiClient.post('/tasks/execute', { task, context });
    },

    // System
    getHealth: async () => {
        return apiClient.get('/system/health');
    },

    getStats: async () => {
        return apiClient.get('/system/stats');
    },
};

// Legacy exports for backward compatibility
export const taskAPI = {
    executeTask: api.executeTask,
};

export const systemAPI = {
    getHealth: api.getHealth,
    getStats: api.getStats,
};

export default apiClient;

