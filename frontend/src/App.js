import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { 
  Header, 
  HomePage, 
  CustomerDashboard, 
  AdminDashboard, 
  LinkAnalytics, 
  UserManagement,
  LoginPage,
  SignupPage,
  CustomDomains,
  DomainSettings,
  CustomerAnalytics,
  CustomerReports,
  DataImportManager
} from "./components";
import { DOMAIN_CONFIG, createShortUrl } from "./config/domains";
import { ThemeProvider } from "./contexts/ThemeContext";
import { SubscriptionProvider } from "./contexts/SubscriptionContext";

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userType, setUserType] = useState('customer'); // 'customer' or 'admin'
  const [links, setLinks] = useState([]);
  const [users, setUsers] = useState([]);
  const [analytics, setAnalytics] = useState({});

  // Mock user data
  const mockUsers = [
    { id: 1, name: 'John Doe', email: 'john@example.com', type: 'customer', plan: 'Pro', status: 'active', joinDate: '2024-01-15' },
    { id: 2, name: 'Sarah Wilson', email: 'sarah@example.com', type: 'customer', plan: 'Basic', status: 'active', joinDate: '2024-02-20' },
    { id: 3, name: 'Admin User', email: `admin@${DOMAIN_CONFIG.SYSTEM_DOMAIN}`, type: 'admin', plan: 'Admin', status: 'active', joinDate: '2023-12-01' },
  ];

  // Mock links data
  const mockLinks = [
    { 
      id: 1, 
      originalUrl: 'https://www.example.com/very-long-url-here', 
      shortUrl: `${DOMAIN_CONFIG.DEFAULT_DOMAIN}/abc123`, 
      title: 'Example Website',
      clicks: 245, 
      createdAt: '2024-06-01', 
      userId: 1,
      isActive: true,
      category: 'Business',
      customDomain: 'go.yourbrand.com'
    },
    { 
      id: 2, 
      originalUrl: 'https://www.google.com/search?q=link+shortener', 
      shortUrl: `${DOMAIN_CONFIG.DEFAULT_DOMAIN}/xyz789`, 
      title: 'Google Search',
      clicks: 89, 
      createdAt: '2024-06-05', 
      userId: 1,
      isActive: true,
      category: 'Research',
      customDomain: ''
    },
    { 
      id: 3, 
      originalUrl: 'https://github.com/user/repository', 
      shortUrl: `${DOMAIN_CONFIG.DEFAULT_DOMAIN}/def456`, 
      title: 'GitHub Repository',
      clicks: 156, 
      createdAt: '2024-06-10', 
      userId: 2,
      isActive: true,
      category: 'Development',
      customDomain: 'short.company.com'
    }
  ];

  // Mock analytics data
  const mockAnalytics = {
    totalClicks: 490,
    totalLinks: 3,
    activeUsers: 2,
    clicksThisMonth: 234,
    clicksLastMonth: 256,
    topCountries: ['United States', 'United Kingdom', 'Canada'],
    clicksByDay: [12, 23, 34, 45, 56, 67, 78]
  };

  useEffect(() => {
    // Initialize mock data
    setUsers(mockUsers);
    setLinks(mockLinks);
    setAnalytics(mockAnalytics);
  }, []);

  const handleLogin = (email, password, type = 'customer') => {
    // Mock authentication
    const foundUser = mockUsers.find(u => u.email === email);
    if (foundUser) {
      setUser(foundUser);
      setIsAuthenticated(true);
      setUserType(foundUser.type);
      setCurrentView(foundUser.type === 'admin' ? 'adminDashboard' : 'customerDashboard');
    }
  };

  const handleSignup = (userData) => {
    // Mock signup
    const newUser = {
      id: users.length + 1,
      ...userData,
      type: 'customer',
      plan: 'Basic',
      status: 'active',
      joinDate: new Date().toISOString().split('T')[0]
    };
    setUsers([...users, newUser]);
    setUser(newUser);
    setIsAuthenticated(true);
    setUserType('customer');
    setCurrentView('customerDashboard');
  };

  const handleLogout = () => {
    setUser(null);
    setIsAuthenticated(false);
    setUserType('customer');
    setCurrentView('home');
  };

  const handleCreateLink = (linkData) => {
    const newLink = {
      id: links.length + 1,
      ...linkData,
      shortUrl: createShortUrl(linkData.customDomain),
      clicks: 0,
      createdAt: new Date().toISOString().split('T')[0],
      userId: user?.id || 1,
      isActive: true
    };
    setLinks([...links, newLink]);
    return newLink;
  };

  const handleDeleteLink = (linkId) => {
    setLinks(links.filter(link => link.id !== linkId));
  };

  const handleToggleLink = (linkId) => {
    setLinks(links.map(link => 
      link.id === linkId ? { ...link, isActive: !link.isActive } : link
    ));
  };

  const handleViewChange = (view) => {
    setCurrentView(view);
  };

  const renderCurrentView = () => {
    if (!isAuthenticated && (currentView === 'customerDashboard' || currentView === 'adminDashboard')) {
      setCurrentView('login');
    }

    switch (currentView) {
      case 'home':
        return <HomePage onViewChange={handleViewChange} onCreateLink={handleCreateLink} />;
      case 'login':
        return <LoginPage onLogin={handleLogin} onViewChange={handleViewChange} />;
      case 'signup':
        return <SignupPage onSignup={handleSignup} onViewChange={handleViewChange} />;
      case 'customerDashboard':
        return <CustomerDashboard 
          user={user}
          links={links.filter(link => link.userId === user?.id)}
          onCreateLink={handleCreateLink}
          onDeleteLink={handleDeleteLink}
          onToggleLink={handleToggleLink}
          onViewChange={handleViewChange}
        />;
      case 'adminDashboard':
        return <AdminDashboard 
          user={user}
          links={links}
          users={users}
          analytics={analytics}
          onViewChange={handleViewChange}
        />;
      case 'linkAnalytics':
        return <LinkAnalytics 
          links={links}
          analytics={analytics}
          onViewChange={handleViewChange}
        />;
      case 'userManagement':
        return <UserManagement 
          users={users}
          onViewChange={handleViewChange}
        />;
      case 'customerAnalytics':
        return <CustomerAnalytics 
          users={users}
          links={links}
          onViewChange={handleViewChange}
        />;
      case 'customerReports':
        return <CustomerReports 
          users={users}
          links={links}
          onViewChange={handleViewChange}
        />;
      case 'dataImport':
        return <DataImportManager 
          onViewChange={handleViewChange}
        />;
      default:
        return <HomePage onViewChange={handleViewChange} onCreateLink={handleCreateLink} />;
    }
  };

  return (
    <ThemeProvider>
      <SubscriptionProvider>
        <div className="App min-h-screen bg-gray-50 dark:bg-gray-900">
          <BrowserRouter>
            <Header 
              currentView={currentView} 
              onViewChange={handleViewChange}
              user={user}
              isAuthenticated={isAuthenticated}
              userType={userType}
              onLogout={handleLogout}
            />
            <main className="pt-16">
              {renderCurrentView()}
            </main>
          </BrowserRouter>
        </div>
      </SubscriptionProvider>
    </ThemeProvider>
  );
}

export default App;