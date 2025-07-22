import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [documents, setDocuments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [sessionId] = useState(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');
  const [contentSource, setContentSource] = useState('files'); // files, urls, recorder
  const [urlInput, setUrlInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadDocuments();
    loadChatHistory();
    loadAnalytics();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadDocuments = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/documents`);
      const data = await response.json();
      if (!data.error) {
        setDocuments(data);
      }
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/chat/history/${sessionId}`);
      const data = await response.json();
      if (!data.error) {
        const formattedHistory = data.map(record => ([
          { type: 'user', content: record.user_message },
          { type: 'ai', content: record.ai_response, sources: record.sources }
        ])).flat();
        setMessages(formattedHistory);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/analytics/content`);
      const data = await response.json();
      if (!data.error) {
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const handleFileUpload = async (files) => {
    setIsLoading(true);
    setUploadStatus('Uploading and processing...');

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${backendUrl}/api/upload`, {
          method: 'POST',
          body: formData,
        });

        const result = await response.json();
        if (result.error) {
          setUploadStatus(`Error uploading ${file.name}: ${result.error}`);
        } else {
          setUploadStatus(`Successfully uploaded ${file.name}!`);
          await loadDocuments();
          await loadAnalytics();
        }
      } catch (error) {
        setUploadStatus(`Error uploading ${file.name}: ${error.message}`);
      }
    }

    setIsLoading(false);
    setTimeout(() => setUploadStatus(''), 3000);
  };

  const handleUrlSubmit = async () => {
    if (!urlInput.trim()) return;
    
    setIsLoading(true);
    setUploadStatus('Processing URL...');
    
    try {
      const response = await fetch(`${backendUrl}/api/process-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: urlInput,
          source_type: 'webpage'
        })
      });
      
      const result = await response.json();
      if (result.error) {
        setUploadStatus(`Error processing URL: ${result.error}`);
      } else {
        setUploadStatus(`Successfully processed: ${result.title || urlInput}`);
        setUrlInput('');
        await loadDocuments();
        await loadAnalytics();
      }
    } catch (error) {
      setUploadStatus(`Error processing URL: ${error.message}`);
    }
    
    setIsLoading(false);
    setTimeout(() => setUploadStatus(''), 3000);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: true, 
        video: false 
      });
      
      const recorder = new MediaRecorder(stream);
      const chunks = [];
      
      recorder.ondataavailable = (e) => {
        chunks.push(e.data);
      };
      
      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        await processRecording(audioBlob);
      };
      
      setMediaRecorder(recorder);
      recorder.start();
      setIsRecording(true);
      setUploadStatus('Recording audio...');
      
    } catch (error) {
      setUploadStatus(`Recording failed: ${error.message}`);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      setUploadStatus('Processing recording...');
    }
  };

  const processRecording = async (audioBlob) => {
    setIsLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, `recording_${Date.now()}.wav`);
      
      const response = await fetch(`${backendUrl}/api/process-recording`, {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      if (result.error) {
        setUploadStatus(`Error processing recording: ${result.error}`);
      } else {
        setUploadStatus('Recording processed successfully!');
        await loadDocuments();
        await loadAnalytics();
      }
    } catch (error) {
      setUploadStatus(`Error processing recording: ${error.message}`);
    }
    
    setIsLoading(false);
    setTimeout(() => setUploadStatus(''), 3000);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    handleFileUpload(files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    handleFileUpload(files);
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const userMessage = { type: 'user', content: currentMessage };
    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentMessage,
          session_id: sessionId,
        }),
      });

      const data = await response.json();
      if (data.error) {
        setMessages(prev => [...prev, {
          type: 'ai',
          content: `Error: ${data.error}`,
          sources: []
        }]);
      } else {
        setMessages(prev => [...prev, {
          type: 'ai',
          content: data.response,
          sources: data.sources || []
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'ai',
        content: `Error: ${error.message}`,
        sources: []
      }]);
    }

    setIsLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-lg">P</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">PromptSupport</h1>
                <p className="text-sm text-gray-500">Enhanced Content Engine</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-gray-600">AI-Native Support Platform</p>
              {analytics && (
                <p className="text-sm text-gray-500">
                  {analytics.total_documents} docs • {analytics.content_chunks} chunks • {analytics.total_chats} chats
                </p>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('upload')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'upload'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Content Engine
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'chat'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              AI Support Chat
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {activeTab === 'upload' && (
          <div className="space-y-6">
            {/* Content Source Selection */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Knowledge Input Sources</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => setContentSource('files')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    contentSource === 'files' 
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-200 hover:border-purple-300'
                  }`}
                >
                  <div className="text-center">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                      📁
                    </div>
                    <h3 className="font-medium">Files</h3>
                    <p className="text-sm text-gray-500">Upload documents, videos, audio</p>
                  </div>
                </button>
                
                <button
                  onClick={() => setContentSource('urls')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    contentSource === 'urls' 
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-200 hover:border-purple-300'
                  }`}
                >
                  <div className="text-center">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                      🌐
                    </div>
                    <h3 className="font-medium">URLs</h3>
                    <p className="text-sm text-gray-500">Process websites, GitHub, YouTube</p>
                  </div>
                </button>
                
                <button
                  onClick={() => setContentSource('recorder')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    contentSource === 'recorder' 
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-200 hover:border-purple-300'
                  }`}
                >
                  <div className="text-center">
                    <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                      🎙️
                    </div>
                    <h3 className="font-medium">Recorder</h3>
                    <p className="text-sm text-gray-500">Record audio directly</p>
                  </div>
                </button>
              </div>
            </div>

            {/* File Upload Section */}
            {contentSource === 'files' && (
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Upload Files</h3>
                
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
                    isDragging
                      ? 'border-purple-400 bg-purple-50'
                      : 'border-gray-300 hover:border-purple-400 hover:bg-gray-50'
                  }`}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    className="hidden"
                    accept=".txt,.md,.doc,.docx,.pdf,.mp3,.wav,.mp4,.mov,.avi"
                    onChange={handleFileSelect}
                  />
                  
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto">
                      <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-xl font-medium text-gray-900">
                        Drop files here or click to browse
                      </p>
                      <p className="text-gray-500">
                        Documents, PDFs, audio, video files supported
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* URL Processing Section */}
            {contentSource === 'urls' && (
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Process URLs</h3>
                
                <div className="space-y-4">
                  <div className="flex space-x-4">
                    <input
                      type="url"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      placeholder="https://example.com or github.com/user/repo or youtube.com/watch?v=..."
                      className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      disabled={isLoading}
                    />
                    <button
                      onClick={handleUrlSubmit}
                      disabled={!urlInput.trim() || isLoading}
                      className="bg-purple-500 hover:bg-purple-600 disabled:bg-gray-300 text-white px-6 py-2 rounded-lg font-medium"
                    >
                      Process URL
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <strong>Websites:</strong> Automatically extract content from web pages
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <strong>GitHub:</strong> Process repositories and documentation
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <strong>YouTube:</strong> Extract video information and transcripts
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Audio Recorder Section */}
            {contentSource === 'recorder' && (
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h3 className="text-xl font-bold text-gray-900 mb-6">Audio Recorder</h3>
                
                <div className="text-center space-y-6">
                  <div className="w-32 h-32 bg-gradient-to-r from-red-100 to-pink-100 rounded-full flex items-center justify-center mx-auto">
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
                      isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-400'
                    }`}>
                      <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
                      </svg>
                    </div>
                  </div>
                  
                  <div>
                    {!isRecording ? (
                      <button
                        onClick={startRecording}
                        disabled={isLoading}
                        className="bg-red-500 hover:bg-red-600 disabled:bg-gray-300 text-white px-8 py-3 rounded-lg font-medium text-lg"
                      >
                        Start Recording
                      </button>
                    ) : (
                      <button
                        onClick={stopRecording}
                        className="bg-gray-500 hover:bg-gray-600 text-white px-8 py-3 rounded-lg font-medium text-lg"
                      >
                        Stop Recording
                      </button>
                    )}
                  </div>
                  
                  <p className="text-gray-500">
                    {isRecording 
                      ? 'Recording audio... Click stop when finished' 
                      : 'Record audio directly in your browser for transcription'
                    }
                  </p>
                </div>
              </div>
            )}

            {/* Status Message */}
            {uploadStatus && (
              <div className={`p-4 rounded-lg ${
                uploadStatus.includes('Error') 
                  ? 'bg-red-50 border border-red-200 text-red-800'
                  : 'bg-green-50 border border-green-200 text-green-800'
              }`}>
                {uploadStatus}
              </div>
            )}

            {/* Enhanced Documents List */}
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Knowledge Base ({documents.length})
              </h3>
              
              {documents.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No content processed yet</p>
              ) : (
                <div className="space-y-3">
                  {documents.map((doc, index) => (
                    <div key={index} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <div className={`w-3 h-3 rounded-full ${
                              doc.status === 'completed' ? 'bg-green-400' :
                              doc.status === 'processing' ? 'bg-yellow-400' :
                              'bg-red-400'
                            }`}></div>
                            <span className="font-medium text-gray-900">{doc.filename}</span>
                            <span className="text-sm text-gray-500 capitalize">{doc.status}</span>
                          </div>
                          
                          {doc.metadata && doc.metadata.summary && (
                            <p className="text-sm text-gray-600 mb-2">{doc.metadata.summary}</p>
                          )}
                          
                          {doc.metadata && doc.metadata.tags && doc.metadata.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mb-2">
                              {doc.metadata.tags.slice(0, 5).map((tag, tagIndex) => (
                                <span key={tagIndex} className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                          
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>{doc.type}</span>
                            {doc.metadata && doc.metadata.word_count && (
                              <span>{doc.metadata.word_count} words</span>
                            )}
                            {doc.metadata && doc.metadata.chunk_count && (
                              <span>{doc.metadata.chunk_count} chunks</span>
                            )}
                            {doc.metadata && doc.metadata.category && (
                              <span className="bg-gray-200 px-2 py-1 rounded">{doc.metadata.category}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="bg-white rounded-xl shadow-lg h-96 flex flex-col">
            {/* Chat Header */}
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Enhanced AI Assistant</h2>
              <p className="text-gray-600">Powered by advanced content analysis and semantic search</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <p>Welcome to the Enhanced Content Engine!</p>
                  <p className="mt-2 text-sm">Upload files, process URLs, or record audio, then ask me anything about your content.</p>
                  <p className="mt-2 text-sm">I can now understand categories, tags, and provide enhanced context from your knowledge base.</p>
                </div>
              ) : (
                messages.map((message, index) => (
                  <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-3xl rounded-lg p-4 ${
                      message.type === 'user'
                        ? 'bg-purple-500 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-300">
                          <p className="text-xs text-gray-600 mb-1">Sources:</p>
                          <div className="flex flex-wrap gap-1">
                            {message.sources.map((source, idx) => (
                              <span key={idx} className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                                {source}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-6 border-t border-gray-200">
              <div className="flex space-x-4">
                <textarea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about your content - I understand categories, tags, and can find specific information..."
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  rows="2"
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={!currentMessage.trim() || isLoading}
                  className="bg-purple-500 hover:bg-purple-600 disabled:bg-gray-300 text-white px-6 py-2 rounded-lg font-medium transition-colors duration-200"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;