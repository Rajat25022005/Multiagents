import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navigation.css';

const Navigation = () => {
    const location = useLocation();
    const { user, isAuthenticated, logout } = useAuth();

    const isActive = (path) => {
        return location.pathname === path;
    };

    const handleLogout = () => {
        logout();
    };

    return (
        <nav className="navigation">
            <div className="nav-container">
                <Link to="/" className="nav-brand">
                    <div className="brand-icon">⚡</div>
                    <span className="brand-text">Multi-Agent Orchestrator</span>
                </Link>

                <div className="nav-links">
                    {isAuthenticated ? (
                        <>
                            <Link
                                to="/"
                                className={`nav-link ${isActive('/') ? 'active' : ''}`}
                            >
                                <span className="nav-icon">🚀</span>
                                Execute Task
                            </Link>
                            <Link
                                to="/history"
                                className={`nav-link ${isActive('/history') ? 'active' : ''}`}
                            >
                                <span className="nav-icon">📜</span>
                                History
                            </Link>
                            <Link
                                to="/health"
                                className={`nav-link ${isActive('/health') ? 'active' : ''}`}
                            >
                                <span className="nav-icon">💚</span>
                                System Health
                            </Link>
                            <div className="nav-user">
                                <span className="user-name">👤 {user?.username}</span>
                                <button onClick={handleLogout} className="btn-logout">
                                    Logout
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <Link
                                to="/login"
                                className={`nav-link ${isActive('/login') ? 'active' : ''}`}
                            >
                                Login
                            </Link>
                            <Link
                                to="/signup"
                                className={`nav-link nav-link-signup ${isActive('/signup') ? 'active' : ''}`}
                            >
                                Sign Up
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navigation;
