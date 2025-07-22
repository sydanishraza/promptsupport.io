import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
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
  Loader
} from 'lucide-react';

const KnowledgeEngine = () => {
  const [activeTab, setActiveTab] = useState('files');
  const [isRecording, setIsRecording] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [urls, setUrls] = useState(['']);
  const [processingStatus, setProcessingStatus] = useState({});
  const fileInputRef = useRef(null);

  const tabs = [
    { id: 'files', label: 'Files', icon: File, description: 'PDF, DOCX, CSV, MP4, etc.' },
    { id: 'urls', label: 'URLs', icon: Globe, description: 'Auth/public, scrape websites, YouTube, GitHub' },
    { id: 'recorder', label: 'Recorder', icon: Video, description: 'Snagit-style audio/video recorder' }
  ];

  const handleFileUpload = (files) => {
    const newFiles = Array.from(files).map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'processing',
      progress: 0,
      metadata: null
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // Simulate processing
    newFiles.forEach(file => {
      simulateProcessing(file.id);
    });
  };

  const simulateProcessing = (fileId) => {
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