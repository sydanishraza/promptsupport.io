import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Upload,
  File,
  FileText,
  Image,
  Video,
  Music,
  Link,
  Youtube,
  Monitor,
  Database,
  Globe,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  X,
  Plus
} from 'lucide-react';

const UploadInterface = ({ moduleData, processingData, setProcessingData, onStatusUpdate }) => {
  const [uploadMethod, setUploadMethod] = useState('file');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [urlInput, setUrlInput] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);

  // Supported resource types as per specifications
  const resourceTypes = [
    { id: 'docx', name: 'Word Document', icon: FileText, extensions: ['.docx', '.doc'], color: 'blue' },
    { id: 'pdf', name: 'PDF Document', icon: File, extensions: ['.pdf'], color: 'red' },
    { id: 'ppt', name: 'PowerPoint', icon: FileText, extensions: ['.ppt', '.pptx'], color: 'orange' },
    { id: 'csv', name: 'CSV Data', icon: Database, extensions: ['.csv'], color: 'green' },
    { id: 'xls', name: 'Excel Spreadsheet', icon: Database, extensions: ['.xls', '.xlsx'], color: 'green' },
    { id: 'html', name: 'HTML Page', icon: Globe, extensions: ['.html', '.htm'], color: 'purple' },
    { id: 'md', name: 'Markdown', icon: FileText, extensions: ['.md'], color: 'gray' },
    { id: 'xml', name: 'XML Document', icon: FileText, extensions: ['.xml'], color: 'yellow' },
    { id: 'video_file', name: 'Video File', icon: Video, extensions: ['.mp4', '.avi', '.mov'], color: 'pink' },
    { id: 'audio_file', name: 'Audio File', icon: Music, extensions: ['.mp3', '.wav', '.m4a'], color: 'indigo' }
  ];

  const urlTypes = [
    { id: 'url', name: 'Web Page', icon: Globe, placeholder: 'https://example.com/page', color: 'blue' },
    { id: 'youtube', name: 'YouTube Video', icon: Youtube, placeholder: 'https://youtube.com/watch?v=...', color: 'red' },
    { id: 'loom', name: 'Loom Video', icon: Monitor, placeholder: 'https://loom.com/share/...', color: 'purple' }
  ];

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  }, []);

  const handleFiles = (files) => {
    const newFiles = files.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: getResourceType(file.name),
      status: 'ready'
    }));
    
    setSelectedFiles(prev => [...prev, ...newFiles]);
  };

  const getResourceType = (filename) => {
    const extension = '.' + filename.split('.').pop().toLowerCase();
    const resourceType = resourceTypes.find(type => 
      type.extensions.includes(extension)
    );
    return resourceType ? resourceType.id : 'unknown';
  };

  const removeFile = (fileId) => {
    setSelectedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const processFiles = async () => {
    if (selectedFiles.length === 0 && !urlInput.trim()) {
      return;
    }

    setUploading(true);
    onStatusUpdate('processing');

    try {
      // Simulate file processing
      const resources = [];
      
      // Process files
      for (const fileData of selectedFiles) {
        const resource = {
          resource_type: fileData.type,
          file: fileData.file,
          name: fileData.name,
          size: fileData.size,
          resource_id: `res_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          status: 'uploaded'
        };
        resources.push(resource);
        
        // Update file status
        setSelectedFiles(prev => prev.map(f => 
          f.id === fileData.id ? { ...f, status: 'uploaded' } : f
        ));
      }

      // Process URL if provided
      if (urlInput.trim()) {
        const urlType = getUrlType(urlInput);
        const resource = {
          resource_type: urlType,
          file: urlInput,
          name: urlInput,
          resource_id: `url_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          status: 'uploaded'
        };
        resources.push(resource);
      }

      // Update processing data to pass to next module
      setProcessingData({
        resources,
        timestamp: new Date().toISOString(),
        totalResources: resources.length
      });

      onStatusUpdate('completed');
      
      // Auto-advance to next module after successful upload
      setTimeout(() => {
        // This would trigger navigation to content extraction
        console.log('Resources uploaded successfully:', resources);
      }, 1000);

    } catch (error) {
      console.error('Upload failed:', error);
      onStatusUpdate('error');
    } finally {
      setUploading(false);
    }
  };

  const getUrlType = (url) => {
    if (url.includes('youtube.com') || url.includes('youtu.be')) return 'youtube';
    if (url.includes('loom.com')) return 'loom';
    return 'url';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Upload className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Upload Interface</h2>
            <p className="text-sm text-gray-600">Emergent Module: resource_upload_handler</p>
          </div>
        </div>
        <p className="text-gray-700">
          Accepts supported file types or URLs for ingestion into the training pipeline.
        </p>
      </div>

      {/* Upload Method Selection */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Method</h3>
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setUploadMethod('file')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${
              uploadMethod === 'file'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Upload className="h-4 w-4" />
            <span>File Upload</span>
          </button>
          <button
            onClick={() => setUploadMethod('url')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${
              uploadMethod === 'url'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Link className="h-4 w-4" />
            <span>URL/Link</span>
          </button>
        </div>

        {uploadMethod === 'file' && (
          <div>
            {/* File Drop Zone */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-lg font-medium text-gray-900 mb-2">
                Drop files here or click to browse
              </p>
              <p className="text-sm text-gray-600 mb-4">
                Supports multiple file types: DOCX, PDF, PPT, CSV, XLS, HTML, MD, XML, Video, Audio
              </p>
              <input
                type="file"
                multiple
                onChange={(e) => handleFiles(Array.from(e.target.files))}
                className="hidden"
                id="file-upload"
                accept=".docx,.doc,.pdf,.ppt,.pptx,.csv,.xls,.xlsx,.html,.htm,.md,.xml,.mp4,.avi,.mov,.mp3,.wav,.m4a"
              />
              <label
                htmlFor="file-upload"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer"
              >
                <Plus className="h-4 w-4 mr-2" />
                Select Files
              </label>
            </div>

            {/* Supported File Types */}
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Supported File Types</h4>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                {resourceTypes.map((type) => {
                  const IconComponent = type.icon;
                  return (
                    <div
                      key={type.id}
                      className={`flex items-center space-x-2 p-2 rounded-lg bg-${type.color}-50 border border-${type.color}-200`}
                    >
                      <IconComponent className={`h-4 w-4 text-${type.color}-600`} />
                      <span className={`text-xs font-medium text-${type.color}-700`}>
                        {type.name}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {uploadMethod === 'url' && (
          <div>
            {/* URL Input */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enter URL or Link
                </label>
                <input
                  type="url"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://example.com/page"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* URL Types */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Supported URL Types</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {urlTypes.map((type) => {
                    const IconComponent = type.icon;
                    return (
                      <div
                        key={type.id}
                        className={`flex items-center space-x-3 p-3 rounded-lg bg-${type.color}-50 border border-${type.color}-200`}
                      >
                        <IconComponent className={`h-5 w-5 text-${type.color}-600`} />
                        <div>
                          <div className={`text-sm font-medium text-${type.color}-700`}>
                            {type.name}
                          </div>
                          <div className="text-xs text-gray-500">
                            {type.placeholder}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Selected Files</h3>
          <div className="space-y-3">
            {selectedFiles.map((fileData) => {
              const resourceType = resourceTypes.find(type => type.id === fileData.type);
              const IconComponent = resourceType?.icon || File;
              
              return (
                <div
                  key={fileData.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <IconComponent className={`h-5 w-5 text-${resourceType?.color || 'gray'}-600`} />
                    <div>
                      <div className="font-medium text-gray-900">{fileData.name}</div>
                      <div className="text-sm text-gray-600">
                        {formatFileSize(fileData.size)} • {resourceType?.name || 'Unknown'}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {fileData.status === 'uploaded' && (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    )}
                    <button
                      onClick={() => removeFile(fileData.id)}
                      className="p-1 text-gray-400 hover:text-red-500"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Process Button */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Start Processing</h3>
            <p className="text-sm text-gray-600">
              Upload resources and trigger the content extraction pipeline
            </p>
          </div>
          <button
            onClick={processFiles}
            disabled={uploading || (selectedFiles.length === 0 && !urlInput.trim())}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium ${
              uploading || (selectedFiles.length === 0 && !urlInput.trim())
                ? 'bg-gray-400 text-white cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {uploading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                <span>Start Processing</span>
              </>
            )}
          </button>
        </div>

        {processingData && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="font-medium text-green-900">
                Upload Complete
              </span>
            </div>
            <p className="text-sm text-green-700 mt-1">
              {processingData.totalResources} resource(s) uploaded successfully and ready for content extraction.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadInterface;