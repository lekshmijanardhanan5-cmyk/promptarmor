import React, { useState } from 'react';
import API from '../services/api';

export default function Auth({ onLoginSuccess }) {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            if (isLogin) {
                const response = await API.post('auth/login/', { username, password });
                localStorage.setItem('access_token', response.data.access);
                localStorage.setItem('refresh_token', response.data.refresh);
                onLoginSuccess();
            } else {
                await API.post('auth/register/', { username, password });
                alert('Registration successful! Please login.');
                setIsLogin(true);
            }
        } catch (err) {
            setError('Authentication failed. Please check your credentials.');
        }
    };

    return (
        <div className="flex justify-center items-center h-screen bg-slate-900 text-white">
            <form onSubmit={handleSubmit} className="bg-slate-800 p-8 rounded-xl shadow-lg w-96">
                <h2 className="text-2xl font-bold mb-6 text-center">{isLogin ? 'PromptArmor Login' : 'Register'}</h2>
                {error && <p className="text-red-400 text-sm mb-4">{error}</p>}
                <div className="mb-4">
                    <label className="block text-sm mb-2">Username</label>
                    <input 
                        type="text" 
                        value={username} 
                        onChange={(e) => setUsername(e.target.value)} 
                        className="w-full p-2 rounded bg-slate-700 border border-slate-600 focus:outline-none"
                        required 
                    />
                </div>
                <div className="mb-6">
                    <label className="block text-sm mb-2">Password</label>
                    <input 
                        type="password" 
                        value={password} 
                        onChange={(e) => setPassword(e.target.value)} 
                        className="w-full p-2 rounded bg-slate-700 border border-slate-600 focus:outline-none"
                        required 
                    />
                </div>
                <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 p-2 rounded font-semibold transition">
                    {isLogin ? 'Login' : 'Register'}
                </button>
                <p className="mt-4 text-center text-sm text-slate-400 cursor-pointer" onClick={() => setIsLogin(!isLogin)}>
                    {isLogin ? "Don't have an account? Register" : "Already have an account? Login"}
                </p>
            </form>
        </div>
    );
}