import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import ThemeToggle from './ThemeToggle';

const Header = ({ currentView, onViewChange, user, isAuthenticated, userType, onLogout }) => {
  const { isDark } = useTheme();
  
  const getNavigation = () => {
    if (!isAuthenticated) {
      return [
        { name: 'Home', view: 'home' },
        { name: 'Login', view: 'login' },
        { name: 'Sign Up', view: 'signup' },
      ];
    }
    
    if (userType === 'admin') {
      return [
        { name: 'Dashboard', view: 'adminDashboard' },
        { name: 'Users', view: 'userManagement' },
        { name: 'Analytics', view: 'linkAnalytics' },
        { name: 'Data Import', view: 'dataImport' },
      ];
    }
    
    return [
      { name: 'Dashboard', view: 'customerDashboard' },
      { name: 'Analytics', view: 'customerAnalytics' },
      { name: 'Reports', view: 'customerReports' },
    ];
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 fixed w-full top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <button
              onClick={() => onViewChange('home')}
              className="text-2xl font-bold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
            >
              LinkAbet
            </button>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            {getNavigation().map((item) => (
              <button
                key={item.name}
                onClick={() => onViewChange(item.view)}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === item.view
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                {item.name}
              </button>
            ))}
          </nav>

          {/* User Actions */}
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Welcome, {user?.name || 'User'}
                </span>
                <span className={`px-2 py-1 rounded text-xs ${
                  userType === 'admin' 
                    ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200' 
                    : 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                }`}>
                  {userType === 'admin' ? 'Admin' : 'Customer'}
                </span>
                <button
                  onClick={onLogout}
                  className="text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 px-3 py-1 rounded transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              <button
                onClick={() => onViewChange('login')}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Get Started
              </button>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;