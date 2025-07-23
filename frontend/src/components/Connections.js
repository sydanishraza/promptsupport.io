import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Link,
  Settings,
  CheckCircle,
  AlertCircle,
  XCircle,
  Plus,
  Trash2,
  Edit3,
  Key,
  Globe,
  Database,
  Zap,
  RefreshCw,
  ExternalLink,
  Shield,
  Clock
} from 'lucide-react';

const Connections = () => {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  
  // Available integrations
  const availableIntegrations = [
    {
      id: 'google-drive',
      name: 'Google Drive',
      description: 'Sync documents and files from Google Drive',
      category: 'Storage',
      icon: '📁',
      authType: 'oauth',
      features: ['Auto-sync documents', 'Real-time updates', 'Folder watching'],
      setupUrl: 'https://console.developers.google.com'
    },
    {
      id: 'dropbox',
      name: 'Dropbox',
      description: 'Import files and folders from Dropbox',
      category: 'Storage',
      icon: '📦',
      authType: 'oauth',
      features: ['File synchronization', 'Batch processing', 'Change notifications'],
      setupUrl: 'https://www.dropbox.com/developers'
    },
    {
      id: 'notion',
      name: 'Notion',
      description: 'Sync pages and databases from Notion workspace',
      category: 'Documentation',
      icon: '📝',
      authType: 'api_key',
      features: ['Page synchronization', 'Database exports', 'Markdown conversion'],
      setupUrl: 'https://developers.notion.com'
    },
    {
      id: 'confluence',
      name: 'Confluence',
      description: 'Import pages and spaces from Atlassian Confluence',
      category: 'Documentation',
      icon: '🏢',
      authType: 'api_key',
      features: ['Space synchronization', 'Page hierarchy', 'Comment extraction'],
      setupUrl: 'https://developer.atlassian.com'
    },
    {
      id: 'slack',
      name: 'Slack',
      description: 'Process messages and files from Slack channels',
      category: 'Communication',
      icon: '💬',
      authType: 'oauth',
      features: ['Channel monitoring', 'File processing', 'Thread analysis'],
      setupUrl: 'https://api.slack.com'
    },
    {
      id: 'github',
      name: 'GitHub',
      description: 'Sync repositories, issues, and documentation',
      category: 'Development',
      icon: '🐙',
      authType: 'token',
      features: ['Repository sync', 'Issue tracking', 'README processing'],
      setupUrl: 'https://github.com/settings/tokens'
    },
    {
      id: 'jira',
      name: 'Jira',
      description: 'Import tickets, projects, and documentation',
      category: 'Project Management',
      icon: '🎯',
      authType: 'api_key',
      features: ['Ticket synchronization', 'Project tracking', 'Comment analysis'],
      setupUrl: 'https://developer.atlassian.com'
    },
    {
      id: 'salesforce',
      name: 'Salesforce',
      description: 'Sync knowledge articles and case data',
      category: 'CRM',
      icon: '☁️',
      authType: 'oauth',
      features: ['Knowledge base sync', 'Case analysis', 'Contact insights'],
      setupUrl: 'https://developer.salesforce.com'
    },
    {
      id: 'zendesk',
      name: 'Zendesk',
      description: 'Import help center articles and ticket data',
      category: 'Support',
      icon: '🎧',
      authType: 'api_key',
      features: ['Article synchronization', 'Ticket analysis', 'Customer insights'],
      setupUrl: 'https://developer.zendesk.com'
    },
    {
      id: 'intercom',
      name: 'Intercom',
      description: 'Sync conversations and help articles',
      category: 'Support',
      icon: '💌',
      authType: 'oauth',
      features: ['Conversation sync', 'Article import', 'User tracking'],
      setupUrl: 'https://developers.intercom.com'
    }
  ];

  // Mock connections data
  useEffect(() => {
    setConnections([
      {
        id: 'google-drive-1',
        integrationId: 'google-drive',
        name: 'Google Drive - Main Account',
        status: 'connected',
        lastSync: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
        documentsSync: 247,
        nextSync: new Date(Date.now() + 1 * 60 * 60 * 1000), // 1 hour from now
        config: {
          folders: ['Marketing Materials', 'Documentation', 'Training'],
          autoSync: true,
          syncInterval: '1h'
        }
      },
      {
        id: 'slack-1',
        integrationId: 'slack',
        name: 'Slack - Engineering Team',
        status: 'needs_reauth',
        lastSync: new Date(Date.now() - 24 * 60 * 60 * 1000), // 24 hours ago
        documentsSync: 89,
        nextSync: null,
        config: {
          channels: ['#general', '#engineering', '#support'],
          includeFiles: true,
          includeThreads: true
        }
      },
      {
        id: 'notion-1',
        integrationId: 'notion',
        name: 'Notion - Company Wiki',
        status: 'connected',
        lastSync: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
        documentsSync: 156,
        nextSync: new Date(Date.now() + 30 * 60 * 1000), // 30 minutes from now
        config: {
          databases: ['Projects', 'Procedures', 'FAQ'],
          includeComments: false,
          syncPrivate: false
        }
      }
    ]);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return 'text-green-600 bg-green-100';
      case 'needs_reauth': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      case 'syncing': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected': return <CheckCircle className="w-4 h-4" />;
      case 'needs_reauth': return <AlertCircle className="w-4 h-4" />;
      case 'error': return <XCircle className="w-4 h-4" />;
      case 'syncing': return <RefreshCw className="w-4 h-4 animate-spin" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Storage': return <Database className="w-5 h-5" />;
      case 'Documentation': return <Globe className="w-5 h-5" />;
      case 'Communication': return <Zap className="w-5 h-5" />;
      case 'Development': return <Settings className="w-5 h-5" />;
      default: return <Link className="w-5 h-5" />;
    }
  };

  const handleConnect = (integration) => {
    setSelectedConnection(integration);
    setShowAuthModal(true);
  };

  const handleReauth = (connection) => {
    setSelectedConnection(connection);
    setShowAuthModal(true);
  };

  const handleDisconnect = (connectionId) => {
    if (confirm('Are you sure you want to disconnect this integration?')) {
      setConnections(prev => prev.filter(conn => conn.id !== connectionId));
    }
  };

  const handleSync = async (connectionId) => {
    setConnections(prev => prev.map(conn => 
      conn.id === connectionId 
        ? { ...conn, status: 'syncing' }
        : conn
    ));

    // Simulate sync process
    setTimeout(() => {
      setConnections(prev => prev.map(conn => 
        conn.id === connectionId 
          ? { 
              ...conn, 
              status: 'connected',
              lastSync: new Date(),
              nextSync: new Date(Date.now() + 60 * 60 * 1000)
            }
          : conn
      ));
    }, 3000);
  };

  const groupedIntegrations = availableIntegrations.reduce((acc, integration) => {
    if (!acc[integration.category]) {
      acc[integration.category] = [];
    }
    acc[integration.category].push(integration);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Connections</h1>
            <p className="text-gray-600">
              Manage integrations and data sources for your Knowledge Engine
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Connection
          </button>
        </div>
      </div>

      {/* Active Connections */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Active Connections</h2>
        
        {connections.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Link className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg mb-2">No connections configured</p>
            <p className="text-sm">Add your first integration to start syncing data</p>
          </div>
        ) : (
          <div className="space-y-4">
            {connections.map((connection) => {
              const integration = availableIntegrations.find(i => i.id === connection.integrationId);
              return (
                <div key={connection.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-2xl">{integration?.icon}</div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{connection.name}</h3>
                        <p className="text-sm text-gray-600">{integration?.description}</p>
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                          <span>📄 {connection.documentsSync} documents synced</span>
                          {connection.lastSync && (
                            <span>🕒 Last sync: {connection.lastSync.toLocaleString()}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(connection.status)}`}>
                        {getStatusIcon(connection.status)}
                        <span className="ml-1 capitalize">{connection.status.replace('_', ' ')}</span>
                      </span>
                      
                      <div className="flex space-x-1">
                        {connection.status === 'connected' && (
                          <button
                            onClick={() => handleSync(connection.id)}
                            className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                            title="Sync now"
                          >
                            <RefreshCw className="w-4 h-4" />
                          </button>
                        )}
                        
                        {connection.status === 'needs_reauth' && (
                          <button
                            onClick={() => handleReauth(connection)}
                            className="p-2 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded"
                            title="Re-authenticate"
                          >
                            <Key className="w-4 h-4" />
                          </button>
                        )}
                        
                        <button
                          onClick={() => setSelectedConnection(connection)}
                          className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded"
                          title="Settings"
                        >
                          <Settings className="w-4 h-4" />
                        </button>
                        
                        <button
                          onClick={() => handleDisconnect(connection.id)}
                          className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                          title="Disconnect"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Available Integrations */}
      {showAddModal && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Available Integrations</h2>
            <button
              onClick={() => setShowAddModal(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {Object.entries(groupedIntegrations).map(([category, integrations]) => (
            <div key={category} className="mb-6">
              <div className="flex items-center mb-3">
                {getCategoryIcon(category)}
                <h3 className="ml-2 font-medium text-gray-900">{category}</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {integrations.map((integration) => {
                  const isConnected = connections.some(conn => conn.integrationId === integration.id);
                  
                  return (
                    <div key={integration.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">{integration.icon}</span>
                          <div>
                            <h4 className="font-semibold text-gray-900">{integration.name}</h4>
                            <p className="text-sm text-gray-600">{integration.description}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <ul className="text-xs text-gray-500 space-y-1">
                          {integration.features.slice(0, 2).map((feature, index) => (
                            <li key={index}>• {feature}</li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <a
                          href={integration.setupUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:text-blue-800 flex items-center"
                        >
                          Setup Guide <ExternalLink className="w-3 h-3 ml-1" />
                        </a>
                        
                        <button
                          onClick={() => handleConnect(integration)}
                          disabled={isConnected}
                          className={`px-3 py-1 text-xs rounded ${
                            isConnected
                              ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                              : 'bg-blue-600 text-white hover:bg-blue-700'
                          }`}
                        >
                          {isConnected ? 'Connected' : 'Connect'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Auth Modal (placeholder) */}
      {showAuthModal && selectedConnection && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Connect to {selectedConnection.name}
            </h3>
            <p className="text-gray-600 mb-4">
              This integration requires authentication. Please provide the necessary credentials.
            </p>
            <div className="space-y-3">
              <input
                type="text"
                placeholder="API Key / Token"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                placeholder="Base URL (if required)"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowAuthModal(false);
                  setSelectedConnection(null);
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  // TODO: Implement actual connection logic
                  setShowAuthModal(false);
                  setSelectedConnection(null);
                  alert('Connection would be established here');
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Connect
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Connections;