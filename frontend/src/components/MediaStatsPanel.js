import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Image, 
  Video, 
  FileText, 
  Eye,
  Brain,
  Target,
  Sparkles
} from 'lucide-react';

const MediaStatsPanel = ({ backendUrl }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMediaStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/media/stats`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setStats(data.statistics);
          setError(null);
        } else {
          setError('Failed to fetch media statistics');
        }
      } else {
        setError(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMediaStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchMediaStats, 30000);
    return () => clearInterval(interval);
  }, [backendUrl]);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Media Intelligence Stats</h3>
        </div>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-500 mt-2">Loading media statistics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <BarChart3 className="h-5 w-5 text-red-600" />
          <h3 className="text-lg font-semibold text-gray-900">Media Intelligence Stats</h3>
        </div>
        <div className="text-center py-8">
          <p className="text-red-600">{error}</p>
          <button 
            onClick={fetchMediaStats}
            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const mediaPercentage = stats.total_articles > 0 
    ? ((stats.articles_with_media / stats.total_articles) * 100).toFixed(1)
    : 0;

  const processedPercentage = stats.articles_with_media > 0
    ? ((stats.processed_articles / stats.articles_with_media) * 100).toFixed(1)
    : 0;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Media Intelligence Stats</h3>
        </div>
        <button 
          onClick={fetchMediaStats}
          className="text-blue-600 hover:text-blue-800 text-sm"
        >
          Refresh
        </button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <FileText className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">Total Articles</span>
          </div>
          <p className="text-2xl font-bold text-blue-900 mt-1">{stats.total_articles}</p>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <Image className="h-4 w-4 text-green-600" />
            <span className="text-sm font-medium text-green-900">With Media</span>
          </div>
          <p className="text-2xl font-bold text-green-900 mt-1">{stats.articles_with_media}</p>
          <p className="text-xs text-green-700">{mediaPercentage}% of total</p>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <Brain className="h-4 w-4 text-purple-600" />
            <span className="text-sm font-medium text-purple-900">AI Processed</span>
          </div>
          <p className="text-2xl font-bold text-purple-900 mt-1">{stats.processed_articles}</p>
          <p className="text-xs text-purple-700">{processedPercentage}% of media articles</p>
        </div>

        <div className="bg-orange-50 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="h-4 w-4 text-orange-600" />
            <span className="text-sm font-medium text-orange-900">Media Items</span>
          </div>
          <p className="text-2xl font-bold text-orange-900 mt-1">{stats.total_media_items}</p>
        </div>
      </div>

      {/* Media Format Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
            <Image className="h-4 w-4 mr-2" />
            Media Formats
          </h4>
          <div className="space-y-2">
            {Object.entries(stats.media_by_format).map(([format, count]) => {
              const percentage = stats.total_media_items > 0 
                ? ((count / stats.total_media_items) * 100).toFixed(1)
                : 0;
              
              return (
                <div key={format} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${
                      format === 'PNG' ? 'bg-blue-500' :
                      format === 'JPEG' ? 'bg-green-500' :
                      format === 'SVG' ? 'bg-purple-500' :
                      format === 'GIF' ? 'bg-yellow-500' :
                      format === 'MP4' ? 'bg-red-500' : 'bg-gray-500'
                    }`}></div>
                    <span className="text-sm text-gray-700">{format}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                    <span className="text-xs text-gray-500 ml-1">({percentage}%)</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div>
          <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
            <Target className="h-4 w-4 mr-2" />
            AI Intelligence Features
          </h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Eye className="h-4 w-4 text-blue-600" />
                <span className="text-sm text-gray-700">Vision Analyzed</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {stats.intelligence_analysis.vision_analyzed}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4 text-green-600" />
                <span className="text-sm text-gray-700">Auto Captioned</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {stats.intelligence_analysis.auto_captioned}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Target className="h-4 w-4 text-purple-600" />
                <span className="text-sm text-gray-700">Contextually Placed</span>
              </div>
              <span className="text-sm font-medium text-gray-900">
                {stats.intelligence_analysis.contextually_placed}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Media Types */}
      {Object.keys(stats.media_by_type).length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
            <Video className="h-4 w-4 mr-2" />
            Media Types
          </h4>
          <div className="flex space-x-4">
            {Object.entries(stats.media_by_type).map(([type, count]) => (
              <div key={type} className="text-center">
                <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-2">
                  {type === 'Image' ? <Image className="h-6 w-6 text-gray-600" /> : 
                   type === 'Video' ? <Video className="h-6 w-6 text-gray-600" /> :
                   <FileText className="h-6 w-6 text-gray-600" />}
                </div>
                <p className="text-sm font-medium text-gray-900">{count}</p>
                <p className="text-xs text-gray-500">{type}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaStatsPanel;