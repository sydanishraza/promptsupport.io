import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Shield,
  CheckCircle,
  AlertTriangle,
  XCircle,
  TrendingUp,
  BarChart3,
  Target,
  Award,
  RefreshCw,
  Eye,
  Download,
  Info,
  Star,
  ThumbsUp,
  ThumbsDown,
  Zap
} from 'lucide-react';

const QualityAssurance = ({ moduleData, processingData, setProcessingData, onStatusUpdate }) => {
  const [qaResults, setQaResults] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);
  const [qaConfig, setQaConfig] = useState({
    completenessThreshold: 7.5,
    clarityThreshold: 7.0,
    coherenceThreshold: 7.5,
    mediaThreshold: 6.0,
    overallThreshold: 7.0
  });
  const [processingProgress, setProcessingProgress] = useState({ current: 0, total: 0 });

  useEffect(() => {
    if (processingData && processingData.imageProcessingResults && processingData.stage === 'images_processed') {
      // Auto-start quality assurance if image processing results are available
      startQualityAssurance();
    }
  }, [processingData]);

  const startQualityAssurance = async () => {
    if (!processingData || !processingData.imageProcessingResults) {
      return;
    }

    setProcessing(true);
    onStatusUpdate('processing');

    try {
      const results = [];
      let totalArticles = 0;
      let processedArticles = 0;

      // Count total articles
      processingData.imageProcessingResults.forEach(resource => {
        totalArticles += resource.articles.length;
      });

      setProcessingProgress({ current: 0, total: totalArticles });
      
      for (const resource of processingData.imageProcessingResults) {
        const resourceQA = [];
        
        for (const article of resource.articles) {
          // Simulate QA processing time
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          const qaResult = await performQualityAssessment(article, resource);
          resourceQA.push(qaResult);
          
          processedArticles++;
          setProcessingProgress({ current: processedArticles, total: totalArticles });
        }

        results.push({
          resource_id: resource.resource_id,
          resource_name: resource.resource_name,
          qa_results: resourceQA,
          averageScore: resourceQA.reduce((sum, qa) => sum + qa.overallScore, 0) / resourceQA.length,
          totalArticles: resourceQA.length,
          status: 'assessed'
        });
      }

      const overallStats = calculateOverallStatistics(results);

      setQaResults({
        resources: results,
        overallStats,
        timestamp: new Date().toISOString(),
        processingTime: `${totalArticles * 1.0}s`
      });

      // Update processing data for next module
      setProcessingData(prev => ({
        ...prev,
        qaResults: results,
        stage: 'qa_complete'
      }));

      onStatusUpdate('completed');

    } catch (error) {
      console.error('Quality assurance failed:', error);
      onStatusUpdate('error');
    } finally {
      setProcessing(false);
      setProcessingProgress({ current: 0, total: 0 });
    }
  };

  const performQualityAssessment = async (article, resource) => {
    // Simulate comprehensive quality assessment based on internal rubric (0-10 scale)
    
    // Content Completeness (0-10)
    const completeness = assessCompleteness(article);
    
    // Clarity and Coherence (0-10)
    const clarity = assessClarity(article);
    const coherence = assessCoherence(article);
    
    // Media Placement Correctness (0-10)
    const mediaPlacement = assessMediaPlacement(article);
    
    // Technical Quality (0-10)
    const technicalQuality = assessTechnicalQuality(article);
    
    // Overall Score (weighted average)
    const overallScore = calculateOverallScore({
      completeness,
      clarity,
      coherence,
      mediaPlacement,
      technicalQuality
    });
    
    // Generate improvement suggestions
    const suggestions = generateImprovementSuggestions({
      completeness,
      clarity,
      coherence,
      mediaPlacement,
      technicalQuality
    });
    
    // Determine pass/fail status
    const passed = overallScore >= qaConfig.overallThreshold;
    
    return {
      article_id: article.article_id,
      title: article.title,
      scores: {
        completeness,
        clarity,
        coherence,
        mediaPlacement,
        technicalQuality
      },
      overallScore,
      passed,
      grade: getGrade(overallScore),
      suggestions,
      wordCount: estimateWordCount(article.updatedContent || ''),
      imageCount: article.imageCount || 0,
      processingTime: Math.random() * 2 + 0.5,
      timestamp: new Date().toISOString()
    };
  };

  const assessCompleteness = (article) => {
    // Simulate content completeness assessment
    const baseScore = 6.5;
    const contentLength = (article.updatedContent || '').length;
    const hasImages = (article.imageCount || 0) > 0;
    const hasStructure = (article.updatedContent || '').includes('<h') && (article.updatedContent || '').includes('<p>');
    
    let score = baseScore;
    if (contentLength > 2000) score += 1.0;
    if (hasImages) score += 0.8;
    if (hasStructure) score += 0.7;
    
    return Math.min(10, score + (Math.random() - 0.5) * 1.0);
  };

  const assessClarity = (article) => {
    // Simulate clarity assessment
    const baseScore = 7.0;
    const wordCount = estimateWordCount(article.updatedContent || '');
    const sentenceVariety = Math.random() * 2; // Simulate sentence structure analysis
    
    let score = baseScore;
    if (wordCount > 300) score += 0.5;
    score += sentenceVariety;
    
    return Math.min(10, score + (Math.random() - 0.3) * 0.8);
  };

  const assessCoherence = (article) => {
    // Simulate coherence assessment
    const baseScore = 6.8;
    const hasTransitions = Math.random() > 0.3; // Simulate transition detection
    const logicalFlow = Math.random() * 1.5; // Simulate flow analysis
    
    let score = baseScore;
    if (hasTransitions) score += 0.8;
    score += logicalFlow;
    
    return Math.min(10, score + (Math.random() - 0.4) * 0.7);
  };

  const assessMediaPlacement = (article) => {
    // Simulate media placement assessment
    const baseScore = 7.2;
    const imageCount = article.imageCount || 0;
    const contextualPlacement = Math.random() * 1.5; // Simulate placement analysis
    
    let score = baseScore;
    if (imageCount > 0) score += 0.5;
    if (imageCount > 2) score += 0.3;
    score += contextualPlacement;
    
    return Math.min(10, score);
  };

  const assessTechnicalQuality = (article) => {
    // Simulate technical quality assessment
    const baseScore = 8.0;
    const hasValidHTML = (article.updatedContent || '').includes('<') && (article.updatedContent || '').includes('>');
    const hasDataAttributes = (article.updatedContent || '').includes('data-block-id');
    
    let score = baseScore;
    if (hasValidHTML) score += 0.5;
    if (hasDataAttributes) score += 0.5;
    
    return Math.min(10, score + (Math.random() - 0.3) * 0.5);
  };

  const calculateOverallScore = (scores) => {
    // Weighted average calculation
    const weights = {
      completeness: 0.25,
      clarity: 0.25,
      coherence: 0.20,
      mediaPlacement: 0.15,
      technicalQuality: 0.15
    };
    
    return Object.keys(weights).reduce((total, key) => {
      return total + (scores[key] * weights[key]);
    }, 0);
  };

  const generateImprovementSuggestions = (scores) => {
    const suggestions = [];
    
    if (scores.completeness < qaConfig.completenessThreshold) {
      suggestions.push('Expand content with more detailed explanations and examples');
    }
    if (scores.clarity < qaConfig.clarityThreshold) {
      suggestions.push('Simplify complex sentences and improve readability');
    }
    if (scores.coherence < qaConfig.coherenceThreshold) {
      suggestions.push('Add transition phrases to improve content flow');
    }
    if (scores.mediaPlacement < qaConfig.mediaThreshold) {
      suggestions.push('Optimize image placement for better context alignment');
    }
    if (scores.technicalQuality < 8.0) {
      suggestions.push('Review HTML structure and ensure proper formatting');
    }
    
    // Add positive feedback for high scores
    if (scores.overallScore > 8.5) {
      suggestions.push('Excellent overall quality - content is ready for publication');
    }
    
    return suggestions;
  };

  const getGrade = (score) => {
    if (score >= 9.0) return 'A+';
    if (score >= 8.5) return 'A';
    if (score >= 8.0) return 'A-';
    if (score >= 7.5) return 'B+';
    if (score >= 7.0) return 'B';
    if (score >= 6.5) return 'B-';
    if (score >= 6.0) return 'C+';
    if (score >= 5.5) return 'C';
    return 'C-';
  };

  const estimateWordCount = (content) => {
    return content.replace(/<[^>]*>/g, '').split(/\s+/).filter(word => word.length > 0).length;
  };

  const calculateOverallStatistics = (results) => {
    const allQAResults = results.flatMap(r => r.qa_results);
    const totalArticles = allQAResults.length;
    
    if (totalArticles === 0) return {};
    
    const overallScores = allQAResults.map(qa => qa.overallScore);
    const passedCount = allQAResults.filter(qa => qa.passed).length;
    
    const avgScores = {
      completeness: allQAResults.reduce((sum, qa) => sum + qa.scores.completeness, 0) / totalArticles,
      clarity: allQAResults.reduce((sum, qa) => sum + qa.scores.clarity, 0) / totalArticles,
      coherence: allQAResults.reduce((sum, qa) => sum + qa.scores.coherence, 0) / totalArticles,
      mediaPlacement: allQAResults.reduce((sum, qa) => sum + qa.scores.mediaPlacement, 0) / totalArticles,
      technicalQuality: allQAResults.reduce((sum, qa) => sum + qa.scores.technicalQuality, 0) / totalArticles
    };
    
    return {
      totalArticles,
      passedCount,
      passRate: (passedCount / totalArticles) * 100,
      averageOverallScore: overallScores.reduce((sum, score) => sum + score, 0) / totalArticles,
      averageScores: avgScores,
      distribution: {
        excellent: allQAResults.filter(qa => qa.overallScore >= 9.0).length,
        good: allQAResults.filter(qa => qa.overallScore >= 7.5 && qa.overallScore < 9.0).length,
        fair: allQAResults.filter(qa => qa.overallScore >= 6.0 && qa.overallScore < 7.5).length,
        poor: allQAResults.filter(qa => qa.overallScore < 6.0).length
      }
    };
  };

  const viewQADetails = (resource, qaResult) => {
    setSelectedResult({ resource, qaResult });
  };

  const exportQAReport = () => {
    const dataStr = JSON.stringify(qaResults, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'quality_assessment_report.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const getScoreColor = (score) => {
    if (score >= 8.5) return 'green';
    if (score >= 7.0) return 'blue';
    if (score >= 6.0) return 'yellow';
    return 'red';
  };

  const getGradeColor = (grade) => {
    if (grade.startsWith('A')) return 'green';
    if (grade.startsWith('B')) return 'blue';
    if (grade.startsWith('C')) return 'yellow';
    return 'red';
  };

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-amber-100 rounded-lg">
            <Shield className="h-6 w-6 text-amber-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Quality Assurance Pipeline</h2>
            <p className="text-sm text-gray-600">Emergent Module: quality_assurance_pipeline</p>
          </div>
        </div>
        <p className="text-gray-700">
          Comprehensive quality evaluation using internal rubric (0-10 scale) for content completeness, clarity, coherence, and media placement.
        </p>
      </div>

      {/* QA Configuration */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quality Thresholds</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { key: 'completenessThreshold', label: 'Content Completeness', min: 5.0, max: 10.0 },
            { key: 'clarityThreshold', label: 'Clarity', min: 5.0, max: 10.0 },
            { key: 'coherenceThreshold', label: 'Coherence', min: 5.0, max: 10.0 },
            { key: 'mediaThreshold', label: 'Media Placement', min: 4.0, max: 10.0 },
            { key: 'overallThreshold', label: 'Overall Quality', min: 5.0, max: 10.0 }
          ].map((config) => (
            <div key={config.key} className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                {config.label}: {qaConfig[config.key].toFixed(1)}
              </label>
              <input
                type="range"
                min={config.min}
                max={config.max}
                step="0.1"
                value={qaConfig[config.key]}
                onChange={(e) => setQaConfig(prev => ({ ...prev, [config.key]: parseFloat(e.target.value) }))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>{config.min}</span>
                <span>{config.max}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <Info className="h-4 w-4 text-amber-600" />
            <span className="text-sm font-medium text-amber-900">Assessment Criteria</span>
          </div>
          <p className="text-xs text-amber-700 mt-1">
            Articles scoring above thresholds pass quality assurance. Detailed suggestions are provided for improvement areas.
          </p>
        </div>
      </div>

      {/* Processing Status */}
      {processingData && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Assessment Status</h3>
          
          {processing ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <RefreshCw className="h-5 w-5 text-amber-600 animate-spin" />
                <div>
                  <div className="font-medium text-amber-900">Assessing Quality...</div>
                  <div className="text-sm text-amber-700">
                    Evaluating article {processingProgress.current} of {processingProgress.total}
                  </div>
                </div>
              </div>
              
              {processingProgress.total > 0 && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-amber-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(processingProgress.current / processingProgress.total) * 100}%` }}
                  ></div>
                </div>
              )}
            </div>
          ) : qaResults ? (
            <div className="flex items-center space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <div className="font-medium text-green-900">Quality Assessment Complete</div>
                <div className="text-sm text-green-700">
                  Assessed {qaResults.overallStats.totalArticles} articles with {qaResults.overallStats.passRate.toFixed(1)}% pass rate
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-amber-600" />
              <div>
                <div className="font-medium text-amber-900">Awaiting Processed Articles</div>
                <div className="text-sm text-amber-700">
                  Complete image processing in the previous module to begin quality assessment
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* QA Results */}
      {qaResults && (
        <div className="space-y-6">
          {/* Overall Statistics */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Assessment Summary</h3>
              <button
                onClick={exportQAReport}
                className="flex items-center space-x-2 px-3 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700"
              >
                <Download className="h-4 w-4" />
                <span>Export Report</span>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-amber-50 rounded-lg">
                <Award className="h-6 w-6 mx-auto mb-2 text-amber-600" />
                <div className="text-2xl font-bold text-amber-600">
                  {qaResults.overallStats.averageOverallScore.toFixed(1)}/10
                </div>
                <div className="text-sm text-gray-600">Average Score</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <ThumbsUp className="h-6 w-6 mx-auto mb-2 text-green-600" />
                <div className="text-2xl font-bold text-green-600">
                  {qaResults.overallStats.passRate.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Pass Rate</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Target className="h-6 w-6 mx-auto mb-2 text-blue-600" />
                <div className="text-2xl font-bold text-blue-600">
                  {qaResults.overallStats.passedCount}/{qaResults.overallStats.totalArticles}
                </div>
                <div className="text-sm text-gray-600">Passed/Total</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Zap className="h-6 w-6 mx-auto mb-2 text-purple-600" />
                <div className="text-2xl font-bold text-purple-600">
                  {qaResults.processingTime}
                </div>
                <div className="text-sm text-gray-600">Processing Time</div>
              </div>
            </div>

            {/* Score Distribution */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Average Scores by Category</h4>
                <div className="space-y-3">
                  {Object.entries(qaResults.overallStats.averageScores).map(([category, score]) => (
                    <div key={category} className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {category.replace(/([A-Z])/g, ' $1')}
                      </span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`bg-${getScoreColor(score)}-500 h-2 rounded-full`}
                            style={{ width: `${(score / 10) * 100}%` }}
                          ></div>
                        </div>
                        <span className={`text-sm font-medium text-${getScoreColor(score)}-600`}>
                          {score.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">Quality Distribution</h4>
                <div className="space-y-3">
                  {[
                    { label: 'Excellent (9.0+)', count: qaResults.overallStats.distribution.excellent, color: 'green' },
                    { label: 'Good (7.5-8.9)', count: qaResults.overallStats.distribution.good, color: 'blue' },
                    { label: 'Fair (6.0-7.4)', count: qaResults.overallStats.distribution.fair, color: 'yellow' },
                    { label: 'Poor (<6.0)', count: qaResults.overallStats.distribution.poor, color: 'red' }
                  ].map((dist) => (
                    <div key={dist.label} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">{dist.label}</span>
                      <div className="flex items-center space-x-2">
                        <div className={`px-2 py-1 bg-${dist.color}-100 text-${dist.color}-800 text-xs font-medium rounded`}>
                          {dist.count}
                        </div>
                        <span className="text-sm text-gray-500">
                          ({((dist.count / qaResults.overallStats.totalArticles) * 100).toFixed(0)}%)
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Results */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Assessment Results</h3>
            <div className="space-y-6">
              {qaResults.resources.map((resource) => (
                <div key={resource.resource_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="font-medium text-gray-900">{resource.resource_name}</h4>
                      <p className="text-sm text-gray-600">
                        {resource.qa_results.length} articles • Average score: {resource.averageScore.toFixed(1)}/10
                      </p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {resource.qa_results.map((qaResult) => {
                      const scoreColor = getScoreColor(qaResult.overallScore);
                      const gradeColor = getGradeColor(qaResult.grade);
                      
                      return (
                        <div
                          key={qaResult.article_id}
                          className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                          onClick={() => viewQADetails(resource, qaResult)}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <h5 className="font-medium text-gray-900 text-sm leading-tight line-clamp-2">
                              {qaResult.title}
                            </h5>
                            <div className={`px-2 py-1 rounded text-xs font-bold bg-${gradeColor}-100 text-${gradeColor}-800`}>
                              {qaResult.grade}
                            </div>
                          </div>
                          
                          <div className="space-y-2 mb-3">
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-gray-600">Overall Score:</span>
                              <span className={`font-medium text-${scoreColor}-600`}>
                                {qaResult.overallScore.toFixed(1)}/10
                              </span>
                            </div>
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-gray-600">Status:</span>
                              <div className="flex items-center space-x-1">
                                {qaResult.passed ? (
                                  <CheckCircle className="h-3 w-3 text-green-500" />
                                ) : (
                                  <XCircle className="h-3 w-3 text-red-500" />
                                )}
                                <span className={qaResult.passed ? 'text-green-600' : 'text-red-600'}>
                                  {qaResult.passed ? 'Passed' : 'Failed'}
                                </span>
                              </div>
                            </div>
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-gray-600">Words:</span>
                              <span>{qaResult.wordCount}</span>
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-1">
                              {qaResult.imageCount > 0 && (
                                <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                                  {qaResult.imageCount} images
                                </span>
                              )}
                            </div>
                            <Eye className="h-3 w-3 text-gray-400" />
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

      {/* QA Details Modal */}
      {selectedResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  Quality Assessment: {selectedResult.qaResult.title}
                </h3>
                <button
                  onClick={() => setSelectedResult(null)}
                  className="text-gray-600 hover:text-gray-800"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-amber-50 p-4 rounded-lg text-center">
                  <div className="text-sm font-medium text-amber-900 mb-1">Overall Score</div>
                  <div className="text-3xl font-bold text-amber-700">
                    {selectedResult.qaResult.overallScore.toFixed(1)}/10
                  </div>
                  <div className={`text-sm font-medium text-${getGradeColor(selectedResult.qaResult.grade)}-600`}>
                    Grade: {selectedResult.qaResult.grade}
                  </div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-sm font-medium text-blue-900 mb-1">Status</div>
                  <div className="flex items-center justify-center space-x-2">
                    {selectedResult.qaResult.passed ? (
                      <CheckCircle className="h-6 w-6 text-green-500" />
                    ) : (
                      <XCircle className="h-6 w-6 text-red-500" />
                    )}
                    <span className={`font-bold ${selectedResult.qaResult.passed ? 'text-green-600' : 'text-red-600'}`}>
                      {selectedResult.qaResult.passed ? 'PASSED' : 'FAILED'}
                    </span>
                  </div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-sm font-medium text-green-900 mb-1">Content</div>
                  <div className="text-lg font-bold text-green-700">
                    {selectedResult.qaResult.wordCount} words
                  </div>
                  <div className="text-sm text-green-600">
                    {selectedResult.qaResult.imageCount} images
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Detailed Scores</h4>
                  <div className="space-y-3">
                    {Object.entries(selectedResult.qaResult.scores).map(([category, score]) => (
                      <div key={category} className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700 capitalize">
                          {category.replace(/([A-Z])/g, ' $1')}
                        </span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`bg-${getScoreColor(score)}-500 h-2 rounded-full`}
                              style={{ width: `${(score / 10) * 100}%` }}
                            ></div>
                          </div>
                          <span className={`text-sm font-bold text-${getScoreColor(score)}-600 w-8`}>
                            {score.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Processing Details</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Assessment Time:</span>
                      <span className="font-medium">{selectedResult.qaResult.processingTime.toFixed(1)}s</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Timestamp:</span>
                      <span className="font-medium">
                        {new Date(selectedResult.qaResult.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Article ID:</span>
                      <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                        {selectedResult.qaResult.article_id}
                      </code>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">Improvement Suggestions</h4>
                <div className="space-y-2">
                  {selectedResult.qaResult.suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start space-x-2 p-3 bg-blue-50 rounded-lg">
                      <Info className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-blue-800">{suggestion}</span>
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

export default QualityAssurance;