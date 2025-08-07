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

        <div className="p-6 max-h-[calc(90vh-200px)] overflow-y-auto">
          {/* Upload Methods Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            
            {/* File Upload */}
            <motion.div
              whileHover={{ y: -2 }}
              className={`relative border-2 border-dashed rounded-lg p-6 cursor-pointer transition-all duration-200 ${
                isDragOver ? 'border-blue-500 bg-blue-50' : 
                activeBlock === 'upload' ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="text-center">
                <div className="p-3 bg-blue-100 rounded-full inline-flex mb-4">
                  <Upload className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Upload Files</h3>
                <p className="text-sm text-gray-600 mb-4">Drag & drop files or click to browse</p>
                
                {/* Supported formats */}
                <div className="space-y-3">
                  {Object.entries(supportedFormats).map(([category, data]) => (
                    <div key={category} className="text-left">
                      <div className={`flex items-center mb-2 text-sm font-medium ${data.color}`}>
                        <data.icon className="w-4 h-4 mr-2" />
                        {data.title}
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {data.formats.slice(0, 6).map(format => (
                          <span key={format.ext} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                            .{format.ext}
                          </span>
                        ))}
                        {data.formats.length > 6 && (
                          <span className="px-2 py-1 bg-gray-200 text-gray-600 rounded text-xs">
                            +{data.formats.length - 6} more
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* File list */}
              {files.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4 p-3 bg-gray-50 rounded-lg border"
                >
                  <div className="text-sm font-medium text-gray-900 mb-2 flex items-center">
                    <CheckCircle2 className="w-4 h-4 mr-2 text-green-600" />
                    {files.length} file{files.length > 1 ? 's' : ''} selected
                  </div>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {files.map(file => (
                      <div key={file.id} className="flex items-center justify-between p-2 bg-white rounded border">
                        <div className="flex items-center space-x-2 min-w-0">
                          <File className="w-4 h-4 text-gray-500 flex-shrink-0" />
                          <div className="min-w-0">
                            <p className="font-medium text-sm text-gray-900 truncate">{file.name}</p>
                            <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                          </div>
                        </div>
                        <button
                          onClick={(e) => { e.stopPropagation(); removeFile(file.id); }}
                          className="p-1 hover:bg-red-100 rounded text-red-500 hover:text-red-700 transition-colors flex-shrink-0"
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

            {/* Text Input */}
            <motion.div
              whileHover={{ y: -2 }}
              className={`border-2 border-dashed rounded-lg p-6 transition-all duration-200 ${
                activeBlock === 'text' ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-gray-400'
              }`}
              onClick={() => setActiveBlock('text')}
            >
              <div className="text-center mb-4">
                <div className="p-3 bg-green-100 rounded-full inline-flex mb-4">
                  <Type className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Paste Text</h3>
                <p className="text-sm text-gray-600 mb-4">Directly paste content for processing</p>
                
                <div className="text-left">
                  <div className="text-xs font-medium text-gray-700 mb-2">Ideal for:</div>
                  <div className="space-y-1">
                    {['Meeting notes', 'Documentation', 'Research content', 'Articles'].map(item => (
                      <div key={item} className="flex items-center text-xs text-gray-600">
                        <div className="w-1 h-1 bg-green-500 rounded-full mr-2"></div>
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <textarea
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                placeholder="Paste your content here...

• Meeting notes and documentation
• Research papers and articles  
• Knowledge base content
• Training materials"
                className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
                onClick={(e) => e.stopPropagation()}
              />
              
              {textContent && (
                <div className="mt-3 text-xs text-green-700 bg-green-100 rounded-lg p-2">
                  <div className="flex items-center justify-between">
                    <span>Content ready for processing</span>
                    <span className="font-medium">{textContent.split(' ').length} words</span>
                  </div>
                </div>
              )}
            </motion.div>

            {/* URL Input */}
            <motion.div
              whileHover={{ y: -2 }}
              className={`border-2 border-dashed rounded-lg p-6 transition-all duration-200 ${
                activeBlock === 'url' ? 'border-purple-500 bg-purple-50' : 'border-gray-300 hover:border-gray-400'
              }`}
              onClick={() => setActiveBlock('url')}
            >
              <div className="text-center mb-4">
                <div className="p-3 bg-purple-100 rounded-full inline-flex mb-4">
                  <Link2 className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Enter URL</h3>
                <p className="text-sm text-gray-600 mb-4">Extract content from web pages</p>
                
                <div className="grid grid-cols-2 gap-2 text-left">
                  {urlTypes.map(type => (
                    <div key={type.name} className="p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <span className="text-base">{type.icon}</span>
                        <div>
                          <div className="font-medium text-xs text-gray-900">{type.name}</div>
                          <div className="text-xs text-gray-600">{type.description}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://docs.example.com"
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                onClick={(e) => e.stopPropagation()}
              />
              
              {urlInput && (
                <div className="mt-3 text-xs text-purple-700 bg-purple-100 rounded-lg p-2">
                  <div className="flex items-center">
                    <Globe className="w-3 h-3 mr-2" />
                    <span>Ready to process: {new URL(urlInput).hostname}</span>
                  </div>
                </div>
              )}
            </motion.div>
          </div>

          {/* Process Button */}
          {canProcess() && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-center"
            >
              <button
                onClick={processContent}
                disabled={processing}
                className="flex items-center space-x-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-8 py-3 rounded-lg font-medium transition-colors shadow-sm"
              >
                {processing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Generate Articles</span>
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Processing Modal */}
      <AnimatePresence>
        {processModal.open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-60"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4"
            >
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h3 className="text-lg font-semibold text-gray-900">Processing Content</h3>
                <p className="text-sm text-gray-600">Transforming your content into knowledge articles</p>
              </div>

              <div className="p-6">
                {processModal.data ? (
                  // Results
                  <div className="text-center space-y-6">
                    <motion.div 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="p-4 bg-green-100 rounded-full inline-flex"
                    >
                      <CheckCircle2 className="w-12 h-12 text-green-600" />
                    </motion.div>
                    <div>
                      <h4 className="text-xl font-semibold text-gray-900 mb-2">Processing Complete!</h4>
                      <p className="text-gray-600">Your content has been successfully processed</p>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">{processModal.data.articlesGenerated}</div>
                          <div className="text-sm text-gray-600">Articles Generated</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-600">{processModal.data.mediaProcessed}</div>
                          <div className="text-sm text-gray-600">Media Processed</div>
                        </div>
                      </div>
                      <div className="pt-2 border-t border-gray-200">
                        <div className="text-sm text-gray-600">Processing time: <span className="font-medium">{processModal.data.processingTime}s</span></div>
                      </div>
                    </div>

                    <div className="text-left">
                      <h5 className="font-medium text-gray-900 mb-3">Generated Articles:</h5>
                      <div className="space-y-2">
                        {processModal.data.articleLinks.map((article, index) => (
                          <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                            <FileText className="w-4 h-4 text-blue-600" />
                            <div className="flex-1">
                              <div className="font-medium text-sm text-gray-900">{article.title}</div>
                              <div className="text-xs text-gray-600">{article.wordCount} words</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex justify-center space-x-4">
                      <button
                        onClick={closeModal}
                        className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg transition-colors"
                      >
                        Done
                      </button>
                      <button
                        onClick={() => {/* Navigate to library */}}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                      >
                        View in Library
                      </button>
                    </div>
                  </div>
                ) : (
                  // Processing steps
                  <div className="space-y-4">
                    {processSteps.map((step, index) => {
                      const Icon = step.icon;
                      const isActive = index === processModal.step - 1;
                      const isCompleted = index < processModal.step - 1;
                      const isPending = index >= processModal.step;

                      return (
                        <div key={step.id} className="flex items-center space-x-4">
                          <div className={`p-3 rounded-full border-2 transition-all ${
                            isCompleted ? 'bg-green-100 border-green-300' : 
                            isActive ? 'bg-blue-100 border-blue-300' : 
                            'bg-gray-50 border-gray-200'
                          }`}>
                            <Icon className={`w-6 h-6 transition-all ${
                              isCompleted ? 'text-green-600' : 
                              isActive ? 'text-blue-600' : 
                              'text-gray-400'
                            }`} />
                          </div>
                          <div className="flex-1">
                            <div className={`font-medium transition-all ${
                              isCompleted ? 'text-green-900' : 
                              isActive ? 'text-blue-900' : 
                              'text-gray-500'
                            }`}>
                              {step.label}
                            </div>
                            {isActive && (
                              <div className="text-sm text-blue-600">In progress...</div>
                            )}
                          </div>
                          <div className={`w-6 h-6 rounded-full transition-all ${
                            isCompleted ? 'bg-green-500' : 
                            isActive ? 'bg-blue-500' : 
                            'bg-gray-300'
                          }`}>
                            {isCompleted && (
                              <CheckCircle2 className="w-4 h-4 text-white m-1" />
                            )}
                          </div>
                        </div>
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