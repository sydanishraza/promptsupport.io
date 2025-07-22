import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, 
  Brain, 
  Users, 
  MessageSquare, 
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Clock
} from 'lucide-react';

const Dashboard = () => {
  const [agentHealth, setAgentHealth] = useState({
    orchestrator: { status: 'healthy', uptime: '99.9%', lastActive: '2 min ago' },
    content: { status: 'healthy', uptime: '99.8%', lastActive: '1 min ago' },
    chatbot: { status: 'healthy', uptime: '100%', lastActive: '30 sec ago' },
    ticketing: { status: 'warning', uptime: '98.5%', lastActive: '5 min ago' },
    community: { status: 'healthy', uptime: '99.7%', lastActive: '3 min ago' }
  });

  const [platformStats, setPlatformStats] = useState({
    totalDocuments: 147,
    activeChats: 23,
    ticketsResolved: 89,
    knowledgeBaseViews: 1205
  });

  const agents = [
    { 
      name: 'OrchestratorAgent', 
      icon: Activity, 
      description: 'Oversees readiness, deployment, health, and coordination',
      status: agentHealth.orchestrator.status,
      uptime: agentHealth.orchestrator.uptime,
      lastActive: agentHealth.orchestrator.lastActive
    },
    { 
      name: 'ContentAgent', 
      icon: Brain, 
      description: 'Handles ingestion, extraction, spec monitoring, article generation',
      status: agentHealth.content.status,
      uptime: agentHealth.content.uptime,
      lastActive: agentHealth.content.lastActive
    },
    { 
      name: 'ChatbotAgent', 
      icon: MessageSquare, 
      description: 'Trains/updates chatbot models + fallback logic',
      status: agentHealth.chatbot.status,
      uptime: agentHealth.chatbot.uptime,
      lastActive: agentHealth.chatbot.lastActive
    },
    { 
      name: 'TicketingAgent', 
      icon: Users, 
      description: 'Triage, reply suggestion, escalation, routing',
      status: agentHealth.ticketing.status,
      uptime: agentHealth.ticketing.uptime,
      lastActive: agentHealth.ticketing.lastActive
    },
    { 
      name: 'CommunityAgent', 
      icon: Users, 
      description: 'Moderation, summarization, tagging, FAQ extraction',
      status: agentHealth.community.status,
      uptime: agentHealth.community.uptime,
      lastActive: agentHealth.community.lastActive
    }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-50 border-green-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Welcome to PromptSupport
            </h1>
            <p className="text-gray-600">
              Your AI-native support platform is running smoothly. Here's an overview of system health and recent activity.
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Last updated</div>
            <div className="text-lg font-semibold text-gray-900">Just now</div>
          </div>
        </div>
      </div>

      {/* Platform Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Documents</p>
              <p className="text-3xl font-bold text-gray-900">{platformStats.totalDocuments}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              📚
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">+12 this week</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Chats</p>
              <p className="text-3xl font-bold text-gray-900">{platformStats.activeChats}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              💬
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">+5 from yesterday</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Tickets Resolved</p>
              <p className="text-3xl font-bold text-gray-900">{platformStats.ticketsResolved}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              🎫
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">94% auto-resolved</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">KB Views</p>
              <p className="text-3xl font-bold text-gray-900">{platformStats.knowledgeBaseViews}</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              👁️
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">+18% this month</span>
          </div>
        </motion.div>
      </div>

      {/* AI Agents Health */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">AI Agents Health</h2>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-sm text-gray-600">All systems operational</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {agents.map((agent, index) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              className={`p-4 rounded-lg border ${getStatusColor(agent.status)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center shadow-sm">
                    {React.createElement(agent.icon, { size: 16, className: 'text-gray-600' })}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{agent.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{agent.description}</p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>Uptime: {agent.uptime}</span>
                      <span>Last active: {agent.lastActive}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(agent.status)}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="p-4 text-left rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mb-2">
              🧠
            </div>
            <h3 className="font-medium text-gray-900">Add Knowledge</h3>
            <p className="text-sm text-gray-600">Upload files or URLs</p>
          </button>

          <button className="p-4 text-left rounded-lg border border-gray-200 hover:border-green-300 hover:bg-green-50 transition-colors">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mb-2">
              🤖
            </div>
            <h3 className="font-medium text-gray-900">Test Chatbot</h3>
            <p className="text-sm text-gray-600">Preview responses</p>
          </button>

          <button className="p-4 text-left rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors">
            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mb-2">
              📊
            </div>
            <h3 className="font-medium text-gray-900">View Analytics</h3>
            <p className="text-sm text-gray-600">Performance insights</p>
          </button>

          <button className="p-4 text-left rounded-lg border border-gray-200 hover:border-orange-300 hover:bg-orange-50 transition-colors">
            <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center mb-2">
              ⚙️
            </div>
            <h3 className="font-medium text-gray-900">Settings</h3>
            <p className="text-sm text-gray-600">Configure platform</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;