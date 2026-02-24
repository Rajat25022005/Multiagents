import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, RefreshCw, FileText } from "lucide-react";
import { useTaskStore } from "../store/taskStore";
import ResultViewer from "../components/ResultViewer";
import StatusBadge from "../components/ui/StatusBadge";
import { format } from "date-fns";

export default function TaskDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { fetchTask, pollJobStatus } = useTaskStore();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    const t = await fetchTask(id);
    if (t) setTask(t);
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await refresh();
      setLoading(false);
    };
    load();
  }, [id]);

  useEffect(() => {
    if (task?.job_id && !["done", "failed"].includes(task.status)) {
      pollJobStatus(task.job_id, async (status) => {
        if (["SUCCESS", "FAILURE"].includes(status.status)) {
          await refresh();
        }
      });
    }
  }, [task?.job_id]);

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (!task) return (
    <div className="p-6 text-gray-500">Task not found.</div>
  );

  return (
    <div className="max-w-4xl mx-auto px-6 py-6 space-y-5">
      {/* Header */}
      <div className="flex items-start gap-4">
        <button onClick={() => navigate("/")} className="btn-ghost p-2 mt-0.5">
          <ArrowLeft size={18} />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-1">
            <StatusBadge status={task.status} />
            <span className="text-xs text-gray-600 font-mono">#{task.id}</span>
            <button
              onClick={refresh}
              className="text-gray-600 hover:text-gray-400 ml-auto"
              title="Refresh"
            >
              <RefreshCw size={14} />
            </button>
          </div>
          <h1 className="text-lg font-semibold text-white">{task.description}</h1>
          <p className="text-xs text-gray-500 mt-1">
            Created {format(new Date(task.created_at), "MMM d, yyyy 'at' HH:mm")}
            {task.completed_at && (
              <> · Completed {format(new Date(task.completed_at), "MMM d, yyyy 'at' HH:mm")}</>
            )}
          </p>
        </div>
      </div>

      {/* Error */}
      {task.error && (
        <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg p-4 text-sm">
          <strong className="block mb-1">Error</strong>
          {task.error}
        </div>
      )}

      {/* Result */}
      {task.result?.result && (
        <div className="card">
          <h2 className="text-sm font-semibold text-white mb-4">Result</h2>
          <ResultViewer content={task.result.result} />
        </div>
      )}

      {/* Files */}
      {task.files && task.files.length > 0 && (
        <div className="card">
          <h2 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <FileText size={16} />
            Files Created
          </h2>
          <div className="space-y-2">
            {task.files.map((f, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-indigo-400 font-mono bg-gray-950 px-3 py-2 rounded-lg border border-gray-800">
                <FileText size={14} className="flex-shrink-0" />
                {f}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Raw subtask results */}
      {task.result?.subtask_results && Object.keys(task.result.subtask_results).length > 0 && (
        <details className="card">
          <summary className="text-sm font-medium text-gray-400 cursor-pointer hover:text-white">
            Subtask Results ({Object.keys(task.result.subtask_results).length})
          </summary>
          <div className="mt-3 space-y-3">
            {Object.entries(task.result.subtask_results).map(([key, val]) => (
              <div key={key} className="bg-gray-950 rounded-lg border border-gray-800 p-3">
                <div className="text-xs font-mono text-indigo-400 mb-2">{key}</div>
                <p className="text-xs text-gray-400 whitespace-pre-wrap font-mono">{val}</p>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
