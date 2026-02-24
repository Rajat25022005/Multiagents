import clsx from "clsx";

const STATUS_CONFIG = {
  pending:    { label: "Pending",    className: "bg-gray-800 text-gray-400" },
  queued:     { label: "Queued",     className: "bg-blue-950 text-blue-400" },
  planning:   { label: "Planning",   className: "bg-purple-950 text-purple-400" },
  executing:  { label: "Running",    className: "bg-yellow-950 text-yellow-400 animate-pulse" },
  finalizing: { label: "Finalizing", className: "bg-indigo-950 text-indigo-400 animate-pulse" },
  done:       { label: "Done",       className: "bg-green-950 text-green-400" },
  failed:     { label: "Failed",     className: "bg-red-950 text-red-400" },
};

export default function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;
  return (
    <span className={clsx("badge font-mono text-xs px-2 py-0.5 rounded-full", config.className)}>
      {config.label}
    </span>
  );
}
