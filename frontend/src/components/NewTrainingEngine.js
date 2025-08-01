import React, { useState } from 'react';
import {
  Brain,
  Zap,
  Target,
  Settings,
  BarChart3,
  Lightbulb,
  Rocket,
  Code,
  Database,
  Cpu,
  Layers,
  ChevronRight,
  Play,
  Pause,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Info,
  Upload,
  Scissors,
  Hash,
  Image,
  FileText,
  Shield,
  ArrowRight,
  ArrowLeft
} from 'lucide-react';

// Import individual pipeline modules
import UploadInterface from './TrainingEngine/UploadInterface';
import ContentExtraction from './TrainingEngine/ContentExtraction';
import TokenizationChunker from './TrainingEngine/TokenizationChunker';
import ImageProcessing from './TrainingEngine/ImageProcessing';
import ArticleGeneration from './TrainingEngine/ArticleGeneration';
import QualityAssurance from './TrainingEngine/QualityAssurance';

const NewTrainingEngine = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [processingData, setProcessingData] = useState(null);
  const [stepStatuses, setStepStatuses] = useState({});

  // Training pipeline steps
  const pipelineSteps = [
    {
      id: 'upload',
      name: 'Resource Upload',
      description: 'Upload files or provide URLs for processing',
      icon: Upload,
      color: 'blue',
      component: UploadInterface
    },
    {
      id: 'extraction',
      name: 'Content Extraction',
      description: 'Parse and structure content with block IDs',
      icon: Database,
      color: 'green',
      component: ContentExtraction
    },
    {
      id: 'chunking',
      name: 'Tokenization & Chunking',
      description: 'Split content into manageable chunks by H1 structure',
      icon: Scissors,
      color: 'purple',
      component: TokenizationChunker
    },
    {
      id: 'images',
      name: 'Image Processing',
      description: 'Process and contextually place images',
      icon: Image,
      color: 'pink',
      component: ImageProcessing
    },
    {
      id: 'generation',
      name: 'Article Generation',
      description: 'Generate improved articles using AI',
      icon: Brain,
      color: 'indigo',
      component: ArticleGeneration
    },
    {
      id: 'quality',
      name: 'Quality Assurance',
      description: 'Evaluate and score generated content',
      icon: Shield,
      color: 'amber',
      component: QualityAssurance
    }
  ];

  const handleStepStatusUpdate = (stepId, status) => {
    setStepStatuses(prev => ({
      ...prev,
      [stepId]: status
    }));
  };

  const canNavigateToStep = (stepIndex) => {
    if (stepIndex === 0) return true; // Can always navigate to first step
    
    // Can navigate to next step if current step is completed
    const previousStep = pipelineSteps[stepIndex - 1];
    return stepStatuses[previousStep.id] === 'completed';
  };

  const getCurrentStepComponent = () => {
    const step = pipelineSteps[currentStep];
    const StepComponent = step.component;
    
    return (
      <StepComponent
        moduleData={step}
        processingData={processingData}
        setProcessingData={setProcessingData}
        onStatusUpdate={(status) => handleStepStatusUpdate(step.id, status)}
      />
    );
  };

  const nextStep = () => {
    if (currentStep < pipelineSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const previousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const goToStep = (stepIndex) => {
    if (canNavigateToStep(stepIndex)) {
      setCurrentStep(stepIndex);
    }
  };

  const getStepStatus = (stepId) => {
    return stepStatuses[stepId] || 'idle';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <div className="h-4 w-4 rounded-full border-2 border-gray-300" />;
    }
  };

  return (
    <div className="h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Training Engine</h1>
                <p className="text-sm text-gray-600 mt-1">
                  Advanced AI model training and optimization platform
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
              NEW
            </div>
            <div className="text-sm text-gray-500">
              Ready for training
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <Info className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-blue-900 mb-1">
                Fresh Start - New Training Engine
              </h3>
              <p className="text-sm text-blue-700">
                This is the foundation for our new training system. Select a pipeline below to begin training AI models 
                for enhanced content processing, generation, and quality assurance.
              </p>
            </div>
          </div>
        </div>

        {/* Pipeline Selection */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Training Pipelines
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
            {trainingPipelines.map((pipeline) => (
              <PipelineCard
                key={pipeline.id}
                pipeline={pipeline}
                isSelected={selectedPipeline === pipeline.id}
                onSelect={setSelectedPipeline}
                onStart={handlePipelineStart}
              />
            ))}
          </div>
        </div>

        {/* Training Status */}
        {pipelineStatus !== 'idle' && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Training Status
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">
                  Pipeline: {trainingPipelines.find(p => p.id === selectedPipeline)?.name}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  pipelineStatus === 'running'
                    ? 'bg-blue-100 text-blue-800'
                    : pipelineStatus === 'completed'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {pipelineStatus}
                </span>
              </div>
              
              {pipelineStatus === 'running' && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '45%' }}></div>
                </div>
              )}
              
              {pipelineStatus === 'completed' && (
                <div className="flex items-center space-x-2 text-green-600">
                  <CheckCircle className="h-5 w-5" />
                  <span className="text-sm font-medium">Training completed successfully!</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Future Features Preview */}
        <div className="mt-8 bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Coming Soon
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <BarChart3 className="h-5 w-5 text-gray-400" />
              <div>
                <div className="text-sm font-medium text-gray-900">Training Analytics</div>
                <div className="text-xs text-gray-500">Performance metrics & insights</div>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <Settings className="h-5 w-5 text-gray-400" />
              <div>
                <div className="text-sm font-medium text-gray-900">Custom Pipelines</div>
                <div className="text-xs text-gray-500">Build your own training workflows</div>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <Rocket className="h-5 w-5 text-gray-400" />
              <div>
                <div className="text-sm font-medium text-gray-900">Auto-scaling</div>
                <div className="text-xs text-gray-500">Dynamic resource allocation</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewTrainingEngine;