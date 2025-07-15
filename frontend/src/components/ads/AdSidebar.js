import React, { useEffect, useState } from 'react';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useTheme } from '../../contexts/ThemeContext';

const AdSidebar = ({ type = 'dashboard', className = '' }) => {
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
      
      // Mock ad content for sidebar
      const mockAds = [
        {
          title: 'Cloud Storage Pro',
          description: 'Secure cloud storage for your business files. 50GB free, unlimited Pro plans available.',
          cta: 'Get Started',
          image: 'https://via.placeholder.com/300x250/0EA5E9/ffffff?text=Cloud+Storage',
          link: '#',
          bgColor: 'from-cyan-500 to-blue-500'
        },
        {
          title: 'SEO Master Tools',
          description: 'Improve your website ranking with professional SEO tools and analytics.',
          cta: 'Try Free',
          image: 'https://via.placeholder.com/300x250/059669/ffffff?text=SEO+Tools',
          link: '#',
          bgColor: 'from-green-500 to-emerald-500'
        },
        {
          title: 'Social Media Manager',
          description: 'Manage all your social media accounts from one powerful dashboard.',
          cta: 'Learn More',
          image: 'https://via.placeholder.com/300x250/7C3AED/ffffff?text=Social+Media',
          link: '#',
          bgColor: 'from-purple-500 to-violet-500'
        },
        {
          title: 'Email Marketing',
          description: 'Create beautiful email campaigns and grow your subscriber list.',
          cta: 'Start Free',
          image: 'https://via.placeholder.com/300x250/DC2626/ffffff?text=Email+Marketing',
          link: '#',
          bgColor: 'from-red-500 to-pink-500'
        },
        {
          title: 'Web Analytics',
          description: 'Track visitor behavior and optimize your website performance.',
          cta: 'View Demo',
          image: 'https://via.placeholder.com/300x250/F59E0B/ffffff?text=Analytics',
          link: '#',
          bgColor: 'from-yellow-500 to-orange-500'
        }
      ];

      // Random ad selection
      const randomAd = mockAds[Math.floor(Math.random() * mockAds.length)];
      setAdContent(randomAd);
    };

    // Delay ad loading to simulate real ad network behavior
    const timer = setTimeout(loadAd, 1500);
    return () => clearTimeout(timer);
  }, [type, isProUser]);

  if (!adVisible || isProUser()) {
    return null;
  }

  return (
    <div className={`ad-sidebar ${className}`}>
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm">
        <div className="text-xs text-gray-400 dark:text-gray-500 mb-3 flex justify-between items-center">
          <span>Sponsored</span>
          <button
            onClick={() => setAdVisible(false)}
            className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 text-sm"
          >
            ×
          </button>
        </div>

        {adContent && (
          <div className="space-y-4">
            {/* Ad Image */}
            <div className="w-full">
              <div className={`w-full h-32 rounded-lg bg-gradient-to-r ${adContent.bgColor} flex items-center justify-center`}>
                <div className="text-center text-white">
                  <svg className="w-12 h-12 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  <p className="text-xs font-medium">{adContent.title}</p>
                </div>
              </div>
            </div>

            {/* Ad Content */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                {adContent.title}
              </h3>
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
                {adContent.description}
              </p>
              
              <a
                href={adContent.link}
                className="inline-flex items-center justify-center w-full px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                onClick={(e) => {
                  e.preventDefault();
                  // Track ad click
                  console.log('Sidebar ad clicked:', adContent.title);
                }}
              >
                {adContent.cta}
              </a>
            </div>
          </div>
        )}

        {/* Loading state */}
        {!adContent && (
          <div className="animate-pulse space-y-4">
            <div className="w-full h-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
            </div>
            <div className="w-full h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        )}

        {/* Ad Network Info */}
        <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Ads help keep LinkAbet free
          </p>
          <p className="text-xs text-blue-600 dark:text-blue-400 text-center mt-1">
            <button onClick={() => console.log('Upgrade to Pro clicked')}>
              Upgrade to Pro to remove ads
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdSidebar;