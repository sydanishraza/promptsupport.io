import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings, 
  Users, 
  Globe, 
  Key, 
  Webhook, 
  Building2,
  Plus,
  Edit,
  Trash2,
  Copy,
  Eye,
  EyeOff,
  CheckCircle,
  AlertCircle,
  Link,
  Shield
} from 'lucide-react';

const AdminConsole = () => {
  const [activeTab, setActiveTab] = useState('organization');
  const [showApiKeys, setShowApiKeys] = useState({});

  const tabs = [
    { id: 'organization', label: 'Organization', icon: Building2 },
    { id: 'users', label: 'Users & Roles', icon: Users },
    { id: 'domains', label: 'Custom Domains', icon: Globe },
    { id: 'api-keys', label: 'API Keys', icon: Key },
    { id: 'webhooks', label: 'Webhooks', icon: Webhook },
    { id: 'integrations', label: 'Integrations', icon: Link }
  ];

  const mockUsers = [
    {
      id: 1,
      name: 'John Doe',
      email: 'john@company.com',
      role: 'Admin',
      status: 'Active',
      lastActive: '2 hours ago',
      permissions: ['All Access']
    },
    {
      id: 2,
      name: 'Sarah Wilson',
      email: 'sarah@company.com',
      role: 'Editor',
      status: 'Active',
      lastActive: '5 minutes ago',
      permissions: ['Content Management', 'Analytics View']
    },
    {
      id: 3,
      name: 'Mike Johnson',
      email: 'mike@company.com',
      role: 'Viewer',
      status: 'Invited',
      lastActive: 'Never',
      permissions: ['Read Only']
    }
  ];

  const mockDomains = [
    {
      id: 1,
      domain: 'support.company.com',
      type: 'Primary',
      status: 'Active',
      ssl: 'Valid',
      module: 'Unified Portal',
      lastVerified: '2 hours ago'
    },
    {
      id: 2,
      domain: 'docs.company.com',
      type: 'Custom',
      status: 'Active',
      ssl: 'Valid',
      module: 'Developer Docs',
      lastVerified: '1 day ago'
    },
    {
      id: 3,
      domain: 'help.company.com',
      type: 'Custom',
      status: 'Pending',
      ssl: 'Pending',
      module: 'Knowledge Base',
      lastVerified: 'Never'
    }
  ];

  const mockApiKeys = [
    {
      id: 1,
      name: 'Production API',
      key: 'pk_live_51234567890abcdef',
      permissions: ['Full Access'],
      status: 'Active',
      lastUsed: '2 minutes ago',
      created: '2024-01-15'
    },
    {
      id: 2,
      name: 'Development API',
      key: 'pk_test_51234567890abcdef',
      permissions: ['Read Only'],
      status: 'Active',
      lastUsed: '1 hour ago',
      created: '2024-01-10'
    },
    {
      id: 3,
      name: 'Integration API',
      key: 'pk_int_51234567890abcdef',
      permissions: ['Content Management'],
      status: 'Inactive',
      lastUsed: '5 days ago',
      created: '2024-01-05'
    }
  ];

  const mockWebhooks = [
    {
      id: 1,
      name: 'Slack Notifications',
      url: 'https://hooks.slack.com/services/...',
      events: ['ticket.created', 'chat.escalated'],
      status: 'Active',
      lastTriggered: '30 minutes ago',
      deliveryRate: '99.8%'
    },
    {
      id: 2,
      name: 'Analytics Webhook',
      url: 'https://analytics.company.com/webhook',
      events: ['article.viewed', 'chat.completed'],
      status: 'Active',
      lastTriggered: '5 minutes ago',
      deliveryRate: '100%'
    },
    {
      id: 3,
      name: 'CRM Integration',
      url: 'https://crm.company.com/api/webhook',
      events: ['ticket.resolved', 'user.feedback'],
      status: 'Error',
      lastTriggered: '2 days ago',
      deliveryRate: '87.3%'
    }
  ];

  const mockIntegrations = [
    {
      id: 1,
      name: 'GitHub',
      type: 'Code Repository',
      status: 'Connected',
      syncStatus: 'Up to date',
      lastSync: '15 minutes ago',
      repos: 3
    },
    {
      id: 2,
      name: 'Notion',
      type: 'Knowledge Management',
      status: 'Connected',
      syncStatus: 'Syncing',
      lastSync: '2 hours ago',
      pages: 47
    },
    {
      id: 3,
      name: 'Slack',
      type: 'Communication',
      status: 'Connected',
      syncStatus: 'Up to date',
      lastSync: '5 minutes ago',
      channels: 8
    },
    {
      id: 4,
      name: 'JIRA',
      type: 'Issue Tracking',
      status: 'Error',
      syncStatus: 'Authentication failed',
      lastSync: '3 days ago',
      issues: 0
    }
  ];

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'connected':
      case 'valid':
        return 'bg-green-100 text-green-700';
      case 'pending':
      case 'syncing':
        return 'bg-yellow-100 text-yellow-700';
      case 'inactive':
      case 'error':
      case 'authentication failed':
        return 'bg-red-100 text-red-700';
      case 'invited':
        return 'bg-blue-100 text-blue-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'connected':
      case 'valid':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
      case 'authentication failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const toggleApiKeyVisibility = (keyId) => {
    setShowApiKeys(prev => ({
      ...prev,
      [keyId]: !prev[keyId]
    }));
  };

  const maskApiKey = (key, show) => {
    if (show) return key;
    return key.substring(0, 8) + '••••••••••••••••••••';
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'organization':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900">Organization Details</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Organization Name</label>
                    <input type="text" defaultValue="Company Inc." className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Subdomain</label>
                    <div className="flex items-center">
                      <input type="text" defaultValue="company" className="px-3 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                      <span className="px-3 py-2 bg-gray-100 border border-l-0 border-gray-300 rounded-r-lg text-gray-600">.promptsupport.ai</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Support Email</label>
                    <input type="email" defaultValue="support@company.com" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900">Branding</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Logo</label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <div className="w-16 h-16 bg-gray-100 rounded-lg mx-auto mb-2"></div>
                      <p className="text-sm text-gray-600">Upload logo (PNG, JPG)</p>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Primary Color</label>
                    <div className="flex items-center space-x-2">
                      <input type="color" defaultValue="#3B82F6" className="w-12 h-10 border border-gray-300 rounded-lg" />
                      <input type="text" defaultValue="#3B82F6" className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end">
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg">
                Save Changes
              </button>
            </div>
          </div>
        );

      case 'users':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Team Members</h3>
              <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                <Plus size={16} />
                <span>Invite User</span>
              </button>
            </div>
            
            <div className="overflow-hidden bg-white border border-gray-200 rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Active</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {mockUsers.map((user) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-medium text-gray-900">{user.name}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{user.role}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(user.status)}`}>
                          {user.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">{user.lastActive}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          <button className="p-1 text-gray-400 hover:text-gray-600">
                            <Edit size={16} />
                          </button>
                          <button className="p-1 text-gray-400 hover:text-red-600">
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );

      case 'domains':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Custom Domains</h3>
              <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                <Plus size={16} />
                <span>Add Domain</span>
              </button>
            </div>
            
            <div className="space-y-4">
              {mockDomains.map((domain) => (
                <div key={domain.id} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Globe size={16} className="text-blue-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{domain.domain}</div>
                        <div className="text-sm text-gray-500">{domain.module}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(domain.status)}`}>
                            {domain.status}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(domain.ssl)}`}>
                            SSL: {domain.ssl}
                          </span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">Verified: {domain.lastVerified}</div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button className="p-2 text-gray-400 hover:text-gray-600">
                          <Settings size={16} />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-red-600">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'api-keys':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">API Keys</h3>
              <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                <Plus size={16} />
                <span>Create API Key</span>
              </button>
            </div>
            
            <div className="space-y-4">
              {mockApiKeys.map((apiKey) => (
                <div key={apiKey.id} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                        <Key size={16} className="text-gray-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{apiKey.name}</div>
                        <div className="text-sm text-gray-500">Created: {apiKey.created}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(apiKey.status)}`}>
                        {apiKey.status}
                      </span>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <Edit size={16} />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-red-600">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                    <code className="text-sm font-mono text-gray-900">
                      {maskApiKey(apiKey.key, showApiKeys[apiKey.id])}
                    </code>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => toggleApiKeyVisibility(apiKey.id)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        {showApiKeys[apiKey.id] ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                      <button className="p-1 text-gray-400 hover:text-gray-600">
                        <Copy size={16} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="mt-3 flex items-center justify-between text-sm">
                    <div className="text-gray-500">
                      Permissions: {apiKey.permissions.join(', ')}
                    </div>
                    <div className="text-gray-500">
                      Last used: {apiKey.lastUsed}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'webhooks':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Webhooks</h3>
              <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                <Plus size={16} />
                <span>Add Webhook</span>
              </button>
            </div>
            
            <div className="space-y-4">
              {mockWebhooks.map((webhook) => (
                <div key={webhook.id} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                        <Webhook size={16} className="text-purple-600" />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{webhook.name}</div>
                        <div className="text-sm text-gray-500 font-mono">{webhook.url}</div>
                        <div className="flex items-center space-x-4 mt-2 text-sm">
                          <span className="text-gray-500">Events: {webhook.events.length}</span>
                          <span className="text-gray-500">Last triggered: {webhook.lastTriggered}</span>
                          <span className="text-gray-500">Delivery: {webhook.deliveryRate}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(webhook.status)}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(webhook.status)}`}>
                        {webhook.status}
                      </span>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <Settings size={16} />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-red-600">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'integrations':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Connected Integrations</h3>
              <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                <Plus size={16} />
                <span>Add Integration</span>
              </button>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {mockIntegrations.map((integration) => (
                <div key={integration.id} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        <span className="text-lg">
                          {integration.name === 'GitHub' ? '🐙' :
                           integration.name === 'Notion' ? '📝' :
                           integration.name === 'Slack' ? '💬' :
                           integration.name === 'JIRA' ? '🎫' : '🔗'}
                        </span>
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{integration.name}</div>
                        <div className="text-sm text-gray-500">{integration.type}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(integration.status)}
                      <button className="p-1 text-gray-400 hover:text-gray-600">
                        <Settings size={16} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Status:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(integration.status)}`}>
                        {integration.status}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Sync Status:</span>
                      <span className="text-gray-900">{integration.syncStatus}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Last Sync:</span>
                      <span className="text-gray-900">{integration.lastSync}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">
                        {integration.repos !== undefined ? 'Repositories:' :
                         integration.pages !== undefined ? 'Pages:' :
                         integration.channels !== undefined ? 'Channels:' : 'Issues:'}
                      </span>
                      <span className="text-gray-900">
                        {integration.repos || integration.pages || integration.channels || integration.issues}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Admin Console</h1>
        <p className="text-gray-600">
          Manage organization settings, users, domains, API keys, and integrations
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {React.createElement(tab.icon, { size: 16 })}
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {renderTabContent()}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default AdminConsole;