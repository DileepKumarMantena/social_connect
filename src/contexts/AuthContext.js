import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
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
  const [token, setToken] = useState(null);

  // Check for existing token on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      // Try to validate with backend
      validateToken(storedToken);
    }
    setLoading(false);
  }, []);

  // Validate token with backend
  const validateToken = async (token) => {
    try {
      console.log('validateToken called with token:', token ? 'token exists' : 'no token');
      console.log('Making profile request to:', `${process.env.REACT_APP_API_LINKS}/api/v1/profile`);
      const response = await axios.get(`${process.env.REACT_APP_API_LINKS}/api/v1/profile`, {
        withCredentials: true,
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data) {
        setUser(response.data);
        setToken(token);
      }
    } catch (error) {
      // Token invalid, clear it
      localStorage.removeItem('token');
      setUser(null);
      setToken(null);
    }
  };

  // Login function
  const login = async (credentials) => {
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_LINKS}/api/v1/login`, credentials, { 
        withCredentials: true,  // Important for httpOnly cookies
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.data.access_token || response.headers['set-cookie']) {
        // Token is now set as httpOnly cookie by backend
        // Update user state
        const userData = response.data.user;
        setUser(userData);
        setToken(response.data.access_token); // Keep for immediate use
        
        // Store token in localStorage for dashboard API calls
        if (response.data.access_token) {
          localStorage.setItem('token', response.data.access_token);
        }
        
        return { success: true, user: userData };
      }
      return { success: false, error: 'Login failed' };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  // Token refresh function
  const refreshToken = async () => {
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_LINKS}/api/v1/refresh-token`, {}, { 
        withCredentials: true,  // Important for httpOnly cookies
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.data.access_token) {
        setToken(response.data.access_token);
        return { success: true };
      }
      return { success: false, error: 'Token refresh failed' };
    } catch (error) {
      console.error('Token refresh error:', error);
      return { success: false, error: error.response?.data?.detail || 'Token refresh failed' };
    }
  };

  // Auto-refresh token before expiration
  const setupTokenRefresh = useCallback(() => {
    // Refresh token every 25 minutes (before 30 min expiration)
    const refreshInterval = setInterval(async () => {
      try {
        await refreshToken();
      } catch (error) {
        console.error('Auto token refresh failed:', error);
        // Could redirect to login on failure
      }
    }, 25 * 60 * 1000); // 25 minutes

    // Cleanup on unmount
    return () => clearInterval(refreshInterval);
  }, []);

  // Logout function
  const logout = useCallback(() => {
    // Clear token from localStorage (backup)
    localStorage.removeItem('token');
    
    // Clear httpOnly cookie via backend call
    axios.post(`${process.env.REACT_APP_API_LINKS}/api/v1/logout`, {}, {
      withCredentials: true
    }).catch(console.error);
    
    // Clear state
    setUser(null);
    setToken(null);
  }, []);

  // Get auth headers function
  const getAuthHeaders = useCallback(() => {
    const currentToken = token || localStorage.getItem('token');
    return currentToken ? { 
      Authorization: `Bearer ${currentToken}`,
      'Content-Type': 'application/json'
    } : {
        'Content-Type': 'application/json'
      };
  }, [token]);

  // Verify token function
  const verifyToken = useCallback(async () => {
    try {
      const currentToken = token || localStorage.getItem('token');
      console.log("verifyToken called, currentToken:", currentToken);
      if (!currentToken) {
        console.log("No token available");
        return { success: false, error: 'No token available' };
      }

      console.log("Making verify token request to:", `${process.env.REACT_APP_API_LINKS}/api/v1/verify-token`);
      try {
        console.log("Making verify token request to:", `${process.env.REACT_APP_API_LINKS}/api/v1/verify-token`);
        const response = await axios.get(`${process.env.REACT_APP_API_LINKS}/api/v1/verify-token`, {
          headers: { 
            Authorization: `Bearer ${currentToken}`,
            'Content-Type': 'application/json'
          }
        });

        console.log("Verify token response:", response);
        console.log("Response status:", response.status);
        console.log("Response data:", response.data);

        if (response.status === 200 && response.data.valid) {
          console.log("Token valid, setting user data:", response.data.data);
          console.log("User data permissions:", response.data.data.permissions);
          setUser(response.data.data);
          return { 
            success: true, 
            data: response.data.data 
          };
        } else {
          console.log("Token invalid or bad response:", response.status, response.data);
          return { 
            success: false, 
            error: 'Invalid token' 
          };
        }
      } catch (error) {
        console.error("Network error in verifyToken:", error);
        console.error("Error details:", error.response?.data);
        return { 
          success: false, 
          error: error.response?.data?.detail || 'Network error' 
        };
      }
    } catch (error) {
      console.error('Token verification error:', error);
      console.error('Error response:', error.response);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Token verification failed' 
      };
    }
  }, [token]);

  // Role checking functions
  const hasRole = useCallback((role) => {
    return user?.role === role;
  }, [user]);

  const hasExactRole = useCallback((role) => {
    return user?.role === role;
  }, [user]);

  const isSuperAdmin = useCallback(() => {
    return user?.role === 'super_admin';
  }, [user]);

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    refreshToken,
    setupTokenRefresh,
    getAuthHeaders,
    verifyToken,
    hasRole,
    hasExactRole,
    isSuperAdmin,
    isAuthenticated: !!user
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
