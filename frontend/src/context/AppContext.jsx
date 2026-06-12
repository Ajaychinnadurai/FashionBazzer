import React, { createContext, useContext, useReducer } from 'react';

const AppContext = createContext();

const initialState = {
  sidebarOpen: true,
  theme: 'dark',
  stats: null,
  products: [],
  postQueue: [],
  platformStatus: [],
  earnings: [],
  loading: {
    dashboard: false,
    products: false,
    queue: false,
    analytics: false,
  },
  refreshing: false,
};

function reducer(state, action) {
  switch (action.type) {
    case 'TOGGLE_SIDEBAR':
      return { ...state, sidebarOpen: !state.sidebarOpen };

    case 'SET_STATS':
      return { ...state, stats: action.payload };

    case 'SET_PRODUCTS':
      return { ...state, products: action.payload };

    case 'SET_POST_QUEUE':
      return { ...state, postQueue: action.payload };

    case 'SET_PLATFORM_STATUS':
      return { ...state, platformStatus: action.payload };

    case 'SET_EARNINGS':
      return { ...state, earnings: action.payload };

    case 'SET_LOADING':
      return {
        ...state,
        loading: { ...state.loading, [action.payload.key]: action.payload.value },
      };

    case 'SET_REFRESHING':
      return { ...state, refreshing: action.payload };

    default:
      return state;
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const value = {
    state,
    dispatch,
    toggleSidebar: () => dispatch({ type: 'TOGGLE_SIDEBAR' }),
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
}
