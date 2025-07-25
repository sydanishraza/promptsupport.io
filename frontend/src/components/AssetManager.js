import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Image, 
  FileText, 
  Video, 
  Music, 
  Archive,
  Eye,
  Download,
  Trash2,
  Search,
  Filter,
  Grid3X3,
  List,
  Calendar,
  User,
  Tag,
  CheckCircle,
  AlertCircle,
  Copy,
  ExternalLink,
  SortAsc,
  SortDesc
} from 'lucide-react';

import AssetModal from './AssetModal';

const AssetManager = ({ articles, onArticleSelect, onPaginationChange }) => {
  const [viewMode, setViewMode] = useState('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('dateAdded');
  const [sortOrder, setSortOrder] = useState('desc');
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [assetsPerPage] = useState(12);

  // Extract media assets from articles
  useEffect(() => {
    const extractedAssets = [];
    
    articles.forEach(article => {
      if (article.content && article.content.includes('data:image')) {
        // Extract base64 images with more flexible regex
        const imageRegex = /!\[([^\]]*)\]\(data:image\/([^;]+);base64,([^)]+)\)/g;
        
        // Also try to find images in HTML format
        const htmlImageRegex = /<img[^>]*src="data:image\/([^;]+);base64,([^"]+)"[^>]*alt="([^"]*)"[^>]*>/g;
        
        let match;
        let assetCounter = 0;
        
        // Process markdown format images
        while ((match = imageRegex.exec(article.content)) !== null) {
          const [fullMatch, altText, format, base64Data] = match;
          
          // Skip if base64 data is too short (likely truncated)
          if (base64Data.length < 50) {
            console.warn(`Skipping truncated image in article ${article.id}: ${base64Data.length} chars`);
            continue;
          }
          
          const assetId = `${article.id}-md-${assetCounter++}`;
          
          extractedAssets.push({
            id: assetId,
            type: 'image',
            format: format.toLowerCase(),
            name: altText || `Image ${assetCounter} from ${article.title}`,
            altText: altText,
            dataUrl: `data:image/${format};base64,${base64Data}`,
            size: Math.round(base64Data.length * 0.75), // Approximate size
            articleId: article.id,
            articleTitle: article.title,
            dateAdded: article.created_at,
            lastUpdated: article.updated_at,
            source: article.source_type,
            processed: article.media_processed || false
          });
        }
        
        // Process HTML format images
        while ((match = htmlImageRegex.exec(article.content)) !== null) {
          const [fullMatch, format, base64Data, altText] = match;
          
          // Skip if base64 data is too short (likely truncated)
          if (base64Data.length < 50) {
            console.warn(`Skipping truncated HTML image in article ${article.id}: ${base64Data.length} chars`);
            continue;
          }
          
          const assetId = `${article.id}-html-${assetCounter++}`;
          
          extractedAssets.push({
            id: assetId,
            type: 'image',
            format: format.toLowerCase(),
            name: altText || `HTML Image ${assetCounter} from ${article.title}`,
            altText: altText,
            dataUrl: `data:image/${format};base64,${base64Data}`,
            size: Math.round(base64Data.length * 0.75), // Approximate size
            articleId: article.id,
            articleTitle: article.title,
            dateAdded: article.created_at,
            lastUpdated: article.updated_at,
            source: article.source_type,
            processed: article.media_processed || false
          });
        }
      }
    });

    console.log(`Extracted ${extractedAssets.length} assets from ${articles.length} articles`);
    setAssets(extractedAssets);
  }, [articles]);

  // Filter and sort assets
  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         asset.articleTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         asset.altText.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFilter = filterType === 'all' || 
                         (filterType === 'image' && asset.type === 'image') ||
                         (filterType === 'png' && asset.format === 'png') ||
                         (filterType === 'jpeg' && asset.format === 'jpeg') ||
                         (filterType === 'gif' && asset.format === 'gif') ||
                         (filterType === 'svg' && asset.format === 'svg') ||
                         (filterType === 'processed' && asset.processed);
    
    return matchesSearch && matchesFilter;
  });

  // Sort assets
  const sortedAssets = [...filteredAssets].sort((a, b) => {
    let comparison = 0;
    
    switch (sortBy) {
      case 'name':
        comparison = a.name.localeCompare(b.name);
        break;
      case 'size':
        comparison = a.size - b.size;
        break;
      case 'format':
        comparison = a.format.localeCompare(b.format);
        break;
      case 'articleTitle':
        comparison = a.articleTitle.localeCompare(b.articleTitle);
        break;
      case 'dateAdded':
      default:
        comparison = new Date(a.dateAdded) - new Date(b.dateAdded);
        break;
    }
    
    return sortOrder === 'asc' ? comparison : -comparison;
  });

  // Pagination
  const totalPages = Math.ceil(sortedAssets.length / assetsPerPage);
  const startIndex = (currentPage - 1) * assetsPerPage;
  const endIndex = startIndex + assetsPerPage;
  const paginatedAssets = sortedAssets.slice(startIndex, endIndex);

  // Send pagination data to parent component
  useEffect(() => {
    if (onPaginationChange) {
      onPaginationChange({
        currentPage,
        totalPages,
        totalItems: sortedAssets.length,
        startIndex: startIndex + 1,
        endIndex: Math.min(endIndex, sortedAssets.length),
        onPageChange: setCurrentPage
      });
    }
  }, [currentPage, totalPages, sortedAssets.length, startIndex, endIndex, onPaginationChange]);

  // Handle asset click
  const handleAssetClick = (asset) => {
    setSelectedAsset(asset);
    setShowModal(true);
  };

  // Handle view in article from modal
  const handleViewInArticleFromModal = (asset) => {
    const article = articles.find(a => a.id === asset.articleId);
    if (article) {
      onArticleSelect(article);
    }
    setShowModal(false);
  };

  // Get asset icon
  const getAssetIcon = (asset) => {
    switch (asset.type) {
      case 'image':
        return <Image className="h-5 w-5 text-blue-600" />;
      case 'video':
        return <Video className="h-5 w-5 text-red-600" />;
      case 'audio':
        return <Music className="h-5 w-5 text-green-600" />;
      default:
        return <FileText className="h-5 w-5 text-gray-600" />;
    }
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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

  // Handle download
  const handleDownload = (asset) => {
    const link = document.createElement('a');
    link.href = asset.dataUrl;
    link.download = `${asset.name.replace(/[^a-zA-Z0-9]/g, '_')}.${asset.format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Handle copy to clipboard
  const handleCopyToClipboard = (asset) => {
    navigator.clipboard.writeText(asset.dataUrl).then(() => {
      console.log('Asset data URL copied to clipboard');
    });
  };

  // Handle view in article
  const handleViewInArticle = (asset) => {
    const article = articles.find(a => a.id === asset.articleId);
    if (article) {
      onArticleSelect(article);
    }
  };

  if (assets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <Archive className="h-12 w-12 mb-4" />
        <p className="text-lg font-medium">No assets found</p>
        <p className="text-sm">Assets will appear here when articles contain media</p>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6 space-y-4">
      {/* Enhanced Asset Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 lg:gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-0">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search assets, articles, or descriptions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-64"
            />
          </div>

          {/* Filter */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="all">All Assets</option>
            <option value="image">Images</option>
            <option value="png">PNG</option>
            <option value="jpeg">JPEG</option>
            <option value="gif">GIF</option>
            <option value="svg">SVG</option>
            <option value="processed">AI Processed</option>
          </select>

          {/* Sort */}
          <div className="flex items-center space-x-2">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            >
              <option value="dateAdded">Date Added</option>
              <option value="name">Name</option>
              <option value="size">File Size</option>
              <option value="format">Format</option>
              <option value="articleTitle">Source Article</option>
            </select>
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
            >
              <ArrowUpDown className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">View:</span>
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'grid'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Grid3X3 className="h-4 w-4" />
              <span>Grid</span>
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'list'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <List className="h-4 w-4" />
              <span>List</span>
            </button>
          </div>
        </div>
      </div>

      {/* Assets Display */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
          {paginatedAssets.map((asset, index) => (
            <motion.div
              key={asset.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => handleAssetClick(asset)}
              className="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-lg transition-all duration-200 cursor-pointer group"
            >
              {/* Asset Thumbnail */}
              <div className="relative aspect-video bg-gray-100 flex items-center justify-center overflow-hidden">
                {asset.dataUrl ? (
                  <img
                    src={asset.dataUrl}
                    alt={asset.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center text-gray-400">
                    <FileImage className="h-8 w-8 mb-2" />
                    <span className="text-xs">Preview unavailable</span>
                  </div>
                )}
                <div className="hidden w-full h-full flex-col items-center justify-center text-gray-400">
                  <FileImage className="h-8 w-8 mb-2" />
                  <span className="text-xs">Preview unavailable</span>
                </div>
                
                {/* Asset overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                
                {/* Asset actions overlay */}
                <div className="absolute top-2 right-2 flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDownload(asset);
                    }}
                    className="p-2 text-gray-400 hover:text-green-600 rounded"
                    title="Download"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopyToClipboard(asset);
                    }}
                    className="p-2 text-gray-400 hover:text-blue-600 rounded"
                    title="Copy Data URL"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Asset Details */}
              <div className="p-4">
                <h3 className="font-medium text-gray-900 truncate" title={asset.name}>
                  {asset.name}
                </h3>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full uppercase">
                    {asset.format}
                  </span>
                  <span>{formatFileSize(asset.size)}</span>
                  {asset.processed && (
                    <CheckCircle className="h-3 w-3 text-green-600" title="AI Processed" />
                  )}
                </div>
                <div className="text-xs text-gray-500 truncate" title={asset.articleTitle}>
                  From: {asset.articleTitle}
                </div>
                <div className="text-xs text-gray-500">
                  {formatDate(asset.dateAdded)}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleViewInArticle(asset);
                  }}
                  className="flex items-center space-x-1 text-xs text-blue-600 hover:text-blue-800"
                >
                  <ExternalLink className="h-3 w-3" />
                  <span>View in Article</span>
                </button>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDownload(asset);
                    }}
                    className="p-1 text-gray-400 hover:text-green-600 rounded"
                    title="Download"
                  >
                    <Download className="h-3 w-3" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopyToClipboard(asset);
                    }}
                    className="p-1 text-gray-400 hover:text-blue-600 rounded"
                    title="Copy Data URL"
                  >
                    <Copy className="h-3 w-3" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {paginatedAssets.map((asset, index) => (
            <motion.div
              key={asset.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.02 }}
              onClick={() => handleAssetClick(asset)}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200 cursor-pointer group"
            >
              <div className="flex items-center space-x-4">
                {/* Thumbnail */}
                <div className="flex-shrink-0 w-16 h-16 bg-gray-100 rounded-lg overflow-hidden">
                  {asset.dataUrl ? (
                    <img
                      src={asset.dataUrl}
                      alt={asset.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <FileImage className="h-6 w-6" />
                    </div>
                  )}
                  <div className="hidden w-full h-full flex items-center justify-center text-gray-400">
                    <FileImage className="h-6 w-6" />
                  </div>
                </div>

                {/* Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium text-gray-900 truncate">{asset.name}</h3>
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs uppercase">
                        {asset.format}
                      </span>
                      <span className="text-sm text-gray-500">{formatFileSize(asset.size)}</span>
                      {asset.processed && (
                        <CheckCircle className="h-4 w-4 text-green-600" title="AI Processed" />
                      )}
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <p className="text-sm text-gray-500 truncate">From: {asset.articleTitle}</p>
                    <p className="text-sm text-gray-500">{formatDate(asset.dateAdded)}</p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewInArticle(asset);
                    }}
                    className="p-2 text-gray-400 hover:text-blue-600 rounded"
                    title="View in Article"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDownload(asset);
                    }}
                    className="p-2 text-gray-400 hover:text-green-600 rounded"
                    title="Download"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopyToClipboard(asset);
                    }}
                    className="p-2 text-gray-400 hover:text-blue-600 rounded"
                    title="Copy Data URL"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* No results message */}
      {paginatedAssets.length === 0 && (
        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
          <Archive className="h-12 w-12 mb-4" />
          <p className="text-lg font-medium">No assets found</p>
          <p className="text-sm">
            {searchQuery || filterType !== 'all' 
              ? 'Try adjusting your search or filter criteria'
              : 'Assets will appear here when articles contain media'}
          </p>
        </div>
      )}

      {/* Enhanced Asset Modal */}
      <AssetModal
        asset={selectedAsset}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onViewInArticle={handleViewInArticleFromModal}
      />
    </div>
  );
};

export default AssetManager;