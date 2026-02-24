import { create } from "zustand";
import api from "../services/api";

export const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem("token"),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await api.post("/auth/login", { email, password });
      localStorage.setItem("token", data.access_token);
      api.defaults.headers.common["Authorization"] = `Bearer ${data.access_token}`;
      set({ token: data.access_token, user: data.user, isLoading: false });
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || "Login failed", isLoading: false });
      return false;
    }
  },

  register: async (email, username, password) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await api.post("/auth/register", { email, username, password });
      localStorage.setItem("token", data.access_token);
      api.defaults.headers.common["Authorization"] = `Bearer ${data.access_token}`;
      set({ token: data.access_token, user: data.user, isLoading: false });
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || "Registration failed", isLoading: false });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem("token");
    delete api.defaults.headers.common["Authorization"];
    set({ token: null, user: null });
  },

  fetchMe: async () => {
    const token = get().token;
    if (!token) return;
    try {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      const { data } = await api.get("/auth/me");
      set({ user: data });
    } catch {
      get().logout();
    }
  },

  clearError: () => set({ error: null }),
}));
