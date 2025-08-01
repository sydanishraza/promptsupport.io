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
                <h1 className="text-2xl font-bold text-gray-900">New Training Engine</h1>
                <p className="text-sm text-gray-600 mt-1">
                  Modular AI training pipeline with sequential workflow
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
              NEW
            </div>
            <div className="text-sm text-gray-500">
              Step {currentStep + 1} of {pipelineSteps.length}
            </div>
          </div>
        </div>
      </div>

      {/* Pipeline Progress */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Training Pipeline Progress</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={previousStep}
              disabled={currentStep === 0}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium ${
                currentStep === 0
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Previous</span>
            </button>
            <button
              onClick={nextStep}
              disabled={currentStep === pipelineSteps.length - 1 || stepStatuses[pipelineSteps[currentStep].id] !== 'completed'}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium ${
                currentStep === pipelineSteps.length - 1 || stepStatuses[pipelineSteps[currentStep].id] !== 'completed'
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              <span>Next</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        <div className="flex items-center space-x-4 overflow-x-auto pb-2">
          {pipelineSteps.map((step, index) => {
            const IconComponent = step.icon;
            const isActive = index === currentStep;
            const isCompleted = stepStatuses[step.id] === 'completed';
            const isProcessing = stepStatuses[step.id] === 'processing';
            const canNavigate = canNavigateToStep(index);
            
            return (
              <div key={step.id} className="flex items-center flex-shrink-0">
                <div
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg cursor-pointer transition-all duration-200 ${
                    isActive
                      ? `bg-${step.color}-100 border-2 border-${step.color}-500`
                      : canNavigate
                      ? 'bg-white border border-gray-200 hover:border-gray-300'
                      : 'bg-gray-50 border border-gray-200 opacity-50 cursor-not-allowed'
                  }`}
                  onClick={() => canNavigate && goToStep(index)}
                >
                  <div className={`p-2 rounded-lg ${
                    isActive
                      ? `bg-${step.color}-200`
                      : isCompleted
                      ? 'bg-green-100'
                      : 'bg-gray-100'
                  }`}>
                    <IconComponent className={`h-5 w-5 ${
                      isActive
                        ? `text-${step.color}-700`
                        : isCompleted
                        ? 'text-green-600'
                        : 'text-gray-500'
                    }`} />
                  </div>
                  <div>
                    <div className={`text-sm font-medium ${
                      isActive
                        ? `text-${step.color}-900`
                        : isCompleted
                        ? 'text-green-900'
                        : 'text-gray-700'
                    }`}>
                      {step.name}
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      {getStatusIcon(getStepStatus(step.id))}
                      <span className="text-xs text-gray-500">
                        {getStepStatus(step.id) === 'completed' ? 'Complete' : 
                         getStepStatus(step.id) === 'processing' ? 'Processing...' :
                         getStepStatus(step.id) === 'error' ? 'Error' : 'Pending'}
                      </span>
                    </div>
                  </div>
                </div>
                {index < pipelineSteps.length - 1 && (
                  <ChevronRight className="h-5 w-5 text-gray-400 mx-2 flex-shrink-0" />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="p-6">
        {/* Current Step Info */}
        <div className="mb-6 bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className={`p-2 bg-${pipelineSteps[currentStep].color}-100 rounded-lg`}>
              {React.createElement(pipelineSteps[currentStep].icon, {
                className: `h-6 w-6 text-${pipelineSteps[currentStep].color}-600`
              })}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {pipelineSteps[currentStep].name}
              </h2>
              <p className="text-sm text-gray-600">
                {pipelineSteps[currentStep].description}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-700">Status:</span>
              {getStatusIcon(getStepStatus(pipelineSteps[currentStep].id))}
              <span className={`text-sm font-medium ${
                getStepStatus(pipelineSteps[currentStep].id) === 'completed' ? 'text-green-600' :
                getStepStatus(pipelineSteps[currentStep].id) === 'processing' ? 'text-blue-600' :
                getStepStatus(pipelineSteps[currentStep].id) === 'error' ? 'text-red-600' :
                'text-gray-600'
              }`}>
                {getStepStatus(pipelineSteps[currentStep].id) === 'completed' ? 'Completed' : 
                 getStepStatus(pipelineSteps[currentStep].id) === 'processing' ? 'Processing...' :
                 getStepStatus(pipelineSteps[currentStep].id) === 'error' ? 'Error occurred' : 'Ready to start'}
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Module: {pipelineSteps[currentStep].id}_pipeline
            </div>
          </div>
        </div>

        {/* Step Component */}
        <div className="mb-6">
          {getCurrentStepComponent()}
        </div>

        {/* Pipeline Overview */}
        {currentStep === 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-blue-900 mb-2">
                  Welcome to the New Training Engine
                </h3>
                <p className="text-sm text-blue-700 mb-3">
                  This modular training pipeline will guide you through the complete process of content training:
                </p>
                <ol className="text-sm text-blue-700 space-y-1">
                  <li>1. <strong>Upload Resources:</strong> Start by uploading documents or providing URLs</li>
                  <li>2. <strong>Extract Content:</strong> Parse and structure your content with block IDs</li>
                  <li>3. <strong>Chunk & Tokenize:</strong> Split content intelligently based on document structure</li>
                  <li>4. <strong>Process Images:</strong> Handle image extraction and contextual placement</li>
                  <li>5. <strong>Generate Articles:</strong> Use AI to create improved, comprehensive articles</li>
                  <li>6. <strong>Quality Assurance:</strong> Evaluate and score the generated content</li>
                </ol>
                <p className="text-sm text-blue-700 mt-3">
                  Each step builds on the previous one, creating a comprehensive training dataset for your AI models.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NewTrainingEngine;