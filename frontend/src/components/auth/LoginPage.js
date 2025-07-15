import React, { useState } from 'react';
import { DOMAIN_CONFIG } from '../../config/domains';
import { useTheme } from '../../contexts/ThemeContext';
import AdBanner from '../ads/AdBanner';
import AdSidebar from '../ads/AdSidebar';

const LoginPage = ({ onLogin, onViewChange }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { isDark } = useTheme();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      onLogin(email, password);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Header Ad Banner */}
      <div className="absolute top-20 left-1/2 transform -translate-x-1/2 w-full max-w-4xl px-4">
        <AdBanner type="header" />
      </div>

      <div className="flex w-full max-w-6xl mx-auto">
        {/* Sidebar Ad */}
        <div className="hidden lg:block w-80 mr-8">
          <AdSidebar type="login" className="sticky top-24" />
        </div>

        {/* Login Form */}
        <div className="flex-1 max-w-md mx-auto space-y-8">
          <div>
            <div className="flex justify-center">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
              Sign in to LinkAbet
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
              Demo accounts: 
              <span className="font-medium text-blue-600 dark:text-blue-400"> admin@{DOMAIN_CONFIG.SYSTEM_DOMAIN}</span> (Admin) or 
              <span className="font-medium text-blue-600 dark:text-blue-400"> john@example.com</span> (Customer)
            </p>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Enter your email"
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={() => onViewChange('signup')}
                className="text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300 text-sm"
              >
                Don't have an account? Sign up
              </button>
            </div>
          </form>

          {/* Demo Account Helpers */}
          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h3 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-2">Quick Login:</h3>
            <div className="space-y-2">
              <button
                onClick={() => {
                  setEmail('admin@' + DOMAIN_CONFIG.SYSTEM_DOMAIN);
                  setPassword('password123');
                }}
                className="block w-full text-left text-xs text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 py-1"
              >
                → Admin Account (admin@{DOMAIN_CONFIG.SYSTEM_DOMAIN} / password123)
              </button>
              <button
                onClick={() => {
                  setEmail('john@example.com');
                  setPassword('password123');
                }}
                className="block w-full text-left text-xs text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 py-1"
              >
                → Customer Account (john@example.com / password123)
              </button>
            </div>
          </div>
        </div>

        {/* Right Sidebar Ad Space */}
        <div className="hidden xl:block w-80 ml-8">
          <AdSidebar type="login-secondary" className="sticky top-24" />
        </div>
      </div>
    </div>
  );
};

export default LoginPage;