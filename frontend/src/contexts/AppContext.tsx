import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface ForecastResults {
  segment_count: number;
  recommended_campaign_type: string;
  recommended_offer: string;
  success_probability: number;
  privacy_compliance: boolean;
  campaign_details: {
    type: string;
    offer: string;
    target: string;
    discount: number;
    budget: number;
    target_size: number;
  };
  report_links: {
    html: string;
    pdf: string;
  };
}

interface AppContextType {
  forecastResults: ForecastResults | null;
  setForecastResults: (results: ForecastResults | null) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [forecastResults, setForecastResults] = useState<ForecastResults | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <AppContext.Provider value={{
      forecastResults,
      setForecastResults,
      isLoading,
      setIsLoading
    }}>
      {children}
    </AppContext.Provider>
  );
};