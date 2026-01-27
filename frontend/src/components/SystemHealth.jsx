import { useState, useEffect } from 'react';
import { systemAPI } from '../services/api';
import './SystemHealth.css';

const SystemHealth = () => {
    const [health, setHealth] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);

        try {
            const [healthData, statsData] = await Promise.all([
                systemAPI.getHealth(),
                systemAPI.getStats(),
            ]);

            setHealth(healthData);
            setStats(statsData);
            setLastUpdated(new Date());
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();

        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);

        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status) => {
        if (status === 'ok' || status === 'healthy') return 'success';
        if (status === 'degraded' || status === 'warning') return 'warning';
        return 'error';
    };

    return (
        <div className="system-health">
            <div className="health-header fade-in">
                <h1>💚 System Health</h1>
                <p className="health-subtitle">
                    Monitor the status and performance of the Multi-Agent Orchestration System
                </p>
            </div>

            <div className="health-content">
                <div className="health-actions fade-in">
                    <button onClick={fetchData} className="btn btn-primary" disabled={loading}>
                        {loading ? (
                            <>
                                <span className="spinner"></span>
                                Refreshing...
                            </>
                        ) : (
                            <>
                                <span>🔄</span>
                                Refresh
                            </>
                        )}
                    </button>
                    {lastUpdated && (
                        <span className="last-updated">
                            Last updated: {lastUpdated.toLocaleTimeString()}
                        </span>
                    )}
                </div>

                {error && (
                    <div className="error-banner card fade-in">
                        <span className="error-icon">⚠️</span>
                        <div>
                            <strong>Failed to fetch system data</strong>
                            <p>{error}</p>
                        </div>
                    </div>
                )}

                {!loading && health && (
                    <div className="health-grid">
                        <div className="health-card card card-glass fade-in">
                            <div className="health-card-header">
                                <h3>System Status</h3>
                                <span className={`badge badge-${getStatusColor(health.status)}`}>
                                    {health.status?.toUpperCase() || 'UNKNOWN'}
                                </span>
                            </div>
                            <div className="health-card-content">
                                {health.status === 'ok' ? (
                                    <div className="status-message success">
                                        <span className="status-icon">✅</span>
                                        <p>All systems operational</p>
                                    </div>
                                ) : (
                                    <div className="status-message error">
                                        <span className="status-icon">❌</span>
                                        <p>System experiencing issues</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="health-card card card-glass fade-in" style={{ animationDelay: '0.1s' }}>
                            <div className="health-card-header">
                                <h3>API Endpoints</h3>
                                <span className="badge badge-info">Active</span>
                            </div>
                            <div className="health-card-content">
                                <div className="endpoint-list">
                                    <div className="endpoint-item">
                                        <span className="endpoint-method post">POST</span>
                                        <code>/tasks/execute</code>
                                        <span className="badge badge-success">OK</span>
                                    </div>
                                    <div className="endpoint-item">
                                        <span className="endpoint-method get">GET</span>
                                        <code>/system/health</code>
                                        <span className="badge badge-success">OK</span>
                                    </div>
                                    <div className="endpoint-item">
                                        <span className="endpoint-method get">GET</span>
                                        <code>/system/stats</code>
                                        <span className="badge badge-success">OK</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {stats && (
                            <div className="health-card card card-glass fade-in" style={{ animationDelay: '0.2s' }}>
                                <div className="health-card-header">
                                    <h3>Statistics</h3>
                                </div>
                                <div className="health-card-content">
                                    <pre>{JSON.stringify(stats, null, 2)}</pre>
                                </div>
                            </div>
                        )}

                        <div className="health-card card card-glass fade-in" style={{ animationDelay: '0.3s' }}>
                            <div className="health-card-header">
                                <h3>System Information</h3>
                            </div>
                            <div className="health-card-content">
                                <div className="info-grid">
                                    <div className="info-item">
                                        <span className="info-label">API Version</span>
                                        <span className="info-value">1.0.0</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Framework</span>
                                        <span className="info-value">FastAPI</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">LLM Provider</span>
                                        <span className="info-value">Ollama</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Environment</span>
                                        <span className="info-value">Development</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {loading && !health && (
                    <div className="loading-container card card-glass fade-in">
                        <div className="loading-spinner-large"></div>
                        <p>Loading system health data...</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SystemHealth;
