import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, 
  Brain, 
  MessageSquare, 
  Users, 
  Ticket,
  CheckCircle,
  AlertCircle,
  Clock,
  Cpu,
  Database,
  Zap,
  Pause,
  Play,
  RotateCcw,
  Settings
} from 'lucide-react';

const AIAgents = () => {
  const [selectedAgent, setSelectedAgent] = useState('orchestrator');

  const agents = {
    orchestrator: {
      name: 'OrchestratorAgent',
      description: 'Oversees readiness, deployment, health, and coordination',
      icon: Activity,
      status: 'healthy',
      uptime: '99.9%',
      lastActive: '30 seconds ago',
      tasksCompleted: 1247,
      tasksQueued: 3,
      cpu: 12,
      memory: 64,
      responsibilities: [
        'System health monitoring',
        'Agent coordination',
        'Deployment orchestration',
        'Resource allocation',
        'Error handling and recovery'
      ],
      recentActivity: [
        { time: '2 min ago', action: 'Coordinated content sync across all agents', status: 'success' },
        { time: '5 min ago', action: 'Deployed knowledge base updates', status: 'success' },
        { time: '10 min ago', action: 'Health check completed for all systems', status: 'success' },
        { time: '15 min ago', action: 'Initiated automated backup process', status: 'success' }
      ],
      metrics: [
        { label: 'Deployments Today', value: '12', trend: 'up' },
        { label: 'Error Rate', value: '0.1%', trend: 'down' },
        { label: 'Avg Response Time', value: '45ms', trend: 'stable' },
        { label: 'Success Rate', value: '99.9%', trend: 'up' }
      ]
    },
    content: {
      name: 'ContentAgent',
      description: 'Handles ingestion, extraction, spec monitoring, article generation',
      icon: Brain,
      status: 'healthy',
      uptime: '99.8%',
      lastActive: '1 minute ago',
      tasksCompleted: 856,
      tasksQueued: 7,
      cpu: 25,
      memory: 128,
      responsibilities: [
        'Document processing and ingestion',
        'Content extraction and chunking',
        'Article generation from sources',
        'Metadata extraction and tagging',
        'Continuous content synchronization'
      ],
      recentActivity: [
        { time: '1 min ago', action: 'Processed 3 new documents from Knowledge Engine', status: 'success' },
        { time: '8 min ago', action: 'Generated article: "API Rate Limiting Best Practices"', status: 'success' },
        { time: '12 min ago', action: 'Extracted metadata from uploaded video content', status: 'success' },
        { time: '18 min ago', action: 'Synchronized content with GitHub repository', status: 'warning' }
      ],
      metrics: [
        { label: 'Documents Processed', value: '47', trend: 'up' },
        { label: 'Articles Generated', value: '23', trend: 'up' },
        { label: 'Processing Speed', value: '1.2s/doc', trend: 'down' },
        { label: 'Quality Score', value: '94%', trend: 'stable' }
      ]
    },
    chatbot: {
      name: 'ChatbotAgent',
      description: 'Trains/updates chatbot models + fallback logic',
      icon: MessageSquare,
      status: 'healthy',
      uptime: '100%',
      lastActive: '15 seconds ago',
      tasksCompleted: 2341,
      tasksQueued: 1,
      cpu: 18,
      memory: 96,
      responsibilities: [
        'Chatbot model training and updates',
        'Response quality optimization',
        'Fallback logic implementation',
        'Conversation flow management',
        'Performance monitoring and tuning'
      ],
      recentActivity: [
        { time: '15 sec ago', action: 'Responded to user query about API authentication', status: 'success' },
        { time: '2 min ago', action: 'Updated response model with new KB content', status: 'success' },
        { time: '7 min ago', action: 'Triggered fallback to ticketing for complex query', status: 'success' },
        { time: '11 min ago', action: 'Completed conversation quality analysis', status: 'success' }
      ],
      metrics: [
        { label: 'Conversations Today', value: '156', trend: 'up' },
        { label: 'Accuracy Rate', value: '94%', trend: 'up' },
        { label: 'Avg Response Time', value: '850ms', trend: 'down' },
        { label: 'User Satisfaction', value: '4.7/5', trend: 'stable' }
      ]
    },
    ticketing: {
      name: 'TicketingAgent',
      description: 'Triage, reply suggestion, escalation, routing',
      icon: Ticket,
      status: 'warning',
      uptime: '98.5%',
      lastActive: '3 minutes ago',
      tasksCompleted: 412,
      tasksQueued: 15,
      cpu: 8,
      memory: 48,
      responsibilities: [
        'Ticket triage and classification',
        'Automated response generation',
        'Escalation logic and routing',
        'SLA monitoring and alerts',
        'Agent workload balancing'
      ],
      recentActivity: [
        { time: '3 min ago', action: 'Triaged incoming ticket: Priority High', status: 'warning' },
        { time: '8 min ago', action: 'Generated auto-response for billing inquiry', status: 'success' },
        { time: '15 min ago', action: 'Escalated complex technical issue to human agent', status: 'success' },
        { time: '22 min ago', action: 'Updated SLA tracking for enterprise customers', status: 'success' }
      ],
      metrics: [
        { label: 'Tickets Processed', value: '89', trend: 'up' },
        { label: 'Auto-Resolution Rate', value: '67%', trend: 'stable' },
        { label: 'Avg Resolution Time', value: '2.4h', trend: 'up' },
        { label: 'SLA Compliance', value: '94%', trend: 'down' }
      ]
    },
    community: {
      name: 'CommunityAgent',
      description: 'Moderation, summarization, tagging, FAQ extraction',
      icon: Users,
      status: 'healthy',
      uptime: '99.7%',
      lastActive: '45 seconds ago',
      tasksCompleted: 234,
      tasksQueued: 5,
      cpu: 6,
      memory: 32,
      responsibilities: [
        'Content moderation and filtering',
        'Thread summarization',
        'Automatic tagging and categorization',
        'FAQ extraction from discussions',
        'Community health monitoring'
      ],
      recentActivity: [
        { time: '45 sec ago', action: 'Moderated new community post for guidelines compliance', status: 'success' },
        { time: '4 min ago', action: 'Generated summary for weekly discussion thread', status: 'success' },
        { time: '9 min ago', action: 'Extracted FAQ from popular support thread', status: 'success' },
        { time: '16 min ago', action: 'Tagged discussion with relevant categories', status: 'success' }
      ],
      metrics: [
        { label: 'Posts Moderated', value: '234', trend: 'up' },
        { label: 'FAQs Extracted', value: '18', trend: 'up' },
        { label: 'Avg Processing Time', value: '1.8s', trend: 'stable' },
        { label: 'Accuracy Score', value: '96%', trend: 'up' }
      ]
    }
  };

  const currentAgent = agents[selectedAgent];

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600';
      case 'warning':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-700';
      case 'warning':
        return 'bg-yellow-100 text-yellow-700';
      case 'error':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-500';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return '📈';
      case 'down':
        return '📉';
      default:
        return '📊';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">AI Agents</h1>
        <p className="text-gray-600">
          Monitor health, status, logs, and queues for all AI agents in your support platform
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent List */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Agents</h2>
          <div className="space-y-2">
            {Object.entries(agents).map(([key, agent]) => (
              <button
                key={key}
                onClick={() => setSelectedAgent(key)}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg text-left transition-colors ${
                  selectedAgent === key
                    ? 'bg-blue-50 border-blue-200 border'
                    : 'hover:bg-gray-50 border border-transparent'
                }`}
              >
                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                  {React.createElement(agent.icon, { size: 16, className: 'text-gray-600' })}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900">{agent.name}</span>
                    {getStatusIcon(agent.status)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {agent.tasksCompleted} tasks completed
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Agent Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Agent Overview */}
          <motion.div
            key={selectedAgent}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center">
                  {React.createElement(currentAgent.icon, { size: 24, className: 'text-gray-600' })}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{currentAgent.name}</h3>
                  <p className="text-gray-600">{currentAgent.description}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                  <Settings size={16} />
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                  <Pause size={16} />
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                  <RotateCcw size={16} />
                </button>
              </div>
            </div>

            {/* Status and Metrics */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(currentAgent.status)}`}>
                  {currentAgent.status}
                </div>
                <p className="text-xs text-gray-500 mt-1">Status</p>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">{currentAgent.uptime}</div>
                <p className="text-xs text-gray-500">Uptime</p>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">{currentAgent.tasksQueued}</div>
                <p className="text-xs text-gray-500">Queued Tasks</p>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">{currentAgent.lastActive}</div>
                <p className="text-xs text-gray-500">Last Active</p>
              </div>
            </div>

            {/* Resource Usage */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">CPU Usage</span>
                  <span className="text-sm text-gray-600">{currentAgent.cpu}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${currentAgent.cpu}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Memory Usage</span>
                  <span className="text-sm text-gray-600">{currentAgent.memory}MB</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(currentAgent.memory / 2, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Performance Metrics */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {currentAgent.metrics.map((metric, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
                  <div className="text-sm text-gray-600 mb-1">{metric.label}</div>
                  <div className="text-lg">{getTrendIcon(metric.trend)}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Responsibilities */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Responsibilities</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {currentAgent.responsibilities.map((responsibility, index) => (
                <div key={index} className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mr-3"></div>
                  {responsibility}
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-3">
              {currentAgent.recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    activity.status === 'success' ? 'bg-green-400' :
                    activity.status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                  }`}></div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{activity.action}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    activity.status === 'success' ? 'bg-green-100 text-green-700' :
                    activity.status === 'warning' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {activity.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAgents;