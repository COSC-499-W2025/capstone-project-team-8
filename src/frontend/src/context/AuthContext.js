'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import config from '@/config';

const AuthContext = createContext();

function getInitialToken() {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token') || null;
  }
  return null;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(getInitialToken);
  const [loading, setLoading] = useState(true);

  // Fetch user information from the API
  const fetchUserInfo = async (authToken) => {
    try {
      const response = await fetch(`${config.API_URL}/api/users/me/`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else if (response.status === 401) {
        // Token is invalid, logout
        logout();
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
  };

  // Load user info if token exists on mount
  useEffect(() => {
    const initializeAuth = async () => {
      if (token) {
        await fetchUserInfo(token);
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (accessToken, refreshToken) => {
    setToken(accessToken);
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    
    // Fetch user info immediately after login
    await fetchUserInfo(accessToken);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  const refreshAccessToken = async () => {
    const storedRefresh = localStorage.getItem('refresh_token');
    if (!storedRefresh) return null;
    try {
      const res = await fetch(`${config.API_URL}/api/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: storedRefresh }),
      });
      if (!res.ok) {
        logout();
        return null;
      }
      const data = await res.json();
      const newToken = data.access;
      setToken(newToken);
      localStorage.setItem('access_token', newToken);
      return newToken;
    } catch {
      return null;
    }
  };

  const setCurrentUser = (userData) => {
    setUser(userData);
  };

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated,
        login,
        logout,
        setCurrentUser,
        refreshAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}