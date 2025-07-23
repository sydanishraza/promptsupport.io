import React, { useState, useMemo } from 'react';
import { 
  Table, 
  Filter, 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown,
  Eye,
  Edit,
  Trash2,
  Calendar,
  FileText,
  Image,
  Bot,
  User,
  Tag,
  CheckCircle,
  XCircle,
  Clock,
  Brain
} from 'lucide-react';

const ContentLibraryTable = ({ 
  articles, 
  onViewArticle, 
  onEditArticle, 
  onDeleteArticle 
}) => {
  const [sortField, setSortField] = useState('updated_at');
  const [sortDirection, setSortDirection] = useState('desc');
  const [filters, setFilters] = useState({
    search: '',
    source: 'all',
    status: 'all',
    dateRange: 'all',
    hasMedia: 'all'
  });

  // Sort function
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Filter and sort articles
  const filteredAndSortedArticles = useMemo(() => {
    let filtered = articles.filter(article => {
      // Search filter
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        if (!article.title?.toLowerCase().includes(searchLower) &&
            !article.content?.toLowerCase().includes(searchLower)) {
          return false;
        }
      }

      // Source filter
      if (filters.source !== 'all' && article.source !== filters.source) {
        return false;
      }

      // Status filter
      if (filters.status !== 'all' && article.status !== filters.status) {
        return false;
      }

      // Media filter
      if (filters.hasMedia !== 'all') {
        const hasMedia = article.content?.includes('data:image') || false;
        if (filters.hasMedia === 'yes' && !hasMedia) return false;
        if (filters.hasMedia === 'no' && hasMedia) return false;
      }

      // Date range filter
      if (filters.dateRange !== 'all') {
        const articleDate = new Date(article.updated_at || article.created_at);
        const now = new Date();
        const daysDiff = (now - articleDate) / (1000 * 60 * 60 * 24);

        switch (filters.dateRange) {
          case 'today':
            if (daysDiff > 1) return false;
            break;
          case 'week':
            if (daysDiff > 7) return false;
            break;
          case 'month':
            if (daysDiff > 30) return false;
            break;
        }
      }

      return true;
    });

    // Sort
    filtered.sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];

      // Handle different data types
      if (sortField === 'updated_at' || sortField === 'created_at') {
        aValue = new Date(aValue || 0);
        bValue = new Date(bValue || 0);
      } else if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue?.toLowerCase() || '';
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [articles, filters, sortField, sortDirection]);

  const getSortIcon = (field) => {
    if (sortField !== field) return <ArrowUpDown className="h-4 w-4 text-gray-400" />;
    return sortDirection === 'asc' 
      ? <ArrowUp className="h-4 w-4 text-blue-600" />
      : <ArrowDown className="h-4 w-4 text-blue-600" />;
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'ai_generated':
        return <Bot className="h-4 w-4 text-purple-600" />;
      case 'manual':
        return <User className="h-4 w-4 text-blue-600" />;
      case 'upload':
        return <FileText className="h-4 w-4 text-green-600" />;
      default:
        return <FileText className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      published: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      draft: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      archived: { color: 'bg-gray-100 text-gray-800', icon: XCircle }
    };

    const config = statusConfig[status] || statusConfig.draft;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="h-3 w-3 mr-1" />
        {status || 'draft'}
      </span>
    );
  };

  const truncateText = (text, maxLength = 60) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Filters Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Table className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Article Table</h3>
            <span className="text-sm text-gray-500">
              ({filteredAndSortedArticles.length} of {articles.length} articles)
            </span>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search articles..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Source</label>
            <select
              value={filters.source}
              onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Sources</option>
              <option value="ai_generated">AI Generated</option>
              <option value="manual">Manual</option>
              <option value="upload">Upload</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Statuses</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
              <option value="archived">Archived</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Date Range</label>
            <select
              value={filters.dateRange}
              onChange={(e) => setFilters(prev => ({ ...prev, dateRange: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Media</label>
            <select
              value={filters.hasMedia}
              onChange={(e) => setFilters(prev => ({ ...prev, hasMedia: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Articles</option>
              <option value="yes">With Media</option>
              <option value="no">No Media</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th 
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('title')}
              >
                <div className="flex items-center space-x-1">
                  <span>Title</span>
                  {getSortIcon('title')}
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('source')}
              >
                <div className="flex items-center space-x-1">
                  <span>Source</span>
                  {getSortIcon('source')}
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('status')}
              >
                <div className="flex items-center space-x-1">
                  <span>Status</span>
                  {getSortIcon('status')}
                </div>
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Media
              </th>
              <th 
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('updated_at')}
              >
                <div className="flex items-center space-x-1">
                  <span>Updated</span>
                  {getSortIcon('updated_at')}
                </div>
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAndSortedArticles.map((article) => {
              const hasMedia = article.content?.includes('data:image') || false;
              const mediaCount = hasMedia ? (article.content?.split('data:image').length - 1) : 0;

              return (
                <tr key={article.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {truncateText(article.title, 50)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {truncateText(article.content?.replace(/<[^>]*>/g, ''), 80)}
                      </div>
                      {article.tags && article.tags.length > 0 && (
                        <div className="flex items-center space-x-1 mt-1">
                          <Tag className="h-3 w-3 text-gray-400" />
                          <span className="text-xs text-gray-500">
                            {article.tags.slice(0, 2).join(', ')}
                            {article.tags.length > 2 && ` +${article.tags.length - 2}`}
                          </span>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center space-x-2">
                      {getSourceIcon(article.source)}
                      <span className="text-sm text-gray-900 capitalize">
                        {article.source || 'manual'}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    {getStatusBadge(article.status)}
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center space-x-2">
                      {hasMedia ? (
                        <>
                          <Image className="h-4 w-4 text-blue-600" />
                          <span className="text-sm text-gray-900">{mediaCount}</span>
                          {article.media_processed && (
                            <Brain className="h-3 w-3 text-purple-600" title="AI Processed" />
                          )}
                        </>
                      ) : (
                        <span className="text-sm text-gray-400">None</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="text-sm text-gray-900">
                      {formatDate(article.updated_at)}
                    </div>
                    <div className="text-xs text-gray-500">
                      v{article.version || 1}
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => onViewArticle(article)}
                        className="p-1 text-gray-400 hover:text-blue-600 rounded"
                        title="View Article"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => onEditArticle(article)}
                        className="p-1 text-gray-400 hover:text-green-600 rounded"
                        title="Edit Article"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => onDeleteArticle && onDeleteArticle(article)}
                        className="p-1 text-gray-400 hover:text-red-600 rounded"
                        title="Delete Article"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredAndSortedArticles.length === 0 && (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No articles match your filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentLibraryTable;