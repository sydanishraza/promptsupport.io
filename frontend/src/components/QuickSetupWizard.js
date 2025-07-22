import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Building2, 
  Users, 
  Upload, 
  Link, 
  Puzzle, 
  Play,
  Check,
  ArrowRight,
  ArrowLeft,
  X
} from 'lucide-react';

const QuickSetupWizard = ({ onComplete, onSkip }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    orgName: '',
    orgLogo: null,
    subdomain: '',
    teammates: ['', ''],
    uploadedFiles: [],
    urls: [''],
    integrations: {
      notion: false,
      github: false,
      jira: false,
      confluence: false,
      drive: false,
      slack: false
    },
    modules: {
      knowledgeBase: true,
      developerDocs: false,
      chatbot: true,
      ticketing: false,
      community: false
    }
  });

  const steps = [
    {
      id: 'org-setup',
      title: 'Organization Setup',
      description: 'Name, logo, custom subdomain',
      icon: Building2
    },
    {
      id: 'teammates',
      title: 'Invite Teammates',
      description: 'Add up to 2 teammates by email',
      icon: Users
    },
    {
      id: 'knowledge',
      title: 'Upload Knowledge',
      description: 'Upload files, paste URLs, record videos',
      icon: Upload
    },
    {
      id: 'integrations',
      title: 'Enable Integrations',
      description: 'Notion, GitHub, JIRA, Confluence, Google Drive, etc.',
      icon: Link
    },
    {
      id: 'modules',
      title: 'Select Modules',
      description: 'KB, Docs, Chatbot, Ticketing, Community',
      icon: Puzzle
    },
    {
      id: 'initialize',
      title: 'Run Initialization',
      description: 'Progress animation while agents bootstrap',
      icon: Play
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const updateFormData = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const renderStepContent = () => {
    switch (steps[currentStep].id) {
      case 'org-setup':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization Name *
              </label>
              <input
                type="text"
                value={formData.orgName}
                onChange={(e) => updateFormData('orgName', e.target.value)}
                placeholder="Enter organization name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Subdomain
              </label>
              <div className="flex items-center">
                <input
                  type="text"
                  value={formData.subdomain}
                  onChange={(e) => updateFormData('subdomain', e.target.value)}
                  placeholder="myorg"
                  className="px-3 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <span className="px-3 py-2 bg-gray-100 border border-l-0 border-gray-300 rounded-r-lg text-gray-600">
                  .promptsupport.ai
                </span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization Logo
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                <p className="text-sm text-gray-600">Upload logo (PNG, JPG)</p>
              </div>
            </div>
          </div>
        );

      case 'teammates':
        return (
          <div className="space-y-4">
            <p className="text-gray-600">Add up to 2 teammates to collaborate on your support platform.</p>
            {formData.teammates.map((email, index) => (
              <div key={index}>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Teammate {index + 1} Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => {
                    const newTeammates = [...formData.teammates];
                    newTeammates[index] = e.target.value;
                    updateFormData('teammates', newTeammates);
                  }}
                  placeholder="colleague@company.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
          </div>
        );

      case 'knowledge':
        return (
          <div className="space-y-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Upload Files</h4>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                <p className="text-sm text-gray-600">Drop files or click to upload</p>
                <p className="text-xs text-gray-500 mt-1">PDF, DOCX, CSV, MP4, MP3, etc.</p>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Add URLs</h4>
              {formData.urls.map((url, index) => (
                <input
                  key={index}
                  type="url"
                  value={url}
                  onChange={(e) => {
                    const newUrls = [...formData.urls];
                    newUrls[index] = e.target.value;
                    updateFormData('urls', newUrls);
                  }}
                  placeholder="https://docs.company.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                />
              ))}
            </div>
          </div>
        );

      case 'integrations':
        return (
          <div className="space-y-4">
            <p className="text-gray-600 mb-4">Connect your existing tools for automatic syncing.</p>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(formData.integrations).map(([key, enabled]) => (
                <div
                  key={key}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    enabled 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onClick={() => updateFormData('integrations', {
                    ...formData.integrations,
                    [key]: !enabled
                  })}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium capitalize">{key}</span>
                    {enabled && <Check className="h-4 w-4 text-blue-600" />}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'modules':
        return (
          <div className="space-y-4">
            <p className="text-gray-600 mb-4">Select which modules to enable for your support platform.</p>
            <div className="space-y-3">
              {Object.entries(formData.modules).map(([key, enabled]) => {
                const labels = {
                  knowledgeBase: 'Knowledge Base',
                  developerDocs: 'Developer Docs',
                  chatbot: 'AI Chatbot',
                  ticketing: 'Ticketing System',
                  community: 'Community Portal'
                };
                return (
                  <div
                    key={key}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      enabled 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    onClick={() => updateFormData('modules', {
                      ...formData.modules,
                      [key]: !enabled
                    })}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{labels[key]}</span>
                      {enabled && <Check className="h-4 w-4 text-blue-600" />}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );

      case 'initialize':
        return (
          <div className="text-center space-y-6">
            <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <Play className="h-8 w-8 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Ready to Initialize PromptSupport!
              </h3>
              <p className="text-gray-600">
                Our AI agents will now bootstrap your support platform with the configuration you've provided.
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-left">
              <h4 className="font-medium text-gray-900 mb-2">What happens next:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Content Engine will process your uploaded knowledge</li>
                <li>• AI Agents will generate your Knowledge Base structure</li>
                <li>• Chatbot will be trained on your content</li>
                <li>• Selected modules will be configured and deployed</li>
              </ul>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Quick Setup Wizard</h2>
            <p className="text-sm text-gray-500">Step {currentStep + 1} of {steps.length}</p>
          </div>
          <button
            onClick={onSkip}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="px-6 py-4 max-h-96 overflow-y-auto">
          <div className="mb-6">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                {React.createElement(steps[currentStep].icon, { size: 16, className: 'text-blue-600' })}
              </div>
              <div>
                <h3 className="font-medium text-gray-900">{steps[currentStep].title}</h3>
                <p className="text-sm text-gray-500">{steps[currentStep].description}</p>
              </div>
            </div>
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderStepContent()}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
          <button
            onClick={handlePrev}
            disabled={currentStep === 0}
            className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:text-gray-400 disabled:cursor-not-allowed"
          >
            <ArrowLeft size={16} />
            <span>Previous</span>
          </button>

          <div className="flex space-x-2">
            {steps.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${
                  index === currentStep 
                    ? 'bg-blue-600' 
                    : index < currentStep 
                    ? 'bg-blue-300' 
                    : 'bg-gray-300'
                }`}
              />
            ))}
          </div>

          <button
            onClick={handleNext}
            className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
          >
            <span>{currentStep === steps.length - 1 ? 'Initialize' : 'Next'}</span>
            <ArrowRight size={16} />
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default QuickSetupWizard;