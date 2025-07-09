import React,
{
  createContext,
  useState,
  useContext,
  useEffect
} from 'react';
import * as api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('accessToken'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      if (token) {
        try {
          const userData = await api.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error("Session expired or token is invalid.", error);
          setToken(null);
          localStorage.removeItem('accessToken');
        }
      }
      setLoading(false);
    };
    fetchUser();
  }, [token]);

  const login = (newToken) => {
    setToken(newToken);
    localStorage.setItem('accessToken', newToken);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('accessToken');
  };

  const value = { user, token, login, logout, isAuthenticated: !!token };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};
