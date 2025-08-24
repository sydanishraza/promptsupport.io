/**
 * PrismDemo Component
 * Demonstrates Prism.js integration with V2 Engine code blocks
 * This component shows how the backend-generated HTML is properly highlighted
 */

import React, { useState } from 'react';
import { HTMLContent, StaticCodeBlock, useCodeHighlighter } from './PrismCodeBlock';
import { Copy, Code, Eye, RefreshCw } from 'lucide-react';

const PrismDemo = () => {
  const { highlightAll, reinitialize } = useCodeHighlighter();
  const [activeTab, setActiveTab] = useState('backend-generated');

  // Example HTML content that matches V2CodeNormalizationSystem simplified output
  const v2BackendGeneratedHTML = `
    <h2>API Integration Example</h2>
    <p>This example shows how to make API calls with proper error handling and authentication.</p>
    
    <!-- evidence: ["b12","b34"] -->
    <pre class="line-numbers" data-lang="JSON" data-start="1">
<code class="language-json">{
  "api_key": "your-api-key-here",
  "endpoint": "https://api.example.com/v1/users",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer token"
  },
  "body": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "user"
  }
}</code>
</pre>

    <p>Here's the corresponding curl command:</p>
    
    <!-- evidence: ["b12","b45"] -->
    <pre class="line-numbers" data-lang="BASH" data-start="1">
<code class="language-bash">curl -X POST \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer your-token-here" \\
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "user"
  }' \\
  https://api.example.com/v1/users</code>
</pre>

    <p>And here's the Python implementation:</p>
    
    <!-- evidence: ["b56","b78"] -->
    <pre class="line-numbers" data-lang="PYTHON" data-start="1">
<code class="language-python">import requests
import json

def create_user(api_key, user_data):
    """
    Create a new user via API
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    response = requests.post(
        'https://api.example.com/v1/users',
        headers=headers,
        json=user_data
    )
    
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f'API Error: {response.status_code}')</code>
</pre>

    <p class="code-caption"><em>Complete Python function with error handling and proper authentication</em></p>
  `;

  const sqlExample = `SELECT u.id, u.name, u.email, p.title as project_title
FROM users u
LEFT JOIN projects p ON u.id = p.user_id
WHERE u.created_at >= '2024-01-01'
  AND u.status = 'active'
ORDER BY u.created_at DESC
LIMIT 10;`;

  const yamlExample = `version: '3.8'
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - API_URL=https://api.example.com
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=secret
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:`;

  const xmlExample = `<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <database>
    <host>localhost</host>
    <port>5432</port>
    <name>myapp</name>
    <credentials>
      <username>admin</username>
      <password>secret</password>
    </credentials>
  </database>
  <logging>
    <level>INFO</level>
    <file>/var/log/app.log</file>
  </logging>
</configuration>`;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          🎨 Prism.js Integration Demo
        </h1>
        <p className="text-gray-600 mb-6">
          This demo showcases the Prism.js integration for PromptSupport V2 Engine code blocks.
          All code blocks feature syntax highlighting, line numbers, and copy-to-clipboard functionality.
        </p>
        
        <div className="flex gap-4 mb-6">
          <button
            onClick={highlightAll}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <RefreshCw size={16} />
            Re-highlight All
          </button>
          <button
            onClick={reinitialize}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Code size={16} />
            Reinitialize Prism
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'backend-generated', label: 'V2 Backend Generated', icon: Eye },
              { id: 'static-examples', label: 'Static Examples', icon: Code }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon size={16} />
                {label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content Tabs */}
      {activeTab === 'backend-generated' && (
        <div className="space-y-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-yellow-800 mb-2">
              V2 Engine Backend Generated HTML
            </h3>
            <p className="text-yellow-700 text-sm">
              This content matches exactly what the V2CodeNormalizationSystem generates on the backend,
              including figure wrappers, toolbars, line numbers, and evidence comments.
            </p>
          </div>
          
          <HTMLContent 
            html={v2BackendGeneratedHTML}
            className="v2-content"
          />
        </div>
      )}

      {activeTab === 'static-examples' && (
        <div className="space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">
              Static Code Block Examples
            </h3>
            <p className="text-blue-700 text-sm">
              These examples demonstrate different programming languages and formats
              supported by the Prism.js integration.
            </p>
          </div>

          <div className="grid gap-6">
            <StaticCodeBlock
              code={sqlExample}
              language="sql"
              caption="SQL query with joins and filtering"
            />

            <StaticCodeBlock
              code={yamlExample}
              language="yaml"
              caption="Docker Compose configuration file"
            />

            <StaticCodeBlock
              code={xmlExample}
              language="xml"
              caption="Application configuration in XML format"
            />
          </div>
        </div>
      )}

      {/* Feature Overview */}
      <div className="mt-12 bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          ✨ Prism.js Features Implemented
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-green-600">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Syntax Highlighting</span>
            </div>
            <div className="flex items-center gap-2 text-green-600">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Line Numbers</span>
            </div>
            <div className="flex items-center gap-2 text-green-600">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Copy to Clipboard</span>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-green-600">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Whitespace Normalization</span>
            </div>
            <div className="flex items-center gap-2 text-green-600">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Responsive Design</span>
            </div>
            <div className="flex items-center gap-2 text-green-600">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Accessibility Support</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrismDemo;