import { useState } from 'react';
import { taskAPI } from '../services/api';
import './TaskExecutor.css';

const TaskExecutor = () => {
    const [task, setTask] = useState('');
    const [context, setContext] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!task.trim()) {
            setError('Please enter a task description');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            // Parse context if provided
            let parsedContext = null;
            if (context.trim()) {
                try {
                    parsedContext = JSON.parse(context);
                } catch (e) {
                    setError('Invalid JSON in context field');
                    setLoading(false);
                    return;
                }
            }

            const response = await taskAPI.executeTask(task, parsedContext);
            setResult(response);

            // Save to history
            const history = JSON.parse(localStorage.getItem('taskHistory') || '[]');
            history.unshift({
                id: Date.now(),
                task,
                context: parsedContext,
                result: response,
                timestamp: new Date().toISOString(),
            });
            // Keep only last 50 tasks
            localStorage.setItem('taskHistory', JSON.stringify(history.slice(0, 50)));

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const clearForm = () => {
        setTask('');
        setContext('');
        setResult(null);
        setError(null);
    };

    return (
        <div className="task-executor">
            <div className="executor-header fade-in">
                <h1>🚀 Execute Task</h1>
                <p className="executor-subtitle">
                    Describe your task and let the multi-agent system bring it to life
                </p>
            </div>

            <div className="executor-content">
                <form onSubmit={handleSubmit} className="task-form card card-glass fade-in">
                    <div className="form-group">
                        <label htmlFor="task">
                            Task Description <span className="required">*</span>
                        </label>
                        <textarea
                            id="task"
                            value={task}
                            onChange={(e) => setTask(e.target.value)}
                            placeholder="E.g., Create a MERN stack application for a car dealership"
                            disabled={loading}
                            rows={4}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="context">
                            Context (Optional JSON)
                        </label>
                        <textarea
                            id="context"
                            value={context}
                            onChange={(e) => setContext(e.target.value)}
                            placeholder='{"key": "value"}'
                            disabled={loading}
                            rows={3}
                        />
                        <small className="helper-text">
                            Provide additional context as JSON if needed
                        </small>
                    </div>

                    <div className="form-actions">
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={loading || !task.trim()}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner"></span>
                                    Executing...
                                </>
                            ) : (
                                <>
                                    <span>⚡</span>
                                    Execute Task
                                </>
                            )}
                        </button>

                        {!loading && (task || context || result) && (
                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={clearForm}
                            >
                                Clear
                            </button>
                        )}
                    </div>
                </form>

                {error && (
                    <div className="result-container card fade-in error-card">
                        <div className="result-header">
                            <h3>❌ Error</h3>
                        </div>
                        <div className="error-message">{error}</div>
                    </div>
                )}

                {result && (
                    <div className="result-container card fade-in">
                        <div className="result-header">
                            <h3>✅ Task Completed</h3>
                            <span className="badge badge-success">Success</span>
                        </div>

                        <div className="result-content">
                            {result.data && (
                                <>
                                    {result.data.final_report && (
                                        <div className="result-section">
                                            <h4>📋 Final Report</h4>
                                            <pre>{result.data.final_report}</pre>
                                        </div>
                                    )}

                                    {result.data.results && (
                                        <div className="result-section">
                                            <h4>🔍 Execution Results</h4>
                                            <pre>{JSON.stringify(result.data.results, null, 2)}</pre>
                                        </div>
                                    )}

                                    {result.data.workspace && (
                                        <div className="result-section">
                                            <h4>📁 Workspace</h4>
                                            <code className="workspace-path">{result.data.workspace}</code>
                                        </div>
                                    )}

                                    {!result.data.final_report && !result.data.results && (
                                        <div className="result-section">
                                            <h4>📊 Response</h4>
                                            <pre>{JSON.stringify(result, null, 2)}</pre>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                )}

                {loading && (
                    <div className="loading-indicator card card-glass fade-in">
                        <div className="loading-content">
                            <div className="loading-spinner-large"></div>
                            <h3>Processing Your Task...</h3>
                            <p className="text-secondary">
                                The multi-agent system is analyzing your request and generating the solution.
                                This may take a minute or two depending on task complexity.
                            </p>
                            <div className="loading-stages">
                                <div className="stage">
                                    <span className="stage-icon">🧠</span>
                                    <span>Planning</span>
                                </div>
                                <div className="stage">
                                    <span className="stage-icon">⚙️</span>
                                    <span>Executing</span>
                                </div>
                                <div className="stage">
                                    <span className="stage-icon">✨</span>
                                    <span>Finalizing</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TaskExecutor;
