import React, { useEffect, useState } from 'react';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useTheme } from '../../contexts/ThemeContext';

const AdBanner = ({ type = 'header', className = '' }) => {
  const { isProUser } = useSubscription();
  const { isDark } = useTheme();
  const [adVisible, setAdVisible] = useState(false);
  const [adContent, setAdContent] = useState(null);

  useEffect(() => {
    // Don't show ads for Pro users
    if (isProUser()) {
      setAdVisible(false);
      return;
    }

    // Simulate ad loading
    const loadAd = () => {
      setAdVisible(true);
      
      // Mock ad content based on type
      const mockAds = {
        header: {
          title: 'Boost Your Marketing',
          description: 'Professional email marketing tools for small businesses',
          cta: 'Start Free Trial',
          image: 'https://via.placeholder.com/728x90/4F46E5/ffffff?text=Marketing+Tools',
          link: '#',
          bgColor: 'from-blue-500 to-purple-500'
        },
        sidebar: {
          title: 'Web Analytics',
          description: 'Track your website performance with advanced analytics',
          cta: 'Learn More',
          image: 'https://via.placeholder.com/300x250/7C3AED/ffffff?text=Analytics+Pro',
          link: '#',
          bgColor: 'from-purple-500 to-pink-500'
        },
        success: {
          title: 'Congratulations!',
          description: 'Share your new short link across all platforms',
          cta: 'Get Started',
          image: 'https://via.placeholder.com/728x90/059669/ffffff?text=Social+Media+Tools',
          link: '#',
          bgColor: 'from-green-500 to-blue-500'
        },
        footer: {
          title: 'Domain & Hosting',
          description: 'Get your website online with reliable hosting solutions',
          cta: 'View Plans',
          image: 'https://via.placeholder.com/728x90/DC2626/ffffff?text=Web+Hosting',
          link: '#',
          bgColor: 'from-red-500 to-orange-500'
        }
      };

      setAdContent(mockAds[type] || mockAds.header);
    };

    // Delay ad loading to simulate real ad network behavior
    const timer = setTimeout(loadAd, 1000);
    return () => clearTimeout(timer);
  }, [type, isProUser]);

  if (!adVisible || isProUser()) {
    return null;
  }

  const sizeClasses = {
    header: 'h-24 max-w-4xl mx-auto',
    sidebar: 'h-64 max-w-sm',
    success: 'h-24 max-w-4xl mx-auto',
    footer: 'h-20 max-w-6xl mx-auto'
  };

  return (
    <div className={`ad-banner ${sizeClasses[type]} ${className}`}>
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 relative overflow-hidden shadow-sm">
        <div className="text-xs text-gray-400 dark:text-gray-500 mb-2 flex justify-between items-center">
          <span>Advertisement</span>
          <button
            onClick={() => setAdVisible(false)}
            className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 text-sm"
          >
            ×
          </button>
        </div>

        {adContent && (
          <div className="flex items-center space-x-4">
            {/* Ad Image */}
            <div className="flex-shrink-0">
              <div className={`w-16 h-16 rounded-lg bg-gradient-to-r ${adContent.bgColor} flex items-center justify-center`}>
                <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </div>
            </div>

            {/* Ad Content */}
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {adContent.title}
              </h3>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                {adContent.description}
              </p>
            </div>

            {/* Ad CTA */}
            <div className="flex-shrink-0">
              <a
                href={adContent.link}
                className="inline-flex items-center px-3 py-2 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                onClick={(e) => {
                  e.preventDefault();
                  // Track ad click
                  console.log('Ad clicked:', type, adContent.title);
                }}
              >
                {adContent.cta}
              </a>
            </div>
          </div>
        )}

        {/* Loading state */}
        {!adContent && (
          <div className="animate-pulse">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              </div>
              <div className="w-20 h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdBanner;