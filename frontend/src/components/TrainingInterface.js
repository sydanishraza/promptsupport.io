import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  Play,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  FileText,
  Image,
  Code,
  Settings,
  Save,
  Download,
  Eye,
  EyeOff,
  Clock,
  Target,
  Zap,
  Brain,
  Layers,
  ArrowRight,
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  Filter,
  Search,
  BookOpen,
  CheckSquare,
  Star,
  TrendingUp,
  Award,
  Lightbulb,
  Gauge
} from 'lucide-react';

const TrainingInterface = () => {
  // State management
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [processingResults, setProcessingResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [activeSession, setActiveSession] = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);
  const [currentIteration, setCurrentIteration] = useState(0);
  const [trainingHistory, setTrainingHistory] = useState([]);
  const [processingStartTime, setProcessingStartTime] = useState(null);
  const [processingDuration, setProcessingDuration] = useState(0);

  // Templates
  const templates = [
    {
      id: 'doc_upload',
      name: 'Document Upload Processing',
      description: 'Process uploaded documents for knowledge extraction and article generation.',
      icon: Upload,
      color: 'blue'
    }
  ];

  // Timer for processing duration
  useEffect(() => {
    let timer;
    if (isProcessing && processingStartTime) {
      timer = setInterval(() => {
        setProcessingDuration(Math.floor((Date.now() - processingStartTime) / 1000));
      }, 1000);
    } else {
      clearInterval(timer);
    }
    return () => clearInterval(timer);
  }, [isProcessing, processingStartTime]);

  // File upload handler
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(file);
      console.log('File uploaded:', file.name);
    }
  };

  // Process with template
  const processWithTemplate = async () => {
    if (!uploadedFile || !selectedTemplate) {
      alert('Please select a template and upload a file.');
      return;
    }

    setIsProcessing(true);
    setProcessingStatus('Starting document processing...');
    setProcessingStartTime(Date.now());
    setShowResults(false);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('template_id', selectedTemplate);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/training/process`, {
        method: 'POST',
        body: formData,
        timeout: 600000 // 10 minutes timeout
      });

      if (response.ok) {
        setProcessingStatus('Processing complete! Generating results...');
        const results = await response.json();
        console.log('🔍 Backend response received:', results.articles?.length || 0, 'articles');
        setProcessingResults(results.articles || []);
        setShowResults(true);

        // Create training session
        const session = {
          id: results.session_id || Date.now().toString(),
          filename: uploadedFile.name,
          template_id: selectedTemplate,
          timestamp: new Date().toISOString(),
          articles_generated: results.articles?.length || 0,
          images_processed: results.images_processed || 0,
          processing_time: results.processing_time || 0,
          status: 'completed'
        };

        setActiveSession(session);
        setTrainingHistory(prev => [session, ...prev]);
        setProcessingStatus(`✅ Processing completed successfully! Generated ${results.articles?.length || 0} articles in ${results.processing_time || 0}s`);

      } else {
        const errorData = await response.json();
        setProcessingStatus(`❌ Error: ${errorData.detail || 'Processing failed'}`);
      }
    } catch (error) {
      console.error('Processing error:', error);
      setProcessingStatus(`❌ Error: ${error.message || 'Processing failed'}`);
    } finally {
      setIsProcessing(false);
      setProcessingStartTime(null);
    }
  };

  // Template Selector Component
  const TemplateSelector = () => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Template</h3>
      <div className="space-y-3">
        {templates.map((template) => {
          const IconComponent = template.icon;
          return (
            <div
              key={template.id}
              className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                selectedTemplate === template.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedTemplate(template.id)}
            >
              <div className="flex items-center space-x-3">
                <IconComponent className={`h-5 w-5 text-${template.color}-600`} />
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{template.name}</h4>
                  <p className="text-sm text-gray-600">{template.description}</p>
                </div>
                {selectedTemplate === template.id && (
                  <CheckCircle className="h-5 w-5 text-blue-600" />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  // File Upload Area Component
  const FileUploadArea = () => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Document</h3>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
        <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
        {uploadedFile ? (
          <div>
            <p className="text-sm font-medium text-gray-900">{uploadedFile.name}</p>
            <p className="text-xs text-gray-500 mt-1">
              {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <>
            <p className="text-sm text-gray-600 mb-2">
              Drop your document here or click to browse
            </p>
            <p className="text-xs text-gray-500">
              Supports DOCX, PDF, PPT, TXT files
            </p>
          </>
        )}
        <input
          type="file"
          onChange={handleFileUpload}
          accept=".docx,.pdf,.ppt,.pptx,.txt"
          className="mt-4 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
      </div>
    </div>
  );

  // Processing Control Component - Always visible
  const ProcessingControl = () => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Process with Template</h3>
      
      <button
        onClick={processWithTemplate}
        disabled={!selectedTemplate || !uploadedFile || isProcessing}
        className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg font-medium ${
          !selectedTemplate || !uploadedFile || isProcessing
            ? 'bg-gray-400 text-white cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {isProcessing ? (
          <>
            <RefreshCw className="h-4 w-4 animate-spin" />
            <span>Processing... ({processingDuration}s)</span>
          </>
        ) : (
          <>
            <Play className="h-4 w-4" />
            <span>Process with Template</span>
          </>
        )}
      </button>

      {!selectedTemplate && (
        <p className="text-sm text-gray-500 mt-2">Please select a template above</p>
      )}
      {!uploadedFile && selectedTemplate && (
        <p className="text-sm text-gray-500 mt-2">Please upload a document above</p>
      )}
      
      {processingStatus && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-700">{processingStatus}</p>
        </div>
      )}
    </div>
  );

  // Results Panel Component  
  const ResultsPanel = () => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Processing Results</h3>
        {activeSession && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock className="h-4 w-4" />
            <span>{new Date(activeSession.timestamp).toLocaleTimeString()}</span>
          </div>
        )}
      </div>
      
      {processingResults.length > 0 ? (
        <div className="space-y-4">
          {/* Summary */}
          <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {processingResults.length}
              </div>
              <div className="text-sm text-gray-600">Articles Generated</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {activeSession?.images_processed || 0}
              </div>
              <div className="text-sm text-gray-600">Images Processed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {activeSession?.processing_time || 0}s
              </div>
              <div className="text-sm text-gray-600">Processing Time</div>
            </div>
          </div>

          {/* Articles List */}
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">Generated Articles:</h4>
            {processingResults.map((result, index) => (
              <div
                key={result.id || index}
                className="p-3 border border-gray-200 rounded-lg hover:border-gray-300 cursor-pointer"
                onClick={() => setSelectedResult(result)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h5 className="font-medium text-gray-900">{result.title}</h5>
                    <p className="text-sm text-gray-600 mt-1">
                      {result.content ? `${Math.min(result.content.length, 150)} characters` : 'No content'}
                    </p>
                  </div>
                  <Eye className="h-4 w-4 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <Clock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>No results yet. Process a document to see articles.</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Engine Lab</h1>
            <p className="text-sm text-gray-600 mt-1">
              Phase 1: Document Upload Processing Lab
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-500">
              Iteration: {currentIteration + 1}
            </span>
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-2 text-gray-600 hover:text-gray-800"
            >
              {sidebarCollapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>

      <div className="flex h-full pt-0">
        {/* Sidebar */}
        <div className={`${sidebarCollapsed ? 'w-16' : 'w-80'} bg-white border-r border-gray-200 transition-all duration-300 overflow-y-auto`}>
          <div className="p-4 space-y-4">
            {!sidebarCollapsed && (
              <>
                <TemplateSelector />
                <FileUploadArea />
                <ProcessingControl />
              </>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6">
            {showResults ? (
              <ResultsPanel />
            ) : (
              <div className="text-center py-12">
                <Brain className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Ready for Lab Testing
                </h2>
                <p className="text-gray-600 mb-6">
                  Select a template and upload a document to begin testing the Knowledge Engine.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <Upload className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                    <h3 className="font-medium text-gray-900 mb-1">Upload Document</h3>
                    <p className="text-sm text-gray-600">Test with DOCX, PDF, PPT, or other formats</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <Settings className="h-8 w-8 mx-auto mb-2 text-green-600" />
                    <h3 className="font-medium text-gray-900 mb-1">Apply Template</h3>
                    <p className="text-sm text-gray-600">Process with selected lab template</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <Target className="h-8 w-8 mx-auto mb-2 text-purple-600" />
                    <h3 className="font-medium text-gray-900 mb-1">Evaluate Results</h3>
                    <p className="text-sm text-gray-600">Review and score the generated output</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Result Detail Modal */}
      {selectedResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  {selectedResult.title}
                </h2>
                <button
                  onClick={() => setSelectedResult(null)}
                  className="text-gray-600 hover:text-gray-800"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
              
              <div className="wysiwyg-content max-w-none">
                <div dangerouslySetInnerHTML={{ __html: selectedResult.content || 'No content available' }} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainingInterface;