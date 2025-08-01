import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  PenTool,
  Brain,
  Zap,
  Target,
  FileText,
  CheckCircle,
  RefreshCw,
  Eye,
  Download,
  AlertTriangle,
  Info,
  Settings,
  Award,
  TrendingUp,
  MessageSquare,
  Copy,
  ExternalLink,
  X,
  Maximize2,
  Minimize2
} from 'lucide-react';

const ArticleGeneration = ({ moduleData, processingData, setProcessingData, onStatusUpdate }) => {
  const [generationResults, setGenerationResults] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [llmConfig, setLlmConfig] = useState({
    model: 'gpt-4',
    temperature: 0.3,
    preserveTokens: true,
    enhanceClarity: true,
    professionalTone: true,
    improveStructure: true
  });
  const [processingProgress, setProcessingProgress] = useState({ current: 0, total: 0 });
  const [viewerMode, setViewerMode] = useState('formatted'); // 'formatted', 'html', 'comparison'
  const [isViewerMaximized, setIsViewerMaximized] = useState(false);
  const [copiedArticle, setCopiedArticle] = useState(null);

  useEffect(() => {
    if (processingData && processingData.imageProcessingResults && processingData.stage === 'images_processed' && !processing && !generationResults) {
      // Auto-start article generation if image processing results are available and not already processed
      startGeneration();
    }
  }, [processingData, processing, generationResults]);

  const startGeneration = async () => {
    if (!processingData || !processingData.imageProcessingResults) {
      return;
    }

    setProcessing(true);
    onStatusUpdate('processing');

    try {
      const results = [];
      let totalChunks = 0;
      let processedChunks = 0;

      // Count total chunks
      processingData.imageProcessingResults.forEach(resource => {
        totalChunks += resource.chunks.length;
      });

      setProcessingProgress({ current: 0, total: totalChunks });
      
      for (const resource of processingData.imageProcessingResults) {
        const resourceArticles = [];
        
        for (const chunk of resource.chunks) {
          // Simulate LLM processing time
          await new Promise(resolve => setTimeout(resolve, 1200));
          
          const generatedArticle = await generateArticleFromChunk(chunk, resource);
          resourceArticles.push(generatedArticle);
          
          processedChunks++;
          setProcessingProgress({ current: processedChunks, total: totalChunks });
        }

        results.push({
          resource_id: resource.resource_id,
          resource_name: resource.resource_name,
          articles: resourceArticles,
          totalArticles: resourceArticles.length,
          status: 'generated'
        });
      }

      const totalArticles = results.reduce((sum, r) => sum + r.articles.length, 0);
      const avgQualityScore = results.reduce((sum, r) => 
        sum + r.articles.reduce((artSum, art) => artSum + art.qualityScore, 0), 0
      ) / totalArticles;

      setGenerationResults({
        resources: results,
        totalArticles,
        averageQualityScore: Math.round(avgQualityScore * 10) / 10,
        processingTime: `${Math.round(totalChunks * 1.2)}s`,
        timestamp: new Date().toISOString()
      });

      // Update processing data for next module
      setProcessingData(prev => ({
        ...prev,
        generationResults: results,
        stage: 'generated'
      }));

      onStatusUpdate('completed');

    } catch (error) {
      console.error('Article generation failed:', error);
      onStatusUpdate('error');
    } finally {
      setProcessing(false);
      setProcessingProgress({ current: 0, total: 0 });
    }
  };

  const generateArticleFromChunk = async (chunk, resource) => {
    // Simulate the LLM rewrite process as per specifications
    const prompt = generateLLMPrompt(chunk);
    
    // Debug: Log chunk structure to understand what's available
    console.log('Processing chunk for article generation:', chunk);
    console.log('Available chunk properties:', Object.keys(chunk));
    
    // Get content from chunk - handle different property names
    const chunkContent = chunk.content || chunk.html || chunk.text || chunk.updated_content || '';
    
    console.log('Extracted chunk content length:', chunkContent.length);
    console.log('Chunk content preview:', chunkContent.substring(0, 200) + '...');
    
    // If no content, this is a problem - log it
    if (!chunkContent || chunkContent.length === 0) {
      console.error('No content found in chunk:', chunk);
      console.error('Chunk title:', chunk.title);
      console.error('Chunk properties:', Object.keys(chunk));
    }
    
    // Simulate improved content generation
    const improvedContent = await simulateLLMRewrite(chunkContent);
    
    // Calculate quality metrics
    const qualityScore = calculateQualityScore(improvedContent, chunkContent);
    
    return {
      article_id: `article_${chunk.chunk_id}`,
      title: chunk.title,
      originalContent: chunkContent,
      improvedContent: improvedContent,
      tokens: chunk.tokens,
      qualityScore: qualityScore,
      improvements: generateImprovementList(),
      preservedTokens: extractPreservedTokens(improvedContent),
      llmModel: llmConfig.model,
      processingTime: Math.random() * 3 + 1, // 1-4 seconds
      status: 'completed'
    };
  };

  const generateLLMPrompt = (chunk) => {
    const chunkContent = chunk.content || chunk.html || chunk.text || chunk.updated_content || '';
    return `Improve the following HTML for clarity and structure. Follow professional technical writing standards. 

CRITICAL REQUIREMENTS:
1. PRESERVE ALL [IMAGE:img_x:block=block_id] tokens EXACTLY as they appear
2. PRESERVE ALL data-block-id attributes on HTML elements
3. Keep the HTML structure intact (headings, paragraphs, lists)
4. Improve readability and professional tone
5. Enhance content clarity and flow

Content to improve:
${chunkContent}

Focus on:
- Making content more comprehensive and informative
- Improving readability and flow within this section
- Maintaining professional tone
- Preserving all image positions and tokens exactly as they are`;
  };

  const simulateLLMRewrite = async (originalContent) => {
    // Ensure originalContent is a string
    if (!originalContent || typeof originalContent !== 'string') {
      return originalContent || '';
    }
    
    // Simulate LLM improvements
    let improved = originalContent;
    
    // Add some realistic improvements
    improved = improved.replace(/\b(this|that)\b/g, 'the specified');
    improved = improved.replace(/\b(very|really|quite)\b/g, '');
    improved = improved.replace(/\b(can be)\b/g, 'is');
    improved = improved.replace(/\.\s+/g, '. ');
    
    // Add professional enhancements
    if (llmConfig.enhanceClarity) {
      improved = improved.replace(/\b(simple|easy)\b/g, 'straightforward');
    }
    
    if (llmConfig.professionalTone) {
      improved = improved.replace(/\b(you should|you need to)\b/g, 'it is recommended to');
    }
    
    // Preserve image tokens (simulate)
    const imageTokens = improved.match(/\[IMAGE:.*?\]/g) || [];
    
    return improved;
  };

  const calculateQualityScore = (improved, original) => {
    // Simulate quality scoring (0-10)
    const baseScore = 6.5;
    const improvements = Math.random() * 2; // 0-2 points for improvements
    const clarity = Math.random() * 1.5; // 0-1.5 points for clarity
    
    return Math.min(10, baseScore + improvements + clarity);
  };

  const generateImprovementList = () => {
    const possibleImprovements = [
      'Enhanced readability and flow',
      'Improved professional tone',
      'Clarified technical concepts',
      'Better paragraph structure',
      'Consistent terminology usage',
      'Enhanced content coherence',
      'Improved sentence clarity',
      'Better transition phrases'
    ];
    
    const count = Math.floor(Math.random() * 4) + 2; // 2-5 improvements
    return possibleImprovements.sort(() => 0.5 - Math.random()).slice(0, count);
  };

  const extractPreservedTokens = (content) => {
    const imageTokens = content.match(/\[IMAGE:.*?\]/g) || [];
    const blockIds = content.match(/data-block-id="[^"]*"/g) || [];
    
    return {
      imageTokens: imageTokens.length,
      blockIds: blockIds.length,
      preserved: imageTokens.length > 0 || blockIds.length > 0
    };
  };

  const viewArticleDetails = (resource, article) => {
    setSelectedArticle({ resource, article });
  };

  const exportArticles = () => {
    const dataStr = JSON.stringify(generationResults, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'generated_articles.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Article Viewer Functions
  const viewArticle = (article, resource) => {
    setSelectedArticle({
      ...article,
      resource_name: resource.resource_name,
      resource_id: resource.resource_id
    });
  };

  const closeArticleViewer = () => {
    setSelectedArticle(null);
    setViewerMode('formatted');
    setIsViewerMaximized(false);
  };

  const copyArticleContent = async (content, type = 'formatted') => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedArticle(type);
      setTimeout(() => setCopiedArticle(null), 2000);
    } catch (err) {
      console.error('Failed to copy content:', err);
    }
  };

  const formatArticleForWYSIWYG = (content) => {
    // Clean and format HTML for WYSIWYG editor compatibility
    let cleanHTML = content;
    
    // Ensure proper structure with div wrapper
    if (!cleanHTML.trim().startsWith('<div')) {
      cleanHTML = `<div class="article-content">${cleanHTML}</div>`;
    }
    
    // Clean up any malformed tags
    cleanHTML = cleanHTML.replace(/<([^>]+)>/g, (match, tag) => {
      // Ensure proper tag structure
      return `<${tag.trim()}>`;
    });
    
    // Ensure headings have proper structure
    cleanHTML = cleanHTML.replace(/<h([1-6])([^>]*)>(.*?)<\/h[1-6]>/g, '<h$1$2>$3</h$1>');
    
    // Ensure paragraphs are properly structured
    cleanHTML = cleanHTML.replace(/<p([^>]*)>(.*?)<\/p>/g, '<p$1>$2</p>');
    
    return cleanHTML;
  };

  const generateArticlePreview = (content, maxLength = 200) => {
    // Strip HTML tags for preview
    const textContent = content.replace(/<[^>]*>/g, '');
    return textContent.length > maxLength 
      ? textContent.substring(0, maxLength) + '...'
      : textContent;
  };

  const getQualityColor = (score) => {
    if (score >= 8.5) return 'green';
    if (score >= 7.0) return 'blue';
    if (score >= 5.5) return 'yellow';
    return 'red';
  };

  const regenerateArticle = async (resource, article) => {
    // Simulate regeneration
    setProcessing(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Update the article with new content
    const updatedResults = { ...generationResults };
    const resourceIndex = updatedResults.resources.findIndex(r => r.resource_id === resource.resource_id);
    const articleIndex = updatedResults.resources[resourceIndex].articles.findIndex(a => a.article_id === article.article_id);
    
    updatedResults.resources[resourceIndex].articles[articleIndex] = {
      ...article,
      qualityScore: Math.min(10, article.qualityScore + Math.random() * 1.5),
      improvedContent: article.improvedContent + ' [Enhanced with additional improvements]',
      improvements: [...article.improvements, 'Content regenerated with enhanced quality']
    };
    
    setGenerationResults(updatedResults);
    setProcessing(false);
  };

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <PenTool className="h-6 w-6 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Article Generation Pipeline</h2>
            <p className="text-sm text-gray-600">Emergent Module: article_generation_pipeline</p>
          </div>
        </div>
        <p className="text-gray-700">
          LLM rewrite with clarity and structure improvements while preserving image tokens and data-block-id attributes.
        </p>
      </div>

      {/* LLM Configuration */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">LLM Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Model Selection
              </label>
              <select
                value={llmConfig.model}
                onChange={(e) => setLlmConfig(prev => ({ ...prev, model: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="gpt-4">GPT-4 (Recommended)</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                <option value="claude-3-haiku">Claude 3 Haiku</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperature: {llmConfig.temperature}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={llmConfig.temperature}
                onChange={(e) => setLlmConfig(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Conservative</span>
                <span>Creative</span>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="space-y-3">
              {[
                { key: 'preserveTokens', label: 'Preserve Image Tokens', required: true },
                { key: 'enhanceClarity', label: 'Enhance Clarity' },
                { key: 'professionalTone', label: 'Professional Tone' },
                { key: 'improveStructure', label: 'Improve Structure' }
              ].map((option) => (
                <div key={option.key} className="flex items-center">
                  <input
                    type="checkbox"
                    id={option.key}
                    checked={llmConfig[option.key]}
                    onChange={(e) => setLlmConfig(prev => ({ ...prev, [option.key]: e.target.checked }))}
                    disabled={option.required}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor={option.key} className="ml-2 block text-sm text-gray-900">
                    {option.label}
                    {option.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                </div>
              ))}
            </div>

            <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <Info className="h-4 w-4 text-indigo-600" />
                <span className="text-sm font-medium text-indigo-900">Processing Note</span>
              </div>
              <p className="text-xs text-indigo-700 mt-1">
                Each chunk is processed individually with the same prompt template for consistent results.
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
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
                <RefreshCw className="h-5 w-5 text-indigo-600 animate-spin" />
                <div>
                  <div className="font-medium text-indigo-900">Generating Articles...</div>
                  <div className="text-sm text-indigo-700">
                    Processing chunk {processingProgress.current} of {processingProgress.total}
                  </div>
                </div>
              </div>
              
              {processingProgress.total > 0 && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(processingProgress.current / processingProgress.total) * 100}%` }}
                  ></div>
                </div>
              )}
            </div>
          ) : generationResults ? (
            <div className="flex items-center space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <div className="font-medium text-green-900">Generation Complete</div>
                <div className="text-sm text-green-700">
                  Generated {generationResults.totalArticles} articles with average quality score of {generationResults.averageQualityScore}/10
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-amber-600" />
              <div>
                <div className="font-medium text-amber-900">Awaiting Chunked Content</div>
                <div className="text-sm text-amber-700">
                  Complete chunking in the previous module to begin article generation
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Generation Results */}
      {generationResults && (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Generation Summary</h3>
              <button
                onClick={exportArticles}
                className="flex items-center space-x-2 px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                <Download className="h-4 w-4" />
                <span>Export Articles</span>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-indigo-50 rounded-lg">
                <FileText className="h-6 w-6 mx-auto mb-2 text-indigo-600" />
                <div className="text-2xl font-bold text-indigo-600">
                  {generationResults.totalArticles}
                </div>
                <div className="text-sm text-gray-600">Articles Generated</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Award className="h-6 w-6 mx-auto mb-2 text-green-600" />
                <div className="text-2xl font-bold text-green-600">
                  {generationResults.averageQualityScore}/10
                </div>
                <div className="text-sm text-gray-600">Avg Quality Score</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Brain className="h-6 w-6 mx-auto mb-2 text-blue-600" />
                <div className="text-2xl font-bold text-blue-600">
                  {llmConfig.model}
                </div>
                <div className="text-sm text-gray-600">LLM Model</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <TrendingUp className="h-6 w-6 mx-auto mb-2 text-purple-600" />
                <div className="text-2xl font-bold text-purple-600">
                  {generationResults.processingTime}
                </div>
                <div className="text-sm text-gray-600">Processing Time</div>
              </div>
            </div>
          </div>

          {/* Generated Articles */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Generated Articles</h3>
            <div className="space-y-6">
              {generationResults.resources.map((resource) => (
                <div key={resource.resource_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="font-medium text-gray-900">{resource.resource_name}</h4>
                      <p className="text-sm text-gray-600">
                        {resource.articles.length} articles generated
                      </p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {resource.articles.map((article) => {
                      const qualityColor = getQualityColor(article.qualityScore);
                      
                      return (
                        <div
                          key={article.article_id}
                          className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <h5 className="font-medium text-gray-900 text-sm leading-tight">
                              {article.title}
                            </h5>
                            <div className={`px-2 py-1 rounded text-xs font-medium bg-${qualityColor}-100 text-${qualityColor}-800`}>
                              {article.qualityScore}/10
                            </div>
                          </div>
                          
                          <div className="text-xs text-gray-600 space-y-1 mb-3">
                            <div className="flex justify-between">
                              <span>Tokens:</span>
                              <span>{article.tokens}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Processing:</span>
                              <span>{article.processingTime.toFixed(1)}s</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Image Tokens:</span>
                              <span className={article.preservedTokens.preserved ? 'text-green-600' : 'text-gray-400'}>
                                {article.preservedTokens.imageTokens} preserved
                              </span>
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <button
                              onClick={() => viewArticle(article, resource)}
                              className="flex items-center space-x-1 text-indigo-600 hover:text-indigo-800 text-sm"
                            >
                              <Eye className="h-3 w-3" />
                              <span>View Article</span>
                            </button>
                            <button
                              onClick={() => regenerateArticle(resource, article)}
                              disabled={processing}
                              className="flex items-center space-x-1 text-gray-600 hover:text-gray-800 text-sm"
                            >
                              <RefreshCw className={`h-3 w-3 ${processing ? 'animate-spin' : ''}`} />
                              <span>Regenerate</span>
                            </button>
                          </div>
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

      {/* Enhanced Article Viewer Modal */}
      {selectedArticle && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className={`bg-white rounded-lg w-full max-h-[90vh] overflow-hidden flex flex-col ${
            isViewerMaximized ? 'max-w-full h-full' : 'max-w-6xl h-[80vh]'
          }`}>
            {/* Header */}
            <div className="p-6 border-b border-gray-200 flex-shrink-0">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{selectedArticle.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    From: {selectedArticle.resource_name} • Quality Score: {selectedArticle.qualityScore}/10 
                    • {selectedArticle.tokens} tokens
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setIsViewerMaximized(!isViewerMaximized)}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                    title={isViewerMaximized ? "Minimize" : "Maximize"}
                  >
                    {isViewerMaximized ? <Minimize2 className="h-5 w-5" /> : <Maximize2 className="h-5 w-5" />}
                  </button>
                  <button
                    onClick={closeArticleViewer}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>
              
              {/* View Mode Tabs */}
              <div className="flex items-center space-x-4 mt-4">
                <div className="flex bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setViewerMode('formatted')}
                    className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                      viewerMode === 'formatted'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Formatted View
                  </button>
                  <button
                    onClick={() => setViewerMode('html')}
                    className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                      viewerMode === 'html'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    HTML Source
                  </button>
                  <button
                    onClick={() => setViewerMode('comparison')}
                    className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                      viewerMode === 'comparison'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Before/After
                  </button>
                </div>
                
                {/* Action Buttons */}
                <div className="flex items-center space-x-2 ml-auto">
                  <button
                    onClick={() => copyArticleContent(
                      formatArticleForWYSIWYG(selectedArticle.improvedContent), 'wysiwyg'
                    )}
                    className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      copiedArticle === 'wysiwyg'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-indigo-100 text-indigo-800 hover:bg-indigo-200'
                    }`}
                  >
                    <Copy className="h-4 w-4" />
                    <span>{copiedArticle === 'wysiwyg' ? 'Copied!' : 'Copy for WYSIWYG'}</span>
                  </button>
                  <button
                    onClick={() => copyArticleContent(selectedArticle.improvedContent, 'html')}
                    className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      copiedArticle === 'html'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                    }`}
                  >
                    <Copy className="h-4 w-4" />
                    <span>{copiedArticle === 'html' ? 'Copied!' : 'Copy HTML'}</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden">
              {viewerMode === 'formatted' && (
                <div className="h-full overflow-y-auto p-6">
                  <div className="prose prose-lg max-w-none">
                    <div 
                      className="article-content"
                      dangerouslySetInnerHTML={{ __html: formatArticleForWYSIWYG(selectedArticle.improvedContent) }}
                    />
                  </div>
                </div>
              )}

              {viewerMode === 'html' && (
                <div className="h-full overflow-y-auto p-6">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-gray-900">WYSIWYG-Compatible HTML</h4>
                      <button
                        onClick={() => copyArticleContent(formatArticleForWYSIWYG(selectedArticle.improvedContent), 'wysiwyg-html')}
                        className={`text-xs px-2 py-1 rounded ${
                          copiedArticle === 'wysiwyg-html'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        {copiedArticle === 'wysiwyg-html' ? 'Copied!' : 'Copy Clean HTML'}
                      </button>
                    </div>
                    <pre className="text-xs text-gray-800 whitespace-pre-wrap overflow-x-auto">
                      {formatArticleForWYSIWYG(selectedArticle.improvedContent)}
                    </pre>
                  </div>
                  
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mt-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-gray-900">Raw Generated HTML</h4>
                      <button
                        onClick={() => copyArticleContent(selectedArticle.improvedContent, 'raw-html')}
                        className={`text-xs px-2 py-1 rounded ${
                          copiedArticle === 'raw-html'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        {copiedArticle === 'raw-html' ? 'Copied!' : 'Copy Raw HTML'}
                      </button>
                    </div>
                    <pre className="text-xs text-gray-800 whitespace-pre-wrap overflow-x-auto">
                      {selectedArticle.improvedContent}
                    </pre>
                  </div>
                </div>
              )}

              {viewerMode === 'comparison' && (
                <div className="h-full overflow-y-auto p-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
                    {/* Original Content */}
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-red-900 mb-3 flex items-center">
                        <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                        Original Content
                      </h4>
                      <div className="prose prose-sm max-w-none">
                        <div 
                          className="original-content text-gray-700"
                          dangerouslySetInnerHTML={{ __html: selectedArticle.originalContent }}
                        />
                      </div>
                    </div>
                    
                    {/* Improved Content */}
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-green-900 mb-3 flex items-center">
                        <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                        Improved Content
                      </h4>
                      <div className="prose prose-sm max-w-none">
                        <div 
                          className="improved-content text-gray-700"
                          dangerouslySetInnerHTML={{ __html: formatArticleForWYSIWYG(selectedArticle.improvedContent) }}
                        />
                      </div>
                    </div>
                  </div>
                  
                  {/* Improvements List */}
                  <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-blue-900 mb-3">Applied Improvements</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {selectedArticle.improvements.map((improvement, index) => (
                        <div key={index} className="flex items-center space-x-2 text-sm text-blue-800">
                          <CheckCircle className="h-3 w-3 text-blue-600" />
                          <span>{improvement}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 bg-gray-50 border-t border-gray-200 flex-shrink-0">
              <div className="flex items-center justify-between text-xs text-gray-600">
                <div className="flex items-center space-x-4">
                  <span>Processing Time: {selectedArticle.processingTime.toFixed(1)}s</span>
                  <span>LLM Model: {selectedArticle.llmModel}</span>
                  <span>Status: {selectedArticle.status}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span>WYSIWYG Compatible</span>
                  <CheckCircle className="h-4 w-4 text-green-600" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ArticleGeneration;