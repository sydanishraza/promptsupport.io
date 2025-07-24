import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Download, 
  Copy, 
  ExternalLink, 
  Calendar, 
  FileText, 
  Eye, 
  Hash,
  User,
  Clock,
  Image as ImageIcon
} from 'lucide-react';

const AssetModal = ({ asset, isOpen, onClose, onViewInArticle }) => {
  if (!asset) return null;

  // Handle download
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = asset.dataUrl;
    link.download = `${asset.name.replace(/[^a-zA-Z0-9]/g, '_')}.${asset.format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Handle copy to clipboard
  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(asset.dataUrl).then(() => {
      console.log('Asset data URL copied to clipboard');
    });
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
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <ImageIcon className="h-6 w-6 text-blue-600" />
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">{asset.name}</h2>
                  <p className="text-sm text-gray-500">
                    {asset.format.toUpperCase()} • {formatFileSize(asset.size)}
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex flex-col lg:flex-row">
              {/* Image Preview */}
              <div className="flex-1 p-6 bg-gray-50 flex items-center justify-center">
                <div className="max-w-full max-h-96 overflow-hidden rounded-lg">
                  <img
                    src={asset.dataUrl}
                    alt={asset.altText || asset.name}
                    className="max-w-full max-h-96 object-contain"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                  <div className="hidden w-full h-48 bg-gray-200 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <ImageIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                      <span className="text-sm text-gray-500">Image Preview Unavailable</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Metadata Panel */}
              <div className="lg:w-80 p-6 border-l border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Asset Details</h3>
                
                <div className="space-y-4">
                  {/* Basic Info */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Format</label>
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs uppercase font-medium">
                        {asset.format}
                      </span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">File Size</label>
                    <p className="text-sm text-gray-900">{formatFileSize(asset.size)}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Alt Text</label>
                    <p className="text-sm text-gray-900">{asset.altText || 'No alt text'}</p>
                  </div>

                  {/* Source Info */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Source Article</label>
                    <div className="flex items-center space-x-2">
                      <FileText className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-900 truncate">{asset.articleTitle}</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Source Type</label>
                    <p className="text-sm text-gray-900">{asset.source}</p>
                  </div>

                  {/* Dates */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Date Added</label>
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-900">{formatDate(asset.dateAdded)}</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Last Updated</label>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-900">{formatDate(asset.lastUpdated)}</span>
                    </div>
                  </div>

                  {/* Processing Status */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">AI Processing</label>
                    <div className="flex items-center space-x-2">
                      {asset.processed ? (
                        <>
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span className="text-sm text-green-700">Processed</span>
                        </>
                      ) : (
                        <>
                          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                          <span className="text-sm text-gray-700">Not Processed</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Asset ID */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Asset ID</label>
                    <div className="flex items-center space-x-2">
                      <Hash className="h-4 w-4 text-gray-400" />
                      <span className="text-xs text-gray-500 font-mono">{asset.id}</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-6 space-y-3">
                  <button
                    onClick={() => onViewInArticle(asset)}
                    className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View in Article
                  </button>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={handleDownload}
                      className="flex-1 flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </button>
                    
                    <button
                      onClick={handleCopyToClipboard}
                      className="flex-1 flex items-center justify-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy URL
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default AssetModal;