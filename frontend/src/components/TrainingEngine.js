import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  Upload,
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
  ChevronLeft,
  Play,
  Pause,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Info,
  FileText,
  Image,
  Link,
  Video,
  Music,
  Youtube,
  Monitor,
  Scissors,
  PenTool,
  MapPin,
  Shield,
  Eye,
  Download,
  ArrowRight,
  Clock,
  Workflow
} from 'lucide-react';

// Import pipeline components
import UploadInterface from './TrainingEngine/UploadInterface';
import ContentExtraction from './TrainingEngine/ContentExtraction';
import TokenizationChunker from './TrainingEngine/TokenizationChunker';
import ArticleGeneration from './TrainingEngine/ArticleGeneration';
import ImageProcessing from './TrainingEngine/ImageProcessing';
import QualityAssurance from './TrainingEngine/QualityAssurance';
import OutputRenderer from './TrainingEngine/OutputRenderer';
import IntegrationSync from './TrainingEngine/IntegrationSync';

const TrainingEngine = () => {
  const [activeModule, setActiveModule] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState({});
  const [processingData, setProcessingData] = useState(null);

  // Training modules configuration
  const trainingModules = [
    {
      id: 'upload-interface',
      name: 'Upload Interface',
      description: 'Accepts supported file types or URLs for ingestion',
      icon: Upload,
      color: 'blue',
      component: UploadInterface,
      emergentModule: 'resource_upload_handler',
      status: 'ready'
    },
    {
      id: 'content-extraction',
      name: 'Content Extraction Pipeline',
      description: 'Parse files → structured HTML with data-block-id',
      icon: Database,
      color: 'green',
      component: ContentExtraction,
      emergentModule: 'content_extraction_pipeline',
      status: 'ready'
    },
    {
      id: 'tokenization-chunker',
      name: 'Tokenization + Chunker',
      description: 'Token estimation and intelligent chunking by H1 boundaries',
      icon: Scissors,
      color: 'purple',
      component: TokenizationChunker,
      emergentModule: 'chunking_engine',
      status: 'ready'
    },
    {
      id: 'article-generation',
      name: 'Article Generation Pipeline',
      description: 'LLM rewrite with clarity and structure improvements',
      icon: PenTool,
      color: 'indigo',
      component: ArticleGeneration,
      emergentModule: 'article_generation_pipeline',
      status: 'ready'
    },
    {
      id: 'image-processing',
      name: 'Image Processing Pipeline',
      description: 'Extract, map, and embed images with captions',
      icon: Image,
      color: 'pink',
      component: ImageProcessing,
      emergentModule: 'image_processing_pipeline',
      status: 'ready'
    },
    {
      id: 'quality-assurance',
      name: 'Quality Assurance Pipeline',
      description: 'Content completeness and quality scoring (0-10)',
      icon: Shield,
      color: 'amber',
      component: QualityAssurance,
      emergentModule: 'quality_assurance_pipeline',
      status: 'ready'
    },
    {
      id: 'output-renderer',
      name: 'Final Output Renderer',
      description: 'Merge chunks, replace tokens, save to Content Library',
      icon: Eye,
      color: 'cyan',
      component: OutputRenderer,
      emergentModule: 'article_finalizer',
      status: 'ready'
    },
    {
      id: 'integration-sync',
      name: 'Integration Sync',
      description: 'Connect Notion, GitHub, Confluence, Slack for auto-sync',
      icon: Link,
      color: 'orange',
      component: IntegrationSync,
      emergentModule: 'integration_sync_setup',
      status: 'ready'
    }
  ];

  const renderModuleContent = () => {
    if (activeModule === 'overview') {
      return <OverviewDashboard />;
    }
    
    const module = trainingModules.find(m => m.id === activeModule);
    if (module && module.component) {
      const ComponentToRender = module.component;
      return (
        <ComponentToRender 
          moduleData={module}
          processingData={processingData}
          setProcessingData={setProcessingData}
          onStatusUpdate={(status) => setPipelineStatus(prev => ({ ...prev, [module.id]: status }))}
        />
      );
    }
    return <OverviewDashboard />;
  };

  const OverviewDashboard = () => (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-white rounded-lg shadow-sm">
            <Brain className="h-8 w-8 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Modular Training Engine
            </h2>
            <p className="text-gray-700">
              Pipeline-based AI training system with independent, reusable modules for content processing, 
              generation, and quality assurance.
            </p>
          </div>
        </div>
      </div>

      {/* Pipeline Overview */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Processing Pipeline Flow
        </h3>
        <div className="flex items-center space-x-2 overflow-x-auto pb-4">
          {trainingModules.map((module, index) => {
            const IconComponent = module.icon;
            return (
              <React.Fragment key={module.id}>
                <div 
                  className={`flex-shrink-0 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                    pipelineStatus[module.id] === 'processing' 
                      ? 'border-blue-500 bg-blue-50' 
                      : pipelineStatus[module.id] === 'completed'
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setActiveModule(module.id)}
                >
                  <IconComponent className={`h-6 w-6 text-${module.color}-600`} />
                  <div className="text-xs font-medium text-gray-700 mt-1 text-center">
                    {module.name.split(' ')[0]}
                  </div>
                </div>
                {index < trainingModules.length - 1 && (
                  <ArrowRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Module Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {trainingModules.map((module) => {
          const IconComponent = module.icon;
          return (
            <motion.div
              key={module.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="bg-white rounded-lg border border-gray-200 p-6 cursor-pointer hover:border-gray-300 transition-all duration-200"
              onClick={() => setActiveModule(module.id)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-lg bg-${module.color}-100`}>
                  <IconComponent className={`h-6 w-6 text-${module.color}-600`} />
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    module.status === 'ready' 
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {module.status}
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                </div>
              </div>
              
              <h4 className="text-lg font-semibold text-gray-900 mb-2">
                {module.name}
              </h4>
              
              <p className="text-sm text-gray-600 mb-4">
                {module.description}
              </p>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Module: {module.emergentModule}</span>
                <span>Ready</span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          System Status
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <Workflow className="h-6 w-6 mx-auto mb-2 text-blue-600" />
            <div className="text-2xl font-bold text-blue-600">8</div>
            <div className="text-sm text-gray-600">Active Modules</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <CheckCircle className="h-6 w-6 mx-auto mb-2 text-green-600" />
            <div className="text-2xl font-bold text-green-600">100%</div>
            <div className="text-sm text-gray-600">System Health</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <Clock className="h-6 w-6 mx-auto mb-2 text-purple-600" />
            <div className="text-2xl font-bold text-purple-600">0</div>
            <div className="text-sm text-gray-600">Processing Jobs</div>
          </div>
          <div className="text-center p-4 bg-amber-50 rounded-lg">
            <Target className="h-6 w-6 mx-auto mb-2 text-amber-600" />
            <div className="text-2xl font-bold text-amber-600">Ready</div>
            <div className="text-sm text-gray-600">Pipeline Status</div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Training Engine</h1>
                <p className="text-sm text-gray-600 mt-1">
                  Modular pipeline-based AI training system • Emergent Modules
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
              EMERGENT
            </div>
            {activeModule !== 'overview' && (
              <button
                onClick={() => setActiveModule('overview')}
                className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200"
              >
                ← Overview
              </button>
            )}
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-2 text-gray-600 hover:text-gray-800"
            >
              {sidebarCollapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>

      <div className="flex h-full pt-0">
        {/* Module Navigation Sidebar */}
        <div className={`${sidebarCollapsed ? 'w-16' : 'w-80'} bg-white border-r border-gray-200 transition-all duration-300 overflow-y-auto`}>
          <div className="p-4">
            {!sidebarCollapsed && (
              <div className="space-y-2">
                <button
                  onClick={() => setActiveModule('overview')}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    activeModule === 'overview'
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <BarChart3 className="h-5 w-5" />
                  <span className="font-medium">Overview</span>
                </button>
                
                <div className="pt-4">
                  <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
                    Training Modules
                  </h3>
                  <div className="space-y-1">
                    {trainingModules.map((module) => {
                      const IconComponent = module.icon;
                      return (
                        <button
                          key={module.id}
                          onClick={() => setActiveModule(module.id)}
                          className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                            activeModule === module.id
                              ? `bg-${module.color}-50 text-${module.color}-600`
                              : 'text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          <IconComponent className="h-4 w-4" />
                          <span className="text-sm">{module.name}</span>
                          {pipelineStatus[module.id] === 'processing' && (
                            <RefreshCw className="h-3 w-3 animate-spin ml-auto" />
                          )}
                          {pipelineStatus[module.id] === 'completed' && (
                            <CheckCircle className="h-3 w-3 text-green-500 ml-auto" />
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeModule}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                {renderModuleContent()}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainingEngine;