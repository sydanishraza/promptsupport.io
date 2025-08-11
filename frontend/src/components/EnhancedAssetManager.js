import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  SortDesc,
  ArrowUpDown,
  FileImage,
  Upload,
  Plus,
  MoreVertical,
  Edit,
  FileEdit,
  X,
  Check,
  ChevronDown,
  Loader2,
  CheckSquare,
  Square
} from 'lucide-react';

const EnhancedAssetManager = ({ 
  articles = [], 
  onArticleSelect, 
  onAssetCountUpdate, // NEW: Callback to update parent with asset count
  searchQuery = '',
  filterType = 'all',
  sortBy = 'dateAdded',
  sortOrder = 'desc',
  viewMode = 'grid'
}) => {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [assetsPerPage] = useState(12);
  
  // NEW: Selection and bulk actions
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [selectAll, setSelectAll] = useState(false);
  const [bulkActionLoading, setBulkActionLoading] = useState(false);
  
  // NEW: Action menu states
  const [openMenuId, setOpenMenuId] = useState(null);
  
  // NEW: Rename functionality
  const [renamingItem, setRenamingItem] = useState(null);
  const [renameTitle, setRenameTitle] = useState('');
  
  // NEW: Upload functionality
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // DEBUG: Log state values
  console.log('EnhancedAssetManager render:', {
    assetsCount: assets.length,
    loading,
    selectionMode,
    showUploadModal,
    showModal,
    renamingItem,
    openMenuId
  });

  // Close menu when clicking outside (but not when clicking on modals)
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Don't close if clicking on modal background or upload modal
      if (showModal || showUploadModal) return;
      
      if (openMenuId) {
        setOpenMenuId(null);
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [openMenuId, showModal, showUploadModal]);

  // Fetch and process assets
  useEffect(() => {
    const fetchAllAssets = async () => {
      setLoading(true);
      try {
        // Combine backend assets and article-extracted assets
        const backendAssets = [];
        const extractedAssets = [];
        
        // Try to fetch backend assets
        try {
          const response = await fetch(`${backendUrl}/api/assets`);
          if (response.ok) {
            const data = await response.json();
            const realAssets = data.assets || [];
            
            realAssets.forEach(asset => {
              if (asset.type === 'image') {
                let imageSource = '';
                if (asset.url) {
                  imageSource = asset.url.startsWith('/') ? `${backendUrl}${asset.url}` : asset.url;
                } else if (asset.data?.startsWith('data:image')) {
                  imageSource = asset.data;
                }
                
                if (imageSource) {
                  backendAssets.push({
                    id: asset.id,
                    type: 'image',
                    format: asset.original_filename?.split('.').pop()?.toLowerCase() || 'unknown',
                    name: asset.name || asset.original_filename || 'Unnamed asset',
                    altText: asset.name || asset.original_filename || 'Image',
                    dataUrl: imageSource,
                    size: asset.size || 0,
                    articleId: null,
                    articleTitle: 'Asset Library',
                    dateAdded: asset.created_at,
                    lastUpdated: asset.updated_at,
                    source: 'asset_library',
                    processed: true,
                    isBackendAsset: true,
                    usedInArticles: [] // Track which articles use this asset
                  });
                }
              }
            });
          }
        } catch (error) {
          console.log('Backend assets not available, using article extraction only');
        }
        
        // Extract assets from articles
        articles.forEach(article => {
          if (article.content?.includes('data:image')) {
            const imageRegex = /!\[([^\]]*)\]\(data:image\/([^;]+);base64,([^)]+)\)/g;
            const htmlImageRegex = /<img[^>]*src="data:image\/([^;]+);base64,([^"]+)"[^>]*alt="([^"]*)"[^>]*>/g;
            
            let match;
            let assetCounter = 0;
            
            while ((match = imageRegex.exec(article.content)) !== null) {
              const [, altText, format, base64Data] = match;
              
              if (base64Data.length >= 50) {
                assetCounter++;
                extractedAssets.push({
                  id: `${article.id}-img-${assetCounter}`,
                  type: 'image',
                  format: format,
                  name: altText || `Image ${assetCounter} from ${article.title}`,
                  altText: altText,
                  dataUrl: `data:image/${format};base64,${base64Data}`,
                  size: Math.round((base64Data.length * 3) / 4),
                  articleId: article.id,
                  articleTitle: article.title,
                  dateAdded: article.created_at,
                  lastUpdated: article.updated_at,
                  source: 'article_extraction',
                  processed: true,
                  isBackendAsset: false
                });
              }
            }
            
            while ((match = htmlImageRegex.exec(article.content)) !== null) {
              const [, format, base64Data, altText] = match;
              
              if (base64Data.length >= 50) {
                assetCounter++;
                extractedAssets.push({
                  id: `${article.id}-html-img-${assetCounter}`,
                  type: 'image',
                  format: format,
                  name: altText || `HTML Image ${assetCounter} from ${article.title}`,
                  altText: altText,
                  dataUrl: `data:image/${format};base64,${base64Data}`,
                  size: Math.round((base64Data.length * 3) / 4),
                  articleId: article.id,
                  articleTitle: article.title,
                  dateAdded: article.created_at,
                  lastUpdated: article.updated_at,
                  source: 'article_extraction',
                  processed: true,
                  isBackendAsset: false
                });
              }
            }
          }
        });
        
        // Combine all assets
        const allAssets = [...backendAssets, ...extractedAssets];
        console.log(`EnhancedAssetManager: Found ${allAssets.length} total assets (${backendAssets.length} backend, ${extractedAssets.length} extracted)`);
        setAssets(allAssets);
        
        // Update parent component with asset count
        if (onAssetCountUpdate) {
          onAssetCountUpdate(allAssets.length);
          console.log(`EnhancedAssetManager: Updated parent with count ${allAssets.length}`);
        }
        
      } catch (error) {
        console.error('Error fetching assets:', error);
        setAssets([]);
        if (onAssetCountUpdate) {
          onAssetCountUpdate(0);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAllAssets();
  }, [articles, backendUrl]);

  // Selection functionality
  const toggleSelection = (assetId) => {
    const newSelection = new Set(selectedItems);
    if (newSelection.has(assetId)) {
      newSelection.delete(assetId);
    } else {
      newSelection.add(assetId);
    }
    setSelectedItems(newSelection);
    setSelectAll(newSelection.size === filteredAssets.length);
  };

  const toggleSelectAll = () => {
    if (selectAll) {
      setSelectedItems(new Set());
      setSelectAll(false);
    } else {
      const allIds = new Set(filteredAssets.map(asset => asset.id));
      setSelectedItems(allIds);
      setSelectAll(true);
    }
  };

  const clearSelection = () => {
    setSelectedItems(new Set());
    setSelectAll(false);
    setSelectionMode(false);
  };

  // Rename functionality
  const startRename = (asset) => {
    setRenamingItem(asset.id);
    setRenameTitle(asset.name || '');
  };

  const executeRename = async (assetId) => {
    if (!renameTitle.trim()) {
      alert('Please enter a valid name');
      return;
    }

    setBulkActionLoading(true);
    try {
      const asset = assets.find(a => a.id === assetId);
      
      if (asset?.isBackendAsset) {
        // Rename backend asset - Try different endpoint format
        const response = await fetch(`${backendUrl}/api/assets/${assetId}/rename`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: renameTitle.trim()
          })
        });

        if (!response.ok) {
          // Try alternative endpoint format
          const response2 = await fetch(`${backendUrl}/api/assets/rename`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              id: assetId,
              name: renameTitle.trim()
            })
          });
          
          if (!response2.ok) {
            throw new Error('Failed to rename asset - API endpoint not available');
          }
        }
      }

      // Update local state regardless of backend call success for extracted assets
      setAssets(prev => prev.map(assetItem => 
        assetItem.id === assetId 
          ? { ...assetItem, name: renameTitle.trim() }
          : assetItem
      ));
      
      setRenamingItem(null);
      setRenameTitle('');
      console.log('Successfully renamed asset');
    } catch (error) {
      console.error('Error renaming asset:', error);
      // For extracted assets (non-backend), allow local rename even if API fails
      const asset = assets.find(a => a.id === assetId);
      if (!asset?.isBackendAsset) {
        setAssets(prev => prev.map(assetItem => 
          assetItem.id === assetId 
            ? { ...assetItem, name: renameTitle.trim() }
            : assetItem
        ));
        setRenamingItem(null);
        setRenameTitle('');
        console.log('Renamed extracted asset locally');
      } else {
        alert('Error renaming asset. Please try again.');
      }
    } finally {
      setBulkActionLoading(false);
    }
  };

  const cancelRename = () => {
    setRenamingItem(null);
    setRenameTitle('');
  };

  // Delete functionality
  const handleDeleteAsset = async (assetId) => {
    if (!confirm('Are you sure you want to delete this asset?')) return;

    setBulkActionLoading(true);
    try {
      const asset = assets.find(a => a.id === assetId);
      
      if (asset?.isBackendAsset) {
        // Delete backend asset
        const response = await fetch(`${backendUrl}/api/assets/${assetId}`, {
          method: 'DELETE'
        });

        if (!response.ok) {
          throw new Error('Failed to delete asset');
        }
      }

      // Remove from local state
      setAssets(prev => prev.filter(a => a.id !== assetId));
      console.log('Successfully deleted asset');
    } catch (error) {
      console.error('Error deleting asset:', error);
      alert('Error deleting asset. Please try again.');
    } finally {
      setBulkActionLoading(false);
    }
  };

  // Bulk delete
  const handleBulkDelete = async () => {
    if (!confirm(`Are you sure you want to delete ${selectedItems.size} asset(s)?`)) return;

    setBulkActionLoading(true);
    try {
      const deletePromises = Array.from(selectedItems).map(id => {
        const asset = assets.find(a => a.id === id);
        if (asset?.isBackendAsset) {
          return fetch(`${backendUrl}/api/assets/${id}`, { method: 'DELETE' });
        }
        return Promise.resolve(); // Skip article-extracted assets
      });
      
      await Promise.all(deletePromises);
      
      // Update local state
      setAssets(prev => prev.filter(a => !selectedItems.has(a.id)));
      clearSelection();
      console.log(`Successfully deleted ${selectedItems.size} assets`);
    } catch (error) {
      console.error('Error deleting assets:', error);
      alert('Error deleting some assets. Please try again.');
    } finally {
      setBulkActionLoading(false);
    }
  };

  // Upload functionality
  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const uploadPromises = Array.from(files).map(async (file, index) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', file.name);
        formData.append('type', 'image');

        try {
          const response = await fetch(`${backendUrl}/api/assets/upload`, {
            method: 'POST',
            body: formData
          });

          if (response.ok) {
            const result = await response.json();
            setUploadProgress(((index + 1) / files.length) * 100);
            return result;
          } else {
            console.error(`Failed to upload ${file.name}: ${response.status}`);
            return null;
          }
        } catch (error) {
          console.error(`Error uploading ${file.name}:`, error);
          return null;
        }
      });

      const results = await Promise.all(uploadPromises);
      const successfulUploads = results.filter(r => r !== null);

      if (successfulUploads.length > 0) {
        // Refresh assets by re-fetching
        const fetchResponse = await fetch(`${backendUrl}/api/assets`);
        if (fetchResponse.ok) {
          const data = await fetchResponse.json();
          
          // Re-process and combine assets like in the main useEffect
          const newBackendAssets = (data.assets || []).map(asset => ({
            id: asset.id,
            type: 'image',
            format: asset.original_filename?.split('.').pop()?.toLowerCase() || 'unknown',
            name: asset.name || asset.original_filename || 'Unnamed asset',
            altText: asset.name || asset.original_filename || 'Image',
            dataUrl: asset.url?.startsWith('/') ? `${backendUrl}${asset.url}` : asset.url || asset.data,
            size: asset.size || 0,
            articleId: null,
            articleTitle: 'Asset Library',
            dateAdded: asset.created_at,
            lastUpdated: asset.updated_at,
            source: 'asset_library',
            processed: true,
            isBackendAsset: true
          }));

          // Update assets and trigger parent count update
          setAssets(prev => {
            const extractedAssets = prev.filter(a => !a.isBackendAsset);
            const combined = [...newBackendAssets, ...extractedAssets];
            if (onAssetCountUpdate) {
              onAssetCountUpdate(combined.length);
            }
            return combined;
          });
        }
      }

      setShowUploadModal(false);
      console.log(`Upload completed: ${successfulUploads.length}/${files.length} files uploaded successfully`);
      
      if (successfulUploads.length < files.length) {
        alert(`${successfulUploads.length} of ${files.length} files uploaded successfully. Some uploads failed.`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error uploading files. Please try again.');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  // Filter and sort assets
  const filteredAssets = assets.filter(asset => {
    // Search filter
    if (searchQuery) {
      const searchLower = searchQuery.toLowerCase();
      const nameMatch = asset.name?.toLowerCase().includes(searchLower);
      const articleMatch = asset.articleTitle?.toLowerCase().includes(searchLower);
      if (!nameMatch && !articleMatch) return false;
    }

    // Type filter
    switch (filterType) {
      case 'image': return asset.type === 'image';
      case 'png': return asset.format === 'png';
      case 'jpeg': return asset.format === 'jpeg' || asset.format === 'jpg';
      case 'gif': return asset.format === 'gif';
      case 'svg': return asset.format === 'svg';
      case 'processed': return asset.processed;
      default: return true;
    }
  }).sort((a, b) => {
    let valueA, valueB;

    switch (sortBy) {
      case 'name':
        valueA = a.name || '';
        valueB = b.name || '';
        break;
      case 'size':
        valueA = a.size || 0;
        valueB = b.size || 0;
        break;
      case 'format':
        valueA = a.format || '';
        valueB = b.format || '';
        break;
      case 'articleTitle':
        valueA = a.articleTitle || '';
        valueB = b.articleTitle || '';
        break;
      case 'dateAdded':
      default:
        valueA = new Date(a.dateAdded || 0);
        valueB = new Date(b.dateAdded || 0);
        break;
    }

    if (sortOrder === 'asc') {
      return valueA < valueB ? -1 : valueA > valueB ? 1 : 0;
    } else {
      return valueA > valueB ? -1 : valueA < valueB ? 1 : 0;
    }
  });

  // Pagination
  const totalPages = Math.ceil(filteredAssets.length / assetsPerPage);
  const startIndex = (currentPage - 1) * assetsPerPage;
  const paginatedAssets = filteredAssets.slice(startIndex, startIndex + assetsPerPage);

  // Utility functions
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleAssetClick = (asset) => {
    setSelectedAsset(asset);
    setShowModal(true);
  };

  const handleDownload = (asset) => {
    try {
      // For base64 data URLs, we need to convert them to blob for proper download
      if (asset.dataUrl.startsWith('data:')) {
        // Convert base64 to blob
        const [header, base64Data] = asset.dataUrl.split(',');
        const mimeMatch = header.match(/data:([^;]+)/);
        const mimeType = mimeMatch ? mimeMatch[1] : 'application/octet-stream';
        
        // Convert base64 to binary
        const binary = atob(base64Data);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          bytes[i] = binary.charCodeAt(i);
        }
        
        // Create blob and download
        const blob = new Blob([bytes], { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `${asset.name.replace(/[^a-zA-Z0-9]/g, '_')}.${asset.format}`;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up the URL object
        setTimeout(() => URL.revokeObjectURL(url), 100);
        
        console.log(`Downloaded asset: ${asset.name}`);
      } else {
        // For regular URLs, use fetch to download
        fetch(asset.dataUrl)
          .then(response => response.blob())
          .then(blob => {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${asset.name.replace(/[^a-zA-Z0-9]/g, '_')}.${asset.format}`;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            setTimeout(() => URL.revokeObjectURL(url), 100);
            console.log(`Downloaded asset: ${asset.name}`);
          })
          .catch(error => {
            console.error('Download failed, falling back to simple method:', error);
            // Fallback to simple download
            const link = document.createElement('a');
            link.href = asset.dataUrl;
            link.download = `${asset.name.replace(/[^a-zA-Z0-9]/g, '_')}.${asset.format}`;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          });
      }
    } catch (error) {
      console.error('Error downloading asset:', error);
      alert('Error downloading asset. Please try again.');
    }
  };

  const handleCopyToClipboard = (asset) => {
    navigator.clipboard.writeText(asset.dataUrl).then(() => {
      console.log('Asset data URL copied to clipboard');
    });
  };

  const handleViewInArticle = (asset) => {
    if (asset.articleId && onArticleSelect) {
      const article = articles.find(a => a.id === asset.articleId);
      if (article) {
        onArticleSelect(article);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (assets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <Archive className="h-12 w-12 mb-4" />
        <p className="text-lg font-medium">No assets found</p>
        <p className="text-sm mb-4">Upload assets or create articles with media</p>
        <button
          onClick={() => setShowUploadModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Upload className="h-4 w-4" />
          <span>Upload Assets</span>
        </button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Header with Upload and Selection */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-semibold">Assets ({filteredAssets.length})</h2>
          <button
            onClick={() => {
              console.log('Upload button clicked, current showUploadModal:', showUploadModal);
              setShowUploadModal(true);
              console.log('After setState, showUploadModal should be true');
            }}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
          >
            <Upload className="h-4 w-4" />
            <span>Upload</span>
          </button>
        </div>
        
        <button
          onClick={() => {
            console.log('Selection mode toggled');
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

      {/* Selection and Bulk Actions */}
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
                {selectedItems.size} of {filteredAssets.length} selected
              </span>
            </div>

            {selectedItems.size > 0 && (
              <div className="flex items-center space-x-2">
                {bulkActionLoading && (
                  <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
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

      {/* Assets Grid */}
      <div className="flex-1 overflow-y-auto">
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {paginatedAssets.map((asset, index) => (
              <motion.div
                key={asset.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`relative bg-white border rounded-lg overflow-hidden hover:shadow-md transition-all cursor-pointer ${
                  selectionMode && selectedItems.has(asset.id) 
                    ? 'border-blue-500 bg-blue-50 shadow-md' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => selectionMode ? toggleSelection(asset.id) : handleAssetClick(asset)}
              >
                {/* Selection Checkbox */}
                {selectionMode && (
                  <div className="absolute top-2 left-2 z-10">
                    <div className={`w-5 h-5 rounded border-2 flex items-center justify-center cursor-pointer transition-colors ${
                      selectedItems.has(asset.id)
                        ? 'bg-blue-600 border-blue-600 text-white'
                        : 'bg-white border-gray-300 hover:border-blue-500'
                    }`}>
                      {selectedItems.has(asset.id) && <Check className="h-3 w-3" />}
                    </div>
                  </div>
                )}

                {/* Asset Thumbnail */}
                <div className="aspect-video bg-gray-100 flex items-center justify-center overflow-hidden">
                  {asset.dataUrl ? (
                    <img
                      src={asset.dataUrl}
                      alt={asset.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <FileImage className="h-8 w-8 text-gray-400" />
                  )}
                </div>

                {/* Asset Info */}
                <div className="p-3">
                  {renamingItem === asset.id ? (
                    <div className="space-y-2">
                      <input
                        type="text"
                        value={renameTitle}
                        onChange={(e) => setRenameTitle(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full px-2 py-1 text-sm border border-blue-500 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        autoFocus
                      />
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            executeRename(asset.id);
                          }}
                          className="p-1 text-green-600 hover:text-green-700 rounded"
                          title="Save"
                        >
                          <Check className="h-3 w-3" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            cancelRename();
                          }}
                          className="p-1 text-red-600 hover:text-red-700 rounded"
                          title="Cancel"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <h3 className="font-medium text-sm text-gray-900 truncate mb-1">
                        {asset.name}
                      </h3>
                      <div className="text-xs text-gray-500 space-y-1">
                        <p>{asset.format?.toUpperCase()} • {formatFileSize(asset.size)}</p>
                        <p>From: {asset.articleTitle}</p>
                      </div>
                    </>
                  )}
                </div>

                {/* Action Menu */}
                {!selectionMode && renamingItem !== asset.id && (
                  <div className="absolute top-2 right-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        console.log(`Action menu clicked for asset ${asset.id}`);
                        setOpenMenuId(openMenuId === asset.id ? null : asset.id);
                      }}
                      className="p-1 text-gray-400 hover:text-gray-600 bg-white rounded shadow"
                      style={{ zIndex: 10 }}
                    >
                      <MoreVertical className="h-4 w-4" />
                    </button>
                    {openMenuId === asset.id && (
                      <div 
                        className="absolute right-0 top-6 bg-white border border-gray-200 rounded-md shadow-lg py-1 z-50 min-w-40"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setOpenMenuId(null);
                            handleAssetClick(asset);
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
                            startRename(asset);
                          }}
                          className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                        >
                          <FileEdit className="h-3 w-3" />
                          <span>Rename</span>
                        </button>
                        {asset.articleId && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenMenuId(null);
                              handleViewInArticle(asset);
                            }}
                            className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                          >
                            <ExternalLink className="h-3 w-3" />
                            <span>View in Article</span>
                          </button>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setOpenMenuId(null);
                            handleDownload(asset);
                          }}
                          className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                        >
                          <Download className="h-3 w-3" />
                          <span>Download</span>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setOpenMenuId(null);
                            handleCopyToClipboard(asset);
                          }}
                          className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                        >
                          <Copy className="h-3 w-3" />
                          <span>Copy URL</span>
                        </button>
                        <hr className="my-1" />
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setOpenMenuId(null);
                            handleDeleteAsset(asset.id);
                          }}
                          className="flex items-center space-x-2 px-3 py-1 text-sm text-red-600 hover:bg-red-50 w-full text-left"
                        >
                          <Trash2 className="h-3 w-3" />
                          <span>Delete</span>
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        ) : (
          /* Table View */
          <div className="bg-white rounded-lg border">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  {selectionMode && (
                    <th className="text-left p-4 font-medium text-gray-900 w-12">
                      <CheckSquare className="h-4 w-4 text-gray-400" />
                    </th>
                  )}
                  <th className="text-left p-4 font-medium text-gray-900">Name</th>
                  <th className="text-left p-4 font-medium text-gray-900">Type</th>
                  <th className="text-left p-4 font-medium text-gray-900">Size</th>
                  <th className="text-left p-4 font-medium text-gray-900">Source</th>
                  <th className="text-left p-4 font-medium text-gray-900">Date Added</th>
                  <th className="text-left p-4 font-medium text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody>
                {paginatedAssets.map((asset) => (
                  <tr 
                    key={asset.id} 
                    className={`border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors ${
                      selectionMode && selectedItems.has(asset.id) ? 'bg-blue-50' : ''
                    }`}
                    onClick={() => {
                      if (!selectionMode && renamingItem !== asset.id) {
                        handleAssetClick(asset);
                      }
                    }}
                  >
                    {selectionMode && (
                      <td className="p-4">
                        <div 
                          className={`w-5 h-5 rounded border-2 flex items-center justify-center cursor-pointer ${
                            selectedItems.has(asset.id)
                              ? 'bg-blue-600 border-blue-600 text-white'
                              : 'bg-white border-gray-300 hover:border-blue-500'
                          }`}
                          onClick={() => toggleSelection(asset.id)}
                        >
                          {selectedItems.has(asset.id) && <Check className="h-3 w-3" />}
                        </div>
                      </td>
                    )}
                    <td className="p-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gray-100 rounded overflow-hidden flex-shrink-0">
                          {asset.dataUrl ? (
                            <img src={asset.dataUrl} alt={asset.name} className="w-full h-full object-cover" />
                          ) : (
                            <FileImage className="w-full h-full p-2 text-gray-400" />
                          )}
                        </div>
                        <div>
                          {renamingItem === asset.id ? (
                            <div className="flex items-center space-x-2">
                              <input
                                type="text"
                                value={renameTitle}
                                onChange={(e) => setRenameTitle(e.target.value)}
                                className="px-2 py-1 text-sm border border-blue-500 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                                autoFocus
                              />
                              <button
                                onClick={() => executeRename(asset.id)}
                                className="p-1 text-green-600 hover:text-green-700"
                              >
                                <Check className="h-4 w-4" />
                              </button>
                              <button
                                onClick={cancelRename}
                                className="p-1 text-red-600 hover:text-red-700"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            </div>
                          ) : (
                            <span className="font-medium text-sm">{asset.name}</span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="p-4 text-sm text-gray-600">
                      {asset.format?.toUpperCase()}
                    </td>
                    <td className="p-4 text-sm text-gray-600">
                      {formatFileSize(asset.size)}
                    </td>
                    <td className="p-4 text-sm text-gray-600">
                      {asset.articleTitle}
                    </td>
                    <td className="p-4 text-sm text-gray-600">
                      {new Date(asset.dateAdded).toLocaleDateString()}
                    </td>
                    <td className="p-4">
                      {!selectionMode && renamingItem !== asset.id && (
                        <div className="relative">
                          <button
                            onClick={() => setOpenMenuId(openMenuId === asset.id ? null : asset.id)}
                            className="p-1 text-gray-400 hover:text-gray-600 rounded"
                          >
                            <MoreVertical className="h-4 w-4" />
                          </button>
                          {openMenuId === asset.id && (
                            <div className="absolute right-0 top-6 bg-white border border-gray-200 rounded-md shadow-lg py-1 z-50 min-w-40">
                              <button
                                onClick={() => {
                                  setOpenMenuId(null);
                                  handleAssetClick(asset);
                                }}
                                className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                              >
                                <Eye className="h-3 w-3" />
                                <span>View</span>
                              </button>
                              <button
                                onClick={() => {
                                  setOpenMenuId(null);
                                  startRename(asset);
                                }}
                                className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                              >
                                <FileEdit className="h-3 w-3" />
                                <span>Rename</span>
                              </button>
                              {asset.articleId && (
                                <button
                                  onClick={() => {
                                    setOpenMenuId(null);
                                    handleViewInArticle(asset);
                                  }}
                                  className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                                >
                                  <ExternalLink className="h-3 w-3" />
                                  <span>View in Article</span>
                                </button>
                              )}
                              <button
                                onClick={() => {
                                  setOpenMenuId(null);
                                  handleDownload(asset);
                                }}
                                className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                              >
                                <Download className="h-3 w-3" />
                                <span>Download</span>
                              </button>
                              <hr className="my-1" />
                              <button
                                onClick={() => {
                                  setOpenMenuId(null);
                                  handleDeleteAsset(asset.id);
                                }}
                                className="flex items-center space-x-2 px-3 py-1 text-sm text-red-600 hover:bg-red-50 w-full text-left"
                              >
                                <Trash2 className="h-3 w-3" />
                                <span>Delete</span>
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 bg-white border-t">
          <div className="text-sm text-gray-700">
            Showing {startIndex + 1} to {Math.min(startIndex + assetsPerPage, filteredAssets.length)} of {filteredAssets.length} assets
          </div>
          <div className="flex space-x-1">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm border rounded-md bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const pageNum = i + 1;
              return (
                <button
                  key={pageNum}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`px-3 py-1 text-sm border rounded-md ${
                    currentPage === pageNum
                      ? 'border-blue-500 bg-blue-50 text-blue-600'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm border rounded-md bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      <AnimatePresence>
        {showUploadModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => {
              console.log('Upload modal background clicked');
              if (!uploading) setShowUploadModal(false);
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl p-6 w-full max-w-md"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Upload Assets</h3>
                {!uploading && (
                  <button
                    onClick={() => {
                      console.log('Upload modal close button clicked');
                      setShowUploadModal(false);
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-5 w-5" />
                  </button>
                )}
              </div>
              
              {uploading ? (
                <div className="space-y-4">
                  <div className="text-center">
                    <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600 mb-2" />
                    <p className="text-sm text-gray-600">Uploading assets...</p>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 text-center">{Math.round(uploadProgress)}% complete</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">
                    Select image files to upload to your asset library.
                  </p>
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={(e) => handleFileUpload(e.target.files)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="flex justify-end space-x-3">
                    <button
                      onClick={() => setShowUploadModal(false)}
                      className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Asset View Modal */}
      <AnimatePresence>
        {showModal && selectedAsset && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
            onClick={() => {
              setShowModal(false);
              setSelectedAsset(null);
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{selectedAsset.name}</h3>
                <button
                  onClick={() => {
                    setShowModal(false);
                    setSelectedAsset(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                {/* Asset Preview */}
                <div className="flex justify-center bg-gray-50 rounded-lg p-4">
                  <img 
                    src={selectedAsset.dataUrl} 
                    alt={selectedAsset.name}
                    className="max-w-full max-h-96 object-contain rounded"
                  />
                </div>
                
                {/* Asset Details */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Format:</span>
                    <span className="ml-2">{selectedAsset.format?.toUpperCase()}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Size:</span>
                    <span className="ml-2">{formatFileSize(selectedAsset.size)}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Source:</span>
                    <span className="ml-2">{selectedAsset.articleTitle}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Date Added:</span>
                    <span className="ml-2">{new Date(selectedAsset.dateAdded).toLocaleDateString()}</span>
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div className="flex items-center justify-end space-x-3 pt-4 border-t">
                  {selectedAsset.articleId && (
                    <button
                      onClick={() => {
                        handleViewInArticle(selectedAsset);
                        setShowModal(false);
                        setSelectedAsset(null);
                      }}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <ExternalLink className="h-4 w-4" />
                      <span>View in Article</span>
                    </button>
                  )}
                  <button
                    onClick={() => handleDownload(selectedAsset)}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    <Download className="h-4 w-4" />
                    <span>Download</span>
                  </button>
                  <button
                    onClick={() => handleCopyToClipboard(selectedAsset)}
                    className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                  >
                    <Copy className="h-4 w-4" />
                    <span>Copy URL</span>
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EnhancedAssetManager;