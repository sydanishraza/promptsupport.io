import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  Filter, 
  ChevronDown,
  Grid3X3,
  Table,
  Plus,
  Camera,
  ArrowLeft,
  FileText,
  Image,
  Video,
  Mic,
  FolderOpen,
  Calendar,
  User,
  Tag,
  Eye,
  Edit,
  Trash2,
  Copy,
  MoreVertical,
  Settings,
  RefreshCw
} from 'lucide-react';

import TinyMCEEditor from './TinyMCEEditor';
import ArticleGrid from './ArticleGrid';
import ArticleTable from './ArticleTable';
import AssetManager from './AssetManager';
import SnipAndRecord from './SnipAndRecord';

const ContentLibrary = () => {
  // State management
  const [currentView, setCurrentView] = useState('articles'); // 'articles' or 'assets'
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'table'
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedSort, setSelectedSort] = useState('date_processed');
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSnipAndRecord, setShowSnipAndRecord] = useState(false);
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterState, setFilterState] = useState(null); // For context preservation

  // Get backend URL
  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Filter options
  const filterOptions = [
    { value: 'all', label: 'All Articles' },
    { value: 'published', label: 'Published' },
    { value: 'draft', label: 'Draft' },
    { value: 'review', label: 'Under Review' },
    { value: 'ai_generated', label: 'AI Generated' },
    { value: 'manual', label: 'Manual' },
    { value: 'with_media', label: 'With Media' },
    { value: 'recent', label: 'Recent (7 days)' }
  ];

  // Sort options
  const sortOptions = [
    { value: 'date_processed', label: 'Date Processed' },
    { value: 'title', label: 'Title A-Z' },
    { value: 'title_desc', label: 'Title Z-A' },
    { value: 'status', label: 'Status' },
    { value: 'created_by', label: 'Created By' },
    { value: 'last_updated', label: 'Last Updated' }
  ];

  // View options
  const viewOptions = [
    { value: 'grid', label: 'Grid View', icon: Grid3X3 },
    { value: 'table', label: 'Table View', icon: Table }
  ];

  // Fetch articles from backend
  const fetchArticles = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/content-library`);
      if (response.ok) {
        const data = await response.json();
        setArticles(data.articles || []);
      } else {
        console.error('Failed to fetch articles:', response.status);
      }
    } catch (error) {
      console.error('Error fetching articles:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
    // Refresh every 30 seconds
    const interval = setInterval(fetchArticles, 30000);
    return () => clearInterval(interval);
  }, [backendUrl]);

  // Handle article selection
  const handleArticleSelect = (article) => {
    setFilterState({ searchQuery, selectedFilter, selectedSort, viewMode }); // Save current state
    setSelectedArticle(article);
    setIsEditing(false);
  };

  // Handle back to library
  const handleBackToLibrary = () => {
    setSelectedArticle(null);
    setIsEditing(false);
    // Restore previous filter state if it exists
    if (filterState) {
      setSearchQuery(filterState.searchQuery);
      setSelectedFilter(filterState.selectedFilter);
      setSelectedSort(filterState.selectedSort);
      setViewMode(filterState.viewMode);
      setFilterState(null);
    }
  };

  // Handle article creation
  const handleCreateArticle = () => {
    setFilterState({ searchQuery, selectedFilter, selectedSort, viewMode });
    setSelectedArticle({
      id: null,
      title: '',
      content: '',
      status: 'draft',
      tags: [],
      metadata: {}
    });
    setIsEditing(true);
    setShowCreateModal(false);
  };

  // Handle article save
  const handleSaveArticle = async (articleData) => {
    try {
      const url = articleData.id 
        ? `${backendUrl}/api/content-library/${articleData.id}`
        : `${backendUrl}/api/content-library`;
      
      const method = articleData.id ? 'PUT' : 'POST';
      
      const formData = new FormData();
      formData.append('title', articleData.title);
      formData.append('content', articleData.content);
      formData.append('status', articleData.status || 'draft');
      formData.append('tags', JSON.stringify(articleData.tags || []));
      formData.append('metadata', JSON.stringify(articleData.metadata || {}));

      const response = await fetch(url, {
        method,
        body: formData
      });

      if (response.ok) {
        await fetchArticles();
        setIsEditing(false);
        return true;
      } else {
        console.error('Failed to save article');
        return false;
      }
    } catch (error) {
      console.error('Error saving article:', error);
      return false;
    }
  };

  // Handle article deletion
  const handleDeleteArticle = async (articleId) => {
    if (!confirm('Are you sure you want to delete this article?')) return;

    try {
      const response = await fetch(`${backendUrl}/api/content-library/${articleId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await fetchArticles();
        if (selectedArticle && selectedArticle.id === articleId) {
          handleBackToLibrary();
        }
      } else {
        console.error('Failed to delete article');
      }
    } catch (error) {
      console.error('Error deleting article:', error);
    }
  };

  // Filter and sort articles
  const filteredAndSortedArticles = React.useMemo(() => {
    let filtered = articles.filter(article => {
      // Search filter
      if (searchQuery) {
        const searchLower = searchQuery.toLowerCase();
        if (!article.title?.toLowerCase().includes(searchLower) &&
            !article.content?.toLowerCase().includes(searchLower) &&
            !article.tags?.some(tag => tag.toLowerCase().includes(searchLower))) {
          return false;
        }
      }

      // Status and type filters
      switch (selectedFilter) {
        case 'published':
          return article.status === 'published';
        case 'draft':
          return article.status === 'draft';
        case 'review':
          return article.status === 'review';
        case 'ai_generated':
          return article.source_type !== 'manual';
        case 'manual':
          return article.source_type === 'manual';
        case 'with_media':
          return article.content?.includes('data:image');
        case 'recent':
          const weekAgo = new Date();
          weekAgo.setDate(weekAgo.getDate() - 7);
          return new Date(article.updated_at || article.created_at) > weekAgo;
        default:
          return true;
      }
    });

    // Sort articles
    filtered.sort((a, b) => {
      switch (selectedSort) {
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        case 'title_desc':
          return (b.title || '').localeCompare(a.title || '');
        case 'status':
          return (a.status || '').localeCompare(b.status || '');
        case 'created_by':
          return (a.metadata?.created_by || '').localeCompare(b.metadata?.created_by || '');
        case 'last_updated':
          return new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at);
        case 'date_processed':
        default:
          return new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at);
      }
    });

    return filtered;
  }, [articles, searchQuery, selectedFilter, selectedSort]);

  // If viewing/editing an article, show the editor
  if (selectedArticle) {
    return (
      <div className="h-full">
        {/* Breadcrumb Navigation */}
        <div className="mb-4 flex items-center space-x-2 text-sm text-gray-600">
          <button
            onClick={handleBackToLibrary}
            className="flex items-center space-x-1 text-blue-600 hover:text-blue-800"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Library</span>
          </button>
          <span>•</span>
          <span>{currentView === 'articles' ? 'Articles' : 'Assets'}</span>
          <span>•</span>
          <span>{selectedArticle.title || 'New Article'}</span>
        </div>

        {/* TinyMCE Editor */}
        <TinyMCEEditor
          article={selectedArticle}
          isEditing={isEditing}
          onEdit={() => setIsEditing(true)}
          onSave={handleSaveArticle}
          onCancel={() => setIsEditing(false)}
          onDelete={() => handleDeleteArticle(selectedArticle.id)}
          backendUrl={backendUrl}
        />
      </div>
    );
  }

  return (
    <div className="h-full space-y-4 max-w-full overflow-hidden">
      {/* Enhanced Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 lg:p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h1 className="text-xl lg:text-2xl font-bold text-gray-900">Content Library</h1>
              <span className="text-gray-400 hidden sm:inline">•</span>
              <span className="text-gray-600 hidden sm:inline">CMS Dashboard</span>
            </div>
            <p className="text-sm lg:text-base text-gray-600 mb-3">
              Manage AI-generated and user-edited articles, assets, and recordings with professional CMS workflows
            </p>
            <div className="flex flex-wrap items-center gap-2 lg:gap-4 text-xs lg:text-sm text-gray-500">
              <span>Total Articles: {articles.length}</span>
              <span className="hidden sm:inline">•</span>
              <span>With Media: {articles.filter(a => a.content?.includes('data:image')).length}</span>
              <span className="hidden sm:inline">•</span>
              <span>Published: {articles.filter(a => a.status === 'published').length}</span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 lg:gap-3">
            <button
              onClick={() => fetchArticles()}
              className="flex items-center px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm"
            >
              <RefreshCw className="h-4 w-4 mr-1 lg:mr-2" />
              <span className="hidden sm:inline">Refresh</span>
            </button>
            <button
              onClick={() => setShowSnipAndRecord(true)}
              className="flex items-center px-3 lg:px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors text-sm"
            >
              <Camera className="h-4 w-4 mr-1 lg:mr-2" />
              <span className="hidden sm:inline">Snip & Record</span>
            </button>
            <button
              onClick={handleCreateArticle}
              className="flex items-center px-3 lg:px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm"
            >
              <Plus className="h-4 w-4 mr-1 lg:mr-2" />
              <span className="hidden sm:inline">Create Article</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-6 border-b border-gray-200">
        <button
          onClick={() => setCurrentView('articles')}
          className={`flex items-center space-x-2 pb-3 px-1 border-b-2 font-medium ${
            currentView === 'articles'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <FileText className="h-4 w-4" />
          <span>Articles</span>
          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
            {articles.length}
          </span>
        </button>
        <button
          onClick={() => setCurrentView('assets')}
          className={`flex items-center space-x-2 pb-3 px-1 border-b-2 font-medium ${
            currentView === 'assets'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <FolderOpen className="h-4 w-4" />
          <span>Assets</span>
          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
            {articles.filter(a => a.content?.includes('data:image')).length}
          </span>
        </button>
      </div>

      {/* Control Bar */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search articles, tags, or content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
              />
            </div>

            {/* Filter Dropdown */}
            <div className="relative">
              <select
                value={selectedFilter}
                onChange={(e) => setSelectedFilter(e.target.value)}
                className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {filterOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <Filter className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
            </div>

            {/* Sort Dropdown */}
            <div className="relative">
              <select
                value={selectedSort}
                onChange={(e) => setSelectedSort(e.target.value)}
                className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    Sort by {option.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {/* View Mode Selector */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500 mr-2">View:</span>
            <div className="flex bg-gray-100 rounded-lg p-1">
              {viewOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => setViewMode(option.value)}
                  className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                    viewMode === option.value
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <option.icon className="h-4 w-4" />
                  <span>{option.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 min-h-96">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : currentView === 'articles' ? (
          viewMode === 'grid' ? (
            <ArticleGrid
              articles={filteredAndSortedArticles}
              onArticleSelect={handleArticleSelect}
              onDeleteArticle={handleDeleteArticle}
            />
          ) : (
            <ArticleTable
              articles={filteredAndSortedArticles}
              onArticleSelect={handleArticleSelect}
              onDeleteArticle={handleDeleteArticle}
            />
          )
        ) : (
          <AssetManager
            articles={filteredAndSortedArticles}
            onArticleSelect={handleArticleSelect}
          />
        )}
      </div>

      {/* Snip and Record Modal */}
      <SnipAndRecord
        isOpen={showSnipAndRecord}
        onClose={() => setShowSnipAndRecord(false)}
        onCapture={(formData) => {
          // Handle captured media
          setShowSnipAndRecord(false);
          fetchArticles();
        }}
      />
    </div>
  );
};

export default ContentLibrary;