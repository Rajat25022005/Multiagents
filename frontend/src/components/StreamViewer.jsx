import { useEffect, useRef } from "react";
import { Brain, Zap, CheckCircle, AlertCircle, Search, FileCode, Loader2 } from "lucide-react";
import clsx from "clsx";

const STAGE_ICONS = {
  memory: <Search size={14} className="text-purple-400" />,
  planning: <Brain size={14} className="text-blue-400" />,
  plan: <Brain size={14} className="text-blue-400" />,
  executing: <Zap size={14} className="text-yellow-400" />,
  result: <CheckCircle size={14} className="text-green-400" />,
  finalizing: <FileCode size={14} className="text-indigo-400" />,
  done: <CheckCircle size={14} className="text-green-400" />,
  error: <AlertCircle size={14} className="text-red-400" />,
};

const STAGE_COLORS = {
  memory: "border-purple-500/30 bg-purple-950/20",
  planning: "border-blue-500/30 bg-blue-950/20",
  plan: "border-blue-500/30 bg-blue-950/20",
  executing: "border-yellow-500/30 bg-yellow-950/20",
  result: "border-green-500/30 bg-green-950/20",
  finalizing: "border-indigo-500/30 bg-indigo-950/20",
  done: "border-green-500/30 bg-green-950/20",
  error: "border-red-500/30 bg-red-950/20",
};

function EventCard({ event }) {
  const icon = STAGE_ICONS[event.stage] || <Zap size={14} className="text-gray-400" />;
  const color = STAGE_COLORS[event.stage] || "border-gray-700 bg-gray-900";

  return (
    <div className={clsx("border rounded-lg p-3 text-sm", color)}>
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="font-medium text-gray-300 capitalize">{event.stage}</span>
        {event.task_id && (
          <span className="text-xs text-gray-500 font-mono">[{event.task_id}]</span>
        )}
      </div>

      {event.message && <p className="text-gray-400 text-xs">{event.message}</p>}

      {event.stage === "plan" && event.subtasks && (
        <div className="mt-2 space-y-1">
          {event.subtasks.map((s, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-gray-400">
              <span className="text-indigo-400 font-mono flex-shrink-0">{s.id}</span>
              <span>{s.description}</span>
              <span className="ml-auto text-gray-600 flex-shrink-0">[{s.agent}]</span>
            </div>
          ))}
        </div>
      )}

      {event.stage === "executing" && (
        <div className="mt-1 text-xs text-gray-400">
          <span className="text-yellow-400 font-medium">{event.agent}</span>
          {" → "}
          {event.description}
        </div>
      )}

      {event.stage === "result" && event.output && (
        <p className="mt-1 text-xs text-gray-500 line-clamp-3 font-mono">{event.output}</p>
      )}
    </div>
  );
}

export default function StreamViewer({ events, isStreaming }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  if (events.length === 0 && !isStreaming) return null;

  return (
    <div className="card mt-4">
      <div className="flex items-center gap-2 mb-3">
        {isStreaming ? (
          <Loader2 size={16} className="text-indigo-400 animate-spin" />
        ) : (
          <CheckCircle size={16} className="text-green-400" />
        )}
        <span className="text-sm font-medium text-gray-300">
          {isStreaming ? "Agent working..." : "Execution complete"}
        </span>
        <span className="text-xs text-gray-600 ml-auto">{events.length} events</span>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
        {events.map((event, i) => (
          <EventCard key={i} event={event} />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
