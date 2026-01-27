import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navigation from './components/Navigation';
import ProtectedRoute from './components/ProtectedRoute';
import TaskExecutor from './components/TaskExecutor';
import TaskHistory from './components/TaskHistory';
import SystemHealth from './components/SystemHealth';
import Login from './pages/Login';
import Signup from './pages/Signup';
import './App.css';

function App() {
    return (
        <Router>
            <AuthProvider>
                <div className="app">
                    <Navigation />
                    <main className="main-content">
                        <Routes>
                            {/* Public routes */}
                            <Route path="/login" element={<Login />} />
                            <Route path="/signup" element={<Signup />} />

                            {/* Protected routes */}
                            <Route
                                path="/"
                                element={
                                    <ProtectedRoute>
                                        <TaskExecutor />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/history"
                                element={
                                    <ProtectedRoute>
                                        <TaskHistory />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/health"
                                element={
                                    <ProtectedRoute>
                                        <SystemHealth />
                                    </ProtectedRoute>
                                }
                            />
                        </Routes>
                    </main>
                    <footer className="app-footer">
                        <p>
                            Multi-Agent Orchestration System © {new Date().getFullYear()}
                        </p>
                        <p className="footer-tech">
                            Powered by FastAPI, Ollama & React
                        </p>
                    </footer>
                </div>
            </AuthProvider>
        </Router>
    );
}

export default App;
