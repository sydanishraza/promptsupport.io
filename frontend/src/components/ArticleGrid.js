import React from 'react';
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
  Download
} from 'lucide-react';

const ArticleGrid = ({ articles, onArticleSelect, onDeleteArticle, onDownloadPDF }) => {
  
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

  // Format date
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
    <div className="p-4 lg:p-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
        {articles.map((article, index) => (
          <motion.div
            key={article.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.3 }}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-gray-300 transition-all cursor-pointer"
            onClick={() => onArticleSelect(article)}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-gray-900 truncate">
                  {article.title || 'Untitled'}
                </h3>
                <div className="flex items-center space-x-2 mt-1">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(article.status)}`}>
                    {getStatusIcon(article.status)}
                    <span className="ml-1">{article.status || 'draft'}</span>
                  </span>
                  <span className="text-xs text-gray-500">v{article.version || 1}</span>
                </div>
              </div>
              <div className="flex items-center space-x-1 ml-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onArticleSelect(article);
                  }}
                  className="p-1 text-gray-400 hover:text-blue-600 rounded"
                  title="View Article"
                >
                  <Eye className="h-4 w-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    downloadArticlePDF(article.id, article.title);
                  }}
                  className="p-1 text-gray-400 hover:text-purple-600 rounded"
                  title="Download PDF"
                >
                  <Download className="h-4 w-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteArticle(article.id);
                  }}
                  className="p-1 text-gray-400 hover:text-red-600 rounded"
                  title="Delete Article"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Metadata */}
            <div className="space-y-2 mb-3">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Source</span>
                <div className="flex items-center space-x-1">
                  {getSourceTypeIcon(article.source_type)}
                  <span>{getSourceTypeLabel(article.source_type)}</span>
                </div>
              </div>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Created by</span>
                <div className="flex items-center space-x-1">
                  <User className="h-3 w-3" />
                  <span>{article.metadata?.created_by || 'System'}</span>
                </div>
              </div>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Date added</span>
                <div className="flex items-center space-x-1">
                  <Calendar className="h-3 w-3" />
                  <span>{formatDateWithTime(article.created_at)}</span>
                </div>
              </div>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Last updated</span>
                <div className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>{formatDate(article.updated_at)}</span>
                </div>
              </div>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Words</span>
                <span>{getWordCount(article.content)}</span>
              </div>
              {hasMedia(article.content) && (
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Media</span>
                  <div className="flex items-center space-x-1">
                    <Image className="h-3 w-3" />
                    <span>{getMediaCount(article.content)}</span>
                    {article.media_processed && (
                      <Brain className="h-3 w-3 text-purple-600" title="AI Enhanced" />
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Content Preview */}
            <div className="mb-3">
              <p className="text-xs text-gray-600 line-clamp-3">
                {article.summary || 
                 (article.content ? article.content.replace(/<[^>]*>/g, '').substring(0, 120) + '...' : 'No content available')}
              </p>
            </div>

            {/* Tags */}
            {article.tags && article.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {article.tags.slice(0, 3).map((tag, tagIndex) => (
                  <span
                    key={tagIndex}
                    className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                  >
                    <Tag className="h-2 w-2 mr-1" />
                    {tag}
                  </span>
                ))}
                {article.tags.length > 3 && (
                  <span className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                    +{article.tags.length - 3} more
                  </span>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-100">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onArticleSelect(article);
                }}
                className="flex items-center space-x-1 px-3 py-1 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 text-xs font-medium transition-colors"
              >
                <Eye className="h-3 w-3" />
                <span>View</span>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onArticleSelect(article);
                }}
                className="flex items-center space-x-1 px-3 py-1 bg-green-50 text-green-600 rounded-md hover:bg-green-100 text-xs font-medium transition-colors"
              >
                <Edit className="h-3 w-3" />
                <span>Edit</span>
              </button>
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <span>{article.metadata?.views || 0} views</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default ArticleGrid;