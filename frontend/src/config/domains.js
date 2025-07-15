// Domain Configuration for LinkAbet
// Update these values when deploying to your custom domain

export const DOMAIN_CONFIG = {
  // Default domain for short links (change this to your domain)
  DEFAULT_DOMAIN: 'lab.et', // Change to 'yourdomain.com' when deploying
  
  // System domain for main application
  SYSTEM_DOMAIN: 'linkabet.com', // Change to your main domain
  
  // Available custom domains for customers
  CUSTOM_DOMAINS: [
    'go.yourbrand.com',
    'short.company.com', 
    'link.business.com'
  ],
  
  // For production deployment, update these:
  // DEFAULT_DOMAIN: 'yourdomain.com',
  // SYSTEM_DOMAIN: 'yourdomain.com',
};

// Helper function to get the full short URL
export const getShortUrl = (shortCode, customDomain = null) => {
  const domain = customDomain || DOMAIN_CONFIG.DEFAULT_DOMAIN;
  return `${domain}/${shortCode}`;
};

// Helper function to generate a short code
export const generateShortCode = () => {
  return Math.random().toString(36).substr(2, 6);
};

// Helper function to create a complete short URL
export const createShortUrl = (customDomain = null) => {
  const shortCode = generateShortCode();
  return getShortUrl(shortCode, customDomain);
};