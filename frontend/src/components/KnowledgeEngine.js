import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  Link, 
  Mic, 
  File, 
  Globe, 
  Video,
  Plus,
  X,
  CheckCircle,
  AlertCircle,
  Loader,
  Search,
  MessageSquare,
  Database,
  FileText,
  Trash2,
  Download,
  Eye,
  Clock,
  Zap,
  Brain,
  Settings
} from 'lucide-react';

const KnowledgeEngine = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [processingJobs, setProcessingJobs] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const fileInputRef = useRef(null);

  // Get backend URL from environment
  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  const tabs = [
    { id: 'upload', label: 'Content Upload', icon: Upload, description: 'Upload files and process content' },
    { id: 'search', label: 'Search', icon: Search, description: 'Search across processed content' },
    { id: 'chat', label: 'AI Chat', icon: MessageSquare, description: 'Chat with AI using your content' },
    { id: 'documents', label: 'Documents', icon: Database, description: 'Manage processed documents' },
    { id: 'jobs', label: 'Processing Jobs', icon: Clock, description: 'Track processing status' }
  ];

  // Fetch system status on component mount
  useEffect(() => {
    fetchSystemStatus();
    fetchDocuments();
    fetchProcessingJobs();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/health`);
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/documents`);
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

  const fetchProcessingJobs = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/status`);
      const data = await response.json();
      setProcessingJobs(data.statistics?.processing_jobs || 0);
    } catch (error) {
      console.error('Failed to fetch processing jobs:', error);
    }
  };

  const handleFileUpload = async (files) => {
    const newFiles = Array.from(files);
    setIsProcessing(true);

    for (const file of newFiles) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('metadata', JSON.stringify({
          uploaded_at: new Date().toISOString(),
          source: 'knowledge_engine_ui'
        }));

        const response = await fetch(`${backendUrl}/api/content/upload`, {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          const result = await response.json();
          setUploadedFiles(prev => [...prev, {
            id: result.job_id,
            name: file.name,
            status: result.status,
            chunksCreated: result.chunks_created,
            fileType: result.file_type
          }]);
        } else {
          console.error('Upload failed:', await response.text());
        }
      } catch (error) {
        console.error('Upload error:', error);
      }
    }

    setIsProcessing(false);
    fetchDocuments();
  };

  const handleTextProcessing = async (text) => {
    setIsProcessing(true);
    try {
      const response = await fetch(`${backendUrl}/api/content/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: text,
          content_type: 'text',
          metadata: {
            processed_at: new Date().toISOString(),
            source: 'knowledge_engine_ui'
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        setUploadedFiles(prev => [...prev, {
          id: result.job_id,
          name: 'Text Content',
          status: result.status,
          chunksCreated: result.chunks_created,
          type: 'text'
        }]);
        fetchDocuments();
      } else {
        console.error('Text processing failed:', await response.text());
      }
    } catch (error) {
      console.error('Text processing error:', error);
    }
    setIsProcessing(false);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const response = await fetch(`${backendUrl}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: searchQuery,
          limit: 10
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
      } else {
        console.error('Search failed:', await response.text());
      }
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const handleChatMessage = async () => {
    if (!chatMessage.trim()) return;

    const userMessage = { role: 'user', content: chatMessage, timestamp: new Date() };
    setChatHistory(prev => [...prev, userMessage]);
    setChatMessage('');

    try {
      const formData = new FormData();
      formData.append('message', chatMessage);
      formData.append('session_id', 'knowledge_engine_session');
      formData.append('model_provider', 'openai');
      formData.append('model_name', 'gpt-4o');

      const response = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage = { 
          role: 'assistant', 
          content: data.response, 
          timestamp: new Date(),
          contextChunks: data.context_chunks_used
        };
        setChatHistory(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error processing your message.', 
          timestamp: new Date(),
          error: true
        };
        setChatHistory(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error processing your message.', 
        timestamp: new Date(),
        error: true
      };
      setChatHistory(prev => [...prev, errorMessage]);
    }
  };

  const renderSystemStatus = () => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Brain className="w-5 h-5 mr-2 text-blue-600" />
          Enhanced Content Engine Status
        </h3>
        {systemStatus?.status === 'healthy' && (
          <span className="flex items-center text-green-600 text-sm font-medium">
            <CheckCircle className="w-4 h-4 mr-1" />
            All Systems Operational
          </span>
        )}
      </div>
      
      {systemStatus && (
        <div className="mt-4 grid grid-cols-2 lg:grid-cols-5 gap-4">
          {Object.entries(systemStatus.services || {}).map(([service, status]) => (
            <div key={service} className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                status === 'connected' || status === 'configured' ? 'bg-green-400' : 'bg-gray-400'
              }`} />
              <span className="text-sm text-gray-600 capitalize">{service}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderUploadTab = () => (
    <div className="space-y-6">
      {/* File Upload Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">File Upload</h3>
        
        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
        >
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-600">Drop files here or click to upload</p>
          <p className="text-sm text-gray-400 mt-2">
            Supports text, audio, video, and image files
          </p>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={(e) => handleFileUpload(e.target.files)}
          className="hidden"
          accept="*/*"
        />
      </div>

      {/* Text Processing Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Text Content Processing</h3>
        <textarea
          placeholder="Paste text content here for processing..."
          rows="6"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.ctrlKey && e.target.value.trim()) {
              handleTextProcessing(e.target.value);
              e.target.value = '';
            }
          }}
        />
        <div className="flex justify-between items-center mt-4">
          <span className="text-sm text-gray-500">Press Ctrl+Enter to process</span>
          <button
            onClick={(e) => {
              const textarea = e.target.closest('.bg-white').querySelector('textarea');
              if (textarea.value.trim()) {
                handleTextProcessing(textarea.value);
                textarea.value = '';
              }
            }}
            disabled={isProcessing}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
          >
            {isProcessing ? <Loader className="w-4 h-4 animate-spin mr-2" /> : <Zap className="w-4 h-4 mr-2" />}
            Process Text
          </button>
        </div>
      </div>

      {/* Recently Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Uploads</h3>
          <div className="space-y-3">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {file.chunksCreated} chunks created • {file.status}
                    </p>
                  </div>
                </div>
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderSearchTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Search</h3>
        
        <div className="flex space-x-4">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search across all processed content..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
          />
          <button
            onClick={handleSearch}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <Search className="w-4 h-4 mr-2" />
            Search
          </button>
        </div>
      </div>

      {searchResults.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Search Results ({searchResults.length})
          </h3>
          <div className="space-y-4">
            {searchResults.map((result, index) => (
              <div key={result.id} className="p-4 border border-gray-200 rounded-lg">
                <p className="text-gray-800 mb-2">{result.content}</p>
                <div className="text-sm text-gray-500">
                  <span>ID: {result.id}</span>
                  {result.metadata?.source && (
                    <span className="ml-4">Source: {result.metadata.source}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderChatTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Chat with Your Content</h3>
        
        {/* Chat History */}
        <div className="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 mb-4">
          {chatHistory.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>Start a conversation with your AI assistant</p>
                <p className="text-sm mt-2">Your messages will be answered using your processed content as context</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {chatHistory.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : message.error
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p>{message.content}</p>
                    {message.contextChunks !== undefined && (
                      <p className="text-xs mt-1 opacity-70">
                        Used {message.contextChunks} content chunks
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Chat Input */}
        <div className="flex space-x-4">
          <input
            type="text"
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
            placeholder="Ask questions about your content..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleChatMessage();
              }
            }}
          />
          <button
            onClick={handleChatMessage}
            disabled={!chatMessage.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            Send
          </button>
        </div>
      </div>
    </div>
  );

  const renderDocumentsTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Processed Documents</h3>
          <button
            onClick={fetchDocuments}
            className="flex items-center px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
          >
            <Database className="w-4 h-4 mr-1" />
            Refresh
          </button>
        </div>
        
        {documents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Database className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No documents processed yet</p>
            <p className="text-sm mt-2">Upload some files or process text to get started</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{doc.content_preview}</p>
                    <div className="text-sm text-gray-500 mt-2">
                      <span>ID: {doc.id}</span>
                      {doc.metadata?.source && (
                        <span className="ml-4">Source: {doc.metadata.source}</span>
                      )}
                      {doc.created_at && (
                        <span className="ml-4">Created: {new Date(doc.created_at).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button className="p-1 text-gray-400 hover:text-blue-600">
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderJobsTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Jobs Status</h3>
        
        <div className="text-center py-8">
          <Clock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500">Job tracking interface</p>
          <p className="text-sm text-gray-400 mt-2">
            Total processing jobs: {processingJobs}
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Enhanced Content Engine</h1>
        <p className="text-gray-600">
          AI-powered content processing, search, and intelligent chat system
        </p>
      </div>

      {/* System Status */}
      {renderSystemStatus()}

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon size={18} />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'upload' && renderUploadTab()}
              {activeTab === 'search' && renderSearchTab()}
              {activeTab === 'chat' && renderChatTab()}
              {activeTab === 'documents' && renderDocumentsTab()}
              {activeTab === 'jobs' && renderJobsTab()}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeEngine;
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 20;
      if (progress >= 100) {
        progress = 100;
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileId ? {
            ...f,
            status: 'completed',
            progress,
            metadata: {
              chunks: Math.floor(Math.random() * 50) + 10,
              words: Math.floor(Math.random() * 5000) + 500,
              extractedAt: new Date().toISOString()
            }
          } : f
        ));
        clearInterval(interval);
      } else {
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileId ? { ...f, progress } : f
        ));
      }
    }, 200);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    handleFileUpload(files);
  };

  const addUrlField = () => {
    setUrls(prev => [...prev, '']);
  };

  const removeUrlField = (index) => {
    setUrls(prev => prev.filter((_, i) => i !== index));
  };

  const updateUrl = (index, value) => {
    setUrls(prev => prev.map((url, i) => i === index ? value : url));
  };

  const processUrls = () => {
    const validUrls = urls.filter(url => url.trim());
    validUrls.forEach(url => {
      const urlId = Date.now() + Math.random();
      setProcessingStatus(prev => ({
        ...prev,
        [urlId]: { url, status: 'processing', progress: 0 }
      }));
      
      // Simulate URL processing
      simulateUrlProcessing(urlId, url);
    });
  };

  const simulateUrlProcessing = (urlId, url) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress >= 100) {
        progress = 100;
        setProcessingStatus(prev => ({
          ...prev,
          [urlId]: {
            ...prev[urlId],
            status: 'completed',
            progress,
            metadata: {
              title: `Content from ${new URL(url).hostname}`,
              words: Math.floor(Math.random() * 3000) + 200,
              chunks: Math.floor(Math.random() * 30) + 5
            }
          }
        }));
        clearInterval(interval);
      } else {
        setProcessingStatus(prev => ({
          ...prev,
          [urlId]: { ...prev[urlId], progress }
        }));
      }
    }, 300);
  };

  const startRecording = () => {
    setIsRecording(true);
    // In a real implementation, this would access navigator.mediaDevices
    setTimeout(() => setIsRecording(false), 5000); // Auto-stop after 5s for demo
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'processing':
        return <Loader className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'files':
        return (
          <div className="space-y-6">
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors"
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                className="hidden"
                onChange={(e) => handleFileUpload(e.target.files)}
                accept=".pdf,.doc,.docx,.txt,.md,.csv,.mp4,.mp3,.wav,.mov,.avi"
              />
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Upload Files</h3>
              <p className="text-gray-600 mb-4">
                Drag and drop files here, or click to select files
              </p>
              <p className="text-sm text-gray-500">
                Supports: PDF, DOCX, TXT, MD, CSV, MP4, MP3, WAV, MOV, AVI
              </p>
            </div>

            {uploadedFiles.length > 0 && (
              <div className="space-y-4">
                <h3 className="font-medium text-gray-900">Processing Files</h3>
                {uploadedFiles.map((file) => (
                  <div key={file.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                          📄
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{file.name}</p>
                          <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                        </div>
                      </div>
                      {getStatusIcon(file.status)}
                    </div>
                    
                    {file.status === 'processing' && (
                      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${file.progress}%` }}
                        />
                      </div>
                    )}

                    {file.metadata && (
                      <div className="text-sm text-gray-600 space-x-4">
                        <span>{file.metadata.chunks} chunks</span>
                        <span>{file.metadata.words} words</span>
                        <span>Processed {new Date(file.metadata.extractedAt).toLocaleTimeString()}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 'urls':
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-medium text-blue-900 mb-2">Supported URL Types</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-blue-800">
                <div>
                  <strong>Websites:</strong> Public pages, documentation sites
                </div>
                <div>
                  <strong>GitHub:</strong> Repositories, README files, wikis
                </div>
                <div>
                  <strong>YouTube:</strong> Video transcripts and metadata
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-gray-900">Add URLs</h3>
                <button
                  onClick={addUrlField}
                  className="flex items-center space-x-1 text-blue-600 hover:text-blue-700"
                >
                  <Plus size={16} />
                  <span>Add URL</span>
                </button>
              </div>

              {urls.map((url, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => updateUrl(index, e.target.value)}
                    placeholder="https://docs.example.com or github.com/user/repo"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  {urls.length > 1 && (
                    <button
                      onClick={() => removeUrlField(index)}
                      className="p-2 text-gray-400 hover:text-gray-600"
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              ))}

              <button
                onClick={processUrls}
                disabled={!urls.some(url => url.trim())}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white py-3 rounded-lg font-medium"
              >
                Process URLs
              </button>
            </div>

            {Object.keys(processingStatus).length > 0 && (
              <div className="space-y-4">
                <h3 className="font-medium text-gray-900">URL Processing Status</h3>
                {Object.entries(processingStatus).map(([id, status]) => (
                  <div key={id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="font-medium text-gray-900 truncate">{status.url}</p>
                        {status.metadata && (
                          <p className="text-sm text-gray-600">{status.metadata.title}</p>
                        )}
                      </div>
                      {getStatusIcon(status.status)}
                    </div>
                    
                    {status.status === 'processing' && (
                      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${status.progress}%` }}
                        />
                      </div>
                    )}

                    {status.metadata && (
                      <div className="text-sm text-gray-600 space-x-4">
                        <span>{status.metadata.chunks} chunks</span>
                        <span>{status.metadata.words} words</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 'recorder':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className={`mx-auto w-32 h-32 rounded-full flex items-center justify-center mb-6 ${
                isRecording ? 'bg-red-100 animate-pulse' : 'bg-gray-100'
              }`}>
                <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
                  isRecording ? 'bg-red-500' : 'bg-gray-400'
                }`}>
                  <Mic className={`h-8 w-8 ${isRecording ? 'text-white' : 'text-gray-600'}`} />
                </div>
              </div>

              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {isRecording ? 'Recording...' : 'Audio/Video Recorder'}
              </h3>
              <p className="text-gray-600 mb-6">
                {isRecording 
                  ? 'Click stop when finished recording' 
                  : 'Record audio or video content directly in your browser'
                }
              </p>

              <div className="flex items-center justify-center space-x-4">
                <button
                  onClick={startRecording}
                  disabled={isRecording}
                  className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                    isRecording
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-red-600 hover:bg-red-700 text-white'
                  }`}
                >
                  {isRecording ? 'Recording...' : 'Start Recording'}
                </button>

                {isRecording && (
                  <button
                    onClick={() => setIsRecording(false)}
                    className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium"
                  >
                    Stop Recording
                  </button>
                )}
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-medium text-yellow-900 mb-2">Recording Features</h4>
              <ul className="text-sm text-yellow-800 space-y-1">
                <li>• Audio recording with automatic transcription</li>
                <li>• Screen recording with voice narration</li>
                <li>• Automatic processing and chunking</li>
                <li>• Integration with knowledge base</li>
              </ul>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Knowledge Engine</h1>
        <p className="text-gray-600">
          Entry point for content ingestion and orchestration. Upload files, process URLs, or record content directly.
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {React.createElement(tab.icon, { size: 16 })}
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          <div className="mb-6">
            <p className="text-gray-600">
              {tabs.find(tab => tab.id === activeTab)?.description}
            </p>
          </div>

          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {renderTabContent()}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeEngine;