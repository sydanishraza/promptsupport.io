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
  Puzzle,
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
  ExternalLink as LinkIcon
} from 'lucide-react';

const KnowledgeEngineUpload = ({ isOpen, onClose, onUploadComplete }) => {
  const [activeBlock, setActiveBlock] = useState(null);
  const [files, setFiles] = useState([]);
  const [textContent, setTextContent] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [selectedIntegrations, setSelectedIntegrations] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processModal, setProcessModal] = useState({ open: false, step: 0, data: null });
  const fileInputRef = useRef();

  // Supported file formats
  const supportedFormats = {
    documents: ['.docx', '.pdf', '.ppt', '.pptx', '.xls', '.xlsx', '.csv', '.xml', '.html', '.md', '.txt'],
    media: ['.mp4', '.avi', '.mov', '.wmv', '.mp3', '.wav', '.jpg', '.jpeg', '.png', '.gif', '.webp']
  };

  // Available integrations
  const integrations = [
    { id: 'notion', name: 'Notion', icon: '📓', connected: false, status: 'Available' },
    { id: 'confluence', name: 'Confluence', icon: '🏢', connected: false, status: 'Available' },
    { id: 'github', name: 'GitHub', icon: '🐙', connected: false, status: 'Available' },
    { id: 'jira', name: 'JIRA', icon: '🎯', connected: false, status: 'Available' },
    { id: 'slack', name: 'Slack', icon: '💬', connected: false, status: 'Available' },
    { id: 'drive', name: 'Google Drive', icon: '📁', connected: false, status: 'Available' },
    { id: 'loom', name: 'Loom', icon: '🎥', connected: false, status: 'Available' },
    { id: 'youtube', name: 'YouTube', icon: '📺', connected: false, status: 'Available' }
  ];

  const processSteps = [
    { id: 'upload', label: 'Upload completed', icon: CheckCircle2 },
    { id: 'analyze', label: 'Resource is being analyzed', icon: Brain },
    { id: 'extract', label: 'Content extracted and structured', icon: Zap },
    { id: 'generate', label: 'Articles generated', icon: Sparkles },
    { id: 'media', label: 'Media processed', icon: ImageIcon }
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

  const toggleIntegration = (integrationId) => {
    setSelectedIntegrations(prev => 
      prev.includes(integrationId) 
        ? prev.filter(id => id !== integrationId)
        : [...prev, integrationId]
    );
  };

  const processContent = async () => {
    setProcessing(true);
    setProcessModal({ open: true, step: 0, data: null });

    // Simulate processing steps
    for (let i = 0; i < processSteps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1500));
      setProcessModal(prev => ({ ...prev, step: i + 1 }));
    }

    // Mock results
    const mockResults = {
      resourceName: files.length > 0 ? files[0].name : (textContent ? 'Direct Text Input' : urlInput || 'Selected Resources'),
      articlesGenerated: Math.floor(Math.random() * 5) + 2,
      mediaEmbedded: Math.floor(Math.random() * 8) + 1,
      articleLinks: [
        'Getting Started Guide',
        'Advanced Configuration',
        'Best Practices'
      ]
    };

    setProcessModal(prev => ({ ...prev, data: mockResults }));
    setProcessing(false);

    if (onUploadComplete) {
      onUploadComplete(mockResults);
    }
  };

  const canProcess = () => {
    return files.length > 0 || textContent.trim() || urlInput.trim() || selectedIntegrations.length > 0;
  };

  const closeModal = () => {
    setProcessModal({ open: false, step: 0, data: null });
    setFiles([]);
    setTextContent('');
    setUrlInput('');
    setSelectedIntegrations([]);
    setActiveBlock(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-3xl shadow-2xl max-w-6xl w-full max-h-[95vh] overflow-hidden relative"
      >
        {/* Gradient Header */}
        <div className="bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 text-white p-8 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 backdrop-blur-sm"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-white/20 backdrop-blur-sm rounded-2xl">
                <Brain className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-blue-100">
                  Content Upload Hub
                </h2>
                <p className="text-blue-100 mt-1">
                  Transform any content into intelligent knowledge base articles ✨
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-3 hover:bg-white/10 rounded-2xl transition-all duration-200 backdrop-blur-sm"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-8 max-h-[calc(95vh-200px)] overflow-y-auto">
          {/* Upload Blocks Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            
            {/* Upload File Block */}
            <motion.div
              whileHover={{ scale: 1.02, y: -5 }}
              className={`relative bg-gradient-to-br from-blue-50 to-indigo-100 border-2 border-dashed border-blue-300 rounded-3xl p-8 cursor-pointer transition-all duration-300 ${
                isDragOver ? 'border-blue-500 bg-blue-100' : ''
              } ${activeBlock === 'upload' ? 'ring-4 ring-blue-300 ring-opacity-50' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="text-center space-y-4">
                <div className="p-4 bg-blue-500 rounded-2xl inline-block shadow-lg">
                  <Upload className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Upload Files</h3>
                  <p className="text-gray-600 text-sm mb-4">Drag & drop or click to browse</p>
                  
                  {/* Format Tags */}
                  <div className="flex flex-wrap gap-2 justify-center">
                    {['DOCX', 'PDF', 'PPT', 'XLS', 'MD', 'HTML'].map(format => (
                      <span key={format} className="px-3 py-1 bg-blue-200 text-blue-800 rounded-full text-xs font-medium">
                        {format}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              {files.length > 0 && (
                <div className="mt-6 bg-white/70 backdrop-blur-sm rounded-2xl p-4">
                  <div className="text-sm font-medium text-gray-900 mb-2">
                    {files.length} file{files.length > 1 ? 's' : ''} selected
                  </div>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {files.map(file => (
                      <div key={file.id} className="flex items-center justify-between text-sm">
                        <span className="truncate text-gray-700">{file.name}</span>
                        <button
                          onClick={(e) => { e.stopPropagation(); removeFile(file.id); }}
                          className="p-1 hover:bg-red-100 rounded-full text-red-500"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept={supportedFormats.documents.concat(supportedFormats.media).join(',')}
                onChange={handleFileSelect}
                className="hidden"
              />
            </motion.div>

            {/* Paste Text Block */}
            <motion.div
              whileHover={{ scale: 1.02, y: -5 }}
              className={`bg-gradient-to-br from-green-50 to-emerald-100 border-2 border-dashed border-green-300 rounded-3xl p-8 transition-all duration-300 ${
                activeBlock === 'text' ? 'ring-4 ring-green-300 ring-opacity-50' : ''
              }`}
              onClick={() => setActiveBlock('text')}
            >
              <div className="text-center space-y-4">
                <div className="p-4 bg-green-500 rounded-2xl inline-block shadow-lg">
                  <Type className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Paste Text</h3>
                  <p className="text-gray-600 text-sm mb-4">Direct text input for quick processing</p>
                </div>
              </div>
              
              <textarea
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                placeholder="Paste your content here..."
                className="w-full h-32 mt-4 p-4 bg-white/70 backdrop-blur-sm border-2 border-green-200 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent text-sm"
                onClick={(e) => e.stopPropagation()}
              />
            </motion.div>

            {/* Enter URL Block */}
            <motion.div
              whileHover={{ scale: 1.02, y: -5 }}
              className={`bg-gradient-to-br from-purple-50 to-violet-100 border-2 border-dashed border-purple-300 rounded-3xl p-8 transition-all duration-300 ${
                activeBlock === 'url' ? 'ring-4 ring-purple-300 ring-opacity-50' : ''
              }`}
              onClick={() => setActiveBlock('url')}
            >
              <div className="text-center space-y-4">
                <div className="p-4 bg-purple-500 rounded-2xl inline-block shadow-lg">
                  <Link2 className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Enter URL</h3>
                  <p className="text-gray-600 text-sm mb-4">Crawl websites and extract content</p>
                  
                  {/* Supported Types */}
                  <div className="flex flex-wrap gap-2 justify-center">
                    {['Websites', 'Docs', 'GitHub', 'Notion', 'YouTube'].map(type => (
                      <span key={type} className="px-3 py-1 bg-purple-200 text-purple-800 rounded-full text-xs font-medium">
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://example.com/documentation"
                className="w-full mt-4 p-4 bg-white/70 backdrop-blur-sm border-2 border-purple-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent text-sm"
                onClick={(e) => e.stopPropagation()}
              />
            </motion.div>

            {/* Integrations Block */}
            <motion.div
              whileHover={{ scale: 1.02, y: -5 }}
              className={`bg-gradient-to-br from-orange-50 to-red-100 border-2 border-dashed border-orange-300 rounded-3xl p-8 transition-all duration-300 ${
                activeBlock === 'integrations' ? 'ring-4 ring-orange-300 ring-opacity-50' : ''
              }`}
              onClick={() => setActiveBlock('integrations')}
            >
              <div className="text-center space-y-4">
                <div className="p-4 bg-orange-500 rounded-2xl inline-block shadow-lg">
                  <Puzzle className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Integrations</h3>
                  <p className="text-gray-600 text-sm mb-4">Connect platforms and sync content</p>
                </div>
              </div>
              
              {/* Integration Cards */}
              <div className="grid grid-cols-4 gap-3 mt-4">
                {integrations.slice(0, 8).map(integration => (
                  <button
                    key={integration.id}
                    onClick={(e) => { e.stopPropagation(); toggleIntegration(integration.id); }}
                    className={`p-3 bg-white/70 backdrop-blur-sm rounded-xl hover:bg-white/90 transition-all duration-200 text-center ${
                      selectedIntegrations.includes(integration.id) ? 'ring-2 ring-orange-400 bg-orange-100' : ''
                    }`}
                  >
                    <div className="text-2xl mb-1">{integration.icon}</div>
                    <div className="text-xs font-medium text-gray-700 truncate">{integration.name}</div>
                  </button>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Action Button */}
          {canProcess() && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-center"
            >
              <button
                onClick={processContent}
                disabled={processing}
                className="group flex items-center space-x-3 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 text-white px-8 py-4 rounded-2xl font-bold text-lg transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50"
              >
                {processing ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-6 h-6 group-hover:rotate-12 transition-transform duration-300" />
                    <span>Generate Articles</span>
                    <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform duration-300" />
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
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-60"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full mx-4 overflow-hidden"
            >
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
                <h3 className="text-2xl font-bold">Processing Your Content</h3>
                <p className="text-blue-100 mt-1">Transforming your content with AI magic ✨</p>
              </div>

              <div className="p-8">
                {processModal.data ? (
                  // Results Summary
                  <div className="space-y-6">
                    <div className="text-center space-y-4">
                      <div className="p-4 bg-green-100 rounded-2xl inline-block">
                        <CheckCircle2 className="w-12 h-12 text-green-600" />
                      </div>
                      <h4 className="text-2xl font-bold text-gray-900">Processing Complete!</h4>
                    </div>

                    <div className="bg-gray-50 rounded-2xl p-6 space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-700">✅ Resource processed</span>
                        <span className="text-gray-600">{processModal.data.resourceName}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-700">📄 Articles generated</span>
                        <span className="text-gray-600">{processModal.data.articlesGenerated} articles</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-700">🖼 Images/media embedded</span>
                        <span className="text-gray-600">{processModal.data.mediaEmbedded} assets</span>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <h5 className="font-semibold text-gray-900">Generated Articles:</h5>
                      {processModal.data.articleLinks.map((article, index) => (
                        <div key={index} className="flex items-center space-x-3 p-3 bg-blue-50 rounded-xl">
                          <FileText className="w-5 h-5 text-blue-600" />
                          <span className="text-gray-800">{article}</span>
                          <LinkIcon className="w-4 h-4 text-gray-400 ml-auto" />
                        </div>
                      ))}
                    </div>

                    <div className="flex justify-center space-x-4 pt-4">
                      <button
                        onClick={closeModal}
                        className="px-6 py-3 bg-gray-200 text-gray-800 rounded-xl font-medium hover:bg-gray-300 transition-colors"
                      >
                        Done
                      </button>
                      <button
                        onClick={() => {/* Navigate to Content Library */}}
                        className="px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors"
                      >
                        View in Library
                      </button>
                    </div>
                  </div>
                ) : (
                  // Processing Steps
                  <div className="space-y-6">
                    {processSteps.map((step, index) => {
                      const Icon = step.icon;
                      const isActive = index === processModal.step - 1;
                      const isCompleted = index < processModal.step - 1;
                      const isPending = index >= processModal.step;

                      return (
                        <div key={step.id} className="flex items-center space-x-4">
                          <div className={`p-3 rounded-xl transition-all duration-300 ${
                            isCompleted ? 'bg-green-100' : 
                            isActive ? 'bg-blue-100' : 
                            'bg-gray-100'
                          }`}>
                            <Icon className={`w-6 h-6 ${
                              isCompleted ? 'text-green-600' : 
                              isActive ? 'text-blue-600 animate-pulse' : 
                              'text-gray-400'
                            }`} />
                          </div>
                          <div className="flex-1">
                            <div className={`font-medium ${
                              isCompleted ? 'text-green-900' : 
                              isActive ? 'text-blue-900' : 
                              'text-gray-600'
                            }`}>
                              {step.label}
                            </div>
                          </div>
                          <div className={`w-6 h-6 rounded-full transition-all duration-300 ${
                            isCompleted ? 'bg-green-500' : 
                            isActive ? 'bg-blue-500 animate-ping' : 
                            'bg-gray-300'
                          }`} />
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