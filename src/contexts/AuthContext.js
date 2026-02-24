import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Get token from cookie
  const getToken = () => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; token=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  };

  // Decode JWT token to get user info
  const decodeToken = (token) => {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  };

  // Check if user has specific role or higher
  const hasRole = (requiredRole) => {
    if (!user) return false;
    
    const roleHierarchy = {
      'user': 1,
      'admin': 2,
      'super_admin': 3
    };
    
    const userLevel = roleHierarchy[user.role] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;
    
    return userLevel >= requiredLevel;
  };

  // Check if user has exact role
  const hasExactRole = (role) => {
    return user?.role === role;
  };

  // Check if user can access company data
  const canAccessCompany = (companyId) => {
    if (!user) return false;
    
    // Super admins can access all companies
    if (user.role === 'super_admin') return true;
    
    // Admins and users can only access their own company
    return user.companyid === companyId;
  };

  // Initialize auth state
  useEffect(() => {
    const token = getToken();
    if (token) {
      const userData = decodeToken(token);
      if (userData) {
        setUser(userData);
      }
    }
    setLoading(false);
  }, []);

  // Login function
  const login = async (credentials) => {
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_LINKS}/api/v1/login`, credentials, { 
        withCredentials: true 
      });
      
      if (response.data.access_token) {
        // Set token cookie
        document.cookie = `token=${response.data.access_token}; path=/; max-age=${60 * 60 * 24}; secure; samesite=strict`;
        
        // Update user state
        const userData = response.data.user;
        setUser(userData);
        
        return { success: true, user: userData };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  // Logout function
  const logout = () => {
    // Clear token cookie
    document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    setUser(null);
  };

  // Get auth headers for API calls
  const getAuthHeaders = () => {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const value = {
    user,
    loading,
    login,
    logout,
    hasRole,
    hasExactRole,
    canAccessCompany,
    getAuthHeaders,
    isAuthenticated: !!user,
    isSuperAdmin: user?.role === 'super_admin',
    isAdmin: user?.role === 'admin',
    isUser: user?.role === 'user'
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
