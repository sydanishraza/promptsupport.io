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
  Plus,
  Minus,
  Info
} from 'lucide-react';

const TrainingInterface = () => {
  // Core state
  const [selectedTemplate, setSelectedTemplate] = useState('document_upload');
  const [templates, setTemplates] = useState([]);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [processingResults, setProcessingResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [processingStartTime, setProcessingStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [activeSession, setActiveSession] = useState(null);
  
  // UI state
  const [showTemplateEditor, setShowTemplateEditor] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Training state
  const [trainingHistory, setTrainingHistory] = useState([]);
  const [currentIteration, setCurrentIteration] = useState(0);
  const [benchmarkScores, setBenchmarkScores] = useState({});
  
  // Get backend URL
  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Load default templates
  useEffect(() => {
    setTemplates([
      {
        id: 'document_upload',
        name: 'Document Upload Processing',
        category: 'File Processing',
        description: 'Phase 1 template for processing uploaded documents (DOCX, PDF, PPT, Markdown, HTML)',
        status: 'active',
        version: '1.0',
        template: {
          input_context: 'Uploaded file containing structured documentation content (e.g., DOCX, PDF, Markdown, or HTML). May include headings, paragraphs, lists, tables, media, multiple topics, and metadata.',
          processing_instructions: [
            'Parse all text, layout, and structure from the source file',
            'Classify and chunk content into logically grouped topics',
            'Identify boundaries between sections, chapters, topics',
            'Distribute extracted content into multiple articles if distinct topics are present',
            'Discard boilerplate metadata like file info, TOC, author name, etc.',
            'Apply smart formatting: use structured output (headings, lists, tables, callouts)',
            'Insert relevant images/media in correct context'
          ],
          output_requirements: {
            format: 'markdown',
            structure: [
              'Clear title (based on section or heading)',
              'Hierarchical headings (H2, H3, H4)',
              'Bulleted or numbered lists where appropriate',
              'Code blocks or inline code if technical content is present',
              'Callouts (Note, Tip, Caution) for emphasis'
            ],
            compatibility: ['HTML', 'WYSIWYG', 'Content Library']
          },
          media_handling: {
            extraction: 'Detect and extract all embedded images/media',
            storage: 'Save each image in the Assets Library with original filename and extension',
            placement: 'Insert images at appropriate location in article content (not at the end)',
            format: 'Image format must NOT be base64 — embed by reference to the stored asset',
            captions: 'If captions exist, convert to paragraph or figcaption-style text'
          },
          target_module: 'Knowledge Base',
          quality_benchmarks: [
            'All sections from input doc are represented',
            'No truncation or omission of important content',
            'No duplication across articles',
            'Images used = images extracted',
            'Output matches tone and formatting of professional help center'
          ]
        }
      }
    ]);
  }, []);

  // Timer for processing elapsed time
  useEffect(() => {
    let timer;
    if (isProcessing && processingStartTime) {
      timer = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - processingStartTime) / 1000));
      }, 1000);
    } else {
      setElapsedTime(0);
    }
    
    return () => {
      if (timer) clearInterval(timer);
    };
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
    if (!uploadedFile || !selectedTemplate) return;
    
    setIsProcessing(true);
    setProcessingResults([]);
    setProcessingStatus('Preparing document for processing...');
    setProcessingStartTime(Date.now());
    
    try {
      const template = templates.find(t => t.id === selectedTemplate);
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('template_id', selectedTemplate);
      formData.append('training_mode', 'true');
      
      // Add template instructions as metadata
      formData.append('template_instructions', JSON.stringify(template.template));
      
      setProcessingStatus('Uploading document and extracting content...');
      
      const response = await fetch(`${backendUrl}/api/training/process`, {
        method: 'POST',
        body: formData,
        // Add timeout handling for long-running processing
        signal: AbortSignal.timeout(300000) // 5 minutes timeout
      });
      
      if (response.ok) {
        setProcessingStatus('Processing complete! Generating results...');
        const results = await response.json();
        setProcessingResults(results.articles || []);
        setShowResults(true);
        
        // Create training session using the session_id returned from backend
        const session = {
          id: results.session_id || Date.now().toString(), // Use backend session_id
          session_id: results.session_id, // Store the actual session_id for PDF downloads
          template_id: selectedTemplate,
          filename: uploadedFile.name,
          timestamp: new Date().toISOString(),
          articles_generated: results.articles?.length || 0,
          images_processed: results.images_processed || 0,
          processing_time: results.processing_time || 0
        };
        
        setActiveSession(session);
        setTrainingHistory(prev => [session, ...prev]);
        
        setProcessingStatus(`Successfully generated ${results.articles?.length || 0} articles in ${results.processing_time || 0}s`);
        
      } else {
        console.error('Processing failed:', response.status);
        setProcessingStatus('Processing failed. Please try again.');
      }
    } catch (error) {
      if (error.name === 'TimeoutError') {
        setProcessingStatus('Processing timed out. The document may be too large or complex.');
      } else {
        console.error('Error processing file:', error);
        setProcessingStatus('An error occurred during processing. Please try again.');
      }
    } finally {
      setIsProcessing(false);
      setProcessingStartTime(null);
    }
  };

  // Download PDF function
  const downloadArticlePDF = async (sessionId, articleIndex, articleTitle) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/training/article/${sessionId}/${articleIndex}/download-pdf`);
      
      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }
      
      // Create blob from response
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Lab_${articleTitle.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      console.log('PDF downloaded successfully');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF. Please try again.');
    }
  };

  // Evaluate result
  const evaluateResult = async (resultId, evaluation) => {
    try {
      const response = await fetch(`${backendUrl}/api/training/evaluate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: activeSession?.id,
          result_id: resultId,
          evaluation: evaluation, // 'accept', 'reject', 'flag'
          feedback: evaluation.feedback || ''
        })
      });
      
      if (response.ok) {
        // Update local state
        setProcessingResults(prev => 
          prev.map(result => 
            result.id === resultId 
              ? { ...result, evaluation: evaluation.status }
              : result
          )
        );
      }
    } catch (error) {
      console.error('Error evaluating result:', error);
    }
  };

  // Template selector
  const TemplateSelector = () => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Lab Templates</h3>
      
      <div className="space-y-3">
        {templates.map(template => (
          <div
            key={template.id}
            className={`p-3 border rounded-lg cursor-pointer transition-colors ${
              selectedTemplate === template.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => setSelectedTemplate(template.id)}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h4 className="font-medium text-gray-900">{template.name}</h4>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    template.status === 'active' 
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {template.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                  <span>Category: {template.category}</span>
                  <span>Version: {template.version}</span>
                </div>
              </div>
              <div className="ml-4">
                <Settings className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <button
        onClick={() => setShowTemplateEditor(true)}
        className="mt-4 flex items-center space-x-2 text-blue-600 hover:text-blue-800 text-sm"
      >
        <Plus className="h-4 w-4" />
        <span>Add New Template</span>
      </button>
    </div>
  );

  // File upload area
  const FileUploadArea = () => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Document</h3>
      
      <div className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
          <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <div className="space-y-2">
            <p className="text-sm text-gray-600">
              Upload a document to test with the selected template
            </p>
            <p className="text-xs text-gray-500">
              Supports: DOCX, PDF, PPT, Markdown, HTML
            </p>
          </div>
          <input
            type="file"
            accept=".docx,.pdf,.ppt,.pptx,.md,.html,.txt"
            onChange={handleFileUpload}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="mt-4 inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer"
          >
            Choose File
          </label>
        </div>
        
        {uploadedFile && (
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <FileText className="h-5 w-5 text-blue-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">{uploadedFile.name}</p>
              <p className="text-xs text-gray-500">
                {(uploadedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              onClick={() => setUploadedFile(null)}
              className="text-red-600 hover:text-red-800"
            >
              <XCircle className="h-5 w-5" />
            </button>
          </div>
        )}
        
        <button
          onClick={processWithTemplate}
          disabled={!uploadedFile || !selectedTemplate || isProcessing}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {isProcessing ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              <span>Process with Template</span>
            </>
          )}
        </button>
        
        {/* Processing Status Display */}
        {isProcessing && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <RefreshCw className="h-4 w-4 animate-spin text-blue-600" />
              <h3 className="font-medium text-blue-900">Processing Document</h3>
            </div>
            <p className="text-sm text-blue-700 mb-2">{processingStatus}</p>
            {processingStartTime && (
              <div className="text-xs text-blue-600">
                Elapsed: {Math.floor((Date.now() - processingStartTime) / 1000)}s
                <br />
                <span className="text-amber-600">This may take 2-5 minutes for comprehensive processing...</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  // Results panel
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
          
          {/* Results List */}
          <div className="space-y-3">
            {processingResults.map((result, index) => (
              <div
                key={result.id || index}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-2">
                      {result.title || `Article ${index + 1}`}
                    </h4>
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {result.content ? result.content.substring(0, 200) + '...' : 'No content preview'}
                    </p>
                    
                    {/* Metadata */}
                    <div className="flex items-center space-x-4 text-xs text-gray-500 mb-3">
                      <span>Words: {result.word_count || 0}</span>
                      <span>Images: {result.image_count || 0}</span>
                      <span>Format: {result.format || 'HTML'}</span>
                    </div>
                  </div>
                  
                  {/* Action buttons */}
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => setSelectedResult(result)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="View Details"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => downloadArticlePDF(activeSession?.session_id || activeSession?.id, index, result.title)}
                      className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                      title="Download PDF"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => evaluateResult(result.id, { status: 'accept' })}
                      className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                      title="Accept"
                    >
                      <CheckCircle className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => evaluateResult(result.id, { status: 'reject' })}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Reject"
                    >
                      <XCircle className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => evaluateResult(result.id, { status: 'flag' })}
                      className="p-2 text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
                      title="Flag for Review"
                    >
                      <AlertCircle className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                
                {/* Evaluation status */}
                {result.evaluation && (
                  <div className={`mt-3 p-2 rounded-lg text-sm ${
                    result.evaluation === 'accept' 
                      ? 'bg-green-100 text-green-800'
                      : result.evaluation === 'reject'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    Status: {result.evaluation}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>No results yet. Upload a document and process it to see results.</p>
        </div>
      )}
    </div>
  );

  // Training history
  const LabHistory = () => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Lab History</h3>
      
      {trainingHistory.length > 0 ? (
        <div className="space-y-3">
          {trainingHistory.map((session, index) => (
            <div key={session.id} className="p-3 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{session.filename}</h4>
                  <p className="text-sm text-gray-600">
                    Template: {templates.find(t => t.id === session.template_id)?.name}
                  </p>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span>{session.articles_generated} articles</span>
                    <span>{session.images_processed} images</span>
                    <span>{new Date(session.timestamp).toLocaleDateString()}</span>
                  </div>
                </div>
                <button
                  onClick={() => setActiveSession(session)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  <Eye className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <Clock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>No lab sessions yet.</p>
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

      <div className="flex h-full">
        {/* Sidebar */}
        <div className={`${sidebarCollapsed ? 'w-16' : 'w-80'} bg-white border-r border-gray-200 transition-all duration-300 overflow-y-auto`}>
          {!sidebarCollapsed && (
            <div className="p-4 space-y-4">
              <TemplateSelector />
              <FileUploadArea />
              <LabHistory />
            </div>
          )}
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
              
              <div className="mt-6 flex items-center justify-end space-x-3">
                <button
                  onClick={() => evaluateResult(selectedResult.id, { status: 'accept' })}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  <CheckCircle className="h-4 w-4" />
                  <span>Accept</span>
                </button>
                <button
                  onClick={() => evaluateResult(selectedResult.id, { status: 'reject' })}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  <XCircle className="h-4 w-4" />
                  <span>Reject</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainingInterface;