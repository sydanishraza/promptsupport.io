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
  Zap,
  Type,
  Link2,
  Plus,
  Globe,
  Github,
  MessageSquare,
  Calendar,
  Folder,
  Play,
  Settings,
  ArrowRight,
  Sparkles,
  ChevronDown,
  ExternalLink as LinkIcon,
  FileAudio,
  FileVideo,
  FileImage,
  Archive,
  Code,
  Cloud
} from 'lucide-react';

const KnowledgeEngineUpload = ({ isOpen, onClose, onUploadComplete }) => {
  const [activeBlock, setActiveBlock] = useState(null);
  const [files, setFiles] = useState([]);
  const [textContent, setTextContent] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processModal, setProcessModal] = useState({ open: false, step: 0, data: null });
  const fileInputRef = useRef();

  // Updated supported file formats with cleaner categorization
  const supportedFormats = {
    documents: {
      title: 'Documents',
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      formats: [
        { ext: 'docx', label: 'Word', icon: FileText },
        { ext: 'pdf', label: 'PDF', icon: FileText },
        { ext: 'ppt', label: 'PowerPoint', icon: FileText },
        { ext: 'pptx', label: 'PowerPoint', icon: FileText },
        { ext: 'xls', label: 'Excel', icon: FileText },
        { ext: 'xlsx', label: 'Excel', icon: FileText },
        { ext: 'csv', label: 'CSV', icon: FileText },
        { ext: 'xml', label: 'XML', icon: Code },
        { ext: 'html', label: 'HTML', icon: Code },
        { ext: 'md', label: 'Markdown', icon: FileText },
        { ext: 'txt', label: 'Text', icon: File }
      ]
    },
    media: {
      title: 'Audio & Video',
      icon: Video,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      formats: [
        { ext: 'mp3', label: 'MP3', icon: FileAudio },
        { ext: 'wav', label: 'WAV', icon: FileAudio },
        { ext: 'm4a', label: 'M4A', icon: FileAudio },
        { ext: 'mp4', label: 'MP4', icon: FileVideo },
        { ext: 'mov', label: 'MOV', icon: FileVideo },
        { ext: 'webm', label: 'WebM', icon: FileVideo }
      ]
    }
  };

  const processSteps = [
    { id: 'upload', label: 'File uploaded successfully', icon: CheckCircle2 },
    { id: 'analyze', label: 'Analyzing content structure', icon: Brain },
    { id: 'extract', label: 'Extracting and processing content', icon: Zap },
    { id: 'generate', label: 'Generating enhanced articles', icon: Sparkles },
    { id: 'finalize', label: 'Finalizing and saving content', icon: Cloud }
  ];

  const urlTypes = [
    { name: 'Documentation', icon: '📚', description: 'Docs, wikis, guides' },
    { name: 'GitHub Repos', icon: '🐙', description: 'Code repositories' },
    { name: 'Websites', icon: '🌐', description: 'Public web pages' },
    { name: 'Videos', icon: '📺', description: 'YouTube, Loom' }
  ];

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

  const addFiles = (newFiles) => {
    const processedFiles = newFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      size: file.size,
      type: file.type
    }));
    setFiles(prev => [...prev, ...processedFiles]);
    setActiveBlock('upload');
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    addFiles(selectedFiles);
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

  const processContent = async () => {
    setProcessing(true);
    setProcessModal({ open: true, step: 0, data: null });

    // Processing simulation
    for (let i = 0; i < processSteps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, i === 0 ? 500 : 2000));
      setProcessModal(prev => ({ ...prev, step: i + 1 }));
    }

    // Mock results
    const mockResults = {
      resourceName: files.length > 0 ? files[0].name : (textContent ? 'Text Content' : urlInput || 'URL Content'),
      resourceSize: files.length > 0 ? formatFileSize(files[0].size) : null,
      resourceType: files.length > 0 ? files[0].type : (textContent ? 'text/plain' : 'url'),
      articlesGenerated: Math.floor(Math.random() * 3) + 2,
      mediaProcessed: Math.floor(Math.random() * 5) + 1,
      processingTime: (Math.random() * 30 + 10).toFixed(1),
      articleLinks: [
        { title: 'Introduction and Overview', wordCount: Math.floor(Math.random() * 800) + 600 },
        { title: 'Core Concepts and Implementation', wordCount: Math.floor(Math.random() * 1200) + 800 },
        { title: 'Advanced Features and Best Practices', wordCount: Math.floor(Math.random() * 900) + 700 }
      ].slice(0, Math.floor(Math.random() * 2) + 2)
    };

    setProcessModal(prev => ({ ...prev, data: mockResults }));
    setProcessing(false);

    if (onUploadComplete) {
      onUploadComplete(mockResults);
    }
  };

  const canProcess = () => {
    return files.length > 0 || textContent.trim() || urlInput.trim();
  };

  const closeModal = () => {
    setProcessModal({ open: false, step: 0, data: null });
    setFiles([]);
    setTextContent('');
    setUrlInput('');
    setActiveBlock(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Brain className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Content Upload</h2>
                <p className="text-sm text-gray-600">Upload files, paste text, or enter URLs to create knowledge articles</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        <div className="p-8 max-h-[calc(95vh-200px)] overflow-y-auto bg-gradient-to-br from-slate-50/50 to-blue-50/30">
          {/* Upload Blocks Grid - Now only 3 blocks */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            
            {/* Upload File Block */}
            <motion.div
              whileHover={{ scale: 1.02, y: -8 }}
              whileTap={{ scale: 0.98 }}
              className={`relative bg-gradient-to-br from-blue-50/80 to-indigo-100/80 backdrop-blur-sm border-2 border-dashed border-blue-300/60 rounded-3xl p-8 cursor-pointer transition-all duration-500 hover:shadow-2xl hover:border-blue-400/80 ${
                isDragOver ? 'border-blue-500 bg-blue-100/80 scale-105' : ''
              } ${activeBlock === 'upload' ? 'ring-4 ring-blue-300/50 shadow-2xl border-blue-400' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="text-center space-y-6">
                <div className="p-6 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl inline-block shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-110">
                  <Upload className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">Upload Files</h3>
                  <p className="text-gray-600 text-sm mb-6 font-medium">Drag & drop or click to browse</p>
                  
                  {/* Enhanced Format Categories */}
                  <div className="space-y-4">
                    {Object.entries(supportedFormats).map(([category, data]) => (
                      <div key={category} className="text-left">
                        <div className={`flex items-center mb-2 text-sm font-semibold bg-gradient-to-r ${data.color} bg-clip-text text-transparent`}>
                          <data.icon className="w-4 h-4 mr-2 text-gray-600" />
                          {data.title}
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {data.formats.slice(0, 4).map(format => (
                            <span key={format.ext} className="px-3 py-1.5 bg-white/80 backdrop-blur-sm text-gray-800 rounded-xl text-xs font-bold border border-gray-200/50 shadow-sm hover:shadow-md transition-all duration-200">
                              {format.ext.toUpperCase()}
                            </span>
                          ))}
                          {data.formats.length > 4 && (
                            <span className="px-3 py-1.5 bg-gray-100/80 text-gray-600 rounded-xl text-xs font-medium">
                              +{data.formats.length - 4} more
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              {files.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 bg-white/80 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg"
                >
                  <div className="text-sm font-bold text-gray-900 mb-3 flex items-center">
                    <CheckCircle2 className="w-4 h-4 mr-2 text-green-600" />
                    {files.length} file{files.length > 1 ? 's' : ''} ready
                  </div>
                  <div className="space-y-3 max-h-40 overflow-y-auto">
                    {files.map(file => (
                      <div key={file.id} className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-blue-100 rounded-lg">
                            <File className="w-4 h-4 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900 text-sm truncate max-w-[200px]">{file.name}</p>
                            <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                          </div>
                        </div>
                        <button
                          onClick={(e) => { e.stopPropagation(); removeFile(file.id); }}
                          className="p-2 hover:bg-red-100 rounded-xl text-red-500 hover:text-red-700 transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept={Object.values(supportedFormats).flatMap(cat => cat.formats.map(f => `.${f.ext}`)).join(',')}
                onChange={handleFileSelect}
                className="hidden"
              />
            </motion.div>

            {/* Paste Text Block */}
            <motion.div
              whileHover={{ scale: 1.02, y: -8 }}
              whileTap={{ scale: 0.98 }}
              className={`bg-gradient-to-br from-green-50/80 to-emerald-100/80 backdrop-blur-sm border-2 border-dashed border-green-300/60 rounded-3xl p-8 transition-all duration-500 hover:shadow-2xl hover:border-green-400/80 ${
                activeBlock === 'text' ? 'ring-4 ring-green-300/50 shadow-2xl border-green-400' : ''
              }`}
              onClick={() => setActiveBlock('text')}
            >
              <div className="text-center space-y-6">
                <div className="p-6 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl inline-block shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-110">
                  <Type className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">Paste Text</h3>
                  <p className="text-gray-600 text-sm mb-6 font-medium">Direct text input for quick processing</p>
                  
                  <div className="text-left space-y-2">
                    <div className="text-xs font-semibold text-green-700 mb-2">Perfect for:</div>
                    <div className="space-y-1">
                      {['Meeting notes', 'Documentation', 'Research content', 'Blog posts'].map(item => (
                        <div key={item} className="flex items-center text-xs text-gray-600">
                          <div className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></div>
                          {item}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              <textarea
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                placeholder="Paste your content here... 

✨ Articles, notes, documentation
📚 Research papers, blog posts  
💡 Meeting notes, ideas"
                className="w-full h-40 mt-6 p-6 bg-white/80 backdrop-blur-md border-2 border-green-200/60 rounded-2xl resize-none focus:outline-none focus:ring-4 focus:ring-green-400/50 focus:border-green-400 text-sm leading-relaxed shadow-inner transition-all duration-300"
                onClick={(e) => e.stopPropagation()}
              />
              
              {textContent && (
                <div className="mt-4 text-xs text-green-700 bg-green-50/80 backdrop-blur-sm rounded-xl p-3 border border-green-200/50">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">Content ready:</span>
                    <span className="text-green-600">{textContent.split(' ').length} words</span>
                  </div>
                </div>
              )}
            </motion.div>

            {/* Enter URL Block */}
            <motion.div
              whileHover={{ scale: 1.02, y: -8 }}
              whileTap={{ scale: 0.98 }}
              className={`bg-gradient-to-br from-purple-50/80 to-violet-100/80 backdrop-blur-sm border-2 border-dashed border-purple-300/60 rounded-3xl p-8 transition-all duration-500 hover:shadow-2xl hover:border-purple-400/80 ${
                activeBlock === 'url' ? 'ring-4 ring-purple-300/50 shadow-2xl border-purple-400' : ''
              }`}
              onClick={() => setActiveBlock('url')}
            >
              <div className="text-center space-y-6">
                <div className="p-6 bg-gradient-to-br from-purple-500 to-violet-500 rounded-2xl inline-block shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-110">
                  <Link2 className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">Enter URL</h3>
                  <p className="text-gray-600 text-sm mb-6 font-medium">Crawl websites and extract content</p>
                  
                  <div className="grid grid-cols-2 gap-3 text-left">
                    {urlTypes.map(type => (
                      <div key={type.name} className="bg-white/60 backdrop-blur-sm rounded-xl p-3 border border-purple-100/50 hover:bg-white/80 transition-all duration-200">
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">{type.icon}</span>
                          <div>
                            <div className="font-semibold text-xs text-gray-900">{type.name}</div>
                            <div className="text-xs text-gray-600">{type.description}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://docs.example.com/guide"
                className="w-full mt-6 p-6 bg-white/80 backdrop-blur-md border-2 border-purple-200/60 rounded-2xl focus:outline-none focus:ring-4 focus:ring-purple-400/50 focus:border-purple-400 text-sm font-medium shadow-inner transition-all duration-300"
                onClick={(e) => e.stopPropagation()}
              />
              
              {urlInput && (
                <div className="mt-4 text-xs text-purple-700 bg-purple-50/80 backdrop-blur-sm rounded-xl p-3 border border-purple-200/50">
                  <div className="flex items-center">
                    <Globe className="w-4 h-4 mr-2" />
                    <span className="font-medium">Ready to crawl: {new URL(urlInput).hostname}</span>
                  </div>
                </div>
              )}
            </motion.div>
          </div>

          {/* Enhanced Action Button */}
          {canProcess() && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-center"
            >
              <button
                onClick={processContent}
                disabled={processing}
                className="group relative flex items-center space-x-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 text-white px-12 py-6 rounded-3xl font-bold text-xl transition-all duration-500 shadow-2xl hover:shadow-3xl disabled:opacity-50 border border-white/20 backdrop-blur-sm overflow-hidden"
                style={{
                  background: processing ? 'linear-gradient(45deg, #6b7280, #9ca3af)' : undefined
                }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <div className="relative z-10 flex items-center space-x-4">
                  {processing ? (
                    <>
                      <Loader2 className="w-7 h-7 animate-spin" />
                      <span>Processing Magic...</span>
                    </>
                  ) : (
                    <>
                      <div className="p-2 bg-white/20 rounded-full group-hover:rotate-12 transition-transform duration-300">
                        <Sparkles className="w-7 h-7" />
                      </div>
                      <span>Generate Articles</span>
                      <ArrowRight className="w-7 h-7 group-hover:translate-x-2 transition-transform duration-300" />
                    </>
                  )}
                </div>
              </button>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Enhanced Processing Modal */}
      <AnimatePresence>
        {processModal.open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 backdrop-blur-lg flex items-center justify-center z-70"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 30 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 30 }}
              className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/30 max-w-3xl w-full mx-4 overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%)',
              }}
            >
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8">
                <h3 className="text-3xl font-bold">Processing Your Content</h3>
                <p className="text-blue-100 mt-2 font-medium">Transforming your content with AI magic ✨</p>
              </div>

              <div className="p-10">
                {processModal.data ? (
                  // Enhanced Results Summary
                  <div className="space-y-8">
                    <div className="text-center space-y-6">
                      <motion.div 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.2, type: "spring" }}
                        className="p-6 bg-gradient-to-br from-green-400 to-emerald-500 rounded-3xl inline-block shadow-xl"
                      >
                        <CheckCircle2 className="w-16 h-16 text-white" />
                      </motion.div>
                      <h4 className="text-3xl font-bold text-gray-900">Processing Complete!</h4>
                      <p className="text-gray-600 font-medium">Your content has been transformed into structured articles</p>
                    </div>

                    <div className="bg-gradient-to-br from-gray-50 to-blue-50/50 rounded-3xl p-8 space-y-6 border border-gray-100 shadow-inner">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-100 shadow-sm">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-gray-700 flex items-center">
                              <FileText className="w-5 h-5 mr-2 text-blue-600" />
                              Resource processed
                            </span>
                            <div className="text-right">
                              <div className="font-semibold text-gray-900">{processModal.data.resourceName}</div>
                              {processModal.data.resourceSize && (
                                <div className="text-sm text-gray-500">{processModal.data.resourceSize}</div>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-100 shadow-sm">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-gray-700 flex items-center">
                              <Sparkles className="w-5 h-5 mr-2 text-purple-600" />
                              Articles generated
                            </span>
                            <span className="font-bold text-2xl text-purple-600">{processModal.data.articlesGenerated}</span>
                          </div>
                        </div>
                        
                        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-100 shadow-sm">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-gray-700 flex items-center">
                              <ImageIcon className="w-5 h-5 mr-2 text-pink-600" />
                              Media embedded
                            </span>
                            <span className="font-bold text-2xl text-pink-600">{processModal.data.mediaEmbedded}</span>
                          </div>
                        </div>
                        
                        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-100 shadow-sm">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-gray-700 flex items-center">
                              <Zap className="w-5 h-5 mr-2 text-yellow-600" />
                              Processing time
                            </span>
                            <span className="font-bold text-2xl text-yellow-600">{processModal.data.processingTime}s</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h5 className="font-bold text-xl text-gray-900 flex items-center">
                        <FileText className="w-6 h-6 mr-2 text-blue-600" />
                        Generated Articles:
                      </h5>
                      <div className="space-y-3">
                        {processModal.data.articleLinks.map((article, index) => (
                          <motion.div 
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="flex items-center space-x-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-100 hover:shadow-md transition-all duration-200"
                          >
                            <div className="p-3 bg-blue-100 rounded-xl">
                              <FileText className="w-5 h-5 text-blue-600" />
                            </div>
                            <div className="flex-1">
                              <div className="font-semibold text-gray-900">{article.title}</div>
                              <div className="text-sm text-gray-600">{article.wordCount} words</div>
                            </div>
                            <LinkIcon className="w-5 h-5 text-gray-400" />
                          </motion.div>
                        ))}
                      </div>
                    </div>

                    <div className="flex justify-center space-x-6 pt-6">
                      <button
                        onClick={closeModal}
                        className="px-8 py-4 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-2xl font-semibold transition-colors shadow-lg"
                      >
                        Done
                      </button>
                      <button
                        onClick={() => {/* Navigate to Content Library */}}
                        className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-2xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl"
                      >
                        View in Library
                      </button>
                    </div>
                  </div>
                ) : (
                  // Enhanced Processing Steps
                  <div className="space-y-8">
                    {processSteps.map((step, index) => {
                      const Icon = step.icon;
                      const isActive = index === processModal.step - 1;
                      const isCompleted = index < processModal.step - 1;
                      const isPending = index >= processModal.step;

                      return (
                        <motion.div 
                          key={step.id} 
                          className="flex items-center space-x-6"
                          initial={{ opacity: 0, x: -30 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <div className={`p-4 rounded-2xl transition-all duration-500 border-2 ${
                            isCompleted ? 'bg-green-100 border-green-300' : 
                            isActive ? 'bg-blue-100 border-blue-300 shadow-lg' : 
                            'bg-gray-50 border-gray-200'
                          }`}>
                            <Icon className={`w-8 h-8 transition-all duration-500 ${
                              isCompleted ? 'text-green-600' : 
                              isActive ? 'text-blue-600 animate-pulse' : 
                              'text-gray-400'
                            }`} />
                          </div>
                          <div className="flex-1">
                            <div className={`font-bold text-lg transition-all duration-500 ${
                              isCompleted ? 'text-green-900' : 
                              isActive ? 'text-blue-900' : 
                              'text-gray-600'
                            }`}>
                              {step.label}
                            </div>
                            {isActive && (
                              <div className="text-sm text-blue-600 mt-1 font-medium">
                                Processing...
                              </div>
                            )}
                          </div>
                          <div className={`w-8 h-8 rounded-full transition-all duration-500 border-2 ${
                            isCompleted ? 'bg-green-500 border-green-500' : 
                            isActive ? 'bg-blue-500 border-blue-500 animate-ping' : 
                            'bg-gray-200 border-gray-300'
                          }`}>
                            {isCompleted && (
                              <CheckCircle2 className="w-4 h-4 text-white m-1" />
                            )}
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default KnowledgeEngineUpload;