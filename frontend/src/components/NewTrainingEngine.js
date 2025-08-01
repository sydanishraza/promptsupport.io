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
  Info
} from 'lucide-react';

const NewTrainingEngine = () => {
  const [selectedPipeline, setSelectedPipeline] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState('idle');

  // Training pipelines configuration
  const trainingPipelines = [
    {
      id: 'content-extraction',
      name: 'Content Extraction Pipeline',
      description: 'Train models to better extract and structure content from various document types',
      icon: Database,
      color: 'blue',
      status: 'ready',
      progress: 0,
      features: ['Document parsing', 'Content structure detection', 'Metadata extraction']
    },
    {
      id: 'article-generation',
      name: 'Article Generation Pipeline',
      description: 'Improve AI models for generating high-quality, coherent articles from source content',
      icon: Brain,
      color: 'purple',
      status: 'ready',
      progress: 0,
      features: ['Natural language generation', 'Content coherence', 'Style consistency']
    },
    {
      id: 'image-processing',
      name: 'Image Processing Pipeline',
      description: 'Enhanced image recognition, captioning, and contextual placement within articles',
      icon: Target,
      color: 'green',
      status: 'ready',
      progress: 0,
      features: ['Image recognition', 'Context understanding', 'Caption generation']
    },
    {
      id: 'quality-assurance',
      name: 'Quality Assurance Pipeline',
      description: 'Train quality scoring models to automatically evaluate and improve generated content',
      icon: CheckCircle,
      color: 'amber',
      status: 'ready',
      progress: 0,
      features: ['Content quality scoring', 'Error detection', 'Improvement suggestions']
    }
  ];

  const handlePipelineStart = (pipelineId) => {
    setSelectedPipeline(pipelineId);
    setPipelineStatus('running');
    // Simulate training progress
    setTimeout(() => {
      setPipelineStatus('completed');
    }, 3000);
  };

  const PipelineCard = ({ pipeline, isSelected, onSelect, onStart }) => {
    const IconComponent = pipeline.icon;
    
    return (
      <div 
        className={`bg-white rounded-lg border-2 p-6 cursor-pointer transition-all duration-200 ${
          isSelected 
            ? `border-${pipeline.color}-500 bg-${pipeline.color}-50` 
            : 'border-gray-200 hover:border-gray-300'
        }`}
        onClick={() => onSelect(pipeline.id)}
      >
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-lg bg-${pipeline.color}-100`}>
            <IconComponent className={`h-6 w-6 text-${pipeline.color}-600`} />
          </div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${
            pipeline.status === 'ready' 
              ? 'bg-green-100 text-green-800'
              : pipeline.status === 'running'
              ? 'bg-blue-100 text-blue-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            {pipeline.status}
          </div>
        </div>
        
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {pipeline.name}
        </h3>
        
        <p className="text-sm text-gray-600 mb-4">
          {pipeline.description}
        </p>
        
        <div className="space-y-2 mb-4">
          {pipeline.features.map((feature, index) => (
            <div key={index} className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm text-gray-700">{feature}</span>
            </div>
          ))}
        </div>
        
        {isSelected && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onStart(pipeline.id);
            }}
            disabled={pipelineStatus === 'running'}
            className={`w-full flex items-center justify-center space-x-2 py-2 px-4 rounded-lg font-medium ${
              pipelineStatus === 'running'
                ? 'bg-gray-400 text-white cursor-not-allowed'
                : `bg-${pipeline.color}-600 text-white hover:bg-${pipeline.color}-700`
            }`}
          >
            {pipelineStatus === 'running' ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Training...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                <span>Start Training</span>
              </>
            )}
          </button>
        )}
      </div>
    );
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