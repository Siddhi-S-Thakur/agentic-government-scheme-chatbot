import React from 'react';
import './i18n';
import { AuthProvider } from './context/AuthContext';
import ChatInterface from './components/ChatInterface';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <ChatInterface />
    </AuthProvider>
  );
};

export default App;
