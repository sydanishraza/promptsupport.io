import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import TiptapEditor from './AdvancedEditor';
import SnipAndRecord from './SnipAndRecord';
import { marked } from 'marked';
import { 
  Search, 
  Filter, 
  Plus, 
  Edit, 
  Eye, 
  Tag, 
  FileText, 
  Image,
  Video,
  Mic,
  Bot,
  User,
  Calendar,
  MoreHorizontal,
  X,
  Save,
  ArrowLeft,
  Settings,
  Trash2,
  Copy,
  ExternalLink,
  Camera,
  Monitor,
  Download,
  Upload2,
  Grid,
  List,
  Star,
  Clock,
  CheckCircle,
  AlertCircle,
  History,
  Database,
  Hash,
  FileEdit,
  Globe,
  Users
} from 'lucide-react';

const ContentLibraryEnhanced = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [viewMode, setViewMode] = useState('grid');
  const [selectedContent, setSelectedContent] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showNewArticleModal, setShowNewArticleModal] = useState(false);
  const [showSnipAndRecord, setShowSnipAndRecord] = useState(false);
  const [showVersionHistory, setShowVersionHistory] = useState(false);
  const [versionHistory, setVersionHistory] = useState([]);
  const [showMetadataEditor, setShowMetadataEditor] = useState(false);
  const [newArticle, setNewArticle] = useState({
    title: '',
    content: '',
    status: 'draft',
    tags: [],
    metadata: {}
  });
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState([
    { id: 'all', label: 'All Content', count: 0 },
    { id: 'articles', label: 'Articles', count: 0 },
    { id: 'assets', label: 'Assets', count: 0 },
    { id: 'recordings', label: 'Recordings', count: 0 }
  ]);

  // Configure marked for better rendering
  marked.setOptions({
    gfm: true,
    breaks: false,
    sanitize: false, // Important: Don't sanitize to preserve base64 images
    smartLists: true,
    smartypants: true,
  });

  // Override the image renderer to ensure base64 images are preserved
  const renderer = new marked.Renderer();
  renderer.image = function(href, title, text) {
    let out = '<img src="' + href + '" alt="' + text + '"';
    if (title) {
      out += ' title="' + title + '"';
    }
    out += ' class="rounded-lg max-w-full h-auto">';
    return out;
  };

  // Convert markdown to HTML with better parsing for all image formats
  const markdownToHtml = (markdown) => {
    try {
      // First, let's preserve base64 images by replacing them temporarily
      let processedMarkdown = markdown;
      const imageReplacements = new Map();
      let replacementCounter = 0;
      
      // Find all markdown images with base64 data - support all formats
      const imagePattern = /!\[(.*?)\]\((data:image\/(?:png|jpeg|jpg|gif|svg\+xml|webp);base64,[^)]+)\)/g;
      let match;
      
      while ((match = imagePattern.exec(markdown)) !== null) {
        const [fullMatch, altText, dataUrl] = match;
        const placeholder = `__IMAGE_PLACEHOLDER_${replacementCounter}__`;
        imageReplacements.set(placeholder, { altText, dataUrl });
        processedMarkdown = processedMarkdown.replace(fullMatch, placeholder);
        replacementCounter++;
      }
      
      console.log(`🔍 Found ${imageReplacements.size} base64 images to preserve (PNG, JPEG, SVG, GIF, etc.)`);
      
      // Convert markdown to HTML with marked
      let html = marked(processedMarkdown, { renderer });
      
      // Restore the base64 images as proper HTML img tags
      imageReplacements.forEach(({ altText, dataUrl }, placeholder) => {
        const imgTag = `<img src="${dataUrl}" alt="${altText}" class="rounded-lg max-w-full h-auto" style="display: block; margin: 1rem 0;" />`;
        html = html.replace(placeholder, imgTag);
        
        // Extract image format for logging
        const formatMatch = dataUrl.match(/data:image\/([^;]+);base64/);
        const format = formatMatch ? formatMatch[1].toUpperCase() : 'UNKNOWN';
        console.log(`✅ Restored ${format} image: ${altText} (${dataUrl.substring(0, 50)}...)`);
      });
      
      return html;
    } catch (error) {
      console.error('Error converting markdown to HTML:', error);
      return `<p>${markdown}</p>`;
    }
  };

  // Check if content contains markdown syntax
  const isMarkdownContent = (content) => {
    if (!content) return false;
    
    // Check for markdown image syntax specifically
    const hasMarkdownImages = content.includes('![') && content.includes('data:image');
    
    const hasMarkdownSyntax = content.includes('#') || 
                              content.includes('**') || 
                              content.includes('- ') || 
                              content.includes('1. ') ||
                              content.includes('```') ||
                              content.includes('> ') ||
                              hasMarkdownImages;
    
    // For markdown images, always convert even if HTML tags are present
    if (hasMarkdownImages) {
      return true;
    }
    
    const hasHtmlTags = content.includes('<') && content.includes('>');
    
    return hasMarkdownSyntax && !hasHtmlTags;
  };

  // Get backend URL from environment
  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Fetch real articles from Content Library
  const fetchContentLibrary = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`${backendUrl}/api/content-library`);
      if (response.ok) {
        const data = await response.json();
        const realArticles = data.articles || [];
        setArticles(realArticles);
        
        // Update filters with real counts
        const totalCount = realArticles.length;
        const articlesCount = realArticles.filter(a => a.source_type === 'text_processing' || a.source_type === 'file_upload').length;
        const assetsCount = realArticles.filter(a => a.source_type === 'recording_processing').length;
        const recordingsCount = realArticles.filter(a => a.metadata?.recording_type).length;
        
        setFilters([
          { id: 'all', label: 'All Content', count: totalCount },
          { id: 'articles', label: 'Articles', count: articlesCount },
          { id: 'assets', label: 'Assets', count: assetsCount },
          { id: 'recordings', label: 'Recordings', count: recordingsCount }
        ]);
        
        return realArticles; // Return articles for use in other functions
      } else {
        console.error('Failed to fetch Content Library:', response.status);
        return [];
      }
    } catch (error) {
      console.error('Error fetching Content Library:', error);
      return [];
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContentLibrary();
    
    // Refresh every 10 seconds to catch new articles from Knowledge Engine
    const interval = setInterval(fetchContentLibrary, 10000);
    return () => clearInterval(interval);
  }, [backendUrl]);

  const statusFilters = [
    { id: 'all', label: 'All Status' },
    { id: 'draft', label: 'Draft' },
    { id: 'published', label: 'Published' },
    { id: 'review', label: 'Under Review' }
  ];

  // Transform real articles into display format
  const contentItems = articles.map((article, index) => ({
    id: article.id || index,
    title: article.title || 'Untitled',
    type: article.metadata?.recording_type ? 'video' : 'article',
    status: article.status || 'draft',
    source: article.source_type === 'file_upload' ? 'File Upload' : 
            article.source_type === 'text_processing' ? 'Text Processing' :
            article.source_type === 'url_processing' ? 'URL Processing' :
            article.source_type === 'recording_processing' ? 'Recording' : 'AI Generated',
    tags: Array.isArray(article.tags) ? article.tags : [],
    wordCount: article.content ? article.content.length / 5 : 0, // Rough estimate
    lastModified: article.updated_at || article.created_at,
    author: 'Knowledge Engine',
    views: Math.floor(Math.random() * 100), // Placeholder for now
    preview: article.summary || (article.content ? article.content.substring(0, 100) + '...' : 'No preview available'),
    content: article.content || '<p>Content not available</p>',
    metadata: article.metadata
  }));

  // Add some default articles if no real articles exist (for demo purposes)
  const defaultArticles = contentItems.length === 0 ? [
    {
      id: 'default-1',
      title: 'Welcome to PromptSupport',
      type: 'article',
      status: 'published',
      source: 'System',
      tags: ['welcome', 'getting-started'],
      wordCount: 250,
      lastModified: new Date().toISOString(),
      author: 'System',
      views: 0,
      preview: 'Welcome to PromptSupport! Start by uploading content to the Knowledge Engine.',
      content: '<h1>Welcome to PromptSupport</h1><p>Upload content to the Knowledge Engine to create your first articles!</p>'
    }
  ] : [];

  const displayItems = contentItems.length > 0 ? contentItems : defaultArticles;

  const getTypeIcon = (type) => {
    switch (type) {
      case 'article': return FileText;
      case 'video': return Video;
      case 'audio': return Mic;
      case 'image': return Image;
      default: return FileText;
    }
  };

  const getSourceColor = (source) => {
    switch (source) {
      case 'AI Generated': return 'bg-blue-100 text-blue-700';
      case 'User Edited': case 'User Created': return 'bg-green-100 text-green-700';
      case 'File Upload': return 'bg-purple-100 text-purple-700';
      case 'Text Processing': return 'bg-indigo-100 text-indigo-700';
      case 'URL Processing': return 'bg-cyan-100 text-cyan-700';
      case 'Recording': return 'bg-orange-100 text-orange-700';
      case 'System': return 'bg-gray-100 text-gray-700';
      case 'Uploaded': return 'bg-purple-100 text-purple-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'published': return 'bg-green-100 text-green-700';
      case 'draft': return 'bg-yellow-100 text-yellow-700';
      case 'review': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const filteredContent = displayItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesFilter = selectedFilter === 'all' || 
                         (selectedFilter === 'articles' && item.type === 'article') ||
                         (selectedFilter === 'assets' && ['image', 'video'].includes(item.type)) ||
                         (selectedFilter === 'recordings' && item.type === 'audio');
    const matchesStatus = selectedStatus === 'all' || item.status === selectedStatus;
    
    return matchesSearch && matchesFilter && matchesStatus;
  });

  const handleEditContent = (content) => {
    // Convert markdown content to HTML if needed
    let processedContent = content.content;
    
    if (processedContent && isMarkdownContent(processedContent)) {
      processedContent = markdownToHtml(processedContent);
      console.log('Converted markdown to HTML for editing:', { 
        original: content.content.substring(0, 200) + '...',
        converted: processedContent.substring(0, 200) + '...'
      });
    }
    
    setSelectedContent({
      ...content,
      content: processedContent,
      // Initialize metadata if not present
      metadata: content.metadata || {},
      // Initialize version info
      version: content.version || 1,
      version_history: content.version_history || []
    });
    setIsEditing(true);
  };

  const handleViewContent = (content) => {
    console.log('🔍 handleViewContent called with:', {
      title: content.title,
      contentLength: content.content?.length,
      contentPreview: content.content?.substring(0, 200),
      hasMarkdownImages: content.content?.includes('![') && content.content?.includes('data:image')
    });
    
    // Convert markdown content to HTML if needed
    let processedContent = content.content;
    
    if (processedContent && isMarkdownContent(processedContent)) {
      console.log('✅ Converting markdown to HTML for:', content.title);
      processedContent = markdownToHtml(processedContent);
      console.log('✅ Markdown converted. New length:', processedContent.length);
      console.log('✅ Converted content preview:', processedContent.substring(0, 300));
      console.log('✅ Contains HTML images:', processedContent.includes('<img'));
    } else {
      console.log('❌ No markdown conversion needed for:', content.title);
      console.log('❌ isMarkdownContent result:', isMarkdownContent(processedContent));
    }
    
    setSelectedContent({
      ...content,
      content: processedContent
    });
    setIsEditing(false);
  };

  const handleSaveArticle = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Prepare form data
      const formData = new FormData();
      formData.append('title', selectedContent.title);
      formData.append('content', selectedContent.content);
      formData.append('status', selectedContent.status || 'draft');
      formData.append('tags', JSON.stringify(selectedContent.tags || []));
      formData.append('metadata', JSON.stringify(selectedContent.metadata || {}));

      let response;
      if (selectedContent.id && selectedContent.id !== 'default-1') {
        // Update existing article
        response = await fetch(`${backendUrl}/api/content-library/${selectedContent.id}`, {
          method: 'PUT',
          body: formData
        });
      } else {
        // Create new article
        response = await fetch(`${backendUrl}/api/content-library`, {
          method: 'POST',
          body: formData
        });
      }

      if (response.ok) {
        const result = await response.json();
        console.log('Article saved:', result);
        
        // Refresh content library
        fetchContentLibrary();
        
        // Show success message
        alert(`Article ${selectedContent.id ? 'updated' : 'created'} successfully!`);
        
        // Exit editing mode
        setIsEditing(false);
        
        // Update local state with new version info
        if (result.version) {
          setSelectedContent(prev => ({
            ...prev,
            version: result.version
          }));
        }
      } else {
        throw new Error('Failed to save article');
      }
    } catch (error) {
      console.error('Error saving article:', error);
      alert('Failed to save article. Please try again.');
    }
  };

  const handleCreateArticle = () => {
    setNewArticle({ 
      title: '', 
      content: '<p>Start writing your article...</p>', 
      tags: [], 
      status: 'draft',
      metadata: {}
    });
    setShowNewArticleModal(true);
  };

  const handleCaptureMedia = async (formData) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Upload captured media to Knowledge Engine for processing
      const response = await fetch(`${backendUrl}/api/content/upload`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Media capture processed:', result);
        
        // Refresh content library to show new articles
        fetchContentLibrary();
        
        // Show success message
        alert(`Media captured and processed! Created ${result.chunks_created} content chunks.`);
      } else {
        throw new Error('Failed to process captured media');
      }
    } catch (error) {
      console.error('Error processing captured media:', error);
      alert('Failed to process captured media. Please try again.');
    }
  };

  // Fetch version history for an article
  const fetchVersionHistory = async (articleId) => {
    try {
      const response = await fetch(`${backendUrl}/api/content-library/${articleId}/versions`);
      if (response.ok) {
        const data = await response.json();
        setVersionHistory([data.current_version, ...data.version_history]);
        setShowVersionHistory(true);
      } else {
        console.error('Failed to fetch version history:', response.status);
      }
    } catch (error) {
      console.error('Error fetching version history:', error);
    }
  };

  // Restore article to specific version
  const restoreVersion = async (articleId, version) => {
    try {
      const response = await fetch(`${backendUrl}/api/content-library/${articleId}/restore/${version}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Article restored to version ${version}`);
        
        // Refresh content and close version history
        fetchContentLibrary();
        setShowVersionHistory(false);
        
        // Refresh the selected content if it's the same article
        if (selectedContent && selectedContent.id === articleId) {
          const updatedArticles = await fetchContentLibrary();
          const updatedArticle = updatedArticles.find(a => a.id === articleId);
          if (updatedArticle) {
            setSelectedContent(updatedArticle);
          }
        }
      } else {
        throw new Error('Failed to restore version');
      }
    } catch (error) {
      console.error('Error restoring version:', error);
      alert('Failed to restore version. Please try again.');
    }
  };

  const handleSaveNewArticle = async () => {
    try {
      const formData = new FormData();
      formData.append('title', newArticle.title);
      formData.append('content', newArticle.content);
      formData.append('status', newArticle.status);
      formData.append('tags', JSON.stringify(newArticle.tags));
      formData.append('metadata', JSON.stringify(newArticle.metadata || {}));

      const response = await fetch(`${backendUrl}/api/content-library`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        console.log('New article created:', result);
        
        // Refresh content library
        fetchContentLibrary();
        
        // Close modal and reset form
        setShowNewArticleModal(false);
        setNewArticle({ 
          title: '', 
          content: '<p>Start writing...</p>', 
          tags: [], 
          status: 'draft',
          metadata: {}
        });
        
        alert('Article created successfully!');
      } else {
        throw new Error('Failed to create article');
      }
    } catch (error) {
      console.error('Error creating article:', error);
      alert('Failed to create article. Please try again.');
    }
  };

  const renderContentEditor = () => (
    <div className="fixed inset-0 bg-white z-50 overflow-y-auto">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => {setSelectedContent(null); setIsEditing(false);}}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {isEditing ? 'Edit Article' : 'View Article'}
              </h1>
              <p className="text-gray-600">{selectedContent.title}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
              >
                <Edit size={16} />
                <span>Edit</span>
              </button>
            )}
            {isEditing && (
              <>
                <button
                  onClick={handleSaveArticle}
                  className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg"
                >
                  <Save size={16} />
                  <span>Save</span>
                </button>
                <button
                  onClick={() => setIsEditing(false)}
                  className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded-lg"
                >
                  <X size={16} />
                  <span>Cancel</span>
                </button>
              </>
            )}
            <button 
              onClick={() => fetchVersionHistory(selectedContent.id)}
              className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-lg"
            >
              <History size={16} />
              <span>History</span>
            </button>
            <button 
              onClick={() => setShowMetadataEditor(true)}
              className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-lg"
            >
              <Database size={16} />
              <span>Metadata</span>
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg">
              <MoreHorizontal size={20} />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="mb-6">
              <input
                type="text"
                value={selectedContent.title}
                onChange={(e) => setSelectedContent(prev => ({...prev, title: e.target.value}))}
                className="w-full text-3xl font-bold border-none focus:outline-none bg-transparent"
                placeholder="Article title..."
                readOnly={!isEditing}
              />
            </div>
            
            <TiptapEditor
              content={selectedContent.content}
              onChange={(content) => {
                setSelectedContent(prev => ({...prev, content}));
              }}
              onSave={handleSaveArticle}
              isReadOnly={!isEditing}
              height="600px"
            />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3">Article Info</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Status:</span>
                  {isEditing ? (
                    <select
                      value={selectedContent.status}
                      onChange={(e) => setSelectedContent(prev => ({...prev, status: e.target.value}))}
                      className="px-2 py-1 text-xs rounded border"
                    >
                      <option value="draft">Draft</option>
                      <option value="review">Under Review</option>
                      <option value="published">Published</option>
                    </select>
                  ) : (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedContent.status)}`}>
                      {selectedContent.status}
                    </span>
                  )}
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Source:</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSourceColor(selectedContent.source)}`}>
                    {selectedContent.source}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Version:</span>
                  <span className="text-gray-900">v{selectedContent.version || 1}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Words:</span>
                  <span className="text-gray-900">{selectedContent.wordCount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Views:</span>
                  <span className="text-gray-900">{selectedContent.views}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Author:</span>
                  <span className="text-gray-900">{selectedContent.author}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Modified:</span>
                  <span className="text-gray-900">{new Date(selectedContent.lastModified).toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3">Tags</h3>
              <div className="flex flex-wrap gap-1">
                {selectedContent.tags.map((tag, index) => (
                  <span key={tag} className="px-2 py-1 bg-white text-gray-700 text-xs rounded-full border flex items-center">
                    {tag}
                    {isEditing && (
                      <button
                        onClick={() => {
                          const newTags = selectedContent.tags.filter((_, i) => i !== index);
                          setSelectedContent(prev => ({...prev, tags: newTags}));
                        }}
                        className="ml-1 text-red-500 hover:text-red-700"
                      >
                        <X size={10} />
                      </button>
                    )}
                  </span>
                ))}
                {isEditing && (
                  <input
                    type="text"
                    placeholder="Add tag..."
                    className="px-2 py-1 bg-white text-gray-700 text-xs rounded-full border"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && e.target.value.trim()) {
                        const newTag = e.target.value.trim();
                        if (!selectedContent.tags.includes(newTag)) {
                          setSelectedContent(prev => ({
                            ...prev, 
                            tags: [...prev.tags, newTag]
                          }));
                        }
                        e.target.value = '';
                      }
                    }}
                  />
                )}
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-3">Actions</h3>
              <div className="space-y-2">
                <button className="w-full flex items-center space-x-2 p-2 text-left hover:bg-white rounded-lg text-sm">
                  <Copy size={16} />
                  <span>Duplicate</span>
                </button>
                <button className="w-full flex items-center space-x-2 p-2 text-left hover:bg-white rounded-lg text-sm">
                  <ExternalLink size={16} />
                  <span>Preview</span>
                </button>
                <button className="w-full flex items-center space-x-2 p-2 text-left hover:bg-white rounded-lg text-sm text-red-600">
                  <Trash2 size={16} />
                  <span>Delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNewArticleModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden"
      >
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Create New Article</h2>
          <button
            onClick={() => setShowNewArticleModal(false)}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 max-h-96 overflow-y-auto">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
              <input
                type="text"
                value={newArticle.title}
                onChange={(e) => setNewArticle(prev => ({...prev, title: e.target.value}))}
                placeholder="Enter article title..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Content</label>
              <TiptapEditor
                content={newArticle.content}
                onChange={(content) => setNewArticle(prev => ({...prev, content}))}
                height="300px"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  value={newArticle.status}
                  onChange={(e) => setNewArticle(prev => ({...prev, status: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="draft">Draft</option>
                  <option value="review">Under Review</option>
                  <option value="published">Published</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
                <input
                  type="text"
                  placeholder="Add tags (comma separated)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
          <button
            onClick={() => setShowNewArticleModal(false)}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={handleSaveNewArticle}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
          >
            <Save size={16} />
            <span>Create Article</span>
          </button>
        </div>
      </motion.div>
    </div>
  );

  // Version History Modal
  const renderVersionHistoryModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden"
      >
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Version History</h2>
          <button
            onClick={() => setShowVersionHistory(false)}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 max-h-96 overflow-y-auto">
          <div className="space-y-4">
            {versionHistory.map((version, index) => (
              <div key={version.version} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-gray-900">
                      Version {version.version}
                      {version.is_current && (
                        <span className="ml-2 px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                          Current
                        </span>
                      )}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(version.updated_at).toLocaleString()}
                    </span>
                    <span className="text-sm text-gray-500">
                      by {version.updated_by}
                    </span>
                  </div>
                  {!version.is_current && (
                    <button
                      onClick={() => restoreVersion(selectedContent.id, version.version)}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded"
                    >
                      Restore
                    </button>
                  )}
                </div>
                <h4 className="font-medium text-gray-800 mb-1">{version.title}</h4>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {version.content.replace(/<[^>]*>/g, '').substring(0, 150)}...
                </p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {version.tags.map(tag => (
                    <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );

  // Metadata Editor Modal
  const renderMetadataEditor = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden"
      >
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Edit Metadata</h2>
          <button
            onClick={() => setShowMetadataEditor(false)}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 max-h-96 overflow-y-auto">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                SEO Description
              </label>
              <textarea
                value={selectedContent.metadata?.seo_description || ''}
                onChange={(e) => setSelectedContent(prev => ({
                  ...prev,
                  metadata: { ...prev.metadata, seo_description: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
                placeholder="SEO description for this article..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Keywords
              </label>
              <input
                type="text"
                value={selectedContent.metadata?.keywords || ''}
                onChange={(e) => setSelectedContent(prev => ({
                  ...prev,
                  metadata: { ...prev.metadata, keywords: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="keyword1, keyword2, keyword3"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                value={selectedContent.metadata?.category || ''}
                onChange={(e) => setSelectedContent(prev => ({
                  ...prev,
                  metadata: { ...prev.metadata, category: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select category...</option>
                <option value="getting-started">Getting Started</option>
                <option value="tutorials">Tutorials</option>
                <option value="troubleshooting">Troubleshooting</option>
                <option value="advanced">Advanced</option>
                <option value="api-docs">API Documentation</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority
              </label>
              <select
                value={selectedContent.metadata?.priority || 'normal'}
                onChange={(e) => setSelectedContent(prev => ({
                  ...prev,
                  metadata: { ...prev.metadata, priority: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="featured"
                checked={selectedContent.metadata?.featured || false}
                onChange={(e) => setSelectedContent(prev => ({
                  ...prev,
                  metadata: { ...prev.metadata, featured: e.target.checked }
                }))}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="featured" className="ml-2 block text-sm text-gray-900">
                Featured Article
              </label>
            </div>
          </div>
        </div>

        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
          <button
            onClick={() => setShowMetadataEditor(false)}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              setShowMetadataEditor(false);
              handleSaveArticle();
            }}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
          >
            <Save size={16} />
            <span>Save Metadata</span>
          </button>
        </div>
      </motion.div>
    </div>
  );

  if (selectedContent) {
    return renderContentEditor();
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Content Library</h1>
            <p className="text-gray-600">
              Manage AI-generated and user-edited articles, assets, and recordings with Tiptap editor
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button 
              onClick={() => setShowSnipAndRecord(true)}
              className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
            >
              <Camera size={16} />
              <span>Snip & Record</span>
            </button>
            <button 
              onClick={handleCreateArticle}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
            >
              <Plus size={16} />
              <span>Create Article</span>
            </button>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="relative flex-1 lg:max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="Search articles, tags, or content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center space-x-4">
            <select
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {filters.map(filter => (
                <option key={filter.id} value={filter.id}>
                  {filter.label} ({filter.count})
                </option>
              ))}
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {statusFilters.map(filter => (
                <option key={filter.id} value={filter.id}>
                  {filter.label}
                </option>
              ))}
            </select>

            <div className="flex border border-gray-300 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-gray-100' : ''}`}
              >
                📊
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 ${viewMode === 'list' ? 'bg-gray-100' : ''}`}
              >
                📋
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content Grid/List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">
            Content ({filteredContent.length})
          </h2>
        </div>

        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContent.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors cursor-pointer"
                onClick={() => item.type === 'article' ? handleViewContent(item) : null}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                      {React.createElement(getTypeIcon(item.type), { size: 16, className: 'text-gray-600' })}
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSourceColor(item.source)}`}>
                      {item.source}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewContent(item);
                      }}
                      className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                    >
                      <Eye size={14} />
                    </button>
                    {item.type === 'article' && (
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditContent(item);
                        }}
                        className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                      >
                        <Edit size={14} />
                      </button>
                    )}
                  </div>
                </div>

                <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">
                  {item.title}
                </h3>
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {item.preview}
                </p>

                <div className="flex flex-wrap gap-1 mb-3">
                  {item.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                    {item.status}
                  </span>
                  <div className="text-xs text-gray-500">
                    {item.wordCount ? `${item.wordCount} words` : item.duration || item.dimensions}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredContent.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors cursor-pointer"
                onClick={() => item.type === 'article' ? handleViewContent(item) : null}
              >
                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                  {React.createElement(getTypeIcon(item.type), { size: 18, className: 'text-gray-600' })}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3 mb-1">
                    <h3 className="font-medium text-gray-900 truncate">{item.title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                      {item.status}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>{item.author}</span>
                    <span>{new Date(item.lastModified).toLocaleDateString()}</span>
                    <span>{item.wordCount ? `${item.wordCount} words` : item.duration || item.dimensions}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-1">
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewContent(item);
                    }}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                  >
                    <Eye size={16} />
                  </button>
                  {item.type === 'article' && (
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditContent(item);
                      }}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                    >
                      <Edit size={16} />
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      <AnimatePresence>
        {showNewArticleModal && renderNewArticleModal()}
        {showVersionHistory && renderVersionHistoryModal()}
        {showMetadataEditor && renderMetadataEditor()}
      </AnimatePresence>

      {/* Snip and Record Modal */}
      <SnipAndRecord
        isOpen={showSnipAndRecord}
        onClose={() => setShowSnipAndRecord(false)}
        onCapture={handleCaptureMedia}
      />
    </div>
  );
};

export default ContentLibraryEnhanced;