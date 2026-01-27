import { useState, useEffect } from 'react';
import './TaskHistory.css';

const TaskHistory = () => {
    const [history, setHistory] = useState([]);
    const [selectedTask, setSelectedTask] = useState(null);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = () => {
        const stored = localStorage.getItem('taskHistory');
        if (stored) {
            try {
                setHistory(JSON.parse(stored));
            } catch (e) {
                console.error('Failed to load history:', e);
            }
        }
    };

    const clearHistory = () => {
        if (window.confirm('Are you sure you want to clear all task history?')) {
            localStorage.removeItem('taskHistory');
            setHistory([]);
            setSelectedTask(null);
        }
    };

    const deleteTask = (id) => {
        const updated = history.filter(task => task.id !== id);
        localStorage.setItem('taskHistory', JSON.stringify(updated));
        setHistory(updated);
        if (selectedTask?.id === id) {
            setSelectedTask(null);
        }
    };

    const formatDate = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleString();
    };

    return (
        <div className="task-history">
            <div className="history-header fade-in">
                <h1>📜 Task History</h1>
                <p className="history-subtitle">
                    Review your previously executed tasks and their results
                </p>
            </div>

            <div className="history-content">
                {history.length === 0 ? (
                    <div className="empty-state card card-glass fade-in">
                        <div className="empty-icon">📋</div>
                        <h3>No Task History</h3>
                        <p>Execute your first task to see it appear here</p>
                    </div>
                ) : (
                    <>
                        <div className="history-actions fade-in">
                            <div className="history-count">
                                <span className="badge badge-info">
                                    {history.length} {history.length === 1 ? 'Task' : 'Tasks'}
                                </span>
                            </div>
                            <button onClick={clearHistory} className="btn btn-secondary">
                                🗑️ Clear History
                            </button>
                        </div>

                        <div className="history-layout">
                            <div className="history-list fade-in">
                                {history.map((task, index) => (
                                    <div
                                        key={task.id}
                                        className={`history-item card ${selectedTask?.id === task.id ? 'selected' : ''
                                            }`}
                                        onClick={() => setSelectedTask(task)}
                                        style={{ animationDelay: `${index * 0.05}s` }}
                                    >
                                        <div className="item-header">
                                            <span className="badge badge-success">✓</span>
                                            <span className="item-date">{formatDate(task.timestamp)}</span>
                                        </div>
                                        <div className="item-task">{task.task}</div>
                                        <div className="item-actions">
                                            <button
                                                className="btn-icon"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    deleteTask(task.id);
                                                }}
                                                title="Delete"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {selectedTask && (
                                <div className="history-detail card card-glass fade-in">
                                    <div className="detail-header">
                                        <h3>Task Details</h3>
                                        <button
                                            className="btn-close"
                                            onClick={() => setSelectedTask(null)}
                                        >
                                            ✕
                                        </button>
                                    </div>

                                    <div className="detail-content">
                                        <div className="detail-section">
                                            <h4>📝 Task</h4>
                                            <p>{selectedTask.task}</p>
                                        </div>

                                        <div className="detail-section">
                                            <h4>🕒 Timestamp</h4>
                                            <p>{formatDate(selectedTask.timestamp)}</p>
                                        </div>

                                        {selectedTask.context && (
                                            <div className="detail-section">
                                                <h4>⚙️ Context</h4>
                                                <pre>{JSON.stringify(selectedTask.context, null, 2)}</pre>
                                            </div>
                                        )}

                                        {selectedTask.result && (
                                            <div className="detail-section">
                                                <h4>📊 Result</h4>
                                                <pre>{JSON.stringify(selectedTask.result, null, 2)}</pre>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default TaskHistory;
