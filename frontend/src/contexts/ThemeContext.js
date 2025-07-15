import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Theme Context
const ThemeContext = createContext();

// Action types
const SET_THEME = 'SET_THEME';
const TOGGLE_THEME = 'TOGGLE_THEME';

// Initial state
const initialState = {
  theme: 'light', // 'light' or 'dark'
  systemTheme: 'light'
};

// Reducer
const themeReducer = (state, action) => {
  switch (action.type) {
    case SET_THEME:
      return {
        ...state,
        theme: action.payload
      };
    case TOGGLE_THEME:
      return {
        ...state,
        theme: state.theme === 'light' ? 'dark' : 'light'
      };
    default:
      return state;
  }
};

// Theme Provider
export const ThemeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(themeReducer, initialState);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('linkabet-theme');
    if (savedTheme) {
      dispatch({ type: SET_THEME, payload: savedTheme });
    } else {
      // Check system preference
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      dispatch({ type: SET_THEME, payload: systemTheme });
    }
  }, []);

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    if (state.theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // Save to localStorage
    localStorage.setItem('linkabet-theme', state.theme);
  }, [state.theme]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e) => {
      // Only apply system theme if user hasn't manually selected a theme
      const savedTheme = localStorage.getItem('linkabet-theme');
      if (!savedTheme) {
        dispatch({ type: SET_THEME, payload: e.matches ? 'dark' : 'light' });
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Theme actions
  const setTheme = (theme) => {
    dispatch({ type: SET_THEME, payload: theme });
  };

  const toggleTheme = () => {
    dispatch({ type: TOGGLE_THEME });
  };

  const isDark = state.theme === 'dark';

  const value = {
    theme: state.theme,
    isDark,
    setTheme,
    toggleTheme
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook to use theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeContext;