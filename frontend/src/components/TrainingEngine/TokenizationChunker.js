import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Scissors,
  Hash,
  Layers,
  Target,
  BarChart3,
  CheckCircle,
  RefreshCw,
  Eye,
  Download,
  AlertTriangle,
  Info,
  Zap,
  Settings
} from 'lucide-react';

const TokenizationChunker = ({ moduleData, processingData, setProcessingData, onStatusUpdate }) => {
  const [chunkingResults, setChunkingResults] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [chunkingConfig, setChunkingConfig] = useState({
    maxTokensPerChunk: 6000,
    chunkByH1: true,
    preserveStructure: true,
    minChunkSize: 100
  });
  const [selectedChunk, setSelectedChunk] = useState(null);

  useEffect(() => {
    if (processingData && processingData.extractionResults && processingData.stage === 'extracted' && !processing && !chunkingResults) {
      // Auto-start chunking if extraction results are available and not already processed
      startChunking();
    }
  }, [processingData, processing, chunkingResults]);

  const startChunking = async () => {
    if (!processingData || !processingData.extractionResults) {
      return;
    }

    setProcessing(true);
    onStatusUpdate('processing');

    try {
      const results = [];
      
      for (const resource of processingData.extractionResults) {
        // Simulate chunking process
        await new Promise(resolve => setTimeout(resolve, 800));
        
        const chunkedData = await performChunking(resource);
        results.push(chunkedData);
      }

      const totalChunks = results.reduce((sum, r) => sum + r.chunks.length, 0);
      const totalTokens = results.reduce((sum, r) => 
        sum + r.chunks.reduce((chunkSum, chunk) => chunkSum + chunk.tokens, 0), 0
      );

      setChunkingResults({
        resources: results,
        totalChunks,
        totalTokens,
        averageTokensPerChunk: Math.round(totalTokens / totalChunks),
        timestamp: new Date().toISOString()
      });

      // Update processing data for next module
      setProcessingData(prev => ({
        ...prev,
        chunkingResults: results,
        stage: 'chunked'
      }));

      onStatusUpdate('completed');

    } catch (error) {
      console.error('Chunking failed:', error);
      onStatusUpdate('error');
    } finally {
      setProcessing(false);
    }
  };

  const performChunking = async (resource) => {
    const { contentBlocks } = resource;
    const chunks = [];
    
    if (chunkingConfig.chunkByH1) {
      // Chunk by H2 boundaries for better article granularity
      let currentChunk = {
        blocks: [],
        tokens: 0,
        h2Title: null,
        parentH1: null
      };
      
      let chunkCounter = 0;
      let currentH1Title = null;
      
      for (const block of contentBlocks) {
        // Track H1 for context but don't chunk by it
        if (block.type === 'h1') {
          currentH1Title = block.html.replace(/<[^>]*>/g, '').trim();
          // Add H1 to current chunk (don't start new chunk)
          currentChunk.blocks.push(block);
          currentChunk.tokens += block.tokens;
        }
        // Start new chunk on H2
        else if (block.type === 'h2') {
          // Save current chunk if it has content
          if (currentChunk.blocks.length > 0) {
            chunks.push(createChunk(currentChunk, chunkCounter++));
          }
          
          // Start new chunk
          currentChunk = {
            blocks: [block],
            tokens: block.tokens,
            h2Title: block.html.replace(/<[^>]*>/g, '').trim(),
            parentH1: currentH1Title
          };
        } else {
          // Add to current chunk
          currentChunk.blocks.push(block);
          currentChunk.tokens += block.tokens;
          
          // Check if chunk exceeds token limit
          if (currentChunk.tokens > chunkingConfig.maxTokensPerChunk) {
            // Save current chunk
            chunks.push(createChunk(currentChunk, chunkCounter++));
            
            // Start new chunk with current block
            currentChunk = {
              blocks: [block],
              tokens: block.tokens,
              h1Title: currentChunk.h1Title + ' (continued)'
            };
          }
        }
      }
      
      // Add final chunk
      if (currentChunk.blocks.length > 0) {
        chunks.push(createChunk(currentChunk, chunkCounter++));
      }
    } else {
      // Simple token-based chunking
      let currentChunk = { blocks: [], tokens: 0 };
      let chunkCounter = 0;
      
      for (const block of contentBlocks) {
        if (currentChunk.tokens + block.tokens > chunkingConfig.maxTokensPerChunk) {
          if (currentChunk.blocks.length > 0) {
            chunks.push(createChunk(currentChunk, chunkCounter++, 'Token-based'));
          }
          currentChunk = { blocks: [block], tokens: block.tokens };
        } else {
          currentChunk.blocks.push(block);
          currentChunk.tokens += block.tokens;
        }
      }
      
      if (currentChunk.blocks.length > 0) {
        chunks.push(createChunk(currentChunk, chunkCounter++, 'Token-based'));
      }
    }

    return {
      resource_id: resource.resource_id,
      resource_name: resource.resource_name,
      chunks,
      totalTokens: chunks.reduce((sum, chunk) => sum + chunk.tokens, 0),
      chunkingMethod: chunkingConfig.chunkByH1 ? 'H1-based' : 'Token-based',
      status: 'chunked',
      // Preserve session information for image processing
      session_id: resource.session_id,
      raw_backend_response: resource.raw_backend_response
    };
  };

  const createChunk = (chunkData, index, defaultTitle = null) => {
    // Use H2 title as primary, fall back to H1 or default
    const title = chunkData.h2Title || chunkData.parentH1 || defaultTitle || `Chunk ${index + 1}`;
    
    return {
      chunk_id: `chunk_${index + 1}`,
      title: title,
      blocks: chunkData.blocks.map(b => b.block_id),
      tokens: chunkData.tokens,
      blockCount: chunkData.blocks.length,
      content: chunkData.blocks.map(b => b.html).join('\n'),
      html: chunkData.blocks.map(b => b.html).join('\n'), // Add html property for article generation
      firstBlockType: chunkData.blocks[0]?.type || 'unknown',
      hasH1: chunkData.blocks.some(b => b.type === 'h1'),
      hasH2: chunkData.blocks.some(b => b.type === 'h2'),
      parentH1: chunkData.parentH1 // Keep H1 context for reference
    };
  };

  const updateConfig = (key, value) => {
    setChunkingConfig(prev => ({ ...prev, [key]: value }));
  };

  const rechunk = () => {
    setChunkingResults(null);
    startChunking();
  };

  const viewChunkDetails = (resource, chunk) => {
    setSelectedChunk({ resource, chunk });
  };

  const exportChunks = () => {
    const dataStr = JSON.stringify(chunkingResults, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'chunked_content.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const getChunkQualityColor = (tokens) => {
    if (tokens > chunkingConfig.maxTokensPerChunk * 0.8) return 'red';
    if (tokens > chunkingConfig.maxTokensPerChunk * 0.6) return 'yellow';
    if (tokens < chunkingConfig.minChunkSize) return 'gray';
    return 'green';
  };

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Scissors className="h-6 w-6 text-purple-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Tokenization + Chunker</h2>
            <p className="text-sm text-gray-600">Emergent Module: chunking_engine</p>
          </div>
        </div>
        <p className="text-gray-700">
          Token estimation per block and intelligent chunking by H1 boundaries with 6000 token cap per chunk.
        </p>
      </div>

      {/* Chunking Configuration */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Configuration</h3>
          {chunkingResults && (
            <button
              onClick={rechunk}
              className="flex items-center space-x-2 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Re-chunk</span>
            </button>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Tokens Per Chunk
              </label>
              <input
                type="number"
                value={chunkingConfig.maxTokensPerChunk}
                onChange={(e) => updateConfig('maxTokensPerChunk', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                min="1000"
                max="12000"
                step="500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Chunk Size
              </label>
              <input
                type="number"
                value={chunkingConfig.minChunkSize}
                onChange={(e) => updateConfig('minChunkSize', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                min="50"
                max="1000"
                step="50"
              />
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="chunkByH1"
                checked={chunkingConfig.chunkByH1}
                onChange={(e) => updateConfig('chunkByH1', e.target.checked)}
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
              />
              <label htmlFor="chunkByH1" className="ml-2 block text-sm text-gray-900">
                Chunk by H2 boundaries (recommended for granular articles)
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="preserveStructure"
                checked={chunkingConfig.preserveStructure}
                onChange={(e) => updateConfig('preserveStructure', e.target.checked)}
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
              />
              <label htmlFor="preserveStructure" className="ml-2 block text-sm text-gray-900">
                Preserve document structure
              </label>
            </div>
            
            <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <Info className="h-4 w-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-900">Chunking Strategy</span>
              </div>
              <p className="text-xs text-purple-700 mt-1">
                H2-based chunking creates granular articles from document sections while respecting token limits for optimal LLM processing.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Processing Status */}
      {processingData && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Status</h3>
          
          {processing ? (
            <div className="flex items-center space-x-3 p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <RefreshCw className="h-5 w-5 text-purple-600 animate-spin" />
              <div>
                <div className="font-medium text-purple-900">Chunking Content...</div>
                <div className="text-sm text-purple-700">
                  Processing {processingData.extractionResults?.length || 0} resource(s)
                </div>
              </div>
            </div>
          ) : chunkingResults ? (
            <div className="flex items-center space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <div className="font-medium text-green-900">Chunking Complete</div>
                <div className="text-sm text-green-700">
                  Generated {chunkingResults.totalChunks} chunks with average {chunkingResults.averageTokensPerChunk} tokens per chunk
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-amber-600" />
              <div>
                <div className="font-medium text-amber-900">Awaiting Extraction Results</div>
                <div className="text-sm text-amber-700">
                  Complete content extraction in the previous module to begin chunking
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Chunking Results */}
      {chunkingResults && (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Chunking Summary</h3>
              <button
                onClick={exportChunks}
                className="flex items-center space-x-2 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                <Download className="h-4 w-4" />
                <span>Export Chunks</span>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Layers className="h-6 w-6 mx-auto mb-2 text-purple-600" />
                <div className="text-2xl font-bold text-purple-600">
                  {chunkingResults.totalChunks}
                </div>
                <div className="text-sm text-gray-600">Total Chunks</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Hash className="h-6 w-6 mx-auto mb-2 text-blue-600" />
                <div className="text-2xl font-bold text-blue-600">
                  {chunkingResults.averageTokensPerChunk}
                </div>
                <div className="text-sm text-gray-600">Avg Tokens/Chunk</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Target className="h-6 w-6 mx-auto mb-2 text-green-600" />
                <div className="text-2xl font-bold text-green-600">
                  {Math.round((chunkingResults.totalTokens / chunkingConfig.maxTokensPerChunk) * 100)}%
                </div>
                <div className="text-sm text-gray-600">Efficiency</div>
              </div>
              <div className="text-center p-4 bg-amber-50 rounded-lg">
                <Zap className="h-6 w-6 mx-auto mb-2 text-amber-600" />
                <div className="text-2xl font-bold text-amber-600">
                  {chunkingResults.resources[0]?.chunkingMethod || 'N/A'}
                </div>
                <div className="text-sm text-gray-600">Method</div>
              </div>
            </div>
          </div>

          {/* Resource Chunks */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Chunked Resources</h3>
            <div className="space-y-6">
              {chunkingResults.resources.map((resource, resourceIndex) => (
                <div key={resource.resource_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="font-medium text-gray-900">{resource.resource_name}</h4>
                      <p className="text-sm text-gray-600">
                        {resource.chunks.length} chunks • {resource.totalTokens.toLocaleString()} tokens • {resource.chunkingMethod}
                      </p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {resource.chunks.map((chunk, chunkIndex) => {
                      const qualityColor = getChunkQualityColor(chunk.tokens);
                      
                      return (
                        <div
                          key={chunk.chunk_id}
                          className={`p-3 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors border-${qualityColor}-300 bg-${qualityColor}-50`}
                          onClick={() => viewChunkDetails(resource, chunk)}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="text-sm font-medium text-gray-900 truncate">
                              {chunk.title}
                            </div>
                            <Eye className="h-4 w-4 text-gray-400" />
                          </div>
                          <div className="text-xs text-gray-600 space-y-1">
                            <div className="flex justify-between">
                              <span>Tokens:</span>
                              <span className={`font-medium text-${qualityColor}-700`}>{chunk.tokens}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Blocks:</span>
                              <span>{chunk.blockCount}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Type:</span>
                              <span className="capitalize">{chunk.firstBlockType}</span>
                            </div>
                          </div>
                          {chunk.hasH1 && (
                            <div className="mt-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded font-medium">
                              H1 Section
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Chunk Details Modal */}
      {selectedChunk && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  Chunk Details: {selectedChunk.chunk.title}
                </h3>
                <button
                  onClick={() => setSelectedChunk(null)}
                  className="text-gray-600 hover:text-gray-800"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-purple-900 mb-1">Chunk ID</div>
                  <div className="text-purple-700">{selectedChunk.chunk.chunk_id}</div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-blue-900 mb-1">Token Count</div>
                  <div className="text-blue-700">{selectedChunk.chunk.tokens.toLocaleString()}</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-green-900 mb-1">Block Count</div>
                  <div className="text-green-700">{selectedChunk.chunk.blockCount}</div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Content Preview</h4>
                <div 
                  className="prose prose-sm max-w-none text-gray-800 max-h-64 overflow-y-auto"
                  dangerouslySetInnerHTML={{ __html: selectedChunk.chunk.content }}
                />
              </div>

              <div className="mt-4 bg-blue-50 p-3 rounded-lg">
                <div className="text-sm text-blue-700">
                  <strong>Block IDs:</strong> {selectedChunk.chunk.blocks.join(', ')}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TokenizationChunker;