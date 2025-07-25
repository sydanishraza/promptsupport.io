import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Home, 
  Brain, 
  BookOpen, 
  Puzzle, 
  Activity, 
  BarChart3, 
  Settings,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Database,
  BookText,
  Bot,
  Users,
  Ticket,
  Upload,
  MessageSquare,
  Clock,
  Link
} from 'lucide-react';

const Sidebar = ({ activeRoute, setActiveRoute, collapsed, setCollapsed }) => {
  const [systemsExpanded, setSystemsExpanded] = useState(false);
  const [knowledgeEngineExpanded, setKnowledgeEngineExpanded] = useState(false);
  const [hoveredItem, setHoveredItem] = useState(null);
  const [showFlyout, setShowFlyout] = useState(null);

  const navigationItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: Home,
      description: 'Overview of platform status, agent health, quick insights'
    },
    {
      id: 'knowledge-engine',
      label: 'Knowledge Engine',
      icon: Brain,
      description: 'AI-powered content processing, search, and intelligent chat',
      expandable: true,
      expanded: knowledgeEngineExpanded,
      setExpanded: setKnowledgeEngineExpanded,
      subitems: [
        { id: 'content-upload', label: 'Content Upload', icon: Upload },
        { id: 'uploaded-content', label: 'Uploaded Content', icon: Database },
        { id: 'chat-with-engine', label: 'Chat with Engine', icon: MessageSquare },
        { id: 'processing-jobs', label: 'Jobs', icon: Clock },
        { id: 'connections', label: 'Connections', icon: Link }
      ]
    },
    {
      id: 'content-library',
      label: 'Content Library',
      icon: BookOpen,
      description: 'Manage AI-generated/user-edited articles and assets'
    },
    {
      id: 'systems',
      label: 'Systems',
      icon: Puzzle,
      description: 'Knowledge Base, Developer Docs, Chatbot, Community, Ticketing',
      expandable: true,
      expanded: systemsExpanded,
      setExpanded: setSystemsExpanded,
      subitems: [
        { id: 'knowledge-base', label: 'Knowledge Base', icon: Database },
        { id: 'developer-docs', label: 'Developer Docs', icon: BookText },
        { id: 'chatbot', label: 'Chatbot', icon: Bot },
        { id: 'community', label: 'Community', icon: Users },
        { id: 'ticketing', label: 'Ticketing', icon: Ticket }
      ]
    },
    {
      id: 'ai-agents',
      label: 'AI Agents',
      icon: Activity,
      description: 'Health/status, logs, queues for all agents'
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: BarChart3,
      description: 'KB usage, bot activity, ticket deflection, insights'
    },
    {
      id: 'admin-console',
      label: 'Admin Console',
      icon: Settings,
      description: 'Org settings, users, domains, API keys, integrations'
    }
  ];

  const handleItemClick = (itemId) => {
    if (itemId === 'systems') {
      setSystemsExpanded(!systemsExpanded);
    } else if (itemId === 'knowledge-engine') {
      setKnowledgeEngineExpanded(!knowledgeEngineExpanded);
    } else if (itemId === 'knowledge-base') {
      setActiveRoute('knowledge-base-builder');
    } else {
      setActiveRoute(itemId);
    }
  };

  return (
    <motion.div
      className={`fixed left-0 top-0 h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 z-30 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
      initial={false}
      animate={{ width: collapsed ? 64 : 256 }}
    >
      {/* Header */}
      <div className="px-6 h-[81px] flex items-center border-b border-gray-200 dark:border-gray-700">
        {!collapsed ? (
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center space-x-3">
              <img
                src="/ps-logo.png"
                alt="PromptSupport Logo"
                className="w-8 h-8 object-contain"
              />
              <span className="font-semibold text-gray-900 dark:text-white text-lg">
                PromptSupport
              </span>
            </div>
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
            >
              <ChevronLeft size={16} />
            </button>
          </div>
        ) : (
          <div className="relative w-full flex items-center justify-center">
            {/* Centered Logo - Larger Size */}
            <img
              src="/ps-logo.png"
              alt="PromptSupport Logo"
              className="w-10 h-10 object-contain"
            />
            {/* Toggle Button - Right Edge, Vertically Centered */}
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="absolute right-0 p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
              title="Expand Sidebar"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        )}
      </div>

      {/* Navigation Items */}
      <nav className="p-2 space-y-1">
        {navigationItems.map((item) => (
          <div key={item.id}>
            <button
              onClick={() => handleItemClick(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
                activeRoute === item.id
                  ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
              title={collapsed ? item.label : item.description}
            >
              <item.icon size={20} />
              {!collapsed && (
                <>
                  <span className="flex-1 font-medium">{item.label}</span>
                  {item.expandable && (
                    <div className="text-gray-400">
                      {item.expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </div>
                  )}
                </>
              )}
            </button>

            {/* Systems Subitems */}
            {item.expandable && item.expanded && !collapsed && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="ml-6 mt-1 space-y-1"
              >
                {item.subitems.map((subitem) => (
                  <button
                    key={subitem.id}
                    onClick={() => handleItemClick(subitem.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                      activeRoute === (subitem.id === 'knowledge-base' ? 'knowledge-base-builder' : subitem.id)
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <subitem.icon size={16} />
                    <span>{subitem.label}</span>
                  </button>
                ))}
              </motion.div>
            )}
          </div>
        ))}
      </nav>
    </motion.div>
  );
};

export default Sidebar;