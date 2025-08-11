import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Eye, 
  Edit, 
  Trash2, 
  Calendar, 
  User, 
  Tag,
  Image,
  FileText,
  Clock,
  CheckCircle,
  AlertCircle,
  FileEdit,
  Bot,
  Upload,
  ExternalLink,
  Mic,
  Brain,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  MoreVertical,
  Check,
  Square,
  CheckSquare,
  X,
  Download,
  FileCheck
} from 'lucide-react';

const ArticleTable = ({ 
  articles, 
  onArticleSelect,
  onArticleEdit, 
  onDeleteArticle, 
  onDownloadPDF,
  selectionMode, 
  selectedItems, 
  onToggleSelection,
  onStartRename,
  renamingItem,
  renameTitle,
  setRenameTitle,
  onExecuteRename,
  onCancelRename,
  onStatusChange,
  bulkActionLoading
}) => {
  const [sortField, setSortField] = useState('updated_at');
  const [sortDirection, setSortDirection] = useState('desc');
  const [openMenuId, setOpenMenuId] = useState(null);
  
  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (openMenuId) {
        setOpenMenuId(null);
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [openMenuId]);

  // Get source type icon
  const getSourceTypeIcon = (sourceType) => {
    switch (sourceType) {
      case 'file_upload':
        return <Upload className="h-4 w-4 text-green-600" />;
      case 'text_processing':
        return <FileEdit className="h-4 w-4 text-blue-600" />;
      case 'url_processing':
        return <ExternalLink className="h-4 w-4 text-purple-600" />;
      case 'recording_processing':
        return <Mic className="h-4 w-4 text-orange-600" />;
      default:
        return <Bot className="h-4 w-4 text-gray-600" />;
    }
  };

  // Get source type label
  const getSourceTypeLabel = (sourceType) => {
    switch (sourceType) {
      case 'file_upload':
        return 'File Upload';
      case 'text_processing':
        return 'Text Processing';
      case 'url_processing':
        return 'URL Processing';
      case 'recording_processing':
        return 'Recording';
      default:
        return 'AI Generated';
    }
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'published':
        return 'bg-green-100 text-green-800';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800';
      case 'review':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'published':
        return <CheckCircle className="h-3 w-3" />;
      case 'draft':
        return <FileEdit className="h-3 w-3" />;
      case 'review':
        return <AlertCircle className="h-3 w-3" />;
      default:
        return <Clock className="h-3 w-3" />;
    }
  };

  // Format date with timestamp
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Format date with timestamp
  const formatDateWithTime = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    
    const dateStr = date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
    
    const timeStr = date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
    
    return `${dateStr} at ${timeStr}`;
  };

  // Format relative time
  const formatRelativeTime = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    if (days < 365) return `${Math.floor(days / 30)} months ago`;
    return `${Math.floor(days / 365)} years ago`;
  };

  // Calculate word count
  const getWordCount = (content) => {
    if (!content) return 0;
    return content.replace(/<[^>]*>/g, '').split(/\s+/).filter(Boolean).length;
  };

  // Check if article has media
  const hasMedia = (content) => {
    return content?.includes('data:image') || false;
  };

  // Get media count
  const getMediaCount = (content) => {
    if (!content) return 0;
    const matches = content.match(/data:image/g);
    return matches ? matches.length : 0;
  };

  // Handle sort
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Sort articles
  const sortedArticles = [...articles].sort((a, b) => {
    let valueA = a[sortField];
    let valueB = b[sortField];

    // Handle special cases
    if (sortField === 'title') {
      valueA = valueA || 'Untitled';
      valueB = valueB || 'Untitled';
    } else if (sortField === 'created_by') {
      valueA = a.metadata?.created_by || 'System';
      valueB = b.metadata?.created_by || 'System';
    } else if (sortField === 'word_count') {
      valueA = getWordCount(a.content);
      valueB = getWordCount(b.content);
    } else if (sortField === 'media_count') {
      valueA = getMediaCount(a.content);
      valueB = getMediaCount(b.content);
    }

    // Handle dates
    if (sortField === 'created_at' || sortField === 'updated_at') {
      valueA = new Date(valueA || 0);
      valueB = new Date(valueB || 0);
    }

    // Compare values
    if (valueA < valueB) return sortDirection === 'asc' ? -1 : 1;
    if (valueA > valueB) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  // Render sort icon
  const renderSortIcon = (field) => {
    if (sortField !== field) {
      return <ArrowUpDown className="h-4 w-4 text-gray-400" />;
    }
    return sortDirection === 'asc' ? 
      <ArrowUp className="h-4 w-4 text-blue-600" /> : 
      <ArrowDown className="h-4 w-4 text-blue-600" />;
  };

  // Download PDF function
  const downloadArticlePDF = async (articleId, articleTitle) => {
    try {
      if (onDownloadPDF) {
        await onDownloadPDF(articleId, articleTitle);
      } else {
        console.error('onDownloadPDF function not provided');
      }
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  if (articles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <FileText className="h-12 w-12 mb-4" />
        <p className="text-lg font-medium">No articles found</p>
        <p className="text-sm">Try adjusting your search or filter criteria</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex-1 overflow-x-auto overflow-y-auto min-h-0">
        <table className="w-full min-w-[800px] table-auto">
        <thead className="sticky top-0 z-10 bg-gray-50">
          <tr className="border-b border-gray-200 bg-gray-50">
            {/* Selection Column */}
            {selectionMode && (
              <th className="text-left p-4 font-medium text-gray-900 w-12">
                <CheckSquare className="h-4 w-4 text-gray-400" />
              </th>
            )}
            <th className="text-left p-3 font-medium text-gray-900 w-40 min-w-32">
              <button
                onClick={() => handleSort('title')}
                className="flex items-center space-x-2 hover:text-blue-600"
              >
                <span>Title</span>
                {renderSortIcon('title')}
              </button>
            </th>
            <th className="text-left p-3 font-medium text-gray-900 w-20 min-w-16">
              <button
                onClick={() => handleSort('source_type')}
                className="flex items-center space-x-2 hover:text-blue-600"
              >
                <span>Source</span>
                {renderSortIcon('source_type')}
              </button>
            </th>
            <th className="text-left p-3 font-medium text-gray-900 w-16 min-w-14">
              <button
                onClick={() => handleSort('status')}
                className="flex items-center space-x-2 hover:text-blue-600"
              >
                <span>Status</span>
                {renderSortIcon('status')}
              </button>
            </th>
            <th className="text-left p-3 font-medium text-gray-900 w-20 min-w-16">
              <button
                onClick={() => handleSort('created_by')}
                className="flex items-center space-x-2 hover:text-blue-600"
              >
                <span>Author</span>
                {renderSortIcon('created_by')}
              </button>
            </th>
            <th className="text-left p-3 font-medium text-gray-900 w-24 min-w-20">
              <button
                onClick={() => handleSort('created_at')}
                className="flex items-center space-x-2 hover:text-blue-600"
              >
                <span>Created</span>
                {renderSortIcon('created_at')}
              </button>
            </th>
            <th className="text-left p-3 font-medium text-gray-900 w-24 min-w-20">
              <button
                onClick={() => handleSort('updated_at')}
                className="flex items-center space-x-2 hover:text-blue-600"
              >
                <span>Updated</span>
                {renderSortIcon('updated_at')}
              </button>
            </th>
            <th className="text-left p-3 font-medium text-gray-900 w-16 min-w-12">
              <button
                onClick={() => handleSort('word_count')}
                className="flex items-center space-x-2 hover:text-blue-600"
              >
                <span>Words</span>
                {renderSortIcon('word_count')}
              </button>
            </th>
            <th className="text-left p-3 font-medium text-gray-900 w-16 min-w-12">
              <button
                onClick={() => handleSort('media_count')}
                className="flex items-center space-x-2 hover:text-blue-600"
              >
                <span>Media</span>
                {renderSortIcon('media_count')}
              </button>
            </th>
            <th className="text-left p-3 font-medium text-gray-900 w-16 min-w-14">Actions</th>
          </tr>
        </thead>
        <tbody>
          {sortedArticles.map((article, index) => (
            <motion.tr
              key={article.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
              className={`border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                selectionMode && selectedItems.has(article.id) 
                  ? 'bg-blue-50 border-blue-200' 
                  : ''
              }`}
              onClick={() => selectionMode ? onToggleSelection(article.id) : onArticleSelect(article)}
            >
              {/* Selection Column */}
              {selectionMode && (
                <td className="p-3">
                  <div className={`w-5 h-5 rounded border-2 flex items-center justify-center cursor-pointer transition-colors ${
                    selectedItems.has(article.id)
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-white border-gray-300 hover:border-blue-500'
                  }`}>
                    {selectedItems.has(article.id) && <Check className="h-3 w-3" />}
                  </div>
                </td>
              )}
              
              <td className="p-3">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <FileText className="h-5 w-5 text-gray-400" />
                  </div>
                  <div className="min-w-0 flex-1">
                    {renamingItem === article.id ? (
                      <div className="flex items-center space-x-2">
                        <input
                          type="text"
                          value={renameTitle}
                          onChange={(e) => setRenameTitle(e.target.value)}
                          onClick={(e) => e.stopPropagation()}
                          className="flex-1 px-2 py-1 text-sm font-medium border border-blue-500 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          autoFocus
                        />
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onExecuteRename(article.id);
                          }}
                          className="p-1 text-green-600 hover:text-green-700 rounded"
                          title="Save"
                        >
                          <Check className="h-4 w-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onCancelRename();
                          }}
                          className="p-1 text-red-600 hover:text-red-700 rounded"
                          title="Cancel"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            if (!selectionMode) onArticleSelect(article);
                          }}
                          className="text-sm font-medium text-blue-600 hover:text-blue-800 truncate block w-full text-left"
                        >
                          {article.title || 'Untitled'}
                        </button>
                        <div className="text-xs text-gray-500 truncate">
                          {article.summary || 
                           (article.content ? article.content.replace(/<[^>]*>/g, '').substring(0, 60) + '...' : 'No content')}
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </td>
              
              <td className="p-3">
                <div className="flex items-center space-x-2">
                  {getSourceTypeIcon(article.source_type)}
                  <span className="text-sm text-gray-900">{getSourceTypeLabel(article.source_type)}</span>
                </div>
              </td>
              
              <td className="p-3">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(article.status)}`}>
                  {getStatusIcon(article.status)}
                  <span className="ml-1">{article.status || 'draft'}</span>
                </span>
              </td>
              
              <td className="p-3">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-900">{article.metadata?.created_by || 'System'}</span>
                </div>
              </td>
              
              <td className="p-3">
                <div className="text-sm text-gray-900">{formatDateWithTime(article.created_at)}</div>
                <div className="text-xs text-gray-500">{formatRelativeTime(article.created_at)}</div>
              </td>
              
              <td className="p-4">
                <div className="text-sm text-gray-900">{formatDate(article.updated_at)}</div>
                <div className="text-xs text-gray-500">{formatRelativeTime(article.updated_at)}</div>
              </td>
              
              <td className="p-4">
                <span className="text-sm text-gray-900">{getWordCount(article.content).toLocaleString()}</span>
              </td>
              
              <td className="p-4">
                {hasMedia(article.content) ? (
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-1">
                      <Image className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-900">{getMediaCount(article.content)}</span>
                    </div>
                    {article.media_processed && (
                      <Brain className="h-4 w-4 text-purple-600" title="AI Enhanced" />
                    )}
                  </div>
                ) : (
                  <span className="text-sm text-gray-400">None</span>
                )}
              </td>
              
              <td className="p-4">
                {!selectionMode && renamingItem !== article.id && (
                  <div className="flex items-center space-x-2">
                    <div className="relative">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setOpenMenuId(openMenuId === article.id ? null : article.id);
                        }}
                        className="p-1 text-gray-400 hover:text-gray-600 rounded"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </button>
                      {openMenuId === article.id && (
                        <div 
                          className="absolute right-0 top-6 bg-white border border-gray-200 rounded-md shadow-lg py-1 z-50 min-w-40"
                          style={{ zIndex: 9999 }}
                          onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenMenuId(null);
                              onArticleSelect(article);
                            }}
                            className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                          >
                            <Eye className="h-3 w-3" />
                            <span>View</span>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenMenuId(null);
                              if (onArticleEdit) {
                                onArticleEdit(article);
                              } else {
                                onArticleSelect(article);
                              }
                            }}
                            className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                          >
                            <Edit className="h-3 w-3" />
                            <span>Edit</span>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenMenuId(null);
                              onStartRename(article);
                            }}
                            className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                          >
                            <FileEdit className="h-3 w-3" />
                            <span>Rename</span>
                          </button>
                          <hr className="my-1" />
                          {article.status !== 'published' && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setOpenMenuId(null);
                                onStatusChange(article.id, 'published');
                              }}
                              className="flex items-center space-x-2 px-3 py-1 text-sm text-green-700 hover:bg-green-50 w-full text-left"
                              disabled={bulkActionLoading}
                            >
                              <FileCheck className="h-3 w-3" />
                              <span>Publish</span>
                            </button>
                          )}
                          {article.status !== 'draft' && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setOpenMenuId(null);
                                onStatusChange(article.id, 'draft');
                              }}
                              className="flex items-center space-x-2 px-3 py-1 text-sm text-yellow-700 hover:bg-yellow-50 w-full text-left"
                              disabled={bulkActionLoading}
                            >
                              <FileEdit className="h-3 w-3" />
                              <span>Move to Draft</span>
                            </button>
                          )}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenMenuId(null);
                              downloadArticlePDF(article.id, article.title);
                            }}
                            className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                          >
                            <Download className="h-3 w-3" />
                            <span>Download PDF</span>
                          </button>
                          <hr className="my-1" />
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenMenuId(null);
                              onDeleteArticle(article.id);
                            }}
                            className="flex items-center space-x-2 px-3 py-1 text-sm text-red-600 hover:bg-red-50 w-full text-left"
                          >
                            <Trash2 className="h-3 w-3" />
                            <span>Delete</span>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
      </div>
    </div>
  );
};

export default ArticleTable;