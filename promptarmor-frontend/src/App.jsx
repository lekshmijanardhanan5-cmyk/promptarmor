import React, { useState, useEffect } from 'react';
import { ArrowLeft } from 'lucide-react';
import Auth from './components/Auth';
import Dashboard from './components/Dashboard';
import Landing from './components/Landing';

export default function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'));
    const [showAuth, setShowAuth] = useState(false);

    useEffect(() => {
        document.title = 'PromptArmor | AI Prompt Security';
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setIsAuthenticated(false);
        setShowAuth(false);
    };

    if (isAuthenticated) {
        return <Dashboard onLogout={handleLogout} />;
    }

    if (showAuth) {
        return (
            <div className="relative">
                <button
                    type="button"
                    onClick={() => setShowAuth(false)}
                    className="fixed top-4 left-4 z-50 flex items-center gap-2 text-sm text-slate-300 hover:text-white bg-slate-900/80 hover:bg-slate-800 border border-slate-700 px-3 py-2 rounded-lg backdrop-blur transition-colors"
                >
                    <ArrowLeft size={16} />
                    Back to home
                </button>

                <Auth onLoginSuccess={() => setIsAuthenticated(true)} />
            </div>
        );
    }

    return <Landing onGetStarted={() => setShowAuth(true)} />;
}