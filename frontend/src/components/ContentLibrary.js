import React, { useState, useEffect, useMemo } from 'react';
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
  RefreshCw,
  Check,
  Square,
  CheckSquare,
  X,
  Combine,
  FileEdit,
  FileCheck,
  RotateCcw,
  Loader2,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

import TinyMCEEditor from './TinyMCEEditor';
import PromptSupportEditor from './PromptSupportEditor';
import ArticleGrid from './ArticleGrid';
import ArticleTable from './ArticleTable';
import AssetManager from './AssetManager';
import EnhancedAssetManager from './EnhancedAssetManager';
import SnipAndRecord from './SnipAndRecord';
import KnowledgeEngineUpload from './KnowledgeEngineUpload';

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
  const [showKnowledgeUpload, setShowKnowledgeUpload] = useState(false);
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterState, setFilterState] = useState(null); // For context preservation
  
  // NEW: Selection and bulk actions state
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [selectAll, setSelectAll] = useState(false);
  
  // NEW: Bulk action states
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [bulkActionLoading, setBulkActionLoading] = useState(false);
  
  // NEW: Merge functionality state
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [mergeTitle, setMergeTitle] = useState('');
  const [mergeStatus, setMergeStatus] = useState('draft');
  
  // NEW: Rename functionality state
  const [renamingItem, setRenamingItem] = useState(null);
  const [renameTitle, setRenameTitle] = useState('');
  
  // State for actual asset count  
  const [actualAssetCount, setActualAssetCount] = useState(0);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [articlesPerPage] = useState(10); // Reduced from 20 to 10 to show pagination
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

  // NEW: Selection functionality
  const toggleSelection = (itemId) => {
    const newSelection = new Set(selectedItems);
    if (newSelection.has(itemId)) {
      newSelection.delete(itemId);
    } else {
      newSelection.add(itemId);
    }
    setSelectedItems(newSelection);
    setSelectAll(newSelection.size === filteredAndSortedArticles.length);
  };

  const toggleSelectAll = () => {
    if (selectAll) {
      setSelectedItems(new Set());
      setSelectAll(false);
    } else {
      const allIds = new Set(filteredAndSortedArticles.map(article => article.id));
      setSelectedItems(allIds);
      setSelectAll(true);
    }
  };

  const clearSelection = () => {
    setSelectedItems(new Set());
    setSelectAll(false);
    setSelectionMode(false);
  };

  // NEW: Individual status change functionality
  const handleStatusChange = async (articleId, newStatus) => {
    setBulkActionLoading(true);
    try {
      const article = articles.find(a => a.id === articleId);
      const requestData = {
        title: article.title,
        content: article.content,
        status: newStatus,
        tags: article.tags || [],
        metadata: article.metadata || {}
      };

      const response = await fetch(`${backendUrl}/api/content-library/${articleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        await fetchArticles();
        console.log(`Successfully changed article status to ${newStatus}`);
      } else {
        throw new Error('Failed to change article status');
      }
    } catch (error) {
      console.error('Error changing article status:', error);
      alert('Error changing article status. Please try again.');
    } finally {
      setBulkActionLoading(false);
    }
  };

  // NEW: Bulk actions
  const handleBulkDelete = async () => {
    if (!confirm(`Are you sure you want to delete ${selectedItems.size} item(s)?`)) return;

    setBulkActionLoading(true);
    try {
      const deletePromises = Array.from(selectedItems).map(id => 
        fetch(`${backendUrl}/api/content-library/${id}`, { method: 'DELETE' })
      );
      
      await Promise.all(deletePromises);
      await fetchArticles();
      clearSelection();
      console.log(`Successfully deleted ${selectedItems.size} items`);
    } catch (error) {
      console.error('Error deleting items:', error);
      alert('Error deleting some items. Please try again.');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const handleBulkPublish = async () => {
    setBulkActionLoading(true);
    try {
      const updatePromises = Array.from(selectedItems).map(id => {
        const article = articles.find(a => a.id === id);
        const requestData = {
          title: article.title,
          content: article.content,
          status: 'published',
          tags: article.tags || [],
          metadata: article.metadata || {}
        };

        return fetch(`${backendUrl}/api/content-library/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        });
      });
      
      await Promise.all(updatePromises);
      await fetchArticles();
      clearSelection();
      console.log(`Successfully published ${selectedItems.size} items`);
    } catch (error) {
      console.error('Error publishing items:', error);
      alert('Error publishing some items. Please try again.');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const handleBulkDraft = async () => {
    setBulkActionLoading(true);
    try {
      const updatePromises = Array.from(selectedItems).map(id => {
        const article = articles.find(a => a.id === id);
        const requestData = {
          title: article.title,
          content: article.content,
          status: 'draft',
          tags: article.tags || [],
          metadata: article.metadata || {}
        };

        return fetch(`${backendUrl}/api/content-library/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        });
      });
      
      await Promise.all(updatePromises);
      await fetchArticles();
      clearSelection();
      console.log(`Successfully moved ${selectedItems.size} items to draft`);
    } catch (error) {
      console.error('Error moving items to draft:', error);
      alert('Error updating some items. Please try again.');
    } finally {
      setBulkActionLoading(false);
    }
  };

  // NEW: Merge functionality
  const handleMergeArticles = () => {
    if (selectedItems.size < 2) {
      alert('Please select at least 2 articles to merge');
      return;
    }
    setShowMergeModal(true);
  };

  const executeMerge = async () => {
    if (!mergeTitle.trim()) {
      alert('Please enter a title for the merged article');
      return;
    }

    setBulkActionLoading(true);
    try {
      const selectedArticles = articles.filter(a => selectedItems.has(a.id));
      
      // Create merged content
      let mergedContent = `<h1>${mergeTitle}</h1>\n\n`;
      let mergedTags = new Set();
      
      selectedArticles.forEach((article, index) => {
        mergedContent += `<h2>Section ${index + 1}: ${article.title}</h2>\n`;
        mergedContent += article.content.replace(/<h1[^>]*>.*?<\/h1>/gi, '') + '\n\n';
        
        if (article.tags) {
          article.tags.forEach(tag => mergedTags.add(tag));
        }
      });

      // Create new merged article with JSON format
      const requestData = {
        title: mergeTitle,
        content: mergedContent,
        status: mergeStatus,
        tags: [...mergedTags],
        metadata: {
          created_by: 'User',
          merge_source: Array.from(selectedItems),
          merged_at: new Date().toISOString()
        }
      };

      const response = await fetch(`${backendUrl}/api/content-library`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        await fetchArticles();
        clearSelection();
        setShowMergeModal(false);
        setMergeTitle('');
        setMergeStatus('draft');
        console.log(`Successfully merged ${selectedItems.size} articles`);
      } else {
        throw new Error('Failed to create merged article');
      }
    } catch (error) {
      console.error('Error merging articles:', error);
      alert('Error merging articles. Please try again.');
    } finally {
      setBulkActionLoading(false);
    }
  };

  // NEW: Rename functionality
  const startRename = (article) => {
    setRenamingItem(article.id);
    setRenameTitle(article.title || '');
  };

  const executeRename = async (articleId) => {
    if (!renameTitle.trim()) {
      alert('Please enter a valid title');
      return;
    }

    setBulkActionLoading(true);
    try {
      const article = articles.find(a => a.id === articleId);
      const requestData = {
        title: renameTitle.trim(),
        content: article.content,
        status: article.status,
        tags: article.tags || [],
        metadata: article.metadata || {}
      };

      const response = await fetch(`${backendUrl}/api/content-library/${articleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        await fetchArticles();
        setRenamingItem(null);
        setRenameTitle('');
        console.log('Successfully renamed article');
      } else {
        throw new Error('Failed to rename article');
      }
    } catch (error) {
      console.error('Error renaming article:', error);
      alert('Error renaming article. Please try again.');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const cancelRename = () => {
    setRenamingItem(null);
    setRenameTitle('');
  };

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

  // Download PDF function
  const downloadArticlePDF = async (articleId, articleTitle) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/content-library/article/${articleId}/download-pdf`);
      
      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }
      
      // Create blob from response
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${articleTitle.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      console.log('PDF downloaded successfully');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF. Please try again.');
    }
  };

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
    // Remove auto-refresh to prevent unexpected reloads
  }, [backendUrl]);

  // Handle article selection for viewing
  const handleArticleSelect = (article) => {
    setFilterState({ searchQuery, selectedFilter, selectedSort, viewMode }); // Save current state
    setSelectedArticle(article);
    setIsEditing(false);
  };

  // Handle article selection for editing
  const handleArticleEdit = (article) => {
    setFilterState({ searchQuery, selectedFilter, selectedSort, viewMode }); // Save current state
    setSelectedArticle(article);
    setIsEditing(true);
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
      
      const requestData = {
        title: articleData.title,
        content: articleData.content,
        status: articleData.status || 'draft',
        tags: articleData.tags || [],
        metadata: articleData.metadata || {}
      };

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        await fetchArticles();
        setIsEditing(false);
        // Navigate back to Content Library after save
        handleBackToLibrary();
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

  // Enhanced filter and sort articles with improved search
  const filteredAndSortedArticles = useMemo(() => {
    let filtered = articles.filter(article => {
      // Enhanced search filter with title prioritization
      if (searchQuery) {
        const searchLower = searchQuery.toLowerCase();
        const titleMatch = article.title?.toLowerCase().includes(searchLower);
        const contentMatch = article.content?.toLowerCase().includes(searchLower);
        const tagMatch = article.tags?.some(tag => tag.toLowerCase().includes(searchLower));
        
        // Return true if any match is found
        if (!titleMatch && !contentMatch && !tagMatch) {
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

    // Enhanced sort with title prioritization when searching
    filtered.sort((a, b) => {
      // If searching, prioritize title matches
      if (searchQuery) {
        const searchLower = searchQuery.toLowerCase();
        const aTitleMatch = a.title?.toLowerCase().includes(searchLower);
        const bTitleMatch = b.title?.toLowerCase().includes(searchLower);
        
        if (aTitleMatch && !bTitleMatch) return -1;
        if (!aTitleMatch && bTitleMatch) return 1;
      }

      // Apply regular sorting
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
            setIsEditing(false);
            handleBackToLibrary();
          }}
          onDelete={handleDeleteArticle}
          className="h-full"
        />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-1 max-w-full overflow-hidden">
      {/* Optimized Header - Compact */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-lg font-bold text-gray-900">Content Library</h1>
            <div className="flex items-center space-x-3 text-xs text-gray-500">
              <span>A: {articles.length}</span>
              <span>M: {articles.filter(a => a.content?.includes('data:image')).length}</span>
              <span>As: {actualAssetCount}</span>
              <span>P: {articles.filter(a => a.status === 'published').length}</span>
            </div>
          </div>
          
          {/* Action Buttons - Compact */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => fetchArticles()}
              className="flex items-center px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </button>
            <button
              onClick={() => setShowKnowledgeUpload(true)}
              className="flex items-center px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors text-sm"
            >
              <FileText className="h-4 w-4 mr-2" />
              Upload
            </button>
            <button
              onClick={() => setShowSnipAndRecord(true)}
              className="flex items-center px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors text-sm"
            >
              <Camera className="h-4 w-4 mr-2" />
              Snip
            </button>
            <button
              onClick={handleCreateArticle}
              className="flex items-center px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation - Compact */}
      <div className="flex space-x-6 border-b border-gray-200 flex-shrink-0 px-3">
        <button
          onClick={() => setCurrentView('articles')}
          className={`flex items-center space-x-2 pb-3 px-1 border-b-2 font-medium whitespace-nowrap text-sm ${
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
          className={`flex items-center space-x-2 pb-3 px-1 border-b-2 font-medium whitespace-nowrap text-sm ${
            currentView === 'assets'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <FolderOpen className="h-4 w-4" />
          <span>Assets</span>
          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
            {actualAssetCount}
          </span>
        </button>
      </div>

      {/* Enhanced Control Bar with Selection */}
      {currentView === 'articles' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 flex-shrink-0">
          <div className="space-y-3">
            {/* Search and Selection Toggle */}
            <div className="flex items-center justify-between gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search articles by title, content, or tags..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-full text-sm"
                />
              </div>
              
              <button
                onClick={() => {
                  setSelectionMode(!selectionMode);
                  if (selectionMode) clearSelection();
                }}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                  selectionMode 
                    ? 'bg-blue-100 text-blue-700 hover:bg-blue-200' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {selectionMode ? <CheckSquare className="h-4 w-4" /> : <Square className="h-4 w-4" />}
                <span>{selectionMode ? 'Exit Select' : 'Select'}</span>
              </button>
            </div>

            {/* Selection and Bulk Actions Bar */}
            {selectionMode && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={toggleSelectAll}
                      className="flex items-center space-x-2 text-sm font-medium text-blue-700"
                    >
                      {selectAll ? <CheckSquare className="h-4 w-4" /> : <Square className="h-4 w-4" />}
                      <span>{selectAll ? 'Deselect All' : 'Select All'}</span>
                    </button>
                    <span className="text-sm text-blue-600">
                      {selectedItems.size} of {filteredAndSortedArticles.length} selected
                    </span>
                  </div>

                  {selectedItems.size > 0 && (
                    <div className="flex items-center space-x-2">
                      {bulkActionLoading && (
                        <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
                      )}
                      
                      <button
                        onClick={handleBulkPublish}
                        disabled={bulkActionLoading}
                        className="flex items-center space-x-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm"
                      >
                        <FileCheck className="h-4 w-4" />
                        <span>Publish</span>
                      </button>
                      
                      <button
                        onClick={handleBulkDraft}
                        disabled={bulkActionLoading}
                        className="flex items-center space-x-1 px-3 py-1.5 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 text-sm"
                      >
                        <FileEdit className="h-4 w-4" />
                        <span>Draft</span>
                      </button>
                      
                      {selectedItems.size >= 2 && (
                        <button
                          onClick={handleMergeArticles}
                          disabled={bulkActionLoading}
                          className="flex items-center space-x-1 px-3 py-1.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 text-sm"
                        >
                          <Combine className="h-4 w-4" />
                          <span>Merge</span>
                        </button>
                      )}
                      
                      <button
                        onClick={handleBulkDelete}
                        disabled={bulkActionLoading}
                        className="flex items-center space-x-1 px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 text-sm"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>Delete</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Filters and View */}
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <select
                    value={selectedFilter}
                    onChange={(e) => setSelectedFilter(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  >
                    {filterOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  <Filter className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                </div>

                <div className="relative">
                  <select
                    value={selectedSort}
                    onChange={(e) => setSelectedSort(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  >
                    {sortOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        Sort: {option.label}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                </div>
              </div>

              {/* View Mode Selector */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">View:</span>
                <div className="relative">
                  <select
                    value={viewMode}
                    onChange={(e) => setViewMode(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  >
                    {viewOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Control Bar - Assets */}
      {currentView === 'assets' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 flex-shrink-0">
          <div className="space-y-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search assets by name, type, or source..."
                value={assetSearchQuery}
                onChange={(e) => setAssetSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-full text-sm"
              />
            </div>

            {/* Filters and View */}
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <select
                    value={assetFilterType}
                    onChange={(e) => setAssetFilterType(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  >
                    <option value="all">All Assets</option>
                    <option value="image">Images</option>
                    <option value="png">PNG</option>
                    <option value="jpeg">JPEG</option>
                    <option value="gif">GIF</option>
                    <option value="svg">SVG</option>
                    <option value="processed">AI Processed</option>
                  </select>
                  <Filter className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                </div>

                <div className="relative">
                  <select
                    value={assetSortBy}
                    onChange={(e) => setAssetSortBy(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  >
                    <option value="dateAdded">Sort: Date Added</option>
                    <option value="name">Sort: Name</option>
                    <option value="size">Sort: File Size</option>
                    <option value="format">Sort: Format</option>
                    <option value="articleTitle">Sort: Source Article</option>
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                </div>
              </div>

              {/* View Mode Selector */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">View:</span>
                <div className="relative">
                  <select
                    value={assetViewMode}
                    onChange={(e) => setAssetViewMode(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  >
                    <option value="grid">Grid View</option>
                    <option value="list">List View</option>
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Maximized Content Area */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex-1 min-h-0 overflow-hidden">
        <div className="h-full overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : currentView === 'articles' ? (
            <>
              {viewMode === 'grid' ? (
                <ArticleGrid 
                  articles={filteredAndSortedArticles}
                  onArticleSelect={handleArticleSelect}
                  onArticleEdit={handleArticleEdit}
                  onDeleteArticle={handleDeleteArticle}
                  onDownloadPDF={downloadArticlePDF}
                  selectionMode={selectionMode}
                  selectedItems={selectedItems}
                  onToggleSelection={toggleSelection}
                  onStartRename={startRename}
                  renamingItem={renamingItem}
                  renameTitle={renameTitle}
                  setRenameTitle={setRenameTitle}
                  onExecuteRename={executeRename}
                  onCancelRename={cancelRename}
                  onStatusChange={handleStatusChange}
                  bulkActionLoading={bulkActionLoading}
                />
              ) : (
                <ArticleTable 
                  articles={filteredAndSortedArticles}
                  onArticleSelect={handleArticleSelect}
                  onArticleEdit={handleArticleEdit}
                  onDeleteArticle={handleDeleteArticle}
                  onDownloadPDF={downloadArticlePDF}
                  selectionMode={selectionMode}
                  selectedItems={selectedItems}
                  onToggleSelection={toggleSelection}
                  onStartRename={startRename}
                  renamingItem={renamingItem}
                  renameTitle={renameTitle}
                  setRenameTitle={setRenameTitle}
                  onExecuteRename={executeRename}
                  onCancelRename={cancelRename}
                  onStatusChange={handleStatusChange}
                  bulkActionLoading={bulkActionLoading}
                />
              )}
            </>
          ) : (
            <EnhancedAssetManager 
              articles={articles}
              onArticleSelect={handleArticleSelect}
              searchQuery={assetSearchQuery}
              filterType={assetFilterType}
              sortBy={assetSortBy}
              sortOrder={assetSortOrder}
              viewMode={assetViewMode}
              pagination={assetPagination}
              setPagination={setAssetPagination}
            />
          )}
        </div>
      </div>

      {/* Pagination */}
      {currentView === 'articles' && totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200">
          <div className="text-sm text-gray-700">
            Showing {startArticle} to {endArticle} of {totalArticles} articles
          </div>
          <div className="flex items-center space-x-1">
            <button
              onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum)}
                  className={`px-3 py-1 text-sm border rounded-md ${
                    currentPage === pageNum
                      ? 'border-blue-500 bg-blue-50 text-blue-600'
                      : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
            
            <button
              onClick={() => handlePageChange(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Merge Modal */}
      <AnimatePresence>
        {showMergeModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowMergeModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl p-6 w-full max-w-md"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Merge Articles</h3>
                <button
                  onClick={() => setShowMergeModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-3">
                  You're merging {selectedItems.size} articles into a new combined article.
                </p>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Merged Article Title
                    </label>
                    <input
                      type="text"
                      value={mergeTitle}
                      onChange={(e) => setMergeTitle(e.target.value)}
                      placeholder="Enter title for merged article"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Status
                    </label>
                    <select
                      value={mergeStatus}
                      onChange={(e) => setMergeStatus(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="draft">Draft</option>
                      <option value="published">Published</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowMergeModal(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={executeMerge}
                  disabled={bulkActionLoading || !mergeTitle.trim()}
                  className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                >
                  {bulkActionLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                  <span>Merge Articles</span>
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modals */}
      {showSnipAndRecord && (
        <SnipAndRecord onClose={() => setShowSnipAndRecord(false)} />
      )}

      {showKnowledgeUpload && (
        <KnowledgeEngineUpload 
          onClose={() => setShowKnowledgeUpload(false)} 
          onSuccess={() => {
            fetchArticles();
            setShowKnowledgeUpload(false);
          }}
        />
      )}
    </div>
  );
};

export default ContentLibrary;