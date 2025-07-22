import React from 'react';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="max-w-2xl mx-auto text-center p-8">
        <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
          <span className="text-white font-bold text-2xl">P</span>
        </div>
        
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          PromptSupport
        </h1>
        
        <p className="text-xl text-gray-600 mb-8">
          Clean Slate - Ready for Fresh Development
        </p>
        
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">System Status</h2>
          <div className="space-y-2 text-sm text-gray-600">
            <div className="flex justify-between">
              <span>Backend:</span>
              <span className="text-green-600 font-medium">Clean & Running</span>
            </div>
            <div className="flex justify-between">
              <span>Frontend:</span>
              <span className="text-green-600 font-medium">Reset Complete</span>
            </div>
            <div className="flex justify-between">
              <span>Database:</span>
              <span className="text-blue-600 font-medium">Fresh Start</span>
            </div>
          </div>
        </div>
        
        <div className="text-gray-500 text-sm">
          <p>All previous code has been cleaned up.</p>
          <p>Ready for your new dev plan and UI blueprint! 🚀</p>
        </div>
      </div>
    </div>
  );
}

export default App;