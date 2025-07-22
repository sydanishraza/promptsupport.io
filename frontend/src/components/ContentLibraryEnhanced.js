import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import TiptapEditor from './TiptapEditor';  // Temporarily disabled due to import errors
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
  MoreHorizontal,
  X,
  Save,
  ArrowLeft,
  Settings,
  Trash2,
  Copy,
  ExternalLink
} from 'lucide-react';

const ContentLibraryEnhanced = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [viewMode, setViewMode] = useState('grid');
  const [selectedContent, setSelectedContent] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showNewArticleModal, setShowNewArticleModal] = useState(false);

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
      preview: 'Learn how to set up and configure PromptSupport for your organization...',
      content: `
        <h1>Getting Started with PromptSupport</h1>
        <p>Welcome to PromptSupport, the first fully autonomous, AI-native support platform. This guide will walk you through the setup process and core features.</p>
        <h2>Quick Setup</h2>
        <p>Follow these steps to get started:</p>
        <ol>
          <li><strong>Organization Setup:</strong> Configure your organization name, logo, and subdomain</li>
          <li><strong>Knowledge Upload:</strong> Add your documentation, videos, and other content</li>
          <li><strong>Agent Configuration:</strong> Let our AI agents process and organize your content</li>
        </ol>
        <h2>Key Features</h2>
        <ul>
          <li>AI-powered content processing</li>
          <li>Automated knowledge base generation</li>
          <li>Intelligent chatbot training</li>
          <li>Seamless integrations</li>
        </ul>
      `
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
      preview: 'Complete guide to implementing secure API authentication...',
      content: `
        <h1>API Authentication Guide</h1>
        <p>This guide covers the authentication methods available in PromptSupport's API.</p>
        <h2>API Keys</h2>
        <p>Use API keys for server-to-server authentication:</p>
        <pre><code>Authorization: Bearer your_api_key_here</code></pre>
        <h2>OAuth 2.0</h2>
        <p>For user-based authentication, implement OAuth 2.0 flow.</p>
      `
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
      title: 'Architecture Overview Diagram',
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

  const [newArticle, setNewArticle] = useState({
    title: '',
    content: '',
    tags: [],
    status: 'draft',
    source: 'User Created'
  });

  const getTypeIcon = (type) => {
    switch (type) {
      case 'article': return FileText;
      case 'video': return Video;
      case 'audio': return Mic;
      case 'image': return Image;
      default: return FileText;
    }
  };

  const getSourceColor = (source) => {
    switch (source) {
      case 'AI Generated': return 'bg-blue-100 text-blue-700';
      case 'User Edited': case 'User Created': return 'bg-green-100 text-green-700';
      case 'Uploaded': return 'bg-purple-100 text-purple-700';
      case 'Recording': return 'bg-orange-100 text-orange-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'published': return 'bg-green-100 text-green-700';
      case 'draft': return 'bg-yellow-100 text-yellow-700';
      case 'review': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
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

  const handleEditContent = (content) => {
    setSelectedContent(content);
    setIsEditing(true);
  };

  const handleViewContent = (content) => {
    setSelectedContent(content);
    setIsEditing(false);
  };

  const handleCreateArticle = () => {
    setShowNewArticleModal(true);
  };

  const handleSaveNewArticle = () => {
    console.log('Saving new article:', newArticle);
    setShowNewArticleModal(false);
    setNewArticle({ title: '', content: '', tags: [], status: 'draft', source: 'User Created' });
  };

  const renderContentEditor = () => (
    <div className="fixed inset-0 bg-white z-50 overflow-y-auto">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => {setSelectedContent(null); setIsEditing(false);}}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {isEditing ? 'Edit Article' : 'View Article'}
              </h1>
              <p className="text-gray-600">{selectedContent.title}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
              >
                <Edit size={16} />
                <span>Edit</span>
              </button>
            )}
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg">
              <MoreHorizontal size={20} />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="mb-6">
              <input
                type="text"
                value={selectedContent.title}
                className="w-full text-3xl font-bold border-none focus:outline-none bg-transparent"
                placeholder="Article title..."
                readOnly={!isEditing}
              />
            </div>
            
            {/* Temporary placeholder for TiptapEditor */}
            <div className="border border-gray-300 rounded-lg p-4 bg-gray-50 min-h-[600px]">
              <div className="text-gray-500 text-center">
                <p className="text-lg mb-2">Rich Text Editor</p>
                <p className="text-sm">TiptapEditor temporarily disabled</p>
                {isEditing ? (
                  <textarea 
                    className="w-full h-96 p-4 mt-4 border rounded"
                    value={selectedContent.content || ''}
                    onChange={(e) => setSelectedContent(prev => ({...prev, content: e.target.value}))}
                    placeholder="Edit content here..."
                  />
                ) : (
                  <div className="mt-4 p-4 bg-white rounded border text-left">
                    {selectedContent.content || 'No content available'}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3">Article Info</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Status:</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedContent.status)}`}>
                    {selectedContent.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Source:</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSourceColor(selectedContent.source)}`}>
                    {selectedContent.source}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Words:</span>
                  <span className="text-gray-900">{selectedContent.wordCount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Views:</span>
                  <span className="text-gray-900">{selectedContent.views}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Author:</span>
                  <span className="text-gray-900">{selectedContent.author}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Modified:</span>
                  <span className="text-gray-900">{new Date(selectedContent.lastModified).toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3">Tags</h3>
              <div className="flex flex-wrap gap-1">
                {selectedContent.tags.map(tag => (
                  <span key={tag} className="px-2 py-1 bg-white text-gray-700 text-xs rounded-full border">
                    {tag}
                  </span>
                ))}
                {isEditing && (
                  <button className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full border border-blue-200">
                    + Add Tag
                  </button>
                )}
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3">Actions</h3>
              <div className="space-y-2">
                <button className="w-full flex items-center space-x-2 p-2 text-left hover:bg-white rounded-lg text-sm">
                  <Copy size={16} />
                  <span>Duplicate</span>
                </button>
                <button className="w-full flex items-center space-x-2 p-2 text-left hover:bg-white rounded-lg text-sm">
                  <ExternalLink size={16} />
                  <span>Preview</span>
                </button>
                <button className="w-full flex items-center space-x-2 p-2 text-left hover:bg-white rounded-lg text-sm text-red-600">
                  <Trash2 size={16} />
                  <span>Delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNewArticleModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden"
      >
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Create New Article</h2>
          <button
            onClick={() => setShowNewArticleModal(false)}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 max-h-96 overflow-y-auto">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
              <input
                type="text"
                value={newArticle.title}
                onChange={(e) => setNewArticle(prev => ({...prev, title: e.target.value}))}
                placeholder="Enter article title..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Content</label>
              <TiptapEditor
                content={newArticle.content}
                onChange={(content) => setNewArticle(prev => ({...prev, content}))}
                height="300px"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  value={newArticle.status}
                  onChange={(e) => setNewArticle(prev => ({...prev, status: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="draft">Draft</option>
                  <option value="review">Under Review</option>
                  <option value="published">Published</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
                <input
                  type="text"
                  placeholder="Add tags (comma separated)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
          <button
            onClick={() => setShowNewArticleModal(false)}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={handleSaveNewArticle}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
          >
            <Save size={16} />
            <span>Create Article</span>
          </button>
        </div>
      </motion.div>
    </div>
  );

  if (selectedContent) {
    return renderContentEditor();
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Content Library</h1>
            <p className="text-gray-600">
              Manage AI-generated and user-edited articles, assets, and recordings with Tiptap editor
            </p>
          </div>
          <button 
            onClick={handleCreateArticle}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            <Plus size={16} />
            <span>Create Article</span>
          </button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
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
        </div>

        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContent.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors cursor-pointer"
                onClick={() => item.type === 'article' ? handleViewContent(item) : null}
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
                  <div className="flex items-center space-x-1">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewContent(item);
                      }}
                      className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                    >
                      <Eye size={14} />
                    </button>
                    {item.type === 'article' && (
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditContent(item);
                        }}
                        className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                      >
                        <Edit size={14} />
                      </button>
                    )}
                  </div>
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

                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                    {item.status}
                  </span>
                  <div className="text-xs text-gray-500">
                    {item.wordCount ? `${item.wordCount} words` : item.duration || item.dimensions}
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
                className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors cursor-pointer"
                onClick={() => item.type === 'article' ? handleViewContent(item) : null}
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
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>{item.author}</span>
                    <span>{new Date(item.lastModified).toLocaleDateString()}</span>
                    <span>{item.wordCount ? `${item.wordCount} words` : item.duration || item.dimensions}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-1">
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewContent(item);
                    }}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                  >
                    <Eye size={16} />
                  </button>
                  {item.type === 'article' && (
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditContent(item);
                      }}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                    >
                      <Edit size={16} />
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      <AnimatePresence>
        {showNewArticleModal && renderNewArticleModal()}
      </AnimatePresence>
    </div>
  );
};

export default ContentLibraryEnhanced;