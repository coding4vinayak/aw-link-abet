import React, { useState } from 'react';

const CustomerAnalytics = ({ users, links, onViewChange }) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('30days');
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  // Mock analytics data
  const analyticsData = {
    totalClicks: 490,
    totalLinks: 3,
    activeUsers: 2,
    thisMonth: 234,
    clicksByDay: [12, 23, 34, 45, 56, 67, 78],
    topCountries: [
      { name: 'United States', clicks: 234, percentage: 47.8 },
      { name: 'United Kingdom', clicks: 123, percentage: 25.1 },
      { name: 'Canada', clicks: 87, percentage: 17.8 },
      { name: 'Australia', clicks: 46, percentage: 9.4 }
    ],
    topLinks: links.slice(0, 5)
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Link Analytics</h1>
              <p className="text-gray-600">Track your link performance and user engagement</p>
            </div>
            <button
              onClick={() => onViewChange('customerDashboard')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Total Clicks</p>
                <p className="text-2xl font-bold text-gray-900">{analyticsData.totalClicks}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Total Links</p>
                <p className="text-2xl font-bold text-gray-900">{analyticsData.totalLinks}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Active Users</p>
                <p className="text-2xl font-bold text-gray-900">{analyticsData.activeUsers}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">This Month</p>
                <p className="text-2xl font-bold text-gray-900">{analyticsData.thisMonth}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Click Trends */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Click Trends</h2>
            <div className="h-64 flex items-end justify-between space-x-2">
              {analyticsData.clicksByDay.map((clicks, index) => (
                <div key={index} className="flex-1 bg-blue-100 rounded-t flex items-end justify-center" style={{ height: `${(clicks / Math.max(...analyticsData.clicksByDay)) * 100}%` }}>
                  <span className="text-xs text-blue-800 mb-2">{clicks}</span>
                </div>
              ))}
            </div>
            <div className="flex justify-between mt-2 text-sm text-gray-500">
              <span>7 days ago</span>
              <span>Today</span>
            </div>
          </div>

          {/* Top Countries */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Top Countries</h2>
            <div className="space-y-4">
              {analyticsData.topCountries.map((country, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-xs font-medium text-blue-600">{index + 1}</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{country.name}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${country.percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-500 w-12">{country.clicks}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Performing Links */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Top Performing Links</h2>
          <div className="space-y-4">
            {analyticsData.topLinks.map((link, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{link.title}</h3>
                  <p className="text-sm text-gray-500">{link.originalUrl}</p>
                  <code className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                    {link.shortUrl}
                  </code>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-900">{link.clicks}</p>
                  <p className="text-sm text-gray-500">clicks</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerAnalytics;