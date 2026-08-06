import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../api/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check session via /auth/me - HttpOnly cookies are sent automatically
  const checkSession = useCallback(async () => {
    try {
      const userData = await authAPI.me();
      setUser({
        username: userData.username,
        role: userData.role || 'user',
        email: userData.email,
        display_name: userData.display_name,
      });
      return true;
    } catch (err) {
      // If 401 and we have a refresh token (cookie), try to refresh
      if (err.response?.status === 401) {
        try {
          await authAPI.refresh();
          // Retry /me after refresh
          const userData = await authAPI.me();
          setUser({
            username: userData.username,
            role: userData.role || 'user',
            email: userData.email,
            display_name: userData.display_name,
          });
          return true;
        } catch {
          // Refresh also failed - user is not authenticated
          setUser(null);
        }
      } else {
        setUser(null);
      }
      return false;
    }
  }, []);

  useEffect(() => {
    const initSession = async () => {
      // Clear any legacy localStorage tokens (migration cleanup)
      localStorage.removeItem('user_id');
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_role');
      
      await checkSession();
      setLoading(false);
    };
    initSession();
  }, [checkSession]);

  // Login - cookies are set by the backend, we just update state
  const login = (username, _token, role = 'user') => {
    // Token parameter kept for backward compatibility but not used
    // HttpOnly cookies are automatically set by the login response
    setUser({ username, role });
  };

  // Logout - backend clears cookies
  const logout = async () => {
    try { 
      await authAPI.logout(); 
    } catch {}
    setUser(null);
  };

  const isAuthenticated = () => !!user;

  const isAdmin = () => user?.role === 'admin';

  // Refresh session (can be called by components when needed)
  const refreshSession = async () => {
    try {
      await authAPI.refresh();
      return await checkSession();
    } catch {
      return false;
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      logout, 
      isAuthenticated, 
      isAdmin, 
      loading,
      refreshSession,
      checkSession 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
