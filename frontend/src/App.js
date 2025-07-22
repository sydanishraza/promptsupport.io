import React, { useState, useEffect } from 'react';
import './App.css';
import MainLayout from './components/MainLayout';
import QuickSetupWizard from './components/QuickSetupWizard';

function App() {
  const [isFirstLogin, setIsFirstLogin] = useState(false); // Changed to false to bypass wizard for testing
  const [showSetupWizard, setShowSetupWizard] = useState(false); // Disabled for testing

  useEffect(() => {
    // Check if setup has been completed - TEMPORARILY DISABLED FOR TESTING
    // const setupCompleted = localStorage.getItem('promptsupport_setup_completed');
    // if (!setupCompleted) {
    //   setShowSetupWizard(true);
    // } else {
    //   setIsFirstLogin(false);
    // }
    setShowSetupWizard(false); // Force wizard off for testing
    setIsFirstLogin(false);
  }, []);

  const handleSetupComplete = () => {
    localStorage.setItem('promptsupport_setup_completed', 'true');
    setShowSetupWizard(false);
    setIsFirstLogin(false);
  };

  const handleSkipSetup = () => {
    setShowSetupWizard(false);
    setIsFirstLogin(false);
  };

  if (showSetupWizard) {
    return (
      <QuickSetupWizard 
        onComplete={handleSetupComplete}
        onSkip={handleSkipSetup}
      />
    );
  }

  return (
    <div className="App">
      <MainLayout />
    </div>
  );
}

export default App;