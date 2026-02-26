import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Send, Zap, History, Trash2, Eye, ChevronDown, ChevronUp } from "lucide-react";
import { useTaskStore } from "../store/taskStore";
import { useAuthStore } from "../store/authStore";
import StreamViewer from "../components/StreamViewer";
import ResultViewer from "../components/ResultViewer";
import StatusBadge from "../components/ui/StatusBadge";
import { formatDistanceToNow } from "date-fns";

const EXAMPLE_TASKS = [
  "Research the latest developments in quantum computing and write a summary report",
  "Write a Python script to scrape and analyze top HackerNews posts",
  "Create a detailed plan for building a SaaS product for project management",
  "Analyze the pros and cons of microservices vs monolith architecture",
];

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const {
    tasks, total, streamEvents, isStreaming, isLoading, error,
    fetchTasks, executeStream, deleteTask, clearStreamEvents, clearError,
  } = useTaskStore();

  const [taskInput, setTaskInput] = useState("");
  const [useStream, setUseStream] = useState(true);
  const [lastResult, setLastResult] = useState(null);
  const [showHistory, setShowHistory] = useState(true);

  useEffect(() => {
    fetchTasks();
  }, []);

  // Extract final result from stream events
  useEffect(() => {
    const doneEvent = [...streamEvents].reverse().find((e) => e.stage === "done");
    if (doneEvent?.result) {
      setLastResult(doneEvent.result);
    }
  }, [streamEvents]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!taskInput.trim() || isStreaming || isLoading) return;

    clearStreamEvents();
    setLastResult(null);

    if (useStream) {
      await executeStream(taskInput.trim());
    } else {
      const task = await useTaskStore.getState().executeAsync(taskInput.trim());
      if (task) navigate(`/tasks/${task.id}`);
    }
    setTaskInput("");
  };

  const handleExampleClick = (example) => {
    setTaskInput(example);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-white">Agent Dashboard</h1>
          <p className="text-sm text-gray-500">
            Welcome back, <span className="text-indigo-400">{user?.username}</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
            <div
              onClick={() => setUseStream((v) => !v)}
              className={`relative w-10 h-5 rounded-full transition-colors ${useStream ? "bg-indigo-600" : "bg-gray-700"}`}
            >
              <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${useStream ? "left-5.5 translate-x-0.5" : "left-0.5"}`} />
            </div>
            <Zap size={14} className={useStream ? "text-indigo-400" : "text-gray-500"} />
            Live stream
          </label>
        </div>
      </div>

      <div className="flex-1 overflow-auto px-6 py-5 space-y-5">
        {/* Task input */}
        <form onSubmit={handleSubmit}>
          <div className="card">
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Describe your task
            </label>
            <textarea
              value={taskInput}
              onChange={(e) => setTaskInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit(e);
              }}
              rows={4}
              placeholder="e.g. Research quantum computing and write a technical summary..."
              className="input resize-none font-mono text-sm"
              disabled={isStreaming}
            />
            <div className="flex items-center justify-between mt-3">
              <div className="flex flex-wrap gap-1.5">
                {EXAMPLE_TASKS.slice(0, 2).map((ex, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleExampleClick(ex)}
                    className="text-xs text-gray-500 hover:text-indigo-400 border border-gray-700 hover:border-indigo-600 px-2 py-1 rounded-md transition-colors"
                  >
                    Example {i + 1}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-600">⌘+Enter to submit</span>
                <button
                  type="submit"
                  disabled={!taskInput.trim() || isStreaming || isLoading}
                  className="btn-primary flex items-center gap-2"
                >
                  {isStreaming || isLoading ? (
                    <span className="flex items-center gap-2">
                      <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      {isStreaming ? "Running..." : "Queuing..."}
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <Send size={14} />
                      Run Task
                    </span>
                  )}
                </button>
              </div>
            </div>
          </div>
        </form>

        {/* Error */}
        {error && (
          <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg p-3 text-sm flex items-center justify-between">
            {error}
            <button onClick={clearError} className="text-red-500 hover:text-red-300 ml-3 text-xs">✕</button>
          </div>
        )}

        {/* Live stream */}
        <StreamViewer events={streamEvents} isStreaming={isStreaming} />

        {/* Final result */}
        {lastResult && !isStreaming && (
          <div className="card">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              Result
            </h3>
            <ResultViewer content={lastResult} />
          </div>
        )}

        {/* Task history */}
        {tasks.length > 0 && (
          <div className="card">
            <button
              onClick={() => setShowHistory((v) => !v)}
              className="w-full flex items-center justify-between text-sm font-medium text-gray-300 hover:text-white"
            >
              <span className="flex items-center gap-2">
                <History size={16} />
                Task History
                <span className="text-xs text-gray-600">({total} total)</span>
              </span>
              {showHistory ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>

            {showHistory && (
              <div className="mt-3 space-y-2">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center gap-3 p-3 rounded-lg bg-gray-950 border border-gray-800 hover:border-gray-700 transition-colors group"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-300 truncate">{task.description}</p>
                      <p className="text-xs text-gray-600 mt-0.5">
                        {formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}
                      </p>
                    </div>
                    <StatusBadge status={task.status} />
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => navigate(`/tasks/${task.id}`)}
                        className="btn-ghost p-1.5"
                        title="View"
                      >
                        <Eye size={14} />
                      </button>
                      <button
                        onClick={() => deleteTask(task.id)}
                        className="text-gray-600 hover:text-red-400 hover:bg-red-950 p-1.5 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
