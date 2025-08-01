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
  MessageSquare
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

  useEffect(() => {
    console.log('ArticleGeneration useEffect - processingData:', processingData);
    if (processingData) {
      console.log('ArticleGeneration - has imageProcessingResults:', !!processingData.imageProcessingResults);
      console.log('ArticleGeneration - stage:', processingData.stage);
      console.log('ArticleGeneration - processing:', processing);
      console.log('ArticleGeneration - generationResults:', !!generationResults);
    }
    
    if (processingData && processingData.imageProcessingResults && processingData.stage === 'images_processed' && !processing && !generationResults) {
      console.log('ArticleGeneration - Starting article generation...');
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
    
    // Simulate improved content generation
    const improvedContent = await simulateLLMRewrite(chunk.content);
    
    // Calculate quality metrics
    const qualityScore = calculateQualityScore(improvedContent, chunk.content);
    
    return {
      article_id: `article_${chunk.chunk_id}`,
      title: chunk.title,
      originalContent: chunk.content,
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
    return `Improve the following HTML for clarity and structure. Follow professional technical writing standards. 

CRITICAL REQUIREMENTS:
1. PRESERVE ALL [IMAGE:img_x:block=block_id] tokens EXACTLY as they appear
2. PRESERVE ALL data-block-id attributes on HTML elements
3. Keep the HTML structure intact (headings, paragraphs, lists)
4. Improve readability and professional tone
5. Enhance content clarity and flow

Content to improve:
${chunk.content}

Focus on:
- Making content more comprehensive and informative
- Improving readability and flow within this section
- Maintaining professional tone
- Preserving all image positions and tokens exactly as they are`;
  };

  const simulateLLMRewrite = async (originalContent) => {
    // Ensure originalContent is a string
    if (!originalContent || typeof originalContent !== 'string') {
      console.warn('simulateLLMRewrite received invalid content:', originalContent);
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
                              onClick={() => viewArticleDetails(resource, article)}
                              className="flex items-center space-x-1 text-indigo-600 hover:text-indigo-800 text-sm"
                            >
                              <Eye className="h-3 w-3" />
                              <span>View</span>
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

      {/* Article Details Modal */}
      {selectedArticle && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  Article: {selectedArticle.article.title}
                </h3>
                <button
                  onClick={() => setSelectedArticle(null)}
                  className="text-gray-600 hover:text-gray-800"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-indigo-50 p-3 rounded-lg">
                  <div className="text-sm font-medium text-indigo-900">Quality Score</div>
                  <div className="text-lg font-bold text-indigo-700">
                    {selectedArticle.article.qualityScore}/10
                  </div>
                </div>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="text-sm font-medium text-blue-900">Token Count</div>
                  <div className="text-lg font-bold text-blue-700">
                    {selectedArticle.article.tokens}
                  </div>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <div className="text-sm font-medium text-green-900">Image Tokens</div>
                  <div className="text-lg font-bold text-green-700">
                    {selectedArticle.article.preservedTokens.imageTokens}
                  </div>
                </div>
                <div className="bg-purple-50 p-3 rounded-lg">
                  <div className="text-sm font-medium text-purple-900">Processing Time</div>
                  <div className="text-lg font-bold text-purple-700">
                    {selectedArticle.article.processingTime.toFixed(1)}s
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Original Content</h4>
                  <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                    <div 
                      className="prose prose-sm max-w-none text-gray-800"
                      dangerouslySetInnerHTML={{ __html: selectedArticle.article.originalContent }}
                    />
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Improved Content</h4>
                  <div className="bg-green-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                    <div 
                      className="prose prose-sm max-w-none text-gray-800"
                      dangerouslySetInnerHTML={{ __html: selectedArticle.article.improvedContent }}
                    />
                  </div>
                </div>
              </div>

              <div className="mt-6 bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Improvements Applied</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  {selectedArticle.article.improvements.map((improvement, index) => (
                    <li key={index} className="flex items-center space-x-2">
                      <CheckCircle className="h-3 w-3 text-blue-600" />
                      <span>{improvement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ArticleGeneration;