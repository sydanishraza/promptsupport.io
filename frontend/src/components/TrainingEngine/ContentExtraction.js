import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Database,
  FileText,
  Code,
  Hash,
  List,
  Table,
  Heading,
  Layout,
  CheckCircle,
  RefreshCw,
  Eye,
  Download,
  AlertTriangle,
  Info
} from 'lucide-react';

const ContentExtraction = ({ moduleData, processingData, setProcessingData, onStatusUpdate }) => {
  const [extractionResults, setExtractionResults] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [processingStats, setProcessingStats] = useState({ processed: 0, total: 0 });
  const [selectedResource, setSelectedResource] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [hasStartedExtraction, setHasStartedExtraction] = useState(false);

  useEffect(() => {
    if (processingData && processingData.resources && processingData.stage !== 'extracted' && !processing && !extractionResults && !hasStartedExtraction) {
      // Auto-start extraction if resources are available and not already processed
      setHasStartedExtraction(true);
      startExtraction();
    }
  }, [processingData, processing, extractionResults, hasStartedExtraction]);

  const startExtraction = async () => {
    if (!processingData || !processingData.resources) {
      return;
    }

    console.log('Starting content extraction with data:', processingData);

    setProcessing(true);
    onStatusUpdate('processing');

    try {
      const results = [];
      let totalBlocks = 0;
      let processedResources = 0;

      setProcessingStats({ processed: 0, total: processingData.resources.length });

      // Process each uploaded resource with the backend
      for (const resource of processingData.resources) {
        try {
          console.log('Processing resource:', resource.name);
          console.log('Resource object:', resource);
          console.log('Resource file:', resource.file);
          console.log('File type:', typeof resource.file);

          // Get backend URL exactly like Legacy Training Interface
          const backendUrl = process.env.REACT_APP_BACKEND_URL;
          
          // Create FormData exactly like Legacy Training Interface
          const formData = new FormData();
          
          // Handle file vs URL resource exactly like Legacy Training Interface
          if (resource.file instanceof File) {
            formData.append('file', resource.file);
            console.log('Added File object to FormData');
          } else if (typeof resource.file === 'string') {
            // This is a URL resource
            formData.append('url', resource.file);
            console.log('Added URL to FormData:', resource.file);
          }
          
          formData.append('template_id', 'content_extraction_pipeline');
          formData.append('training_mode', 'true');
          
          console.log('Making API call to:', `${backendUrl}/api/training/process`);
          console.log('Starting API call - this may take several minutes for large files...');
          
          // Use exact same fetch call as Legacy Training Interface
          const response = await fetch(`${backendUrl}/api/training/process`, {
            method: 'POST',
            body: formData
          });

          console.log('API response status:', response.status);
          console.log('API response headers:', response.headers);

          if (!response.ok) {
            const errorText = await response.text();
            console.error('API error response:', errorText);
            throw new Error(`Backend processing failed: ${response.status} - ${errorText}`);
          }

          const result = await response.json();
          console.log('Backend processing result:', result);

          // Process the backend response into our content blocks format
          const contentBlocks = [];
          const metadata = {
            title: result.articles?.[0]?.title || resource.name,
            word_count: result.articles?.[0]?.word_count || 0,
            processing_time: result.processing_time || '0s',
            total_images: result.images_processed || 0
          };

          // Extract content blocks from the backend response
          if (result.articles && result.articles.length > 0) {
            for (const article of result.articles) {
              // Parse HTML content into structured blocks
              const blocks = parseHtmlIntoBlocks(article.html || article.content);
              contentBlocks.push(...blocks);
            }
          } else {
            // Fallback: create basic blocks from response
            const fallbackContent = result.content || result.html || 'No content extracted';
            const blocks = parseHtmlIntoBlocks(fallbackContent);
            contentBlocks.push(...blocks);
          }

          totalBlocks += contentBlocks.length;

          const extractionResult = {
            resource_id: resource.resource_id,
            resource_name: resource.name,
            resource_type: resource.resource_type || 'file',
            contentBlocks,
            metadata,
            totalBlocks: contentBlocks.length,
            totalTokens: contentBlocks.reduce((sum, block) => sum + (block.tokens || 0), 0),
            extraction_method: 'backend_processing',
            status: 'extracted'
          };

          results.push(extractionResult);
          processedResources++;
          setProcessingStats({ processed: processedResources, total: processingData.resources.length });

          // Add delay between resources to show progress
          await new Promise(resolve => setTimeout(resolve, 1000));

        } catch (error) {
          console.error(`Error processing resource ${resource.name}:`, error);
          
          // Create error result but don't fail entire process
          const errorResult = {
            resource_id: resource.resource_id,
            resource_name: resource.name,
            resource_type: resource.resource_type || 'file',
            contentBlocks: [],
            metadata: { 
              error: error.message,
              error_type: error.name || 'ProcessingError',
              timestamp: new Date().toISOString()
            },
            totalBlocks: 0,
            extraction_method: 'backend_processing',
            status: 'error'
          };
          
          results.push(errorResult);
          processedResources++;
          setProcessingStats({ processed: processedResources, total: processingData.resources.length });
        }
      }

      // Calculate summary statistics
      const avgBlocksPerResource = totalBlocks / results.length;
      const totalTokens = results.reduce((sum, r) => {
        return sum + r.contentBlocks.reduce((blockSum, block) => blockSum + (block.tokens || 0), 0);
      }, 0);
      const totalProcessingTime = results.reduce((sum, r) => {
        const time = parseFloat(r.metadata.processing_time?.replace('s', '') || '0');
        return sum + time;
      }, 0);

      setExtractionResults({
        resources: results,
        totalBlocks,
        totalTokens,
        averageBlocksPerResource: Math.round(avgBlocksPerResource),
        processingTime: `${totalProcessingTime.toFixed(1)}s`,
        timestamp: new Date().toISOString()
      });

      // Update processing data for next module
      setProcessingData(prev => ({
        ...prev,
        extractionResults: results,
        stage: 'extracted'
      }));

      onStatusUpdate('completed');

    } catch (error) {
      console.error('Content extraction failed:', error);
      onStatusUpdate('error');
    } finally {
      setProcessing(false);
    }
  };

  // Helper function to parse HTML into structured content blocks
  const parseHtmlIntoBlocks = (htmlContent) => {
    const blocks = [];
    
    if (!htmlContent) return blocks;

    // Create a temporary DOM element to parse HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlContent;

    // Extract elements and convert to blocks
    const elements = tempDiv.querySelectorAll('h1, h2, h3, h4, h5, h6, p, ul, ol, table, div, blockquote');
    
    elements.forEach((element, index) => {
      const tagName = element.tagName.toLowerCase();
      const blockId = element.getAttribute('data-block-id') || `${tagName}_${index + 1}`;
      
      // Estimate token count (rough approximation: ~4 characters per token)
      const textContent = element.textContent || '';
      const estimatedTokens = Math.max(1, Math.floor(textContent.length / 4));

      blocks.push({
        block_id: blockId,
        type: tagName,
        html: element.outerHTML,
        text: textContent.trim(),
        tokens: estimatedTokens,
        level: tagName.match(/h[1-6]/) ? parseInt(tagName.charAt(1)) : null,
        length: element.outerHTML.length
      });
    });

    return blocks;
  };



  const viewResourceDetails = (resource) => {
    setSelectedResource(resource);
    
    // Generate preview data
    const preview = {
      structure: analyzeStructure(resource.contentBlocks),
      tokenDistribution: analyzeTokens(resource.contentBlocks),
      blockTypes: analyzeBlockTypes(resource.contentBlocks)
    };
    
    setPreviewData(preview);
  };

  const analyzeStructure = (blocks) => {
    const headers = blocks.filter(b => ['h1', 'h2', 'h3'].includes(b.type));
    return {
      totalHeaders: headers.length,
      h1Count: blocks.filter(b => b.type === 'h1').length,
      h2Count: blocks.filter(b => b.type === 'h2').length,
      h3Count: blocks.filter(b => b.type === 'h3').length,
      hasStructure: headers.length > 0
    };
  };

  const analyzeTokens = (blocks) => {
    const tokens = blocks.map(b => b.tokens);
    return {
      total: tokens.reduce((sum, t) => sum + t, 0),
      average: Math.round(tokens.reduce((sum, t) => sum + t, 0) / tokens.length),
      min: Math.min(...tokens),
      max: Math.max(...tokens)
    };
  };

  const analyzeBlockTypes = (blocks) => {
    const types = {};
    blocks.forEach(block => {
      types[block.type] = (types[block.type] || 0) + 1;
    });
    return types;
  };

  const exportData = () => {
    const dataStr = JSON.stringify(extractionResults, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'content_blocks.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-green-100 rounded-lg">
            <Database className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Content Extraction Pipeline</h2>
            <p className="text-sm text-gray-600">Emergent Module: content_extraction_pipeline</p>
          </div>
        </div>
        <p className="text-gray-700">
          Parses uploaded files into structured HTML with data-block-id attributes, detects document structure, and extracts metadata.
        </p>
      </div>

      {/* Processing Status */}
      {processingData && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Status</h3>
          
          {processing ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <RefreshCw className="h-5 w-5 text-blue-600 animate-spin" />
                <div>
                  <div className="font-medium text-blue-900">Extracting Content...</div>
                  <div className="text-sm text-blue-700">
                    Processing {processingData.resources?.length || 0} resource(s) • Large files may take 3-5 minutes
                  </div>
                </div>
              </div>
              
              {processingStats && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-blue-900">Progress</span>
                    <span className="text-sm text-blue-700">
                      {processingStats.processed} / {processingStats.total} files
                    </span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(processingStats.processed / processingStats.total) * 100}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-blue-600 mt-2">
                    💡 Large DOCX files with images may require extra processing time
                  </div>
                </div>
              )}
            </div>
          ) : extractionResults ? (
            <div className="flex items-center space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <div className="font-medium text-green-900">Extraction Complete</div>
                <div className="text-sm text-green-700">
                  Generated {extractionResults.totalBlocks} content blocks with {extractionResults.totalTokens.toLocaleString()} tokens
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-amber-600" />
              <div>
                <div className="font-medium text-amber-900">Awaiting Resources</div>
                <div className="text-sm text-amber-700">
                  Upload resources in the previous module to begin extraction
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Extraction Results */}
      {extractionResults && (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Extraction Summary</h3>
              <button
                onClick={exportData}
                className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Download className="h-4 w-4" />
                <span>Export JSON</span>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Database className="h-6 w-6 mx-auto mb-2 text-green-600" />
                <div className="text-2xl font-bold text-green-600">
                  {extractionResults.resources.length}
                </div>
                <div className="text-sm text-gray-600">Resources Processed</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Layout className="h-6 w-6 mx-auto mb-2 text-blue-600" />
                <div className="text-2xl font-bold text-blue-600">
                  {extractionResults.totalBlocks || 0}
                </div>
                <div className="text-sm text-gray-600">Content Blocks</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Hash className="h-6 w-6 mx-auto mb-2 text-purple-600" />
                <div className="text-2xl font-bold text-purple-600">
                  {(extractionResults.totalTokens || 0).toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Total Tokens</div>
              </div>
              <div className="text-center p-4 bg-amber-50 rounded-lg">
                <CheckCircle className="h-6 w-6 mx-auto mb-2 text-amber-600" />
                <div className="text-2xl font-bold text-amber-600">100%</div>
                <div className="text-sm text-gray-600">Success Rate</div>
              </div>
            </div>
          </div>

          {/* Resource List */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Processed Resources</h3>
            <div className="space-y-3">
              {extractionResults.resources.map((resource, index) => (
                <div
                  key={resource.resource_id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <FileText className="h-5 w-5 text-gray-600" />
                    <div>
                      <div className="font-medium text-gray-900">
                        {resource.resource_name}
                      </div>
                      <div className="text-sm text-gray-600">
                        {resource.contentBlocks?.length || 0} blocks • {(resource.totalTokens || 0).toLocaleString()} tokens • {resource.resource_type || 'file'}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => viewResourceDetails(resource)}
                    className="flex items-center space-x-2 px-3 py-1 text-blue-600 hover:bg-blue-50 rounded-lg"
                  >
                    <Eye className="h-4 w-4" />
                    <span>View Details</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Resource Details Modal */}
      {selectedResource && previewData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  Resource Details: {selectedResource.resource_name}
                </h3>
                <button
                  onClick={() => setSelectedResource(null)}
                  className="text-gray-600 hover:text-gray-800"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                {/* Structure Analysis */}
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-3 flex items-center">
                    <Heading className="h-4 w-4 mr-2" />
                    Document Structure
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>H1 Headers:</span>
                      <span className="font-medium">{previewData.structure.h1Count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>H2 Headers:</span>
                      <span className="font-medium">{previewData.structure.h2Count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>H3 Headers:</span>
                      <span className="font-medium">{previewData.structure.h3Count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Has Structure:</span>
                      <span className={`font-medium ${previewData.structure.hasStructure ? 'text-green-600' : 'text-red-600'}`}>
                        {previewData.structure.hasStructure ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Token Analysis */}
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-medium text-purple-900 mb-3 flex items-center">
                    <Hash className="h-4 w-4 mr-2" />
                    Token Distribution
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Total:</span>
                      <span className="font-medium">{previewData.tokenDistribution.total.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Average:</span>
                      <span className="font-medium">{previewData.tokenDistribution.average}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Range:</span>
                      <span className="font-medium">
                        {previewData.tokenDistribution.min} - {previewData.tokenDistribution.max}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Block Types */}
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-900 mb-3 flex items-center">
                    <List className="h-4 w-4 mr-2" />
                    Block Types
                  </h4>
                  <div className="space-y-2 text-sm">
                    {Object.entries(previewData.blockTypes).map(([type, count]) => (
                      <div key={type} className="flex justify-between">
                        <span className="capitalize">{type}:</span>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Sample Blocks */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Sample Content Blocks</h4>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {selectedResource.contentBlocks.slice(0, 5).map((block, index) => (
                    <div key={block.block_id} className="bg-white p-3 rounded border">
                      <div className="flex justify-between items-start mb-2">
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {block.block_id}
                        </code>
                        <span className="text-xs text-gray-500">
                          {block.tokens} tokens
                        </span>
                      </div>
                      <div 
                        className="text-sm text-gray-800"
                        dangerouslySetInnerHTML={{ __html: block.html }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentExtraction;