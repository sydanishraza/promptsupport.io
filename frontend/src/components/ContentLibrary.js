import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Filter, 
  Plus, 
  Edit, 
  Eye, 
  Tag, 
  FileText, 
  Image,
  Video,
  Mic,
  Bot,
  User,
  Calendar,
  MoreHorizontal
} from 'lucide-react';

const ContentLibrary = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [viewMode, setViewMode] = useState('grid'); // grid or list

  const filters = [
    { id: 'all', label: 'All Content', count: 47 },
    { id: 'articles', label: 'Articles', count: 23 },
    { id: 'assets', label: 'Assets', count: 18 },
    { id: 'recordings', label: 'Recordings', count: 6 }
  ];

  const statusFilters = [
    { id: 'all', label: 'All Status' },
    { id: 'draft', label: 'Draft' },
    { id: 'published', label: 'Published' },
    { id: 'review', label: 'Under Review' }
  ];

  const mockContent = [
    {
      id: 1,
      title: 'Getting Started with PromptSupport',
      type: 'article',
      status: 'published',
      source: 'AI Generated',
      tags: ['onboarding', 'setup', 'guide'],
      wordCount: 1250,
      lastModified: '2024-01-15T10:30:00Z',
      author: 'ContentAgent',
      views: 89,
      preview: 'Learn how to set up and configure PromptSupport for your organization...'
    },
    {
      id: 2,
      title: 'API Authentication Guide',
      type: 'article',
      status: 'draft',
      source: 'User Edited',
      tags: ['api', 'authentication', 'security'],
      wordCount: 850,
      lastModified: '2024-01-14T16:45:00Z',
      author: 'John Doe',
      views: 12,
      preview: 'Complete guide to implementing secure API authentication...'
    },
    {
      id: 3,
      title: 'Product Demo Video',
      type: 'video',
      status: 'published',
      source: 'Uploaded',
      tags: ['demo', 'product', 'walkthrough'],
      duration: '5:42',
      lastModified: '2024-01-13T09:15:00Z',
      author: 'Marketing Team',
      views: 156,
      preview: 'Comprehensive product walkthrough and feature demonstration'
    },
    {
      id: 4,
      title: 'Support Team Recording',
      type: 'audio',
      status: 'review',
      source: 'Recording',
      tags: ['support', 'training', 'internal'],
      duration: '12:30',
      lastModified: '2024-01-12T14:20:00Z',
      author: 'Support Team',
      views: 8,
      preview: 'Training session on handling complex customer inquiries'
    },
    {
      id: 5,
      title: 'Architecture Diagram',
      type: 'image',
      status: 'published',
      source: 'Uploaded',
      tags: ['architecture', 'technical', 'diagram'],
      dimensions: '1920x1080',
      lastModified: '2024-01-11T11:00:00Z',
      author: 'Tech Team',
      views: 34,
      preview: 'System architecture overview and component relationships'
    }
  ];

  const getTypeIcon = (type) => {
    switch (type) {
      case 'article':
        return FileText;
      case 'video':
        return Video;
      case 'audio':
        return Mic;
      case 'image':
        return Image;
      default:
        return FileText;
    }
  };

  const getSourceColor = (source) => {
    switch (source) {
      case 'AI Generated':
        return 'bg-blue-100 text-blue-700';
      case 'User Edited':
        return 'bg-green-100 text-green-700';
      case 'Uploaded':
        return 'bg-purple-100 text-purple-700';
      case 'Recording':
        return 'bg-orange-100 text-orange-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'published':
        return 'bg-green-100 text-green-700';
      case 'draft':
        return 'bg-yellow-100 text-yellow-700';
      case 'review':
        return 'bg-blue-100 text-blue-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const filteredContent = mockContent.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesFilter = selectedFilter === 'all' || 
                         (selectedFilter === 'articles' && item.type === 'article') ||
                         (selectedFilter === 'assets' && ['image', 'video'].includes(item.type)) ||
                         (selectedFilter === 'recordings' && item.type === 'audio');
    const matchesStatus = selectedStatus === 'all' || item.status === selectedStatus;
    
    return matchesSearch && matchesFilter && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Content Library</h1>
            <p className="text-gray-600">
              Manage AI-generated and user-edited articles, assets, and recordings
            </p>
          </div>
          <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
            <Plus size={16} />
            <span>Create Article</span>
          </button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          {/* Search */}
          <div className="relative flex-1 lg:max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="Search articles, tags, or content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center space-x-4">
            <select
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {filters.map(filter => (
                <option key={filter.id} value={filter.id}>
                  {filter.label} ({filter.count})
                </option>
              ))}
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {statusFilters.map(filter => (
                <option key={filter.id} value={filter.id}>
                  {filter.label}
                </option>
              ))}
            </select>

            <div className="flex border border-gray-300 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-gray-100' : ''}`}
              >
                📊
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 ${viewMode === 'list' ? 'bg-gray-100' : ''}`}
              >
                📋
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content Grid/List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">
            Content ({filteredContent.length})
          </h2>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <span>Sort by: Last Modified</span>
          </div>
        </div>

        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContent.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                      {React.createElement(getTypeIcon(item.type), { size: 16, className: 'text-gray-600' })}
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSourceColor(item.source)}`}>
                      {item.source}
                    </span>
                  </div>
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <MoreHorizontal size={16} />
                  </button>
                </div>

                <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">
                  {item.title}
                </h3>
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {item.preview}
                </p>

                <div className="flex flex-wrap gap-1 mb-3">
                  {item.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                  <span>{item.wordCount ? `${item.wordCount} words` : item.duration || item.dimensions}</span>
                  <span>{item.views} views</span>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                      {item.status}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded">
                      <Eye size={14} />
                    </button>
                    <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded">
                      <Edit size={14} />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredContent.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
              >
                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                  {React.createElement(getTypeIcon(item.type), { size: 18, className: 'text-gray-600' })}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3 mb-1">
                    <h3 className="font-medium text-gray-900 truncate">{item.title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                      {item.status}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSourceColor(item.source)}`}>
                      {item.source}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>{item.author}</span>
                    <span>{new Date(item.lastModified).toLocaleDateString()}</span>
                    <span>{item.wordCount ? `${item.wordCount} words` : item.duration || item.dimensions}</span>
                    <span>{item.views} views</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1">
                  {item.tags.slice(0, 2).map(tag => (
                    <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center space-x-1">
                  <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded">
                    <Eye size={16} />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded">
                    <Edit size={16} />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded">
                    <MoreHorizontal size={16} />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentLibrary;