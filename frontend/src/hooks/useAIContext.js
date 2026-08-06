import { useState, useCallback, useContext, createContext } from 'react';

const AIContext = createContext(null);

export function AIProvider({ children }) {
  const [aiState, setAiState] = useState({
    isEnabled: true,
    model: 'moonshot/kimi-k2.6',
    temperature: 0.7,
    maxTokens: 2000,
  });

  const updateAIConfig = useCallback((config) => {
    setAiState(prev => ({ ...prev, ...config }));
  }, []);

  return (
    <AIContext.Provider value={{ ...aiState, updateAIConfig }}>
      {children}
    </AIContext.Provider>
  );
}

export function useAIContext() {
  const context = useContext(AIContext);
  if (!context) {
    throw new Error('useAIContext must be used within an AIProvider');
  }
  return context;
}
