import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Move, 
  ChevronRight, 
  ChevronDown,
  Folder,
  FileText,
  Eye,
  Settings,
  Palette,
  Globe,
  Search,
  Save,
  ArrowLeft,
  ExternalLink
} from 'lucide-react';

const KnowledgeBaseBuilder = () => {
  const [activeView, setActiveView] = useState('builder'); // builder, preview, settings, deploy
  const [tocStructure, setTocStructure] = useState([
    {
      id: 'category-1',
      title: 'Getting Started',
      type: 'category',
      expanded: true,
      children: [
        {
          id: 'section-1',
          title: 'Setup & Configuration',
          type: 'section',
          expanded: true,
          children: [
            {
              id: 'article-1',
              title: 'Initial Setup',
              type: 'article',
              published: true,
              wordCount: 850
            },
            {
              id: 'article-2',
              title: 'Configuration Guide',
              type: 'article',
              published: true,
              wordCount: 1200
            }
          ]
        },
        {
          id: 'section-2',
          title: 'Basic Usage',
          type: 'section',
          expanded: false,
          children: [
            {
              id: 'article-3',
              title: 'Creating Your First Article',
              type: 'article',
              published: false,
              wordCount: 650
            }
          ]
        }
      ]
    },
    {
      id: 'category-2',
      title: 'Advanced Features',
      type: 'category',
      expanded: false,
      children: [
        {
          id: 'section-3',
          title: 'Integrations',
          type: 'section',
          expanded: false,
          children: [
            {
              id: 'article-4',
              title: 'GitHub Integration',
              type: 'article',
              published: true,
              wordCount: 950
            },
            {
              id: 'article-5',
              title: 'Slack Integration',
              type: 'article',
              published: true,
              wordCount: 750
            }
          ]
        }
      ]
    }
  ]);

  const [theme, setTheme] = useState({
    primaryColor: '#3B82F6',
    backgroundColor: '#FFFFFF',
    textColor: '#111827',
    fontFamily: 'Inter',
    layout: 'sidebar',
    logoUrl: '',
    faviconUrl: ''
  });

  const [searchEnabled, setSearchEnabled] = useState(true);
  const [customDomain, setCustomDomain] = useState('');
  const [deploymentMode, setDeploymentMode] = useState('standalone'); // standalone, unified
  
  const [showNewItemModal, setShowNewItemModal] = useState(false);
  const [newItemType, setNewItemType] = useState('category');
  const [newItemTitle, setNewItemTitle] = useState('');
  const [selectedParent, setSelectedParent] = useState(null);

  const reorder = (list, startIndex, endIndex) => {
    const result = Array.from(list);
    const [removed] = result.splice(startIndex, 1);
    result.splice(endIndex, 0, removed);
    return result;
  };

  const findItem = (items, id) => {
    for (const item of items) {
      if (item.id === id) return item;
      if (item.children) {
        const found = findItem(item.children, id);
        if (found) return found;
      }
    }
    return null;
  };

  const removeItem = (items, id) => {
    return items.filter(item => {
      if (item.id === id) return false;
      if (item.children) {
        item.children = removeItem(item.children, id);
      }
      return true;
    });
  };

  const addItemToParent = (items, parentId, newItem) => {
    return items.map(item => {
      if (item.id === parentId) {
        return {
          ...item,
          children: [...(item.children || []), newItem]
        };
      }
      if (item.children) {
        return {
          ...item,
          children: addItemToParent(item.children, parentId, newItem)
        };
      }
      return item;
    });
  };

  const toggleExpanded = (items, id) => {
    return items.map(item => {
      if (item.id === id) {
        return { ...item, expanded: !item.expanded };
      }
      if (item.children) {
        return { ...item, children: toggleExpanded(item.children, id) };
      }
      return item;
    });
  };

  const onDragEnd = (result) => {
    if (!result.destination) return;

    const { source, destination } = result;
    
    if (source.droppableId === destination.droppableId) {
      // Reordering within the same level
      if (source.droppableId === 'root') {
        const reordered = reorder(tocStructure, source.index, destination.index);
        setTocStructure(reordered);
      }
      // Handle nested reordering for children
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'category': return Folder;
      case 'section': return Folder;
      case 'article': return FileText;
      default: return FileText;
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'category': return 'text-blue-600 bg-blue-100';
      case 'section': return 'text-green-600 bg-green-100';
      case 'article': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const renderTocItem = (item, index, level = 0) => (
    <Draggable key={item.id} draggableId={item.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          className={`${snapshot.isDragging ? 'opacity-75' : ''}`}
        >
          <div 
            className={`flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 group ${
              level > 0 ? `ml-${level * 4}` : ''
            }`}
            style={{ paddingLeft: `${level * 20 + 8}px` }}
          >
            <div {...provided.dragHandleProps} className="opacity-0 group-hover:opacity-100 cursor-grab">
              <Move size={14} className="text-gray-400" />
            </div>

            {item.children && item.children.length > 0 && (
              <button 
                onClick={() => setTocStructure(toggleExpanded(tocStructure, item.id))}
                className="p-1 hover:bg-gray-200 rounded"
              >
                {item.expanded ? 
                  <ChevronDown size={14} className="text-gray-500" /> : 
                  <ChevronRight size={14} className="text-gray-500" />
                }
              </button>
            )}

            <div className={`w-6 h-6 rounded-lg flex items-center justify-center ${getTypeColor(item.type)}`}>
              {React.createElement(getIcon(item.type), { size: 14 })}
            </div>

            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <span className="font-medium text-gray-900">{item.title}</span>
                {item.type === 'article' && (
                  <>
                    <span className={`w-2 h-2 rounded-full ${item.published ? 'bg-green-400' : 'bg-yellow-400'}`} />
                    <span className="text-xs text-gray-500">{item.wordCount} words</span>
                  </>
                )}
              </div>
            </div>

            <div className="opacity-0 group-hover:opacity-100 flex items-center space-x-1">
              <button 
                className="p-1 text-gray-400 hover:text-blue-600 rounded"
                onClick={() => {
                  setSelectedParent(item.id);
                  setShowNewItemModal(true);
                }}
              >
                <Plus size={14} />
              </button>
              <button className="p-1 text-gray-400 hover:text-gray-600 rounded">
                <Edit size={14} />
              </button>
              <button 
                onClick={() => setTocStructure(removeItem(tocStructure, item.id))}
                className="p-1 text-gray-400 hover:text-red-600 rounded"
              >
                <Trash2 size={14} />
              </button>
            </div>
          </div>

          {item.expanded && item.children && (
            <div>
              {item.children.map((child, childIndex) => 
                renderTocItem(child, childIndex, level + 1)
              )}
            </div>
          )}
        </div>
      )}
    </Draggable>
  );

  const handleAddItem = () => {
    const newItem = {
      id: `${newItemType}-${Date.now()}`,
      title: newItemTitle,
      type: newItemType,
      expanded: false,
      children: newItemType !== 'article' ? [] : undefined,
      published: newItemType === 'article' ? false : undefined,
      wordCount: newItemType === 'article' ? 0 : undefined
    };

    if (selectedParent) {
      setTocStructure(addItemToParent(tocStructure, selectedParent, newItem));
    } else {
      setTocStructure([...tocStructure, newItem]);
    }

    setShowNewItemModal(false);
    setNewItemTitle('');
    setSelectedParent(null);
  };

  const renderBuilder = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
      {/* TOC Structure */}
      <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Table of Contents</h2>
            <button
              onClick={() => setShowNewItemModal(true)}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-sm"
            >
              <Plus size={14} />
              <span>Add Item</span>
            </button>
          </div>
          <p className="text-gray-600 text-sm mt-1">Drag and drop to reorder items</p>
        </div>

        <div className="p-6 max-h-96 overflow-y-auto">
          <DragDropContext onDragEnd={onDragEnd}>
            <Droppable droppableId="root">
              {(provided) => (
                <div {...provided.droppableProps} ref={provided.innerRef} className="space-y-1">
                  {tocStructure.map((item, index) => renderTocItem(item, index))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </div>
      </div>

      {/* Settings Panel */}
      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Build Settings</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">AI Search</label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={searchEnabled}
                  onChange={(e) => setSearchEnabled(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-600">Enable AI-powered search (Qdrant)</span>
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Deployment Mode</label>
              <select
                value={deploymentMode}
                onChange={(e) => setDeploymentMode(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="standalone">Standalone Knowledge Base</option>
                <option value="unified">Unified Portal Mode</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Custom Domain</label>
              <input
                type="text"
                value={customDomain}
                onChange={(e) => setCustomDomain(e.target.value)}
                placeholder="help.company.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <button
              onClick={() => setActiveView('preview')}
              className="w-full flex items-center space-x-2 p-2 text-left hover:bg-gray-50 rounded-lg"
            >
              <Eye size={16} />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setActiveView('settings')}
              className="w-full flex items-center space-x-2 p-2 text-left hover:bg-gray-50 rounded-lg"
            >
              <Palette size={16} />
              <span>Theming</span>
            </button>
            <button
              onClick={() => setActiveView('deploy')}
              className="w-full flex items-center space-x-2 p-2 text-left hover:bg-gray-50 rounded-lg"
            >
              <Globe size={16} />
              <span>Deploy</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderThemeSettings = () => (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={() => setActiveView('builder')}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Theme Settings</h2>
          <p className="text-gray-600">Customize the appearance of your knowledge base</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Colors</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Primary Color</label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={theme.primaryColor}
                  onChange={(e) => setTheme(prev => ({ ...prev, primaryColor: e.target.value }))}
                  className="w-12 h-10 border border-gray-300 rounded-lg"
                />
                <input
                  type="text"
                  value={theme.primaryColor}
                  onChange={(e) => setTheme(prev => ({ ...prev, primaryColor: e.target.value }))}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Background Color</label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={theme.backgroundColor}
                  onChange={(e) => setTheme(prev => ({ ...prev, backgroundColor: e.target.value }))}
                  className="w-12 h-10 border border-gray-300 rounded-lg"
                />
                <input
                  type="text"
                  value={theme.backgroundColor}
                  onChange={(e) => setTheme(prev => ({ ...prev, backgroundColor: e.target.value }))}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Text Color</label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={theme.textColor}
                  onChange={(e) => setTheme(prev => ({ ...prev, textColor: e.target.value }))}
                  className="w-12 h-10 border border-gray-300 rounded-lg"
                />
                <input
                  type="text"
                  value={theme.textColor}
                  onChange={(e) => setTheme(prev => ({ ...prev, textColor: e.target.value }))}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Typography & Layout</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Font Family</label>
              <select
                value={theme.fontFamily}
                onChange={(e) => setTheme(prev => ({ ...prev, fontFamily: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Inter">Inter</option>
                <option value="Roboto">Roboto</option>
                <option value="Open Sans">Open Sans</option>
                <option value="Lato">Lato</option>
                <option value="Poppins">Poppins</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Layout Style</label>
              <select
                value={theme.layout}
                onChange={(e) => setTheme(prev => ({ ...prev, layout: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="sidebar">Sidebar Navigation</option>
                <option value="top">Top Navigation</option>
                <option value="minimal">Minimal</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Logo URL</label>
              <input
                type="url"
                value={theme.logoUrl}
                onChange={(e) => setTheme(prev => ({ ...prev, logoUrl: e.target.value }))}
                placeholder="https://company.com/logo.png"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg">
          Save Theme Settings
        </button>
      </div>
    </div>
  );

  const renderPreview = () => (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setActiveView('builder')}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Knowledge Base Preview</h2>
            <p className="text-gray-600">Preview how your knowledge base will look to users</p>
          </div>
        </div>
        <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-700">
          <ExternalLink size={16} />
          <span>Open in New Tab</span>
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-lg">
        {/* Preview Header */}
        <div className="bg-gray-50 border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg"></div>
              <span className="font-semibold">Company Knowledge Base</span>
            </div>
            <div className="flex items-center space-x-2">
              <Search size={16} className="text-gray-400" />
              <input 
                type="text" 
                placeholder="Search..." 
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
                disabled 
              />
            </div>
          </div>
        </div>

        {/* Preview Content */}
        <div className="flex h-96">
          {/* Sidebar TOC */}
          <div className="w-1/3 border-r border-gray-200 bg-gray-50 overflow-y-auto">
            <div className="p-4">
              {tocStructure.map((category) => (
                <div key={category.id} className="mb-4">
                  <div className="font-medium text-gray-900 mb-2 flex items-center space-x-2">
                    <Folder size={16} className="text-blue-600" />
                    <span>{category.title}</span>
                  </div>
                  {category.children?.map((section) => (
                    <div key={section.id} className="ml-4 mb-2">
                      <div className="text-sm font-medium text-gray-700 mb-1 flex items-center space-x-2">
                        <Folder size={14} className="text-green-600" />
                        <span>{section.title}</span>
                      </div>
                      {section.children?.map((article) => (
                        <div key={article.id} className="ml-4">
                          <div className="text-sm text-gray-600 py-1 hover:text-blue-600 cursor-pointer flex items-center space-x-2">
                            <FileText size={12} className="text-purple-600" />
                            <span>{article.title}</span>
                            {article.published && <span className="w-2 h-2 bg-green-400 rounded-full" />}
                          </div>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Content Area */}
          <div className="flex-1 p-6">
            <div className="max-w-3xl">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">Welcome to our Knowledge Base</h1>
              <p className="text-gray-600 mb-6">
                Find answers to common questions and learn how to use our platform effectively.
              </p>
              
              <div className="space-y-4">
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">Getting Started</h3>
                  <p className="text-gray-600 text-sm">
                    Learn the basics and set up your account in minutes.
                  </p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">Advanced Features</h3>
                  <p className="text-gray-600 text-sm">
                    Explore powerful features and integrations.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderDeploy = () => (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={() => setActiveView('builder')}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Deploy Knowledge Base</h2>
          <p className="text-gray-600">Publish your knowledge base and make it available to users</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Deployment Status</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-green-800 font-medium">Knowledge Base Ready</span>
              </div>
              <span className="text-green-600 text-sm">23 articles</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-blue-800 font-medium">AI Search Enabled</span>
              </div>
              <span className="text-blue-600 text-sm">Qdrant</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span className="text-yellow-800 font-medium">Custom Domain</span>
              </div>
              <span className="text-yellow-600 text-sm">{customDomain || 'Not configured'}</span>
            </div>
          </div>

          <button className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-medium">
            Deploy to Production
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Deployment Options</h3>
          
          <div className="space-y-4">
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Standalone Mode</h4>
                <input
                  type="radio"
                  name="deployMode"
                  checked={deploymentMode === 'standalone'}
                  onChange={() => setDeploymentMode('standalone')}
                  className="text-blue-600"
                />
              </div>
              <p className="text-gray-600 text-sm">
                Deploy as a dedicated knowledge base with its own domain and branding.
              </p>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Unified Portal</h4>
                <input
                  type="radio"
                  name="deployMode"
                  checked={deploymentMode === 'unified'}
                  onChange={() => setDeploymentMode('unified')}
                  className="text-blue-600"
                />
              </div>
              <p className="text-gray-600 text-sm">
                Include in the unified support portal alongside other modules.
              </p>
            </div>
          </div>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Deployment URL</h4>
            <code className="text-sm text-gray-600 bg-white px-2 py-1 rounded border">
              {customDomain || 'kb.promptsupport.ai/your-org'}
            </code>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Knowledge Base Builder</h1>
            <p className="text-gray-600">
              Create and organize your knowledge base with drag-and-drop TOC builder, theming, and deployment options
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveView('builder')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeView === 'builder'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Builder
            </button>
            <button
              onClick={() => setActiveView('preview')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeView === 'preview'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Preview
            </button>
            <button
              onClick={() => setActiveView('settings')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeView === 'settings'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Theme
            </button>
            <button
              onClick={() => setActiveView('deploy')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeView === 'deploy'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Deploy
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="min-h-[600px]">
        {activeView === 'builder' && renderBuilder()}
        {activeView === 'preview' && renderPreview()}
        {activeView === 'settings' && renderThemeSettings()}
        {activeView === 'deploy' && renderDeploy()}
      </div>

      {/* New Item Modal */}
      <AnimatePresence>
        {showNewItemModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4"
            >
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Add New Item</h3>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                  <select
                    value={newItemType}
                    onChange={(e) => setNewItemType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="category">Category</option>
                    <option value="section">Section</option>
                    <option value="article">Article</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                  <input
                    type="text"
                    value={newItemTitle}
                    onChange={(e) => setNewItemTitle(e.target.value)}
                    placeholder={`Enter ${newItemType} title...`}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
                <button
                  onClick={() => setShowNewItemModal(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddItem}
                  disabled={!newItemTitle.trim()}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-6 py-2 rounded-lg"
                >
                  Add Item
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default KnowledgeBaseBuilder;