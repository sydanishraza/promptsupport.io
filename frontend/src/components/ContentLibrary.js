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
import PromptSupportEditor from './PromptSupportEditor';
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
  
  // State for actual asset count  
  const [actualAssetCount, setActualAssetCount] = useState(0);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [articlesPerPage] = useState(20);
  const [totalArticles, setTotalArticles] = useState(0);
  
  // State for asset pagination
  const [assetPagination, setAssetPagination] = useState(null);
  
  // State for asset filters
  const [assetSearchQuery, setAssetSearchQuery] = useState('');
  const [assetFilterType, setAssetFilterType] = useState('all');
  const [assetSortBy, setAssetSortBy] = useState('dateAdded');
  const [assetSortOrder, setAssetSortOrder] = useState('desc');
  const [assetViewMode, setAssetViewMode] = useState('grid');

  // Get backend URL
  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Calculate actual asset count from articles
  useEffect(() => {
    let totalAssets = 0;
    
    articles.forEach(article => {
      if (article.content && article.content.includes('data:image')) {
        // Count markdown format images
        const markdownImages = (article.content.match(/!\[([^\]]*)\]\(data:image\/([^;]+);base64,([^)]+)\)/g) || []);
        // Count HTML format images  
        const htmlImages = (article.content.match(/<img[^>]*src="data:image\/([^;]+);base64,([^"]+)"[^>]*>/g) || []);
        
        // Filter out truncated images (less than 50 chars)
        const validMarkdownImages = markdownImages.filter(img => {
          const match = img.match(/base64,([^)]+)/);
          return match && match[1].length >= 50;
        });
        
        const validHtmlImages = htmlImages.filter(img => {
          const match = img.match(/base64,([^"]+)/);
          return match && match[1].length >= 50;
        });
        
        totalAssets += validMarkdownImages.length + validHtmlImages.length;
      }
    });
    
    setActualAssetCount(totalAssets);
  }, [articles]);

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

  // Filter and sort articles with pagination
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

    // Update total count
    setTotalArticles(filtered.length);

    // Apply pagination
    const startIndex = (currentPage - 1) * articlesPerPage;
    const endIndex = startIndex + articlesPerPage;
    return filtered.slice(startIndex, endIndex);
  }, [articles, searchQuery, selectedFilter, selectedSort, currentPage, articlesPerPage]);

  // Calculate pagination info
  const totalPages = Math.ceil(totalArticles / articlesPerPage);
  const startArticle = (currentPage - 1) * articlesPerPage + 1;
  const endArticle = Math.min(startArticle + articlesPerPage - 1, totalArticles);

  // Handle page change
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, selectedFilter, selectedSort]);

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

        {/* ModernMediaArticleViewer */}
        <PromptSupportEditor
          article={selectedArticle}
          isEditing={isEditing}
          onEdit={() => setIsEditing(true)}
          onSave={handleSaveArticle}
          onCancel={() => {
            setIsEditMode(false);
            setSelectedArticle(null);
          }}
          onDelete={handleDeleteArticle}
          className="h-full"
        />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-2 sm:space-y-4 max-w-full overflow-hidden p-2 sm:p-3 md:p-0">
      {/* Enhanced Header - Mobile Compact */}
      <div className="bg-white rounded-lg sm:rounded-xl shadow-sm border border-gray-200 p-2 sm:p-3 lg:p-6 flex-shrink-0">
        <div className="flex flex-col space-y-2 sm:space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1 sm:mb-2">
                <h1 className="text-base sm:text-lg lg:text-2xl font-bold text-gray-900">Content Library</h1>
              </div>
              <p className="text-xs sm:text-sm lg:text-base text-gray-600 mb-1 sm:mb-3 hidden sm:block">
                Manage articles and assets.
              </p>
            </div>
            
            {/* Action Buttons - Mobile Compact */}
            <div className="flex flex-row sm:flex-row gap-1.5 sm:gap-2 lg:gap-3 w-full sm:w-auto">
              <button
                onClick={() => fetchArticles()}
                className="flex items-center justify-center sm:justify-start px-2 sm:px-3 py-1.5 sm:py-2.5 md:py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md sm:rounded-lg transition-colors text-xs sm:text-sm flex-1 sm:flex-none"
              >
                <RefreshCw className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                <span className="hidden xs:inline">Refresh</span>
              </button>
              <button
                onClick={() => setShowSnipAndRecord(true)}
                className="flex items-center justify-center sm:justify-start px-2 sm:px-3 py-1.5 sm:py-2.5 md:py-2 bg-green-600 hover:bg-green-700 text-white rounded-md sm:rounded-lg transition-colors text-xs sm:text-sm flex-1 sm:flex-none"
              >
                <Camera className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                <span className="hidden xs:inline">Snip</span>
              </button>
              <button
                onClick={handleCreateArticle}
                className="flex items-center justify-center sm:justify-start px-2 sm:px-3 py-1.5 sm:py-2.5 md:py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md sm:rounded-lg transition-colors text-xs sm:text-sm flex-1 sm:flex-none"
              >
                <Plus className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                <span className="hidden xs:inline">Create</span>
              </button>
            </div>
          </div>
          
          {/* Stats - Mobile Compact */}
          <div className="grid grid-cols-4 sm:flex sm:flex-wrap items-center gap-1 sm:gap-2 lg:gap-4 text-xs text-gray-500">
            <span className="whitespace-nowrap text-center sm:text-left">A: {articles.length}</span>
            <span className="whitespace-nowrap text-center sm:text-left">M: {articles.filter(a => a.content?.includes('data:image')).length}</span>
            <span className="whitespace-nowrap text-center sm:text-left">As: {actualAssetCount}</span>
            <span className="whitespace-nowrap text-center sm:text-left">P: {articles.filter(a => a.status === 'published').length}</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation - Mobile Compact */}
      <div className="flex space-x-2 sm:space-x-4 lg:space-x-6 border-b border-gray-200 overflow-x-auto flex-shrink-0 px-2 sm:px-3 md:px-0 -mx-2 sm:-mx-3 md:mx-0">
        <button
          onClick={() => setCurrentView('articles')}
          className={`flex items-center space-x-1 sm:space-x-2 pb-2 sm:pb-3 px-1 border-b-2 font-medium whitespace-nowrap text-xs sm:text-sm md:text-base ${
            currentView === 'articles'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <FileText className="h-3 w-3 sm:h-4 sm:w-4" />
          <span>Articles</span>
          <span className="bg-gray-100 text-gray-600 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full text-xs">
            {articles.length}
          </span>
        </button>
        <button
          onClick={() => setCurrentView('assets')}
          className={`flex items-center space-x-1 sm:space-x-2 pb-2 sm:pb-3 px-1 border-b-2 font-medium whitespace-nowrap text-xs sm:text-sm md:text-base ${
            currentView === 'assets'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <FolderOpen className="h-3 w-3 sm:h-4 sm:w-4" />
          <span>Assets</span>
          <span className="bg-gray-100 text-gray-600 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full text-xs">
            {actualAssetCount}
          </span>
        </button>
      </div>

      {/* Control Bar - Articles - Mobile Compact */}
      {currentView === 'articles' && (
        <div className="bg-white rounded-lg sm:rounded-xl shadow-sm border border-gray-200 p-2 sm:p-3 lg:p-4 flex-shrink-0">
          <div className="flex flex-col space-y-2 sm:space-y-3">
            {/* Search - Compact on Mobile */}
            <div className="relative">
              <Search className="absolute left-2 sm:left-3 top-1/2 transform -translate-y-1/2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-7 sm:pl-10 pr-3 sm:pr-4 py-1.5 sm:py-2.5 md:py-2 border border-gray-300 rounded-md sm:rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-full text-xs sm:text-sm md:text-base"
              />
            </div>

            {/* Filters and View - Mobile Compact */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0 sm:space-x-4">
              <div className="flex flex-col sm:flex-row gap-1.5 sm:gap-2 lg:gap-3">
                <div className="relative">
                  <select
                    value={selectedFilter}
                    onChange={(e) => setSelectedFilter(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-md sm:rounded-lg px-2 sm:px-3 py-1.5 sm:py-2.5 md:py-2 pr-6 sm:pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-xs sm:text-sm w-full sm:w-auto"
                  >
                    {filterOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  <Filter className="absolute right-1.5 sm:right-2 top-1/2 transform -translate-y-1/2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400 pointer-events-none" />
                </div>

                <div className="relative">
                  <select
                    value={selectedSort}
                    onChange={(e) => setSelectedSort(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-md sm:rounded-lg px-2 sm:px-3 py-1.5 sm:py-2.5 md:py-2 pr-6 sm:pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-xs sm:text-sm w-full sm:w-auto"
                  >
                    {sortOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        Sort: {option.label}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-1.5 sm:right-2 top-1/2 transform -translate-y-1/2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400 pointer-events-none" />
                </div>
              </div>

              {/* View Mode Selector */}
              <div className="flex items-center gap-1 sm:gap-2">
                <span className="text-xs sm:text-sm text-gray-500 hidden sm:inline">View:</span>
                <div className="relative">
                  <select
                    value={viewMode}
                    onChange={(e) => setViewMode(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-md sm:rounded-lg px-2 sm:px-3 py-1.5 sm:py-2.5 md:py-2 pr-6 sm:pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-xs sm:text-sm w-full sm:w-auto"
                  >
                    {viewOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-1.5 sm:right-2 top-1/2 transform -translate-y-1/2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Control Bar - Assets - Mobile Compact */}
      {currentView === 'assets' && (
        <div className="bg-white rounded-lg sm:rounded-xl shadow-sm border border-gray-200 p-2 sm:p-3 lg:p-4 flex-shrink-0">
          <div className="flex flex-col space-y-2 sm:space-y-3">
            {/* Search - Compact on Mobile */}
            <div className="relative">
              <Search className="absolute left-2 sm:left-3 top-1/2 transform -translate-y-1/2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search assets..."
                value={assetSearchQuery}
                onChange={(e) => setAssetSearchQuery(e.target.value)}
                className="pl-7 sm:pl-10 pr-3 sm:pr-4 py-1.5 sm:py-2.5 md:py-2 border border-gray-300 rounded-md sm:rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-full text-xs sm:text-sm md:text-base"
              />
            </div>

            {/* Filters and View - Mobile Compact */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0 sm:space-x-4">
              <div className="flex flex-col sm:flex-row gap-1.5 sm:gap-2 lg:gap-3">
                <div className="relative">
                  <select
                    value={assetFilterType}
                    onChange={(e) => setAssetFilterType(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-md sm:rounded-lg px-2 sm:px-3 py-1.5 sm:py-2.5 md:py-2 pr-6 sm:pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-xs sm:text-sm w-full sm:w-auto"
                  >
                    <option value="all">All Assets</option>
                    <option value="image">Images</option>
                    <option value="png">PNG</option>
                    <option value="jpeg">JPEG</option>
                    <option value="gif">GIF</option>
                    <option value="svg">SVG</option>
                    <option value="processed">AI Processed</option>
                  </select>
                  <Filter className="absolute right-1.5 sm:right-2 top-1/2 transform -translate-y-1/2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400 pointer-events-none" />
                </div>

                <div className="relative">
                  <select
                    value={assetSortBy}
                    onChange={(e) => setAssetSortBy(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-md sm:rounded-lg px-2 sm:px-3 py-1.5 sm:py-2.5 md:py-2 pr-6 sm:pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-xs sm:text-sm w-full sm:w-auto"
                  >
                    <option value="dateAdded">Sort: Date Added</option>
                    <option value="name">Sort: Name</option>
                    <option value="size">Sort: File Size</option>
                    <option value="format">Sort: Format</option>
                    <option value="articleTitle">Sort: Source Article</option>
                  </select>
                  <ChevronDown className="absolute right-1.5 sm:right-2 top-1/2 transform -translate-y-1/2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400 pointer-events-none" />
                </div>
              </div>

              {/* View Mode Selector */}
              <div className="flex items-center gap-1 sm:gap-2">
                <span className="text-xs sm:text-sm text-gray-500 hidden sm:inline">View:</span>
                <div className="relative">
                  <select
                    value={assetViewMode}
                    onChange={(e) => setAssetViewMode(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-md sm:rounded-lg px-2 sm:px-3 py-1.5 sm:py-2.5 md:py-2 pr-6 sm:pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-xs sm:text-sm w-full sm:w-auto"
                  >
                    <option value="grid">Grid View</option>
                    <option value="list">List View</option>
                  </select>
                  <ChevronDown className="absolute right-1.5 sm:right-2 top-1/2 transform -translate-y-1/2 h-3 w-3 sm:h-4 sm:w-4 text-gray-400 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Content Area - Mobile Optimized */}
      <div className="bg-white rounded-lg sm:rounded-xl shadow-sm border border-gray-200 flex-1 min-h-0 overflow-hidden">
        <div className="h-full overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-24 sm:h-32 md:h-64">
              <div className="animate-spin rounded-full h-4 w-4 sm:h-6 sm:w-6 md:h-8 md:w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : currentView === 'articles' ? (
            <div className="overflow-x-auto">
              {viewMode === 'grid' ? (
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
              )}
            </div>
          ) : (
            <AssetManager
              articles={articles}
              onArticleSelect={handleArticleSelect}
              onPaginationChange={setAssetPagination}
              searchQuery={assetSearchQuery}
              filterType={assetFilterType}
              sortBy={assetSortBy}
              sortOrder={assetSortOrder}
              viewMode={assetViewMode}
            />
          )}
        </div>
      </div>

      {/* Pagination - Articles - Mobile Compact */}
      {currentView === 'articles' && articles.length > 0 && (
        <div className="bg-white rounded-lg sm:rounded-xl shadow-sm border border-gray-200 p-2 sm:p-3 lg:p-4 flex-shrink-0">
          <div className="flex flex-col space-y-2 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-xs text-gray-500 text-center sm:text-left">
              {startArticle}-{endArticle} of {totalArticles}
              {totalPages > 1 && (
                <span className="block sm:inline sm:ml-1">({currentPage}/{totalPages})</span>
              )}
            </div>
            {totalPages > 1 && (
              <div className="flex items-center justify-center space-x-1">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-1.5 sm:px-2 md:px-3 py-1 text-xs sm:text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="hidden sm:inline">Previous</span>
                  <span className="sm:hidden">‹</span>
                </button>
                
                {/* Page numbers - Responsive */}
                <div className="flex items-center space-x-0.5 sm:space-x-1">
                  {[...Array(Math.min(window.innerWidth < 640 ? 3 : 5, totalPages))].map((_, index) => {
                    let pageNum;
                    const maxPages = window.innerWidth < 640 ? 3 : 5;
                    if (totalPages <= maxPages) {
                      pageNum = index + 1;
                    } else if (currentPage <= Math.floor(maxPages/2) + 1) {
                      pageNum = index + 1;
                    } else if (currentPage >= totalPages - Math.floor(maxPages/2)) {
                      pageNum = totalPages - maxPages + 1 + index;
                    } else {
                      pageNum = currentPage - Math.floor(maxPages/2) + index;
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        className={`px-1.5 sm:px-2 md:px-3 py-1 text-xs sm:text-sm rounded transition-colors ${
                          currentPage === pageNum
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-600 hover:bg-gray-100'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-1.5 sm:px-2 md:px-3 py-1 text-xs sm:text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="hidden sm:inline">Next</span>
                  <span className="sm:hidden">›</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Pagination - Assets - Mobile Compact */}
      {currentView === 'assets' && assetPagination && assetPagination.totalPages > 1 && (
        <div className="bg-white rounded-lg sm:rounded-xl shadow-sm border border-gray-200 p-2 sm:p-3 lg:p-4 flex-shrink-0">
          <div className="flex flex-col space-y-2 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-xs text-gray-500 text-center sm:text-left">
              {assetPagination.startIndex}-{assetPagination.endIndex} of {assetPagination.totalItems}
              {assetPagination.totalPages > 1 && (
                <span className="block sm:inline sm:ml-1">({assetPagination.currentPage}/{assetPagination.totalPages})</span>
              )}
            </div>
            {assetPagination.totalPages > 1 && (
              <div className="flex items-center justify-center space-x-1">
                <button
                  onClick={() => assetPagination.onPageChange(assetPagination.currentPage - 1)}
                  disabled={assetPagination.currentPage === 1}
                  className="px-1.5 sm:px-2 md:px-3 py-1 text-xs sm:text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="hidden sm:inline">Previous</span>
                  <span className="sm:hidden">‹</span>
                </button>
                
                {/* Page numbers - Responsive */}
                <div className="flex items-center space-x-0.5 sm:space-x-1">
                  {[...Array(Math.min(window.innerWidth < 640 ? 3 : 5, assetPagination.totalPages))].map((_, index) => {
                    let pageNum;
                    const maxPages = window.innerWidth < 640 ? 3 : 5;
                    if (assetPagination.totalPages <= maxPages) {
                      pageNum = index + 1;
                    } else if (assetPagination.currentPage <= Math.floor(maxPages/2) + 1) {
                      pageNum = index + 1;
                    } else if (assetPagination.currentPage >= assetPagination.totalPages - Math.floor(maxPages/2)) {
                      pageNum = assetPagination.totalPages - maxPages + 1 + index;
                    } else {
                      pageNum = assetPagination.currentPage - Math.floor(maxPages/2) + index;
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => assetPagination.onPageChange(pageNum)}
                        className={`px-1.5 sm:px-2 md:px-3 py-1 text-xs sm:text-sm rounded transition-colors ${
                          assetPagination.currentPage === pageNum
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-600 hover:bg-gray-100'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  onClick={() => assetPagination.onPageChange(assetPagination.currentPage + 1)}
                  disabled={assetPagination.currentPage === assetPagination.totalPages}
                  className="px-1.5 sm:px-2 md:px-3 py-1 text-xs sm:text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="hidden sm:inline">Next</span>
                  <span className="sm:hidden">›</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

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