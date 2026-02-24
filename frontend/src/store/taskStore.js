import { create } from "zustand";
import api from "../services/api";

export const useTaskStore = create((set, get) => ({
  tasks: [],
  activeTask: null,
  streamEvents: [],
  isStreaming: false,
  isLoading: false,
  error: null,
  total: 0,

  fetchTasks: async (skip = 0, limit = 20) => {
    set({ isLoading: true });
    try {
      const { data } = await api.get(`/tasks/?skip=${skip}&limit=${limit}`);
      set({ tasks: data.tasks, total: data.total, isLoading: false });
    } catch (err) {
      set({ error: err.message, isLoading: false });
    }
  },

  fetchTask: async (id) => {
    try {
      const { data } = await api.get(`/tasks/${id}`);
      set({ activeTask: data });
      return data;
    } catch (err) {
      set({ error: err.message });
    }
  },

  executeStream: async (taskText, options = {}) => {
    const token = localStorage.getItem("token");
    set({ isStreaming: true, streamEvents: [], error: null });

    try {
      const response = await fetch("/tasks/execute/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          task: taskText,
          provider: options.provider || null,
          model: options.model || null,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const raw = line.slice(6).trim();
            if (raw === "[DONE]") {
              set({ isStreaming: false });
              get().fetchTasks();
              return;
            }
            try {
              const event = JSON.parse(raw);
              set((state) => ({
                streamEvents: [...state.streamEvents, { ...event, ts: Date.now() }],
              }));
            } catch {
              // skip malformed event
            }
          }
        }
      }
    } catch (err) {
      set({ error: err.message });
    } finally {
      set({ isStreaming: false });
    }
  },

  executeAsync: async (taskText, options = {}) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await api.post("/tasks/execute", {
        task: taskText,
        ...options,
      });
      set((state) => ({
        tasks: [data, ...state.tasks],
        isLoading: false,
      }));
      return data;
    } catch (err) {
      set({ error: err.response?.data?.detail || err.message, isLoading: false });
    }
  },

  deleteTask: async (id) => {
    try {
      await api.delete(`/tasks/${id}`);
      set((state) => ({
        tasks: state.tasks.filter((t) => t.id !== id),
      }));
    } catch (err) {
      set({ error: err.message });
    }
  },

  pollJobStatus: async (jobId, onUpdate) => {
    const poll = async () => {
      try {
        const { data } = await api.get(`/tasks/status/${jobId}`);
        onUpdate(data);
        if (!["SUCCESS", "FAILURE"].includes(data.status)) {
          setTimeout(poll, 2000);
        }
      } catch {
        setTimeout(poll, 3000);
      }
    };
    poll();
  },

  clearStreamEvents: () => set({ streamEvents: [] }),
  clearError: () => set({ error: null }),
}));
