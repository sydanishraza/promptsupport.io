import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  Scissors,
  Image,
  PenTool,
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  Activity,
  Zap,
  Clock,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';

// Import pipeline modules
import UploadInterface from './TrainingEngine/UploadInterface';
import ContentExtraction from './TrainingEngine/ContentExtraction';
import TokenizationChunker from './TrainingEngine/TokenizationChunker';
import ImageProcessing from './TrainingEngine/ImageProcessing';
import ArticleGeneration from './TrainingEngine/ArticleGeneration';
import QualityAssurance from './TrainingEngine/QualityAssurance';

const NewTrainingEngine = () => {
  // Pipeline state management
  const [currentStage, setCurrentStage] = useState(0);
  const [processingData, setProcessingData] = useState(null);
  const [moduleStatuses, setModuleStatuses] = useState({
    upload: 'pending',
    extraction: 'pending',
    chunking: 'pending',
    images: 'pending',
    generation: 'pending',
    qa: 'pending'
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [processingTime, setProcessingTime] = useState(0);

  // Pipeline stages configuration
  const stages = [
    {
      id: 'upload',
      title: 'Resource Upload',
      icon: Upload,
      component: UploadInterface,
      description: 'Upload documents, URLs, or media files'
    },
    {
      id: 'extraction',
      title: 'Content Extraction',
      icon: FileText,
      component: ContentExtraction,
      description: 'Extract and parse content structure'
    },
    {
      id: 'chunking',
      title: 'Tokenization & Chunking',
      icon: Scissors,
      component: TokenizationChunker,
      description: 'Split content into manageable chunks'
    },
    {
      id: 'images',
      title: 'Image Processing',
      icon: Image,
      component: ImageProcessing,
      description: 'Process and optimize images'
    },
    {
      id: 'generation',
      title: 'Article Generation',
      icon: PenTool,
      component: ArticleGeneration,
      description: 'Generate enhanced articles'
    },
    {
      id: 'qa',
      title: 'Quality Assurance',
      icon: CheckCircle,
      component: QualityAssurance,
      description: 'Validate and score content quality'
    }
  ];

  // Timer effect
  useEffect(() => {
    let interval;
    if (isProcessing && startTime) {
      interval = setInterval(() => {
        setProcessingTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
    } else {
      setProcessingTime(0);
    }
    return () => clearInterval(interval);
  }, [isProcessing, startTime]);

  // Handle stage navigation
  const goToStage = (stageIndex) => {
    if (stageIndex >= 0 && stageIndex < stages.length) {
      setCurrentStage(stageIndex);
    }
  };

  const nextStage = () => {
    if (currentStage < stages.length - 1) {
      setCurrentStage(currentStage + 1);
    }
  };

  const previousStage = () => {
    if (currentStage > 0) {
      setCurrentStage(currentStage - 1);
    }
  };

  // Handle module status updates
  const updateModuleStatus = (moduleId, status) => {
    setModuleStatuses(prev => ({
      ...prev,
      [moduleId]: status
    }));

    // Auto-advance on completion
    if (status === 'completed') {
      setTimeout(() => {
        const currentStageIndex = stages.findIndex(stage => stage.id === moduleId);
        if (currentStageIndex < stages.length - 1) {
          setCurrentStage(currentStageIndex + 1);
        }
      }, 1500); // Delay for better UX
    }
  };

  // Handle processing state
  const updateProcessingState = (processing) => {
    setIsProcessing(processing);
    if (processing && !startTime) {
      setStartTime(Date.now());
    } else if (!processing) {
      setStartTime(null);
    }
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'processing': return 'text-blue-600 bg-blue-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  // Format processing time
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Zap className="h-8 w-8 text-blue-600" />
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">New Training Engine</h1>
              </div>
              {isProcessing && (
                <div className="flex items-center space-x-2 bg-blue-50 px-3 py-1 rounded-full">
                  <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" />
                  <span className="text-sm font-medium text-blue-700">
                    Processing {formatTime(processingTime)}
                  </span>
                </div>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600 hidden sm:block">
                Stage {currentStage + 1} of {stages.length}
              </div>
              <div className="flex items-center space-x-2">
                {currentStage > 0 && (
                  <button
                    onClick={previousStage}
                    className="flex items-center space-x-1 px-3 py-1 text-gray-600 hover:text-gray-800 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    <span className="hidden sm:inline">Previous</span>
                  </button>
                )}
                {currentStage < stages.length - 1 && (
                  <button
                    onClick={nextStage}
                    className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <span className="hidden sm:inline">Next</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Pipeline - Fully Responsive */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-wrap items-center justify-center lg:justify-between gap-2 sm:gap-4">
            {stages.map((stage, index) => {
              const status = moduleStatuses[stage.id];
              const isActive = index === currentStage;
              const isCompleted = status === 'completed';
              const isProcessing = status === 'processing';
              const isError = status === 'error';

              return (
                <div key={stage.id} className="flex items-center">
                  {/* Stage Item */}
                  <motion.div
                    className={`flex items-center space-x-2 px-2 sm:px-3 py-2 rounded-lg cursor-pointer transition-all duration-300 min-w-0 ${
                      isActive
                        ? 'bg-blue-600 text-white shadow-lg scale-105'
                        : isCompleted
                        ? 'bg-green-100 text-green-800 hover:bg-green-200'
                        : isError
                        ? 'bg-red-100 text-red-800 hover:bg-red-200'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    onClick={() => goToStage(index)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className={`flex-shrink-0`}>
                      {isCompleted ? (
                        <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5" />
                      ) : isProcessing ? (
                        <RefreshCw className="h-4 w-4 sm:h-5 sm:w-5 animate-spin" />
                      ) : isError ? (
                        <AlertTriangle className="h-4 w-4 sm:h-5 sm:w-5" />
                      ) : (
                        <stage.icon className="h-4 w-4 sm:h-5 sm:w-5" />
                      )}
                    </div>
                    <div className="min-w-0 hidden sm:block">
                      <div className="font-medium text-xs sm:text-sm truncate">{stage.title}</div>
                      <div className={`text-xs opacity-75 truncate ${
                        isActive ? 'text-blue-100' : ''
                      }`}>
                        {stage.description}
                      </div>
                    </div>
                    {/* Mobile: Show stage number */}
                    <div className="sm:hidden text-xs font-bold">
                      {index + 1}
                    </div>
                  </motion.div>

                  {/* Connector */}
                  {index < stages.length - 1 && (
                    <div className="hidden lg:flex items-center mx-2">
                      <ArrowRight className={`h-4 w-4 ${
                        moduleStatuses[stage.id] === 'completed' 
                          ? 'text-green-500' 
                          : 'text-gray-300'
                      }`} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 min-h-[500px] sm:min-h-[600px]">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStage}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="p-4 sm:p-6 h-full"
            >
              {/* Stage Header */}
              <div className="mb-4 sm:mb-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-3 space-y-2 sm:space-y-0 mb-2">
                  <div className="flex items-center space-x-3">
                    <stages[currentStage].icon className="h-5 w-5 sm:h-6 sm:w-6 text-blue-600 flex-shrink-0" />
                    <h2 className="text-lg sm:text-xl font-semibold text-gray-900">
                      {stages[currentStage].title}
                    </h2>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium self-start sm:self-auto ${
                    getStatusColor(moduleStatuses[stages[currentStage].id])
                  }`}>
                    {moduleStatuses[stages[currentStage].id]}
                  </div>
                </div>
                <p className="text-sm sm:text-base text-gray-600">{stages[currentStage].description}</p>
              </div>

              {/* Stage Component with Overflow Handling */}
              <div className="h-full overflow-y-auto overflow-x-hidden">
                {React.createElement(stages[currentStage].component, {
                  processingData,
                  setProcessingData,
                  onStatusUpdate: (status) => updateModuleStatus(stages[currentStage].id, status),
                  onProcessingChange: updateProcessingState,
                  stage: stages[currentStage].id
                })}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default NewTrainingEngine;