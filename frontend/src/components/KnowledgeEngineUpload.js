import React, { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  File, 
  FileText, 
  Image as ImageIcon, 
  Video, 
  Music, 
  X, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Eye, 
  ExternalLink,
  Brain,
  Zap
} from 'lucide-react';

const KnowledgeEngineUpload = ({ isOpen, onClose, onUploadComplete }) => {
  const [files, setFiles] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadResults, setUploadResults] = useState([]);
  const fileInputRef = useRef();

  // Supported file types with their icons and descriptions
  const supportedTypes = {
    // Documents
    'pdf': { icon: FileText, color: 'text-red-500', label: 'PDF Documents', description: 'Text extraction with images' },
    'doc': { icon: FileText, color: 'text-blue-500', label: 'Word Documents', description: 'Full content and media extraction' },
    'docx': { icon: FileText, color: 'text-blue-500', label: 'Word Documents', description: 'Full content and media extraction' },
    'txt': { icon: File, color: 'text-gray-500', label: 'Text Files', description: 'Direct text processing' },
    'md': { icon: File, color: 'text-purple-500', label: 'Markdown Files', description: 'Formatted text with media' },
    
    // Spreadsheets
    'xls': { icon: FileText, color: 'text-green-500', label: 'Excel Spreadsheets', description: 'Data table extraction' },
    'xlsx': { icon: FileText, color: 'text-green-500', label: 'Excel Spreadsheets', description: 'Data table extraction' },
    'csv': { icon: FileText, color: 'text-green-600', label: 'CSV Files', description: 'Structured data processing' },
    
    // Presentations
    'ppt': { icon: FileText, color: 'text-orange-500', label: 'PowerPoint', description: 'Slide-by-slide conversion' },
    'pptx': { icon: FileText, color: 'text-orange-500', label: 'PowerPoint', description: 'Slide-by-slide conversion' },
    
    // Media
    'jpg': { icon: ImageIcon, color: 'text-pink-500', label: 'Images', description: 'OCR and visual analysis' },
    'jpeg': { icon: ImageIcon, color: 'text-pink-500', label: 'Images', description: 'OCR and visual analysis' },
    'png': { icon: ImageIcon, color: 'text-pink-500', label: 'Images', description: 'OCR and visual analysis' },
    'gif': { icon: ImageIcon, color: 'text-pink-500', label: 'Images', description: 'OCR and visual analysis' },
    'webp': { icon: ImageIcon, color: 'text-pink-500', label: 'Images', description: 'OCR and visual analysis' },
    
    // Other
    'json': { icon: File, color: 'text-yellow-500', label: 'JSON Files', description: 'Structured data processing' }
  };

  const getFileIcon = (filename) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    const typeInfo = supportedTypes[extension];
    return typeInfo ? typeInfo.icon : File;
  };

  const getFileColor = (filename) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    const typeInfo = supportedTypes[extension];
    return typeInfo ? typeInfo.color : 'text-gray-500';
  };

  const isSupported = (filename) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    return supportedTypes.hasOwnProperty(extension);
  };

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    addFiles(selectedFiles);
  };

  const addFiles = (newFiles) => {
    const processedFiles = newFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending', // pending, processing, completed, error
      progress: 0,
      supported: isSupported(file.name),
      result: null,
      error: null
    }));

    setFiles(prev => [...prev, ...processedFiles]);
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const processFiles = async () => {
    if (files.length === 0) return;

    setProcessing(true);
    const results = [];

    for (const fileData of files) {
      if (!fileData.supported) {
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { ...f, status: 'error', error: 'Unsupported file type' }
            : f
        ));
        continue;
      }

      try {
        // Update status to processing
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { ...f, status: 'processing', progress: 10 }
            : f
        ));

        // Create form data
        const formData = new FormData();
        formData.append('file', fileData.file);
        formData.append('metadata', JSON.stringify({
          original_name: fileData.name,
          type: 'file_upload',
          uploaded_at: new Date().toISOString()
        }));

        // Simulate progress updates
        const progressInterval = setInterval(() => {
          setFiles(prev => prev.map(f => 
            f.id === fileData.id && f.progress < 90
              ? { ...f, progress: f.progress + 10 }
              : f
          ));
        }, 500);

        // Upload file
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/content/upload`, {
          method: 'POST',
          body: formData
        });

        clearInterval(progressInterval);

        if (response.ok) {
          const result = await response.json();
          
          // Update status to completed
          setFiles(prev => prev.map(f => 
            f.id === fileData.id 
              ? { 
                  ...f, 
                  status: 'completed', 
                  progress: 100, 
                  result 
                }
              : f
          ));

          results.push({
            filename: fileData.name,
            success: true,
            result
          });

        } else {
          const error = await response.text();
          setFiles(prev => prev.map(f => 
            f.id === fileData.id 
              ? { 
                  ...f, 
                  status: 'error', 
                  progress: 0,
                  error: `Upload failed: ${error}`
                }
              : f
          ));
          
          results.push({
            filename: fileData.name,
            success: false,
            error
          });
        }

      } catch (error) {
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { 
                ...f, 
                status: 'error', 
                progress: 0,
                error: error.message
              }
            : f
        ));

        results.push({
          filename: fileData.name,
          success: false,
          error: error.message
        });
      }
    }

    setUploadResults(results);
    setProcessing(false);

    // Call completion handler
    if (onUploadComplete) {
      onUploadComplete(results);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return File;
      case 'processing': return Loader2;
      case 'completed': return CheckCircle2;
      case 'error': return AlertCircle;
      default: return File;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'text-gray-500';
      case 'processing': return 'text-blue-500';
      case 'completed': return 'text-green-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const reset = () => {
    setFiles([]);
    setUploadResults([]);
    setProcessing(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white/20 rounded-xl">
                <Brain className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Knowledge Engine Upload</h2>
                <p className="text-blue-100 text-sm">
                  Upload documents to automatically generate AI-powered knowledge base articles
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-xl transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-6 max-h-[calc(90vh-120px)] overflow-y-auto">
          {/* Upload Area */}
          {files.length === 0 && (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-200 ${
                isDragOver
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
              }`}
            >
              <div className="flex flex-col items-center space-y-4">
                <div className="p-4 bg-blue-100 rounded-2xl">
                  <Upload className="w-12 h-12 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Drop files here or click to browse
                  </h3>
                  <p className="text-gray-600">
                    Support for documents, spreadsheets, presentations, and images
                  </p>
                </div>

                {/* Supported Types Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mt-6 w-full max-w-2xl">
                  {Object.entries(supportedTypes).slice(0, 8).map(([ext, info]) => {
                    const IconComponent = info.icon;
                    return (
                      <div key={ext} className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
                        <IconComponent className={`w-4 h-4 ${info.color}`} />
                        <span className="text-xs font-medium text-gray-700 uppercase">
                          {ext}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.md,.xls,.xlsx,.csv,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.webp,.json"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
          )}

          {/* Files List */}
          {files.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Files to Process ({files.length})
                </h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    Add More Files
                  </button>
                  <button
                    onClick={reset}
                    className="text-gray-600 hover:text-gray-700 text-sm font-medium"
                  >
                    Clear All
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                {files.map((fileData) => {
                  const IconComponent = getFileIcon(fileData.name);
                  const StatusIcon = getStatusIcon(fileData.status);
                  
                  return (
                    <div
                      key={fileData.id}
                      className="flex items-center space-x-4 p-4 border border-gray-200 rounded-xl hover:border-gray-300 transition-colors"
                    >
                      <div className={`p-2 rounded-lg bg-gray-100`}>
                        <IconComponent className={`w-5 h-5 ${getFileColor(fileData.name)}`} />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {fileData.name}
                          </p>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-500">
                              {formatFileSize(fileData.size)}
                            </span>
                            {!fileData.supported && (
                              <span className="text-xs text-red-500 bg-red-100 px-2 py-1 rounded">
                                Unsupported
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Progress Bar */}
                        {fileData.status === 'processing' && (
                          <div className="mt-2">
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${fileData.progress}%` }}
                              />
                            </div>
                          </div>
                        )}

                        {/* Error Message */}
                        {fileData.status === 'error' && fileData.error && (
                          <p className="mt-1 text-xs text-red-600">
                            {fileData.error}
                          </p>
                        )}

                        {/* Success Message */}
                        {fileData.status === 'completed' && fileData.result && (
                          <p className="mt-1 text-xs text-green-600">
                            Processing complete • {fileData.result.chunks_created} chunks created
                          </p>
                        )}
                      </div>

                      <div className="flex items-center space-x-2">
                        <StatusIcon
                          className={`w-5 h-5 ${getStatusColor(fileData.status)} ${
                            fileData.status === 'processing' ? 'animate-spin' : ''
                          }`}
                        />
                        
                        {fileData.status === 'pending' && (
                          <button
                            onClick={() => removeFile(fileData.id)}
                            className="p-1 text-gray-400 hover:text-red-500 rounded"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.md,.xls,.xlsx,.csv,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.webp,.json"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
          )}

          {/* Action Buttons */}
          {files.length > 0 && (
            <div className="flex items-center justify-between pt-6 border-t border-gray-200 mt-6">
              <div className="text-sm text-gray-600">
                {files.filter(f => f.supported).length} of {files.length} files supported
              </div>
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium"
                  disabled={processing}
                >
                  Cancel
                </button>
                
                <button
                  onClick={processFiles}
                  disabled={processing || files.filter(f => f.supported).length === 0}
                  className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-xl font-medium transition-colors"
                >
                  {processing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      <span>Process with AI</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Results Summary */}
          {uploadResults.length > 0 && (
            <div className="mt-6 p-4 bg-gray-50 rounded-xl">
              <h4 className="font-semibold text-gray-900 mb-3">Processing Results</h4>
              <div className="space-y-2">
                {uploadResults.map((result, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">{result.filename}</span>
                    {result.success ? (
                      <span className="text-green-600 font-medium">✓ Processed</span>
                    ) : (
                      <span className="text-red-600 font-medium">✗ Failed</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default KnowledgeEngineUpload;