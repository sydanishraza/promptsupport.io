import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './Sidebar';
import Dashboard from './Dashboard';
import KnowledgeEngine from './KnowledgeEngine';
import ContentLibrary from './ContentLibrary';
import SystemsModule from './SystemsModule';
import AIAgents from './AIAgents';
import Analytics from './Analytics';
import KnowledgeBaseBuilder from './KnowledgeBaseBuilder';
import Settings from './Settings';
import AdminConsole from './AdminConsole';
import Connections from './Connections';


const MainLayout = () => {
  const [activeRoute, setActiveRoute] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  // Auto-collapse sidebar on mobile
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) { // md breakpoint
        setSidebarCollapsed(true);
      } else {
        setSidebarCollapsed(false);
      }
    };

    // Set initial state
    handleResize();
    
    // Add event listener
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const renderMainContent = () => {
    switch (activeRoute) {
      case 'dashboard':
        return <Dashboard />;
      case 'knowledge-engine':
        return <KnowledgeEngine />;
      case 'content-upload':
        return <KnowledgeEngine activeModule="upload" />;
      case 'uploaded-content':
        return <KnowledgeEngine activeModule="content" />;
      case 'chat-with-engine':
        return <KnowledgeEngine activeModule="chat" />;
      case 'processing-jobs':
        return <KnowledgeEngine activeModule="jobs" />;
      case 'connections':
        return <Connections />;
      case 'content-library':
        return <ContentLibrary />;
      case 'refined-engine-test':
        return <RefinedEngineTest />;
      case 'systems':
        return <SystemsModule onNavigate={setActiveRoute} />;
      case 'knowledge-base-builder':
        return <KnowledgeBaseBuilder />;
      case 'ai-agents':
        return <AIAgents />;
      case 'analytics':
        return <Analytics />;
      case 'admin-console':
        return <AdminConsole />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Left Sidebar */}
      <Sidebar
        activeRoute={activeRoute}
        setActiveRoute={setActiveRoute}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
      />

      {/* Main Content Area */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${
        sidebarCollapsed ? 'ml-16 md:ml-20' : 'ml-64'
      }`}>
        {/* Top Bar - Mobile Optimized */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-3 sm:px-6 h-[60px] sm:h-[81px] flex items-center">
          <div className="flex items-center justify-between w-full">
            <div className="hidden sm:block">
              <p className="text-sm sm:text-lg font-medium text-gray-600 dark:text-gray-300">
                AI-Native. Fully Autonomous. Always On.
              </p>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-4 ml-auto sm:ml-0">
              <button className="p-1.5 sm:p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors text-sm sm:text-base">
                🔔
              </button>
              <button 
                onClick={() => setSettingsOpen(true)}
                className="p-1.5 sm:p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors text-sm sm:text-base"
                title="Settings"
              >
                ⚙️
              </button>
            </div>
          </div>
        </header>

        {/* Dynamic Main View - Mobile Optimized */}
        <main className="flex-1 overflow-auto p-2 sm:p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeRoute}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              {renderMainContent()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Settings Modal */}
      <Settings 
        isOpen={settingsOpen} 
        onClose={() => setSettingsOpen(false)} 
      />
    </div>
  );
};

export default MainLayout;