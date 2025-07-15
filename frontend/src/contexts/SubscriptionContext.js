import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Subscription Context
const SubscriptionContext = createContext();

// Action types
const SET_SUBSCRIPTION = 'SET_SUBSCRIPTION';
const SET_PLANS = 'SET_PLANS';
const SET_LOADING = 'SET_LOADING';
const SET_ERROR = 'SET_ERROR';
const UPDATE_USAGE = 'UPDATE_USAGE';

// Initial state
const initialState = {
  currentSubscription: null,
  availablePlans: [],
  loading: false,
  error: null,
  usage: {
    linksCreated: 0,
    maxLinks: 5,
    clicksThisMonth: 0,
    maxClicksPerMonth: 1000
  }
};

// Reducer
const subscriptionReducer = (state, action) => {
  switch (action.type) {
    case SET_SUBSCRIPTION:
      return {
        ...state,
        currentSubscription: action.payload,
        loading: false,
        error: null
      };
    case SET_PLANS:
      return {
        ...state,
        availablePlans: action.payload,
        loading: false,
        error: null
      };
    case SET_LOADING:
      return {
        ...state,
        loading: action.payload
      };
    case SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false
      };
    case UPDATE_USAGE:
      return {
        ...state,
        usage: {
          ...state.usage,
          ...action.payload
        }
      };
    default:
      return state;
  }
};

// Subscription Provider
export const SubscriptionProvider = ({ children }) => {
  const [state, dispatch] = useReducer(subscriptionReducer, initialState);

  // Get backend URL from environment
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Load subscription data
  const loadSubscription = async (userId) => {
    if (!userId) return;
    
    dispatch({ type: SET_LOADING, payload: true });
    try {
      const response = await fetch(`${backendUrl}/api/subscription/current/${userId}`);
      if (response.ok) {
        const subscription = await response.json();
        dispatch({ type: SET_SUBSCRIPTION, payload: subscription });
      } else {
        throw new Error('Failed to load subscription');
      }
    } catch (error) {
      dispatch({ type: SET_ERROR, payload: error.message });
    }
  };

  // Load available plans
  const loadPlans = async () => {
    dispatch({ type: SET_LOADING, payload: true });
    try {
      const response = await fetch(`${backendUrl}/api/subscription/plans`);
      if (response.ok) {
        const plans = await response.json();
        dispatch({ type: SET_PLANS, payload: plans });
      } else {
        throw new Error('Failed to load plans');
      }
    } catch (error) {
      dispatch({ type: SET_ERROR, payload: error.message });
    }
  };

  // Upgrade subscription
  const upgradeSubscription = async (userId, planType, paymentMethod = 'card', billingCycle = 'monthly') => {
    dispatch({ type: SET_LOADING, payload: true });
    try {
      const formData = new FormData();
      formData.append('user_id', userId);
      formData.append('plan_type', planType);
      formData.append('payment_method', paymentMethod);
      formData.append('billing_cycle', billingCycle);

      const response = await fetch(`${backendUrl}/api/subscription/upgrade`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const subscription = await response.json();
        dispatch({ type: SET_SUBSCRIPTION, payload: subscription });
        return { success: true, subscription };
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upgrade subscription');
      }
    } catch (error) {
      dispatch({ type: SET_ERROR, payload: error.message });
      return { success: false, error: error.message };
    }
  };

  // Check plan limits
  const checkPlanLimits = async (userId, action) => {
    try {
      const formData = new FormData();
      formData.append('user_id', userId);
      formData.append('action', action);

      const response = await fetch(`${backendUrl}/api/subscription/validate-limits`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        return result;
      } else {
        throw new Error('Failed to check plan limits');
      }
    } catch (error) {
      console.error('Error checking plan limits:', error);
      return { allowed: false, message: 'Error checking limits' };
    }
  };

  // Increment usage
  const incrementUsage = async (userId, action) => {
    try {
      const formData = new FormData();
      formData.append('user_id', userId);
      formData.append('action', action);

      const response = await fetch(`${backendUrl}/api/subscription/increment-usage`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        // Update local usage state
        if (action === 'link_created') {
          dispatch({ 
            type: UPDATE_USAGE, 
            payload: { 
              linksCreated: state.usage.linksCreated + 1 
            } 
          });
        }
        return { success: true };
      } else {
        throw new Error('Failed to increment usage');
      }
    } catch (error) {
      console.error('Error incrementing usage:', error);
      return { success: false, error: error.message };
    }
  };

  // Get plan features
  const getPlanFeatures = (planType) => {
    const plan = state.availablePlans.find(p => p.plan_type === planType);
    return plan ? plan.features : [];
  };

  // Get plan limits
  const getPlanLimits = (planType) => {
    const plan = state.availablePlans.find(p => p.plan_type === planType);
    return plan ? plan.limits : null;
  };

  // Check if user has specific feature
  const hasFeature = (feature) => {
    if (!state.currentSubscription) return false;
    
    const planLimits = getPlanLimits(state.currentSubscription.plan_type);
    if (!planLimits) return false;

    switch (feature) {
      case 'custom_domains':
        return planLimits.custom_domains;
      case 'api_access':
        return planLimits.api_access;
      case 'ads_free':
        return planLimits.ads_free;
      default:
        return false;
    }
  };

  // Check if user is on pro plan
  const isProUser = () => {
    return state.currentSubscription?.plan_type === 'pro';
  };

  // Check if user is on basic plan
  const isBasicUser = () => {
    return state.currentSubscription?.plan_type === 'basic' || !state.currentSubscription;
  };

  // Initialize plans on mount
  useEffect(() => {
    loadPlans();
  }, []);

  const value = {
    ...state,
    loadSubscription,
    loadPlans,
    upgradeSubscription,
    checkPlanLimits,
    incrementUsage,
    getPlanFeatures,
    getPlanLimits,
    hasFeature,
    isProUser,
    isBasicUser
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
};

// Custom hook to use subscription context
export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
};

export default SubscriptionContext;