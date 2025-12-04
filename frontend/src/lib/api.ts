import axios, { InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/store/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' },
});

// Request Interceptor: Inject Token
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = useAuthStore.getState().accessToken;
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 & Refresh
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (value: unknown) => void;
    reject: (reason?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                return new Promise(function (resolve, reject) {
                    failedQueue.push({ resolve, reject });
                })
                    .then((token) => {
                        originalRequest.headers['Authorization'] = 'Bearer ' + token;
                        return api(originalRequest);
                    })
                    .catch((err) => {
                        return Promise.reject(err);
                    });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            const refreshToken = useAuthStore.getState().refreshToken;

            if (!refreshToken) {
                useAuthStore.getState().logout();
                return Promise.reject(error);
            }

            try {
                const response = await axios.post(`${API_URL}/auth/refresh/`, {
                    refresh: refreshToken,
                });

                const { access } = response.data;
                useAuthStore.getState().setAccessToken(access);

                api.defaults.headers.common['Authorization'] = 'Bearer ' + access;
                originalRequest.headers['Authorization'] = 'Bearer ' + access;

                processQueue(null, access);
                return api(originalRequest);
            } catch (err) {
                processQueue(err, null);
                useAuthStore.getState().logout();
                return Promise.reject(err);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);

// Helper functions
export const apiGet = <T>(url: string, params?: any) =>
    api.get<T>(url, { params }).then((res) => res.data);

export const apiPost = <T>(url: string, data?: any) =>
    api.post<T>(url, data).then((res) => res.data);

export const apiPut = <T>(url: string, data?: any) =>
    api.put<T>(url, data).then((res) => res.data);

export const apiDelete = <T>(url: string) =>
    api.delete<T>(url).then((res) => res.data);