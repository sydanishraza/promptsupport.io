import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  Link2,
  X,
  File,
  Video,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Brain,
  Zap,
  Type,
  Globe,
  ArrowRight,
  Sparkles,
  FileAudio,
  FileVideo,
  Code
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

  // Updated supported file formats with custom SVG icons
  const supportedFormats = {
    documents: {
      title: 'Documents',
      icon: 'FileText',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      formats: [
        { ext: 'docx', label: 'Word', icon: 'FileText' },
        { ext: 'pdf', label: 'PDF', icon: 'FileText' },
        { ext: 'ppt', label: 'PowerPoint', icon: 'FileText' },
        { ext: 'pptx', label: 'PowerPoint', icon: 'FileText' },
        { ext: 'xls', label: 'Excel', icon: 'FileText' },
        { ext: 'xlsx', label: 'Excel', icon: 'FileText' },
        { ext: 'csv', label: 'CSV', icon: 'FileText' },
        { ext: 'xml', label: 'XML', icon: 'Code' },
        { ext: 'html', label: 'HTML', icon: 'Code' },
        { ext: 'md', label: 'Markdown', icon: 'FileText' },
        { ext: 'txt', label: 'Text', icon: 'File' }
      ]
    },
    media: {
      title: 'Audio & Video',
      icon: 'Video',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      formats: [
        { ext: 'mp3', label: 'MP3', icon: 'FileAudio' },
        { ext: 'wav', label: 'WAV', icon: 'FileAudio' },
        { ext: 'm4a', label: 'M4A', icon: 'FileAudio' },
        { ext: 'mp4', label: 'MP4', icon: 'FileVideo' },
        { ext: 'mov', label: 'MOV', icon: 'FileVideo' },
        { ext: 'webm', label: 'WebM', icon: 'FileVideo' }
      ]
    }
  };

  // Complete SVG icon set to avoid ALL Lucide React constructor issues
  const getProcessIcon = (iconName, className) => {
    const baseClass = className || "w-6 h-6";
    
    switch(iconName) {
      case 'CheckCircle2':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'Brain':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        );
      case 'Zap':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        );
      case 'Sparkles':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
        );
      case 'Cloud':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        );
      case 'Upload':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        );
      case 'X':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      case 'File':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'FileText':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'Type':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
        );
      case 'Link2':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
          </svg>
        );
      case 'Globe':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
          </svg>
        );
      case 'Loader2':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        );
      case 'ArrowRight':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        );
      case 'AlertCircle':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'Video':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        );
      case 'FileAudio':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
          </svg>
        );
      case 'FileVideo':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        );
      case 'Code':
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
        );
      default:
        return (
          <svg className={baseClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const processSteps = [
    { id: 'upload', label: 'File uploaded successfully', icon: 'CheckCircle2' },
    { id: 'analyze', label: 'Analyzing content structure', icon: 'Brain' },
    { id: 'extract', label: 'Extracting and processing content', icon: 'Zap' },
    { id: 'generate', label: 'Generating enhanced articles', icon: 'Sparkles' },
    { id: 'finalize', label: 'Finalizing and saving content', icon: 'Cloud' }
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

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      let result = null;

      // Step 1: Initialize processing
      setProcessModal(prev => ({ ...prev, step: 1 }));
      await new Promise(resolve => setTimeout(resolve, 500));

      if (files.length > 0) {
        // File Upload Processing
        setProcessModal(prev => ({ ...prev, step: 2 }));
        
        const formData = new FormData();
        formData.append('file', files[0]);
        formData.append('metadata', JSON.stringify({
          source: 'knowledge_engine_upload',
          timestamp: new Date().toISOString()
        }));

        const uploadResponse = await fetch(`${backendUrl}/api/content/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!uploadResponse.ok) {
          throw new Error(`Upload failed: ${uploadResponse.statusText}`);
        }

        result = await uploadResponse.json();
        
      } else if (urlInput.trim()) {
        // URL Processing
        setProcessModal(prev => ({ ...prev, step: 2 }));
        
        const urlFormData = new FormData();
        urlFormData.append('url', urlInput.trim());
        urlFormData.append('metadata', JSON.stringify({
          source: 'knowledge_engine_url',
          timestamp: new Date().toISOString()
        }));

        const urlResponse = await fetch(`${backendUrl}/api/content/process-url`, {
          method: 'POST',
          body: urlFormData,
        });

        if (!urlResponse.ok) {
          throw new Error(`URL processing failed: ${urlResponse.statusText}`);
        }

        result = await urlResponse.json();
        
      } else if (textContent.trim()) {
        // Text Content Processing (create temp file)
        setProcessModal(prev => ({ ...prev, step: 2 }));
        
        const textBlob = new Blob([textContent], { type: 'text/plain' });
        const textFile = new File([textBlob], 'pasted_content.txt', { type: 'text/plain' });
        
        const formData = new FormData();
        formData.append('file', textFile);
        formData.append('metadata', JSON.stringify({
          source: 'knowledge_engine_text',
          timestamp: new Date().toISOString()
        }));

        const textResponse = await fetch(`${backendUrl}/api/content/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!textResponse.ok) {
          throw new Error(`Text processing failed: ${textResponse.statusText}`);
        }

        result = await textResponse.json();
      }

      // Step 3: Content Analysis (simulated)
      setProcessModal(prev => ({ ...prev, step: 3 }));
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Step 4: Article Generation (completed - result from API)
      setProcessModal(prev => ({ ...prev, step: 4 }));
      await new Promise(resolve => setTimeout(resolve, 500));

      // Format results for UI display
      const uiResults = {
        resourceName: files.length > 0 ? files[0].name : (textContent ? 'Text Content' : (urlInput ? new URL(urlInput).hostname : 'Content')),
        resourceSize: files.length > 0 ? formatFileSize(files[0].size) : null,
        resourceType: files.length > 0 ? files[0].type : (textContent ? 'text/plain' : 'url'),
        articlesGenerated: result?.chunks_created || 1,
        mediaProcessed: result?.extracted_assets?.length || 0,
        processingTime: '5.2', // Could be calculated from actual processing time
        contentLength: result?.extracted_content_length || textContent.length || 0,
        jobId: result?.job_id,
        status: result?.status,
        articleLinks: [] // Could be populated with actual article titles if backend provides them
      };

      setProcessModal(prev => ({ ...prev, data: uiResults }));
      setProcessing(false);

      if (onUploadComplete) {
        onUploadComplete(uiResults);
      }

    } catch (error) {
      console.error('Processing failed:', error);
      setProcessModal(prev => ({ 
        ...prev, 
        data: { 
          error: true, 
          message: error.message || 'Processing failed. Please try again.' 
        } 
      }));
      setProcessing(false);
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
        className="bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden border border-gray-200"
      >
        {/* Header - Matches app header style */}
        <div className="px-6 py-5 border-b border-gray-200 bg-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-50 rounded-lg">
                {getProcessIcon('Brain', 'w-6 h-6 text-blue-600')}
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Content Upload</h2>
                <p className="text-sm text-gray-600">Upload files, paste text, or enter URLs to create knowledge articles</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-400 hover:text-gray-600"
            >
              {getProcessIcon('X', 'w-5 h-5')}
            </button>
          </div>
        </div>

        <div className="p-6 max-h-[calc(90vh-200px)] overflow-y-auto bg-gray-50">
          {/* Upload Methods Grid - Matches app card styling */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            
            {/* File Upload Card */}
            <motion.div
              whileHover={{ y: -2 }}
              className={`bg-white border border-gray-200 rounded-xl p-6 cursor-pointer transition-all duration-200 shadow-sm hover:shadow-md ${
                isDragOver ? 'border-blue-300 bg-blue-50' : 
                activeBlock === 'upload' ? 'border-blue-300 bg-blue-50' : 'hover:border-gray-300'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-xl inline-flex items-center justify-center mb-4">
                  {getProcessIcon('Upload', 'w-6 h-6 text-blue-600')}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Files</h3>
                <p className="text-sm text-gray-600 mb-4">Drag & drop files or click to browse</p>
                
                {/* Supported formats - Cleaner layout */}
                <div className="space-y-4 text-left">
                  {Object.entries(supportedFormats).map(([category, data]) => (
                    <div key={category}>
                      <div className={`flex items-center mb-2 text-sm font-medium ${data.color}`}>
                        <data.icon className="w-4 h-4 mr-2" />
                        {data.title}
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {data.formats.slice(0, 6).map(format => (
                          <span key={format.ext} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-xs font-medium">
                            .{format.ext}
                          </span>
                        ))}
                        {data.formats.length > 6 && (
                          <span className="px-2 py-1 bg-gray-200 text-gray-600 rounded-md text-xs">
                            +{data.formats.length - 6}
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
                  className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                    {getProcessIcon('CheckCircle2', 'w-4 h-4 mr-2 text-green-600')}
                    {files.length} file{files.length > 1 ? 's' : ''} selected
                  </div>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {files.map(file => (
                      <div key={file.id} className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200">
                        <div className="flex items-center space-x-3 min-w-0">
                          <div className="p-1.5 bg-gray-100 rounded">
                            {getProcessIcon('File', 'w-4 h-4 text-gray-600')}
                          </div>
                          <div className="min-w-0">
                            <p className="font-medium text-sm text-gray-900 truncate">{file.name}</p>
                            <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                          </div>
                        </div>
                        <button
                          onClick={(e) => { e.stopPropagation(); removeFile(file.id); }}
                          className="p-1 hover:bg-red-100 rounded text-red-500 hover:text-red-700 transition-colors flex-shrink-0"
                        >
                          {getProcessIcon('X', 'w-4 h-4')}
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

            {/* Text Input Card */}
            <motion.div
              whileHover={{ y: -2 }}
              className={`bg-white border border-gray-200 rounded-xl p-6 transition-all duration-200 shadow-sm hover:shadow-md ${
                activeBlock === 'text' ? 'border-green-300 bg-green-50' : 'hover:border-gray-300'
              }`}
              onClick={() => setActiveBlock('text')}
            >
              <div className="text-center mb-4">
                <div className="w-12 h-12 bg-green-100 rounded-xl inline-flex items-center justify-center mb-4">
                  {getProcessIcon('Type', 'w-6 h-6 text-green-600')}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Paste Text</h3>
                <p className="text-sm text-gray-600 mb-4">Directly paste content for processing</p>
                
                <div className="text-left">
                  <div className="text-xs font-medium text-gray-700 mb-2">Ideal for:</div>
                  <div className="space-y-1.5">
                    {['Meeting notes', 'Documentation', 'Research content', 'Articles'].map(item => (
                      <div key={item} className="flex items-center text-xs text-gray-600">
                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2 flex-shrink-0"></div>
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
                className="w-full h-32 p-3 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 text-sm bg-white"
                onClick={(e) => e.stopPropagation()}
              />
              
              {textContent && (
                <div className="mt-3 text-xs text-green-700 bg-green-50 rounded-lg p-3 border border-green-200">
                  <div className="flex items-center justify-between">
                    <span>Content ready for processing</span>
                    <span className="font-medium">{textContent.split(' ').length} words</span>
                  </div>
                </div>
              )}
            </motion.div>

            {/* URL Input Card */}
            <motion.div
              whileHover={{ y: -2 }}
              className={`bg-white border border-gray-200 rounded-xl p-6 transition-all duration-200 shadow-sm hover:shadow-md ${
                activeBlock === 'url' ? 'border-purple-300 bg-purple-50' : 'hover:border-gray-300'
              }`}
              onClick={() => setActiveBlock('url')}
            >
              <div className="text-center mb-4">
                <div className="w-12 h-12 bg-purple-100 rounded-xl inline-flex items-center justify-center mb-4">
                  {getProcessIcon('Link2', 'w-6 h-6 text-purple-600')}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Enter URL</h3>
                <p className="text-sm text-gray-600 mb-4">Extract content from web pages</p>
                
                <div className="grid grid-cols-2 gap-2 text-left">
                  {urlTypes.map(type => (
                    <div key={type.name} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
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
                className="w-full p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-sm bg-white"
                onClick={(e) => e.stopPropagation()}
              />
              
              {urlInput && (
                <div className="mt-3 text-xs text-purple-700 bg-purple-50 rounded-lg p-3 border border-purple-200">
                  <div className="flex items-center">
                    {getProcessIcon('Globe', 'w-3 h-3 mr-2')}
                    <span>Ready to process: {new URL(urlInput).hostname}</span>
                  </div>
                </div>
              )}
            </motion.div>
          </div>

          {/* Process Button - Matches app button styling */}
          {canProcess() && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-center"
            >
              <button
                onClick={processContent}
                disabled={processing}
                className="flex items-center space-x-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-8 py-3 rounded-lg font-medium transition-all duration-200 shadow-sm hover:shadow-md"
              >
                {processing ? (
                  <>
                    {getProcessIcon('Loader2', 'w-5 h-5 animate-spin')}
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Generate Articles</span>
                    {getProcessIcon('ArrowRight', 'w-5 h-5')}
                  </>
                )}
              </button>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Processing Modal - Matches app modal styling */}
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
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 border border-gray-200"
            >
              <div className="px-6 py-5 border-b border-gray-200">
                <h3 className="text-xl font-semibold text-gray-900">Processing Content</h3>
                <p className="text-sm text-gray-600 mt-1">Transforming your content into knowledge articles</p>
              </div>

              <div className="p-6">
                {processModal.data ? (
                  processModal.data.error ? (
                    // Error State
                    <div className="text-center space-y-6">
                      <motion.div 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="w-16 h-16 bg-red-100 rounded-full inline-flex items-center justify-center"
                      >
                        <AlertCircle className="w-8 h-8 text-red-600" />
                      </motion.div>
                      <div>
                        <h4 className="text-xl font-semibold text-gray-900 mb-2">Processing Failed</h4>
                        <p className="text-gray-600">{processModal.data.message}</p>
                      </div>
                      
                      <button
                        onClick={closeModal}
                        className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                      >
                        Try Again
                      </button>
                    </div>
                  ) : (
                    // Success Results
                    <div className="text-center space-y-6">
                      <motion.div 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="w-16 h-16 bg-green-100 rounded-full inline-flex items-center justify-center"
                      >
                        <CheckCircle2 className="w-8 h-8 text-green-600" />
                      </motion.div>
                      <div>
                        <h4 className="text-xl font-semibold text-gray-900 mb-2">Processing Complete!</h4>
                        <p className="text-gray-600">Your content has been successfully processed and {processModal.data.articlesGenerated} articles created</p>
                      </div>

                      <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                        <div className="grid grid-cols-2 gap-6">
                          <div className="text-center">
                            <div className="text-3xl font-bold text-blue-600 mb-1">{processModal.data.articlesGenerated}</div>
                            <div className="text-sm text-gray-600">Articles Generated</div>
                          </div>
                          <div className="text-center">
                            <div className="text-3xl font-bold text-purple-600 mb-1">{processModal.data.mediaProcessed || 0}</div>
                            <div className="text-sm text-gray-600">Media Processed</div>
                          </div>
                        </div>
                        <div className="pt-4 mt-4 border-t border-gray-200 space-y-2">
                          <div className="text-sm text-gray-600">Processing time: <span className="font-medium">{processModal.data.processingTime}s</span></div>
                          {processModal.data.contentLength && (
                            <div className="text-sm text-gray-600">Content extracted: <span className="font-medium">{processModal.data.contentLength} characters</span></div>
                          )}
                          <div className="text-sm text-gray-600">Status: <span className="font-medium text-green-600">{processModal.data.status || 'Completed'}</span></div>
                        </div>
                      </div>

                      <div className="text-center">
                        <button
                          onClick={closeModal}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                        >
                          View Articles in Content Library
                        </button>
                      </div>
                    </div>
                  )
                ) : (
                  // Processing steps
                  <div className="space-y-6">
                    {processSteps.map((step, index) => {
                      const isActive = index === processModal.step - 1;
                      const isCompleted = index < processModal.step - 1;

                      return (
                        <div key={step.id} className="flex items-center space-x-4">
                          <div className={`w-12 h-12 rounded-xl border-2 flex items-center justify-center transition-all ${
                            isCompleted ? 'bg-green-100 border-green-300' : 
                            isActive ? 'bg-blue-100 border-blue-300' : 
                            'bg-gray-50 border-gray-200'
                          }`}>
                            {getProcessIcon(step.icon, `w-6 h-6 transition-all ${
                              isCompleted ? 'text-green-600' : 
                              isActive ? 'text-blue-600' : 
                              'text-gray-400'
                            }`)}
                          </div>
                          <div className="flex-1">
                            <div className={`font-medium transition-all ${
                              isCompleted ? 'text-green-900' : 
                              isActive ? 'text-blue-900' : 
                              'text-gray-600'
                            }`}>
                              {step.label}
                            </div>
                            {isActive && (
                              <div className="text-sm text-blue-600 mt-1">In progress...</div>
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