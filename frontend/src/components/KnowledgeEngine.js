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
  Settings,
  Monitor,
  Camera,
  Scissors,
  RefreshCw,
  ExternalLink,
  Play,
  Pause,
  StopCircle,
  Save
} from 'lucide-react';

const KnowledgeEngine = ({ activeModule = "upload" }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [processingJobs, setProcessingJobs] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [urlInput, setUrlInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingType, setRecordingType] = useState('screen'); // 'screen', 'audio', 'video'
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [showUrlModal, setShowUrlModal] = useState(false);
  
  const fileInputRef = useRef(null);
  const recordingInterval = useRef(null);

  // Get backend URL from environment
  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Fetch system status and data on component mount
  useEffect(() => {
    fetchSystemStatus();
    fetchDocuments();
    fetchProcessingJobs();
  }, []);

  // Recording timer
  useEffect(() => {
    if (isRecording) {
      recordingInterval.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(recordingInterval.current);
      setRecordingDuration(0);
    }
    return () => clearInterval(recordingInterval.current);
  }, [isRecording]);

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
      // Sort documents by creation date (latest first)
      const sortedDocs = (data.documents || []).sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      );
      setDocuments(sortedDocs);
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
          source: 'knowledge_engine_ui',
          type: 'file_upload'
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
            fileType: result.file_type,
            uploadTime: new Date()
          }]);
          
          // Process content for Content Library
          await processIntoContentLibrary(result.job_id, file.name, 'file');
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

  const handleUrlUpload = async (url) => {
    if (!url.trim()) return;
    
    setIsProcessing(true);
    try {
      // For now, we'll process the URL as text content
      // In a full implementation, this would scrape the website
      const response = await fetch(`${backendUrl}/api/content/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: `Website content from: ${url}`,
          content_type: 'url',
          metadata: {
            url: url,
            processed_at: new Date().toISOString(),
            source: 'knowledge_engine_ui',
            type: 'url_upload'
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        setUploadedFiles(prev => [...prev, {
          id: result.job_id,
          name: `Website: ${url}`,
          status: result.status,
          chunksCreated: result.chunks_created,
          type: 'url',
          uploadTime: new Date()
        }]);
        
        // Process content for Content Library
        await processIntoContentLibrary(result.job_id, url, 'url');
        fetchDocuments();
      }
    } catch (error) {
      console.error('URL processing error:', error);
    }
    setIsProcessing(false);
    setUrlInput('');
    setShowUrlModal(false);
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
            source: 'knowledge_engine_ui',
            type: 'text_processing'
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
          type: 'text',
          uploadTime: new Date()
        }]);
        
        // Process content for Content Library
        await processIntoContentLibrary(result.job_id, 'Text Content', 'text');
        fetchDocuments();
      } else {
        console.error('Text processing failed:', await response.text());
      }
    } catch (error) {
      console.error('Text processing error:', error);
    }
    setIsProcessing(false);
  };

  // AI-powered content processing for Content Library integration
  const processIntoContentLibrary = async (jobId, title, type) => {
    try {
      // This would typically:
      // 1. Extract key information from processed chunks
      // 2. Generate a structured article with AI
      // 3. Create tags and metadata
      // 4. Save to Content Library
      
      console.log(`Processing ${title} (${type}) for Content Library integration`);
      // TODO: Implement actual Content Library integration
    } catch (error) {
      console.error('Content Library processing error:', error);
    }
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

  const startRecording = (type) => {
    setRecordingType(type);
    setIsRecording(true);
    // TODO: Implement actual recording functionality
    console.log(`Started ${type} recording`);
  };

  const stopRecording = () => {
    setIsRecording(false);
    // TODO: Process recorded content
    console.log(`Stopped ${recordingType} recording after ${recordingDuration} seconds`);
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const viewDocument = (doc) => {
    // TODO: Implement document preview modal
    console.log('Viewing document:', doc);
  };

  const renderSystemStatus = () => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Brain className="w-5 h-5 mr-2 text-blue-600" />
          Knowledge Engine Status
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

  const renderContentUpload = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Content Upload</h1>
        <p className="text-gray-600 mb-6">
          Upload and process content from multiple sources to build your knowledge base
        </p>

        {/* Upload Methods Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          
          {/* File Upload */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
               onClick={() => fileInputRef.current?.click()}>
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">File Upload</h3>
            <p className="text-sm text-gray-500">
              Upload documents, images, audio, and video files
            </p>
          </div>

          {/* Website/Link Upload */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
               onClick={() => setShowUrlModal(true)}>
            <Globe className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Website/Link</h3>
            <p className="text-sm text-gray-500">
              Scrape websites, YouTube videos, GitHub repos
            </p>
          </div>

          {/* Screen Recording */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
               onClick={() => startRecording('screen')}>
            <Monitor className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Screen Recording</h3>
            <p className="text-sm text-gray-500">
              Record your screen with audio narration
            </p>
          </div>

          {/* Video Recording */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
               onClick={() => startRecording('video')}>
            <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Video Recording</h3>
            <p className="text-sm text-gray-500">
              Record video content with your camera
            </p>
          </div>

          {/* Audio Recording */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
               onClick={() => startRecording('audio')}>
            <Mic className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Audio Recording</h3>
            <p className="text-sm text-gray-500">
              Record audio notes and conversations
            </p>
          </div>

          {/* Snipping Tool */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer">
            <Scissors className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Snipping Tool</h3>
            <p className="text-sm text-gray-500">
              Capture and annotate screenshots
            </p>
          </div>
        </div>

        {/* Text Processing Section */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Direct Text Processing</h3>
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
                const textarea = e.target.closest('.bg-gray-50').querySelector('textarea');
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

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={(e) => handleFileUpload(e.target.files)}
          className="hidden"
          accept="*/*"
        />
      </div>

      {/* Recording Status */}
      {isRecording && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-red-700 font-medium">
                Recording {recordingType} - {formatDuration(recordingDuration)}
              </span>
            </div>
            <button
              onClick={stopRecording}
              className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              <StopCircle className="w-4 h-4 mr-2" />
              Stop Recording
            </button>
          </div>
        </div>
      )}

      {/* Recent Uploads */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Uploads</h3>
          <div className="space-y-3">
            {uploadedFiles.slice(0, 5).map((file) => (
              <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {file.chunksCreated} chunks created • {file.status} • {file.uploadTime?.toLocaleTimeString()}
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

  const renderUploadedContent = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Uploaded Content</h1>
            <p className="text-gray-600">
              Manage and search through all your processed content
            </p>
          </div>
          <button
            onClick={fetchDocuments}
            className="flex items-center px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>

        {/* Search Bar */}
        <div className="flex space-x-4 mb-6">
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

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Search Results ({searchResults.length})
            </h3>
            <div className="space-y-4">
              {searchResults.map((result, index) => (
                <div key={result.id} className="p-4 border border-gray-200 rounded-lg bg-blue-50">
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

        {/* Documents List */}
        {documents.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Database className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg mb-2">No content processed yet</p>
            <p className="text-sm">Upload some files or process text to get started</p>
          </div>
        ) : (
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              All Documents ({documents.length})
            </h3>
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 mb-2">{doc.content_preview}</p>
                    <div className="text-sm text-gray-500">
                      <span>ID: {doc.id}</span>
                      {doc.metadata?.source && (
                        <span className="ml-4">Source: {doc.metadata.source}</span>
                      )}
                      {doc.metadata?.type && (
                        <span className="ml-4">Type: {doc.metadata.type}</span>
                      )}
                      {doc.created_at && (
                        <span className="ml-4">
                          Created: {new Date(doc.created_at).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button 
                      onClick={() => viewDocument(doc)}
                      className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                      title="View document"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    {doc.metadata?.url && (
                      <button 
                        onClick={() => window.open(doc.metadata.url, '_blank')}
                        className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded"
                        title="Open source URL"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderChatWithEngine = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Chat with Engine</h1>
        <p className="text-gray-600 mb-6">
          Ask questions and get answers based on your processed content
        </p>
        
        {/* Chat History */}
        <div className="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 mb-6">
          {chatHistory.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg mb-2">Start a conversation with your AI assistant</p>
                <p className="text-sm">Your messages will be answered using your processed content as context</p>
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
                    className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : message.error
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p>{message.content}</p>
                    {message.contextChunks !== undefined && (
                      <p className="text-xs mt-2 opacity-70">
                        ✨ Used {message.contextChunks} content chunks
                      </p>
                    )}
                    <p className="text-xs mt-1 opacity-70">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
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
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleChatMessage();
              }
            }}
          />
          <button
            onClick={handleChatMessage}
            disabled={!chatMessage.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            Send
          </button>
        </div>
      </div>
    </div>
  );

  const renderProcessingJobs = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Processing Jobs</h1>
        <p className="text-gray-600 mb-6">
          Monitor real-time processing status and background job logs
        </p>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <p className="text-sm text-blue-600 font-medium">Total Jobs</p>
                <p className="text-2xl font-bold text-blue-900">{processingJobs}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <p className="text-sm text-green-600 font-medium">Completed</p>
                <p className="text-2xl font-bold text-green-900">{uploadedFiles.filter(f => f.status === 'completed').length}</p>
              </div>
            </div>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4">
            <div className="flex items-center">
              <Loader className="w-8 h-8 text-yellow-600 mr-3" />
              <div>
                <p className="text-sm text-yellow-600 font-medium">Processing</p>
                <p className="text-2xl font-bold text-yellow-900">{uploadedFiles.filter(f => f.status === 'processing').length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Job Activity */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          {uploadedFiles.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Clock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No processing jobs yet</p>
              <p className="text-sm mt-2">Upload content to see job activity</p>
            </div>
          ) : (
            <div className="space-y-3">
              {uploadedFiles.slice(0, 10).map((job) => (
                <div key={job.id} className="flex items-center justify-between p-3 bg-white rounded-lg">
                  <div className="flex items-center space-x-3">
                    {job.status === 'completed' ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : job.status === 'processing' ? (
                      <Loader className="w-5 h-5 text-yellow-600 animate-spin" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-600" />
                    )}
                    <div>
                      <p className="font-medium text-gray-900">{job.name}</p>
                      <p className="text-sm text-gray-500">
                        {job.chunksCreated} chunks • {job.status} • {job.uploadTime?.toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    job.status === 'completed' ? 'bg-green-100 text-green-800' :
                    job.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {job.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // URL Modal
  const urlModal = showUrlModal && (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Add Website or Link</h3>
          <button onClick={() => setShowUrlModal(false)}>
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>
        <div className="space-y-4">
          <input
            type="url"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="Enter URL (website, YouTube, GitHub, etc.)"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleUrlUpload(urlInput);
              }
            }}
          />
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setShowUrlModal(false)}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={() => handleUrlUpload(urlInput)}
              disabled={!urlInput.trim() || isProcessing}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isProcessing ? <Loader className="w-4 h-4 animate-spin" /> : 'Process URL'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* System Status - Always show */}
      {renderSystemStatus()}

      {/* Module Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeModule}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.2 }}
        >
          {activeModule === 'upload' && renderContentUpload()}
          {activeModule === 'content' && renderUploadedContent()}
          {activeModule === 'chat' && renderChatWithEngine()}
          {activeModule === 'jobs' && renderProcessingJobs()}
          {!activeModule && renderContentUpload()} {/* Default */}
        </motion.div>
      </AnimatePresence>

      {/* URL Modal */}
      {urlModal}
    </div>
  );
};

export default KnowledgeEngine;