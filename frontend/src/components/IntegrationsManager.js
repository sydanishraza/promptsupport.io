import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Settings, 
  CheckCircle2,
  AlertCircle,
  Link,
  ExternalLink,
  RefreshCw,
  Plus,
  ChevronRight,
  Database,
  Globe,
  FileText,
  MessageSquare,
  Calendar,
  Folder,
  Video,
  Github
} from 'lucide-react';

const IntegrationsManager = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('available');
  const [integrations, setIntegrations] = useState([
    {
      id: 'notion',
      name: 'Notion',
      description: 'Sync pages, databases, and documentation',
      icon: '📓',
      color: 'from-gray-700 to-black',
      status: 'connected',
      lastSync: '2 hours ago',
      resources: ['4 workspaces', '23 pages', '12 databases'],
      category: 'Documentation'
    },
    {
      id: 'github',
      name: 'GitHub',
      description: 'Import README files, docs, and code comments',
      icon: '🐙',
      color: 'from-gray-800 to-gray-900',
      status: 'connected',
      lastSync: '1 day ago',
      resources: ['3 repositories', '15 README files', '8 wikis'],
      category: 'Development'
    },
    {
      id: 'confluence',
      name: 'Confluence',
      description: 'Access team documentation and knowledge base',
      icon: '🏢',
      color: 'from-blue-600 to-blue-800',
      status: 'available',
      lastSync: null,
      resources: [],
      category: 'Documentation'
    },
    {
      id: 'slack',
      name: 'Slack',
      description: 'Import conversations and knowledge from channels',
      icon: '💬',
      color: 'from-purple-600 to-purple-800',
      status: 'available',
      lastSync: null,
      resources: [],
      category: 'Communication'
    },
    {
      id: 'jira',
      name: 'JIRA',
      description: 'Sync project documentation and ticket information',
      icon: '🎯',
      color: 'from-blue-500 to-blue-700',
      status: 'error',
      lastSync: '5 days ago',
      resources: ['Connection failed'],
      category: 'Project Management'
    },
    {
      id: 'drive',
      name: 'Google Drive',
      description: 'Access documents, sheets, and presentations',
      icon: '📁',
      color: 'from-green-500 to-green-700',
      status: 'available',
      lastSync: null,
      resources: [],
      category: 'Storage'
    },
    {
      id: 'youtube',
      name: 'YouTube',
      description: 'Extract transcripts and content from videos',
      icon: '📺',
      color: 'from-red-500 to-red-700',
      status: 'available',
      lastSync: null,
      resources: [],
      category: 'Media'
    },
    {
      id: 'loom',
      name: 'Loom',
      description: 'Process video recordings and extract insights',
      icon: '🎥',
      color: 'from-purple-500 to-pink-500',
      status: 'available',
      lastSync: null,
      resources: [],
      category: 'Media'
    }
  ]);

  const [selectedIntegration, setSelectedIntegration] = useState(null);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected': return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'error': return <AlertCircle className="w-5 h-5 text-red-600" />;
      default: return <Plus className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return 'bg-green-100 text-green-800 border-green-200';
      case 'error': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'connected': return 'Connected';
      case 'error': return 'Error';
      default: return 'Available';
    }
  };

  const filteredIntegrations = integrations.filter(integration => {
    if (activeTab === 'connected') return integration.status === 'connected';
    if (activeTab === 'available') return integration.status === 'available';
    return true;
  });

  const handleConnect = (integrationId) => {
    setIntegrations(prev => prev.map(integration => 
      integration.id === integrationId 
        ? { ...integration, status: 'connected', lastSync: 'Just now', resources: ['Connecting...'] }
        : integration
    ));
  };

  const handleDisconnect = (integrationId) => {
    setIntegrations(prev => prev.map(integration => 
      integration.id === integrationId 
        ? { ...integration, status: 'available', lastSync: null, resources: [] }
        : integration
    ));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-slate-900/95 via-purple-900/95 to-slate-900/95 backdrop-blur-xl flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 max-w-6xl w-full max-h-[90vh] overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,250,252,0.98) 100%)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255,255,255,0.2)'
        }}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white p-8 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400/30 to-purple-400/30 backdrop-blur-sm"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-4 bg-white/20 backdrop-blur-sm rounded-2xl border border-white/30">
                <Settings className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-3xl font-bold">Integrations Manager</h2>
                <p className="text-blue-100 mt-1 font-medium">
                  Connect platforms and sync your content seamlessly
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-3 hover:bg-white/10 rounded-2xl transition-all duration-300 backdrop-blur-sm border border-white/20"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="flex h-[calc(90vh-200px)]">
          {/* Sidebar */}
          <div className="w-80 bg-gradient-to-b from-gray-50 to-white border-r border-gray-200 p-6">
            <div className="space-y-2 mb-8">
              {[
                { id: 'all', label: 'All Integrations', count: integrations.length },
                { id: 'connected', label: 'Connected', count: integrations.filter(i => i.status === 'connected').length },
                { id: 'available', label: 'Available', count: integrations.filter(i => i.status === 'available').length }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center justify-between p-4 rounded-2xl font-medium transition-all duration-200 ${
                    activeTab === tab.id 
                      ? 'bg-blue-100 text-blue-900 shadow-md' 
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <span>{tab.label}</span>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    activeTab === tab.id 
                      ? 'bg-blue-200 text-blue-800' 
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {tab.count}
                  </span>
                </button>
              ))}
            </div>

            {/* Categories */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Categories</h3>
              {['Documentation', 'Development', 'Communication', 'Project Management', 'Storage', 'Media'].map(category => (
                <div key={category} className="flex items-center space-x-3 text-sm text-gray-600">
                  <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                  <span>{category}</span>
                  <span className="text-xs bg-gray-100 text-gray-500 px-2 py-1 rounded-full">
                    {integrations.filter(i => i.category === category).length}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 p-8 overflow-y-auto bg-gradient-to-br from-slate-50/30 to-blue-50/20">
            {selectedIntegration ? (
              // Integration Details View
              <div className="space-y-8">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setSelectedIntegration(null)}
                    className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
                  >
                    <ChevronRight className="w-5 h-5 rotate-180" />
                  </button>
                  <div className="flex items-center space-x-4">
                    <div className={`p-4 bg-gradient-to-br ${selectedIntegration.color} rounded-2xl text-white text-2xl shadow-lg`}>
                      {selectedIntegration.icon}
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900">{selectedIntegration.name}</h3>
                      <p className="text-gray-600">{selectedIntegration.description}</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-100 shadow-sm">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">Connection Status</h4>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(selectedIntegration.status)}
                          <span className="font-medium text-gray-900">{getStatusText(selectedIntegration.status)}</span>
                        </div>
                        {selectedIntegration.status === 'connected' ? (
                          <button
                            onClick={() => handleDisconnect(selectedIntegration.id)}
                            className="px-4 py-2 bg-red-100 text-red-700 rounded-xl hover:bg-red-200 transition-colors font-medium"
                          >
                            Disconnect
                          </button>
                        ) : (
                          <button
                            onClick={() => handleConnect(selectedIntegration.id)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium"
                          >
                            Connect
                          </button>
                        )}
                      </div>
                      {selectedIntegration.lastSync && (
                        <div className="mt-4 text-sm text-gray-600">
                          Last synced: {selectedIntegration.lastSync}
                        </div>
                      )}
                    </div>

                    {selectedIntegration.status === 'connected' && selectedIntegration.resources.length > 0 && (
                      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-100 shadow-sm">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Connected Resources</h4>
                        <div className="space-y-3">
                          {selectedIntegration.resources.map((resource, index) => (
                            <div key={index} className="flex items-center space-x-3 p-3 bg-blue-50 rounded-xl">
                              <Database className="w-4 h-4 text-blue-600" />
                              <span className="text-gray-800">{resource}</span>
                            </div>
                          ))}
                        </div>
                        <button className="mt-4 flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium">
                          <RefreshCw className="w-4 h-4" />
                          <span>Sync Now</span>
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="space-y-6">
                    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-100 shadow-sm">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">Configuration</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Sync Frequency
                          </label>
                          <select className="w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <option>Every hour</option>
                            <option>Every 6 hours</option>
                            <option>Daily</option>
                            <option>Weekly</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Content Types
                          </label>
                          <div className="space-y-2">
                            {['Documentation', 'Code Comments', 'README Files', 'Wiki Pages'].map(type => (
                              <label key={type} className="flex items-center space-x-3">
                                <input type="checkbox" defaultChecked className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                <span className="text-gray-700">{type}</span>
                              </label>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              // Integrations Grid View
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-2xl font-bold text-gray-900">
                    {activeTab === 'all' && 'All Integrations'}
                    {activeTab === 'connected' && 'Connected Integrations'}
                    {activeTab === 'available' && 'Available Integrations'}
                  </h3>
                  <div className="flex items-center space-x-4">
                    <button className="flex items-center space-x-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-xl hover:bg-blue-200 transition-colors">
                      <RefreshCw className="w-4 h-4" />
                      <span>Refresh All</span>
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredIntegrations.map((integration) => (
                    <motion.div
                      key={integration.id}
                      whileHover={{ scale: 1.02, y: -4 }}
                      className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer"
                      onClick={() => setSelectedIntegration(integration)}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className={`p-3 bg-gradient-to-br ${integration.color} rounded-xl text-white text-xl shadow-md`}>
                          {integration.icon}
                        </div>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(integration.status)}
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(integration.status)}`}>
                            {getStatusText(integration.status)}
                          </span>
                        </div>
                      </div>
                      
                      <h4 className="text-xl font-bold text-gray-900 mb-2">{integration.name}</h4>
                      <p className="text-gray-600 text-sm mb-4 leading-relaxed">{integration.description}</p>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                          {integration.category}
                        </span>
                        {integration.lastSync && (
                          <span className="text-xs text-gray-500">
                            {integration.lastSync}
                          </span>
                        )}
                      </div>
                      
                      {integration.resources.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-100">
                          <div className="text-xs text-gray-600 mb-2">Connected Resources:</div>
                          <div className="space-y-1">
                            {integration.resources.slice(0, 2).map((resource, index) => (
                              <div key={index} className="text-xs text-gray-700 bg-gray-50 px-2 py-1 rounded-lg">
                                {resource}
                              </div>
                            ))}
                            {integration.resources.length > 2 && (
                              <div className="text-xs text-gray-500">
                                +{integration.resources.length - 2} more
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>

                {filteredIntegrations.length === 0 && (
                  <div className="text-center py-16">
                    <Settings className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-600 mb-2">
                      No {activeTab} integrations found
                    </h3>
                    <p className="text-gray-500">
                      {activeTab === 'connected' 
                        ? 'Connect some integrations to get started'
                        : 'Check back later for more integrations'
                      }
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default IntegrationsManager;