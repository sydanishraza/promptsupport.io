import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FlaskConical,
  Brain,
  Archive,
  ChevronRight,
  Settings,
  BarChart3,
  Target,
  Lightbulb,
  Rocket,
  Clock
} from 'lucide-react';
import NewTrainingEngine from './NewTrainingEngine';
import LegacyTrainingInterface from './LegacyTrainingInterface';

const LabInterface = () => {
  const [activeView, setActiveView] = useState('overview');

  const labModules = [
    {
      id: 'training-engine',
      name: 'Training Engine',
      description: 'Advanced AI model training and optimization platform',
      icon: Brain,
      color: 'blue',
      status: 'new',
      component: NewTrainingEngine
    },
    {
      id: 'legacy-training',
      name: 'Legacy Training Engine',
      description: 'Original document processing and training interface',
      icon: Archive,
      color: 'amber',
      status: 'legacy',
      component: LegacyTrainingInterface
    }
  ];

  const renderModuleView = () => {
    const module = labModules.find(m => m.id === activeView);
    if (module && module.component) {
      const ComponentToRender = module.component;
      return <ComponentToRender />;
    }
    return null;
  };

  if (activeView !== 'overview') {
    return renderModuleView();
  }

  return (
    <div className="h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <FlaskConical className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Lab</h1>
                <p className="text-sm text-gray-600 mt-1">
                  Internal training and development environment for PromptSupport AI models
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="text-sm text-gray-500">
              Environment: Development
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 mb-8">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white rounded-lg shadow-sm">
              <FlaskConical className="h-8 w-8 text-purple-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Welcome to the Lab
              </h2>
              <p className="text-gray-700">
                This is your development environment for training, testing, and improving PromptSupport's AI models.
                Choose a module below to get started.
              </p>
            </div>
          </div>
        </div>

        {/* Lab Modules */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Available Modules
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {labModules.map((module) => {
              const IconComponent = module.icon;
              return (
                <motion.div
                  key={module.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="bg-white rounded-lg border border-gray-200 p-6 cursor-pointer hover:border-gray-300 transition-all duration-200"
                  onClick={() => setActiveView(module.id)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-lg bg-${module.color}-100`}>
                      <IconComponent className={`h-6 w-6 text-${module.color}-600`} />
                    </div>
                    <div className="flex items-center space-x-2">
                      {module.status === 'new' && (
                        <div className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                          NEW
                        </div>
                      )}
                      {module.status === 'legacy' && (
                        <div className="px-2 py-1 bg-amber-100 text-amber-800 text-xs font-medium rounded-full">
                          LEGACY
                        </div>
                      )}
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
                    <span>Click to access</span>
                    <span>Ready</span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Lab Statistics
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <Brain className="h-6 w-6 mx-auto mb-2 text-blue-600" />
              <div className="text-2xl font-bold text-blue-600">2</div>
              <div className="text-sm text-gray-600">Training Modules</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <Target className="h-6 w-6 mx-auto mb-2 text-green-600" />
              <div className="text-2xl font-bold text-green-600">4</div>
              <div className="text-sm text-gray-600">Training Pipelines</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <Clock className="h-6 w-6 mx-auto mb-2 text-purple-600" />
              <div className="text-2xl font-bold text-purple-600">0</div>
              <div className="text-sm text-gray-600">Active Sessions</div>
            </div>
            <div className="text-center p-4 bg-amber-50 rounded-lg">
              <BarChart3 className="h-6 w-6 mx-auto mb-2 text-amber-600" />
              <div className="text-2xl font-bold text-amber-600">Ready</div>
              <div className="text-sm text-gray-600">System Status</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LabInterface;