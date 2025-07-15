import React, { useState, useEffect } from 'react';
import { useSubscription } from '../../contexts/SubscriptionContext';

const PlanSelector = ({ onClose, userId }) => {
  const { 
    availablePlans, 
    currentSubscription, 
    upgradeSubscription, 
    loading, 
    error 
  } = useSubscription();

  const [selectedPlan, setSelectedPlan] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [upgrading, setUpgrading] = useState(false);

  useEffect(() => {
    if (currentSubscription) {
      setSelectedPlan(currentSubscription.plan_type);
    }
  }, [currentSubscription]);

  const handleUpgrade = async () => {
    if (!selectedPlan || selectedPlan === currentSubscription?.plan_type) {
      onClose();
      return;
    }

    setUpgrading(true);
    const result = await upgradeSubscription(userId, selectedPlan, 'card', billingCycle);
    setUpgrading(false);

    if (result.success) {
      onClose();
      // Show success message
      alert(`Successfully upgraded to ${selectedPlan} plan!`);
    } else {
      alert(`Failed to upgrade: ${result.error}`);
    }
  };

  const getPlanPrice = (plan) => {
    return billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  };

  const getPlanSavings = (plan) => {
    if (billingCycle === 'yearly' && plan.price_monthly > 0) {
      const monthlyTotal = plan.price_monthly * 12;
      const savings = monthlyTotal - plan.price_yearly;
      return savings;
    }
    return 0;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Choose Your Plan</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          {/* Billing Cycle Toggle */}
          <div className="flex justify-center mb-8">
            <div className="bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  billingCycle === 'monthly'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  billingCycle === 'yearly'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Yearly
                <span className="ml-1 text-xs text-green-600 font-bold">SAVE 17%</span>
              </button>
            </div>
          </div>

          {/* Plans Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {availablePlans.map((plan) => {
              const isCurrentPlan = currentSubscription?.plan_type === plan.plan_type;
              const isSelected = selectedPlan === plan.plan_type;
              const price = getPlanPrice(plan);
              const savings = getPlanSavings(plan);

              return (
                <div
                  key={plan.plan_type}
                  className={`relative p-6 border-2 rounded-lg cursor-pointer transition-all ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } ${isCurrentPlan ? 'ring-2 ring-green-500' : ''}`}
                  onClick={() => setSelectedPlan(plan.plan_type)}
                >
                  {isCurrentPlan && (
                    <div className="absolute top-0 right-0 bg-green-500 text-white text-xs px-2 py-1 rounded-bl-lg rounded-tr-lg">
                      Current Plan
                    </div>
                  )}

                  {plan.plan_type === 'pro' && (
                    <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-purple-500 to-blue-500 text-white text-xs px-3 py-1 rounded-full">
                      Most Popular
                    </div>
                  )}

                  <div className="text-center">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                    
                    <div className="mb-4">
                      <span className="text-4xl font-bold text-gray-900">
                        ${price}
                      </span>
                      <span className="text-gray-500 ml-2">
                        /{billingCycle === 'monthly' ? 'month' : 'year'}
                      </span>
                      
                      {savings > 0 && (
                        <div className="text-sm text-green-600 mt-1">
                          Save ${savings.toFixed(2)} per year
                        </div>
                      )}
                    </div>

                    <div className="text-left">
                      <h4 className="font-semibold text-gray-900 mb-3">Features:</h4>
                      <ul className="space-y-2">
                        {plan.features.map((feature, index) => (
                          <li key={index} className="flex items-center text-sm text-gray-600">
                            <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="mt-6 text-left">
                      <h4 className="font-semibold text-gray-900 mb-2">Limits:</h4>
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>Links: {plan.limits.max_links}</div>
                        <div>Clicks/month: {plan.limits.max_clicks_per_month.toLocaleString()}</div>
                        <div>Analytics: {plan.limits.analytics_retention_days} days</div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-4 mt-8">
            <button
              onClick={onClose}
              className="px-6 py-2 text-gray-600 hover:text-gray-800 font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleUpgrade}
              disabled={upgrading || !selectedPlan || selectedPlan === currentSubscription?.plan_type}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                upgrading || !selectedPlan || selectedPlan === currentSubscription?.plan_type
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {upgrading ? 'Processing...' : 
               selectedPlan === currentSubscription?.plan_type ? 'Current Plan' : 
               selectedPlan === 'pro' ? 'Upgrade to Pro' : 'Continue with Basic'}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlanSelector;