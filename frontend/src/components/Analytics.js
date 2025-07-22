import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Users, 
  MessageSquare, 
  BookOpen, 
  Target,
  Clock,
  CheckCircle,
  AlertCircle,
  Calendar,
  Download
} from 'lucide-react';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('overview');

  const timeRanges = [
    { id: '24h', label: 'Last 24 Hours' },
    { id: '7d', label: 'Last 7 Days' },
    { id: '30d', label: 'Last 30 Days' },
    { id: '90d', label: 'Last 90 Days' }
  ];

  const overviewMetrics = [
    {
      id: 'kb-usage',
      title: 'Knowledge Base Usage',
      value: '1,205',
      change: '+18%',
      trend: 'up',
      icon: BookOpen,
      color: 'blue',
      description: 'Total article views this period'
    },
    {
      id: 'bot-activity',
      title: 'Chatbot Activity',
      value: '156',
      change: '+23%',
      trend: 'up',
      icon: MessageSquare,
      color: 'green',
      description: 'Conversations handled by AI'
    },
    {
      id: 'ticket-deflection',
      title: 'Ticket Deflection',
      value: '87%',
      change: '+5%',
      trend: 'up',
      icon: Target,
      color: 'purple',
      description: 'Issues resolved without human intervention'
    },
    {
      id: 'user-satisfaction',
      title: 'User Satisfaction',
      value: '4.7/5',
      change: '+0.2',
      trend: 'up',
      icon: Users,
      color: 'orange',
      description: 'Average user rating'
    }
  ];

  const agentPerformance = [
    {
      agent: 'OrchestratorAgent',
      uptime: '99.9%',
      tasksCompleted: 1247,
      avgResponseTime: '45ms',
      errorRate: '0.1%',
      status: 'excellent'
    },
    {
      agent: 'ContentAgent',
      uptime: '99.8%',
      tasksCompleted: 856,
      avgResponseTime: '1.2s',
      errorRate: '0.2%',
      status: 'good'
    },
    {
      agent: 'ChatbotAgent',
      uptime: '100%',
      tasksCompleted: 2341,
      avgResponseTime: '850ms',
      errorRate: '0.05%',
      status: 'excellent'
    },
    {
      agent: 'TicketingAgent',
      uptime: '98.5%',
      tasksCompleted: 412,
      avgResponseTime: '2.1s',
      errorRate: '1.2%',
      status: 'warning'
    },
    {
      agent: 'CommunityAgent',
      uptime: '99.7%',
      tasksCompleted: 234,
      avgResponseTime: '1.8s',
      errorRate: '0.3%',
      status: 'good'
    }
  ];

  const contentCoverage = [
    { category: 'Getting Started', articles: 12, coverage: 85, gaps: 2 },
    { category: 'API Documentation', articles: 18, coverage: 92, gaps: 1 },
    { category: 'Troubleshooting', articles: 8, coverage: 67, gaps: 4 },
    { category: 'Integration Guides', articles: 15, coverage: 78, gaps: 3 },
    { category: 'Best Practices', articles: 6, coverage: 90, gaps: 1 }
  ];

  const chatbotInsights = {
    successRate: 94,
    topIntents: [
      { intent: 'Authentication Help', count: 89, success: 96 },
      { intent: 'API Usage', count: 67, success: 91 },
      { intent: 'Billing Questions', count: 45, success: 88 },
      { intent: 'Technical Support', count: 34, success: 82 },
      { intent: 'Account Management', count: 28, success: 94 }
    ],
    failureReasons: [
      { reason: 'Complex Technical Query', percentage: 35 },
      { reason: 'Missing Documentation', percentage: 28 },
      { reason: 'Ambiguous Request', percentage: 22 },
      { reason: 'Account-Specific Issue', percentage: 15 }
    ]
  };

  const getTrendIcon = (trend) => {
    return trend === 'up' ? 
      <TrendingUp className="h-4 w-4 text-green-500" /> : 
      <TrendingDown className="h-4 w-4 text-red-500" />;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'excellent':
        return 'bg-green-100 text-green-700';
      case 'good':
        return 'bg-blue-100 text-blue-700';
      case 'warning':
        return 'bg-yellow-100 text-yellow-700';
      case 'error':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getMetricColor = (colorName) => {
    const colors = {
      blue: 'from-blue-100 to-blue-200',
      green: 'from-green-100 to-green-200',
      purple: 'from-purple-100 to-purple-200',
      orange: 'from-orange-100 to-orange-200'
    };
    return colors[colorName] || 'from-gray-100 to-gray-200';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Analytics</h1>
            <p className="text-gray-600">
              Performance metrics, insights, and AI feedback loop tracking
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {timeRanges.map(range => (
                <option key={range.id} value={range.id}>{range.label}</option>
              ))}
            </select>
            <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
              <Download size={16} />
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {overviewMetrics.map((metric, index) => (
          <motion.div
            key={metric.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`bg-gradient-to-r ${getMetricColor(metric.color)} rounded-xl p-6`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-sm">
                {React.createElement(metric.icon, { size: 24, className: 'text-gray-700' })}
              </div>
              <div className="flex items-center space-x-1 text-sm font-medium text-gray-700">
                {getTrendIcon(metric.trend)}
                <span>{metric.change}</span>
              </div>
            </div>
            <div>
              <div className="text-3xl font-bold text-gray-900 mb-1">{metric.value}</div>
              <div className="text-sm font-medium text-gray-700 mb-2">{metric.title}</div>
              <div className="text-xs text-gray-600">{metric.description}</div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agent Performance */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Agent Performance</h2>
          <div className="space-y-4">
            {agentPerformance.map((agent, index) => (
              <motion.div
                key={agent.agent}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900">{agent.agent}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(agent.status)}`}>
                    {agent.status}
                  </span>
                </div>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500">Uptime</div>
                    <div className="font-medium text-gray-900">{agent.uptime}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Tasks</div>
                    <div className="font-medium text-gray-900">{agent.tasksCompleted}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Response</div>
                    <div className="font-medium text-gray-900">{agent.avgResponseTime}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Error Rate</div>
                    <div className="font-medium text-gray-900">{agent.errorRate}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Content Coverage */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Content Coverage</h2>
          <div className="space-y-4">
            {contentCoverage.map((category, index) => (
              <motion.div
                key={category.category}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">{category.category}</span>
                  <span className="text-sm text-gray-600">
                    {category.articles} articles • {category.gaps} gaps
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${category.coverage}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Coverage: {category.coverage}%</span>
                  <span className={category.gaps > 2 ? 'text-red-500' : 'text-gray-500'}>
                    {category.gaps} gaps identified
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Chatbot Insights */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Chatbot Success Analysis</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Intents */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Top User Intents</h3>
            <div className="space-y-3">
              {chatbotInsights.topIntents.map((intent, index) => (
                <div key={intent.intent} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{intent.intent}</div>
                    <div className="text-sm text-gray-600">{intent.count} queries • {intent.success}% success</div>
                  </div>
                  <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center">
                    <span className="text-lg">
                      {intent.success >= 95 ? '🎯' : intent.success >= 90 ? '✅' : '⚠️'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Failure Analysis */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Common Failure Reasons</h3>
            <div className="space-y-3">
              {chatbotInsights.failureReasons.map((reason, index) => (
                <div key={reason.reason} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900">{reason.reason}</span>
                    <span className="text-sm text-gray-600">{reason.percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-red-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${reason.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* AI Feedback Loop Tracking */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Feedback Loop Tracking</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <BarChart3 className="h-8 w-8 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">94%</div>
            <div className="text-sm text-gray-600">Learning Accuracy</div>
            <div className="text-xs text-gray-500 mt-1">Improvement from user feedback</div>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">127</div>
            <div className="text-sm text-gray-600">Auto-Improvements</div>
            <div className="text-xs text-gray-500 mt-1">Self-optimizations this month</div>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Clock className="h-8 w-8 text-purple-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">2.3s</div>
            <div className="text-sm text-gray-600">Learning Cycle</div>
            <div className="text-xs text-gray-500 mt-1">Average feedback processing time</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;