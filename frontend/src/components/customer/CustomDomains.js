import React, { useState } from 'react';

const CustomDomains = ({ user, onViewChange }) => {
  const [showAddDomain, setShowAddDomain] = useState(false);
  const [newDomain, setNewDomain] = useState('');

  const mockDomains = [
    { id: 1, domain: 'go.yourbrand.com', status: 'active', verified: true, links: 45, clicks: 1234 },
    { id: 2, domain: 'short.company.com', status: 'pending', verified: false, links: 0, clicks: 0 },
  ];

  const handleAddDomain = (e) => {
    e.preventDefault();
    if (newDomain) {
      console.log('Adding domain:', newDomain);
      setNewDomain('');
      setShowAddDomain(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Custom Domains</h1>
              <p className="text-gray-600">Manage your custom domains for branded short links</p>
            </div>
            <button
              onClick={() => onViewChange('customerDashboard')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>

        {/* Add Domain Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Add Custom Domain</h2>
            <button
              onClick={() => setShowAddDomain(!showAddDomain)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              {showAddDomain ? 'Cancel' : 'Add Domain'}
            </button>
          </div>
          
          {showAddDomain && (
            <form onSubmit={handleAddDomain} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Domain Name
                </label>
                <input
                  type="text"
                  value={newDomain}
                  onChange={(e) => setNewDomain(e.target.value)}
                  placeholder="example.com"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Enter your domain without protocol (e.g., go.yourbrand.com)
                </p>
              </div>
              <button
                type="submit"
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
              >
                Add Domain
              </button>
            </form>
          )}
        </div>

        {/* Domains List */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Your Domains</h2>
          <div className="space-y-4">
            {mockDomains.map((domain) => (
              <div key={domain.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="font-semibold text-gray-900">{domain.domain}</h3>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        domain.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {domain.status}
                      </span>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        domain.verified ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {domain.verified ? 'Verified' : 'Unverified'}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 mt-2">
                      <span className="text-sm text-gray-500">
                        {domain.links} links
                      </span>
                      <span className="text-sm text-gray-500">
                        {domain.clicks} clicks
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button className="text-blue-600 hover:text-blue-800 text-sm">
                      Configure
                    </button>
                    <button className="text-red-600 hover:text-red-800 text-sm">
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomDomains;