import React, { useState } from 'react';
import { useSubscription } from '../../contexts/SubscriptionContext';
import AdBanner from '../ads/AdBanner';
import UpgradeModal from '../subscription/UpgradeModal';

const HomePage = ({ onViewChange, onCreateLink }) => {
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [shortenedLink, setShortenedLink] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const { checkPlanLimits, incrementUsage, isProUser } = useSubscription();

  const handleShortenUrl = async (e) => {
    e.preventDefault();
    if (!url) return;

    // Check plan limits for anonymous users (assume they have basic plan)
    const limitCheck = await checkPlanLimits('anonymous', 'create_link');
    if (!limitCheck.allowed) {
      alert(limitCheck.message);
      setShowUpgradeModal(true);
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/links`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          original_url: url,
          title: title || 'Untitled Link',
          user_email: 'anonymous@linkly.com'
        }),
      });

      if (response.ok) {
        const newLink = await response.json();
        setShortenedLink(newLink);
        setUrl('');
        setTitle('');
        
        // Increment usage for anonymous users
        incrementUsage('anonymous', 'link_created');
      } else {
        throw new Error('Failed to create link');
      }
    } catch (error) {
      console.error('Error creating link:', error);
      alert('Error creating short link. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const handleUpgrade = () => {
    setShowUpgradeModal(false);
    onViewChange('signup');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header Ad Banner */}
      <AdBanner type="header" className="pt-4" />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 via-purple-600 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">
                Shorten URLs with
                <span className="text-yellow-300"> LinkAbet</span>
              </h1>
              <p className="mt-6 text-xl text-blue-100 leading-relaxed">
                Create branded short links with custom domains, detailed analytics, 
                and professional link management tools.
              </p>
              <div className="mt-8 bg-white dark:bg-gray-800 rounded-xl p-6 shadow-2xl">
                <form onSubmit={handleShortenUrl} className="space-y-4">
                  <div>
                    <input
                      type="url"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="Enter your long URL here..."
                      className="w-full px-4 py-3 text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                  </div>
                  <div>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="Optional: Enter a title for your link"
                      className="w-full px-4 py-3 text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg disabled:opacity-50"
                  >
                    {loading ? 'Shortening...' : 'Shorten URL'}
                  </button>
                </form>
              </div>
            </div>
            <div className="text-center lg:text-right">
              <img
                src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2015&q=80"
                alt="Link shortening illustration"
                className="w-full max-w-md mx-auto lg:max-w-lg rounded-lg shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Success Message & Result */}
      {shortenedLink && (
        <section className="py-8 bg-green-50 dark:bg-green-900/20">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                🎉 Your short link is ready!
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                  <span className="text-gray-900 dark:text-white font-medium">
                    {shortenedLink.short_url}
                  </span>
                  <button
                    onClick={() => copyToClipboard(shortenedLink.short_url)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      copySuccess 
                        ? 'bg-green-600 text-white' 
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {copySuccess ? 'Copied!' : 'Copy Link'}
                  </button>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <strong>Original URL:</strong> {shortenedLink.original_url}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <strong>Title:</strong> {shortenedLink.title}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <strong>Category:</strong> {shortenedLink.category}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <strong>Clicks:</strong> {shortenedLink.clicks}
                </div>
              </div>
            </div>
          </div>
          
          {/* Success Ad Banner */}
          <AdBanner type="success" className="mt-6" />
        </section>
      )}

      {/* Features Section */}
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
              Why Choose LinkAbet?
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
              Powerful features to manage your links professionally
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Link Management
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Organize and manage all your links in one place with folders and tags
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Detailed Analytics
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Track clicks, locations, devices, and more with comprehensive analytics
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Custom Domains
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Use your own domain to create branded short links
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-16 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
              Simple, Transparent Pricing
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
              Choose the plan that fits your needs
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Basic Plan */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Basic</h3>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                  Free
                </p>
                <ul className="text-left space-y-2 mb-6">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300">5 links per month</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300">Basic analytics</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300">Standard support</span>
                  </li>
                </ul>
                <button
                  onClick={() => onViewChange('signup')}
                  className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
                >
                  Get Started
                </button>
              </div>
            </div>
            
            {/* Pro Plan */}
            <div className="bg-white dark:bg-gray-800 border border-blue-500 rounded-lg p-6 relative">
              <div className="absolute top-0 right-0 bg-blue-500 text-white px-3 py-1 rounded-bl-lg rounded-tr-lg text-sm font-semibold">
                Popular
              </div>
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Pro</h3>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                  $9.99<span className="text-base font-normal text-gray-600 dark:text-gray-400">/month</span>
                </p>
                <ul className="text-left space-y-2 mb-6">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300">Unlimited links</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300">Advanced analytics</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300">No advertisements</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300">Priority support</span>
                  </li>
                </ul>
                <button
                  onClick={() => setShowUpgradeModal(true)}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Start Pro Trial
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to start shortening your links?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of users who trust LinkAbet for their link management needs
          </p>
          <button
            onClick={() => onViewChange('signup')}
            className="bg-white text-blue-600 py-3 px-8 rounded-lg font-semibold hover:bg-gray-100 transition-colors text-lg"
          >
            Get Started Free
          </button>
        </div>
      </section>

      {/* Upgrade Modal */}
      {showUpgradeModal && (
        <UpgradeModal 
          onClose={() => setShowUpgradeModal(false)}
          onUpgrade={handleUpgrade}
        />
      )}
    </div>
  );
};

export default HomePage;