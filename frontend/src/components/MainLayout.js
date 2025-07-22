import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './Sidebar';
import Dashboard from './Dashboard';
import KnowledgeEngine from './KnowledgeEngine';
import ContentLibraryEnhanced from './ContentLibraryEnhanced';
import SystemsModule from './SystemsModule';
import AIAgents from './AIAgents';
import Analytics from './Analytics';
import AdminConsole from './AdminConsole';

const MainLayout = () => {
  const [activeRoute, setActiveRoute] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const renderMainContent = () => {
    switch (activeRoute) {
      case 'dashboard':
        return <Dashboard />;
      case 'knowledge-engine':
        return <KnowledgeEngine />;
      case 'content-library':
        return <ContentLibrary />;
      case 'systems':
        return <SystemsModule />;
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
        sidebarCollapsed ? 'ml-16' : 'ml-64'
      }`}>
        {/* Top Bar */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
                PromptSupport
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                AI-Native Support Platform
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                🔔
              </button>
              <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                ⚙️
              </button>
            </div>
          </div>
        </header>

        {/* Dynamic Main View */}
        <main className="flex-1 overflow-auto p-6">
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
    </div>
  );
};

export default MainLayout;