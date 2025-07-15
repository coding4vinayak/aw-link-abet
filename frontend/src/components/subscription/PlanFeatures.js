import React from 'react';
import { useSubscription } from '../../contexts/SubscriptionContext';

const PlanFeatures = ({ planType, detailed = false }) => {
  const { availablePlans } = useSubscription();

  const plan = availablePlans.find(p => p.plan_type === planType);

  if (!plan) {
    return <div className="text-gray-500">Plan not found</div>;
  }

  if (!detailed) {
    return (
      <div className="text-sm text-gray-600">
        <div className="font-medium mb-1">{plan.name} Plan</div>
        <div>
          {plan.limits.max_links} links • {plan.limits.analytics_retention_days} days analytics
          {plan.limits.ads_free ? ' • Ad-free' : ''}
          {plan.limits.custom_domains ? ' • Custom domains' : ''}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="border-b pb-2">
        <h3 className="text-lg font-semibold text-gray-900">{plan.name} Plan</h3>
        <div className="text-2xl font-bold text-gray-900">
          ${plan.price_monthly}
          <span className="text-base font-normal text-gray-500">/month</span>
        </div>
        {plan.price_yearly < plan.price_monthly * 12 && (
          <div className="text-sm text-green-600">
            Save ${(plan.price_monthly * 12 - plan.price_yearly).toFixed(2)} with yearly billing
          </div>
        )}
      </div>

      <div>
        <h4 className="font-medium text-gray-900 mb-2">Features:</h4>
        <ul className="space-y-1">
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

      <div>
        <h4 className="font-medium text-gray-900 mb-2">Limits:</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Max Links:</span>
            <span className="ml-2 font-medium">{plan.limits.max_links}</span>
          </div>
          <div>
            <span className="text-gray-600">Clicks/month:</span>
            <span className="ml-2 font-medium">{plan.limits.max_clicks_per_month.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-gray-600">Analytics:</span>
            <span className="ml-2 font-medium">{plan.limits.analytics_retention_days} days</span>
          </div>
          <div>
            <span className="text-gray-600">API Access:</span>
            <span className={`ml-2 font-medium ${plan.limits.api_access ? 'text-green-600' : 'text-red-600'}`}>
              {plan.limits.api_access ? 'Yes' : 'No'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {plan.limits.custom_domains && (
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
            Custom Domains
          </span>
        )}
        {plan.limits.ads_free && (
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
            Ad-Free
          </span>
        )}
        {plan.limits.api_access && (
          <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
            API Access
          </span>
        )}
      </div>
    </div>
  );
};

export default PlanFeatures;