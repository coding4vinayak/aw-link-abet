import React from 'react';
import { useSubscription } from '../../contexts/SubscriptionContext';

const UpgradeModal = ({ onClose, onUpgrade, currentPlan = 'basic' }) => {
  const { availablePlans, isProUser } = useSubscription();

  if (isProUser()) {
    return null; // Don't show upgrade modal for Pro users
  }

  const proPlan = availablePlans.find(plan => plan.plan_type === 'pro');
  const basicPlan = availablePlans.find(plan => plan.plan_type === 'basic');

  if (!proPlan || !basicPlan) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-md w-full mx-4">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Upgrade to Pro</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          <div className="mb-6">
            <div className="bg-gradient-to-r from-purple-500 to-blue-500 text-white p-4 rounded-lg mb-4">
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-2">Pro Plan</h3>
                <div className="text-3xl font-bold">
                  ${proPlan.price_monthly}
                  <span className="text-lg font-normal">/month</span>
                </div>
                <div className="text-sm opacity-90 mt-1">
                  or ${proPlan.price_yearly}/year (save 17%)
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">What you get with Pro:</h4>
                <ul className="space-y-2">
                  {proPlan.features.map((feature, index) => (
                    <li key={index} className="flex items-center text-sm text-gray-600">
                      <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Comparison:</h4>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="font-medium text-gray-700">Feature</div>
                  <div className="font-medium text-gray-700">Basic</div>
                  <div className="font-medium text-gray-700">Pro</div>
                  
                  <div className="text-gray-600">Links</div>
                  <div className="text-gray-600">{basicPlan.limits.max_links}</div>
                  <div className="text-green-600 font-semibold">{proPlan.limits.max_links}</div>
                  
                  <div className="text-gray-600">Analytics</div>
                  <div className="text-gray-600">{basicPlan.limits.analytics_retention_days} days</div>
                  <div className="text-green-600 font-semibold">{proPlan.limits.analytics_retention_days} days</div>
                  
                  <div className="text-gray-600">Ads</div>
                  <div className="text-red-600">Yes</div>
                  <div className="text-green-600 font-semibold">None</div>
                  
                  <div className="text-gray-600">Custom Domains</div>
                  <div className="text-red-600">No</div>
                  <div className="text-green-600 font-semibold">Yes</div>
                  
                  <div className="text-gray-600">API Access</div>
                  <div className="text-red-600">No</div>
                  <div className="text-green-600 font-semibold">Yes</div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-600 hover:text-gray-800 font-medium border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Maybe Later
            </button>
            <button
              onClick={onUpgrade}
              className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white font-medium rounded-lg hover:from-purple-600 hover:to-blue-600 transition-all"
            >
              Upgrade Now
            </button>
          </div>

          <div className="mt-4 text-xs text-gray-500 text-center">
            Cancel anytime. No hidden fees.
          </div>
        </div>
      </div>
    </div>
  );
};

export default UpgradeModal;