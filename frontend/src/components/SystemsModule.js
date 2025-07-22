import React from 'react';
import { motion } from 'framer-motion';
import { 
  Database, 
  BookText, 
  Bot, 
  Users, 
  Ticket,
  ArrowRight,
  Settings,
  Eye,
  Globe,
  Zap
} from 'lucide-react';

const SystemsModule = ({ onNavigate }) => {
  const systems = [
    {
      id: 'knowledge-base',
      title: 'Knowledge Base',
      description: 'Structured, searchable knowledge base with drag-and-drop TOC builder',
      icon: Database,
      status: 'active',
      stats: { articles: 47, categories: 8, views: 1205 },
      features: ['Drag-and-drop TOC', 'AI Search', 'Custom theming', 'Analytics'],
      color: 'blue'
    },
    {
      id: 'developer-docs',
      title: 'Developer Docs',
      description: 'Auto-generated interactive API documentation with live spec sync',
      icon: BookText,
      status: 'active',
      stats: { endpoints: 23, schemas: 12, uptime: '99.9%' },
      features: ['OpenAPI sync', 'GraphQL support', 'Interactive testing', 'Code examples'],
      color: 'purple'
    },
    {
      id: 'chatbot',
      title: 'AI Chatbot',
      description: 'Intelligent chatbot trained on your knowledge base and documentation',
      icon: Bot,
      status: 'active',
      stats: { conversations: 156, accuracy: '94%', deflection: '87%' },
      features: ['Multi-channel', 'Smart fallback', 'Custom behavior', 'Analytics'],
      color: 'green'
    },
    {
      id: 'community',
      title: 'Community Portal',
      description: 'Self-moderating community with AI-powered insights and FAQ extraction',
      icon: Users,
      status: 'inactive',
      stats: { members: 0, threads: 0, engagement: 'N/A' },
      features: ['AI moderation', 'Thread summarization', 'FAQ extraction', 'Multi-platform'],
      color: 'orange'
    },
    {
      id: 'ticketing',
      title: 'Ticketing System',
      description: 'AI-powered ticketing with smart triage and automated responses',
      icon: Ticket,
      status: 'inactive',
      stats: { tickets: 0, resolution: 'N/A', sla: 'N/A' },
      features: ['Smart triage', 'Auto-response', 'SLA tracking', 'Multi-channel'],
      color: 'red'
    }
  ];

  const getStatusColor = (status) => {
    return status === 'active' ? 'text-green-600' : 'text-gray-400';
  };

  const getStatusBadge = (status) => {
    return status === 'active' 
      ? 'bg-green-100 text-green-700' 
      : 'bg-gray-100 text-gray-500';
  };

  const getSystemColor = (color, active) => {
    if (!active) return 'from-gray-100 to-gray-200';
    
    const colors = {
      blue: 'from-blue-100 to-blue-200',
      purple: 'from-purple-100 to-purple-200',
      green: 'from-green-100 to-green-200',
      orange: 'from-orange-100 to-orange-200',
      red: 'from-red-100 to-red-200'
    };
    
    return colors[color] || 'from-gray-100 to-gray-200';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Systems</h1>
        <p className="text-gray-600">
          Manage and configure your support system modules: Knowledge Base, Developer Docs, Chatbot, Community, and Ticketing
        </p>
      </div>

      {/* Systems Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {systems.map((system, index) => (
          <motion.div
            key={system.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
          >
            {/* Header */}
            <div className={`bg-gradient-to-r ${getSystemColor(system.color, system.status === 'active')} p-6`}>
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-sm">
                    {React.createElement(system.icon, { 
                      size: 24, 
                      className: system.status === 'active' ? 'text-gray-700' : 'text-gray-400' 
                    })}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{system.title}</h3>
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium capitalize ${getStatusBadge(system.status)}`}>
                      {system.status}
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {system.status === 'active' && (
                    <>
                      <button className="p-2 text-gray-600 hover:text-gray-800 hover:bg-white/50 rounded-lg">
                        <Settings size={16} />
                      </button>
                      <button className="p-2 text-gray-600 hover:text-gray-800 hover:bg-white/50 rounded-lg">
                        <Eye size={16} />
                      </button>
                      <button className="p-2 text-gray-600 hover:text-gray-800 hover:bg-white/50 rounded-lg">
                        <Globe size={16} />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              <p className="text-gray-600 mb-4">{system.description}</p>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                {Object.entries(system.stats).map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div className="text-lg font-semibold text-gray-900">{value}</div>
                    <div className="text-xs text-gray-500 capitalize">{key}</div>
                  </div>
                ))}
              </div>

              {/* Features */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Key Features</h4>
                <div className="grid grid-cols-2 gap-1">
                  {system.features.map((feature) => (
                    <div key={feature} className="flex items-center text-sm text-gray-600">
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2"></div>
                      {feature}
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between">
                {system.status === 'active' ? (
                  <div className="flex items-center space-x-2">
                    <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-sm">
                      <Settings size={14} />
                      <span>Configure</span>
                    </button>
                    <button className="flex items-center space-x-2 border border-gray-300 hover:border-gray-400 text-gray-700 px-3 py-2 rounded-lg text-sm">
                      <Eye size={14} />
                      <span>Preview</span>
                    </button>
                  </div>
                ) : (
                  <button className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">
                    <Zap size={16} />
                    <span>Activate</span>
                  </button>
                )}
                
                <button className="flex items-center space-x-1 text-blue-600 hover:text-blue-700">
                  <span className="text-sm">View Details</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mb-2">
              🚀
            </div>
            <h3 className="font-medium text-gray-900">Deploy All Active Systems</h3>
            <p className="text-sm text-gray-600">Publish all configured systems to production</p>
          </button>

          <button className="p-4 text-left border border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mb-2">
              🔄
            </div>
            <h3 className="font-medium text-gray-900">Sync All Content</h3>
            <p className="text-sm text-gray-600">Update all systems with latest content</p>
          </button>

          <button className="p-4 text-left border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-colors">
            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mb-2">
              📊
            </div>
            <h3 className="font-medium text-gray-900">View Analytics</h3>
            <p className="text-sm text-gray-600">Performance metrics across all systems</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SystemsModule;