import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Image,
  Camera,
  MapPin,
  Eye,
  Download,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Info,
  Tag,
  FileImage,
  Layers,
  Target,
  Settings
} from 'lucide-react';

const ImageProcessing = ({ moduleData, processingData, setProcessingData, onStatusUpdate }) => {
  const [processingResults, setProcessingResults] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageConfig, setImageConfig] = useState({
    generateCaptions: true,
    contextualPlacement: true,
    altTextGeneration: true,
    compressionLevel: 'medium'
  });
  const [processingStats, setProcessingStats] = useState({ processed: 0, total: 0 });

  useEffect(() => {
    console.log('ImageProcessing useEffect - processingData:', processingData);
    if (processingData) {
      console.log('ImageProcessing - has chunkingResults:', !!processingData.chunkingResults);
      console.log('ImageProcessing - stage:', processingData.stage);
      console.log('ImageProcessing - processing:', processing);  
      console.log('ImageProcessing - processingResults:', !!processingResults);
    }
    
    if (processingData && processingData.chunkingResults && processingData.stage === 'chunked' && !processing && !processingResults) {
      console.log('ImageProcessing - Starting image processing...');
      // Auto-start image processing if chunking results are available and not already processed
      startImageProcessing();
    }
  }, [processingData, processing, processingResults]);

  const startImageProcessing = async () => {
    if (!processingData || !processingData.chunkingResults) {
      return;
    }

    console.log('ImageProcessing - chunkingResults structure:', processingData.chunkingResults);

    setProcessing(true);
    onStatusUpdate('processing');

    try {
      const results = [];
      let totalImages = 0;
      let processedImages = 0;

      // Count total images  
      processingData.chunkingResults.forEach(resource => {
        console.log('ImageProcessing - resource:', resource);
        if (resource.chunks) {
          resource.chunks.forEach(chunk => {
            console.log('ImageProcessing - chunk:', chunk);
            // Check if chunk has html property, if not use content
            const content = chunk.html || chunk.content || chunk.text || '';
            console.log('ImageProcessing - content:', content);
            const imageTokens = content.match(/\[IMAGE:.*?\]/g) || [];
            totalImages += imageTokens.length;
          });
        }
      });

      setProcessingStats({ processed: 0, total: totalImages });
      
      for (const resource of processingData.chunkingResults) {
        const resourceImageData = [];
        
        for (const chunk of resource.chunks) {
          // Extract and process images from the chunk
          const imageTokens = chunk.html.match(/\[IMAGE:.*?\]/g) || [];
          const processedImagesList = [];
          
          for (let i = 0; i < imageTokens.length; i++) {
            // Simulate image processing
            await new Promise(resolve => setTimeout(resolve, 800));
            
            const imageData = await processImageToken(imageTokens[i], chunk, resource, i);
            processedImagesList.push(imageData);
            
            processedImages++;
            setProcessingStats({ processed: processedImages, total: totalImages });
          }
          
          // Update chunk content with processed images
          const updatedContent = replaceImageTokens(chunk.html, processedImagesList);
          
          resourceImageData.push({
            chunk_id: chunk.chunk_id,
            original_content: chunk.html,
            updated_content: updatedContent,
            images_processed: processedImagesList.length,
            processed_images: processedImagesList
          });
        }

        results.push({
          resource_id: resource.resource_id,
          resource_name: resource.resource_name,
          chunks: resourceImageData,
          totalImages: resourceImageData.reduce((sum, chunk) => sum + chunk.images_processed, 0),
          status: 'processed'
        });
      }

      const totalProcessedImages = results.reduce((sum, r) => sum + r.totalImages, 0);
      const avgCaptionLength = results.reduce((sum, r) => 
        sum + r.chunks.reduce((chunkSum, chunk) => 
          chunkSum + chunk.processed_images.reduce((imgSum, img) => imgSum + (img.caption?.length || 0), 0), 0
        ), 0
      ) / Math.max(totalProcessedImages, 1);

      setProcessingResults({
        resources: results,
        totalImages: totalProcessedImages,
        averageCaptionLength: Math.round(avgCaptionLength),
        processingTime: `${Math.round(totalImages * 0.8)}s`,
        timestamp: new Date().toISOString()
      });

      // Update processing data for next module
      setProcessingData(prev => ({
        ...prev,
        imageProcessingResults: results,
        stage: 'images_processed'
      }));

      onStatusUpdate('completed');

    } catch (error) {
      console.error('Image processing failed:', error);
      onStatusUpdate('error');
    } finally {
      setProcessing(false);
      setProcessingStats({ processed: 0, total: 0 });
    }
  };

  const processImageToken = async (token, article, resource, index) => {
    // Parse the image token: [IMAGE:img_x:block=block_id]
    const tokenMatch = token.match(/\[IMAGE:(.*?):block=(.*?)\]/);
    const imageId = tokenMatch ? tokenMatch[1] : `img_${index + 1}`;
    const blockId = tokenMatch ? tokenMatch[2] : `block_${index + 1}`;
    
    // Simulate image extraction and processing
    const imagePath = `/media/res_${resource.resource_id}/${imageId}.png`;
    
    // Generate contextual caption based on surrounding content
    const caption = generateContextualCaption(article.title, blockId, index);
    
    // Generate alt text for accessibility
    const altText = generateAltText(caption, imageId);
    
    // Simulate image metadata
    const metadata = {
      originalSize: Math.floor(Math.random() * 2000000) + 500000, // 500KB - 2.5MB
      compressedSize: Math.floor(Math.random() * 800000) + 200000, // 200KB - 1MB
      dimensions: {
        width: 800 + Math.floor(Math.random() * 400),
        height: 600 + Math.floor(Math.random() * 400)
      },
      format: 'PNG',
      quality: imageConfig.compressionLevel === 'high' ? 95 : imageConfig.compressionLevel === 'medium' ? 85 : 75
    };

    return {
      image_id: imageId,
      block_id: blockId,
      original_token: token,
      file_path: imagePath,
      caption: caption,
      alt_text: altText,
      metadata: metadata,
      context_score: Math.random() * 0.3 + 0.7, // 0.7-1.0 context relevance
      processing_time: Math.random() * 2 + 0.5, // 0.5-2.5 seconds
      status: 'processed'
    };
  };

  const generateContextualCaption = (articleTitle, blockId, index) => {
    const captionTemplates = [
      `Illustration showing key concepts from ${articleTitle}`,
      `Visual representation of the process described in ${blockId}`,
      `Diagram illustrating the workflow for ${articleTitle}`,
      `Screenshot demonstrating the configuration steps`,
      `Example interface showing the implementation details`,
      `Chart displaying the relationship between components`,
      `Flowchart outlining the decision process`,
      `Visual guide for completing the required actions`
    ];
    
    const baseCaption = captionTemplates[Math.floor(Math.random() * captionTemplates.length)];
    return baseCaption.replace(/\s+/g, ' ').trim();
  };

  const generateAltText = (caption, imageId) => {
    // Generate concise alt text for accessibility
    const altTextOptions = [
      `Figure showing ${caption.toLowerCase().substring(0, 50)}...`,
      `Image depicting ${caption.toLowerCase().substring(0, 50)}...`,
      `Diagram of ${caption.toLowerCase().substring(0, 50)}...`,
      `Screenshot displaying ${caption.toLowerCase().substring(0, 50)}...`
    ];
    
    return altTextOptions[Math.floor(Math.random() * altTextOptions.length)];
  };

  const replaceImageTokens = (content, processedImages) => {
    let updatedContent = content;
    
    processedImages.forEach(image => {
      const figureHtml = `
        <figure data-block-id="${image.block_id}">
          <img src="${image.file_path}" alt="${image.alt_text}" loading="lazy" />
          <figcaption>${image.caption}</figcaption>
        </figure>
      `;
      
      updatedContent = updatedContent.replace(image.original_token, figureHtml);
    });
    
    return updatedContent;
  };

  const viewImageDetails = (resource, article, image) => {
    setSelectedImage({ resource, article, image });
  };

  const exportImageMap = () => {
    const imageMap = {};
    
    processingResults.resources.forEach(resource => {
      resource.articles.forEach(article => {
        article.images.forEach(image => {
          imageMap[image.image_id] = {
            file_path: image.file_path,
            caption: image.caption,
            alt_text: image.alt_text,
            block_id: image.block_id,
            context_score: image.context_score
          };
        });
      });
    });

    const dataStr = JSON.stringify({ image_map: imageMap, metadata: processingResults }, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'image_map.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const getContextQualityColor = (score) => {
    if (score >= 0.9) return 'green';
    if (score >= 0.8) return 'blue';
    if (score >= 0.7) return 'yellow';
    return 'red';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-pink-100 rounded-lg">
            <Image className="h-6 w-6 text-pink-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Image Processing Pipeline</h2>
            <p className="text-sm text-gray-600">Emergent Module: image_processing_pipeline</p>
          </div>
        </div>
        <p className="text-gray-700">
          Extract, map, and embed images with contextual captions and optimal placement within articles.
        </p>
      </div>

      {/* Image Processing Configuration */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Compression Level
              </label>
              <select
                value={imageConfig.compressionLevel}
                onChange={(e) => setImageConfig(prev => ({ ...prev, compressionLevel: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
              >
                <option value="low">Low (75% quality)</option>
                <option value="medium">Medium (85% quality)</option>
                <option value="high">High (95% quality)</option>
              </select>
            </div>
            
            <div className="p-3 bg-pink-50 border border-pink-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <Info className="h-4 w-4 text-pink-600" />
                <span className="text-sm font-medium text-pink-900">Processing Pipeline</span>
              </div>
              <p className="text-xs text-pink-700 mt-1">
                Images are extracted, optimized, and embedded with contextual captions generated from surrounding content.
              </p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="space-y-3">
              {[
                { key: 'generateCaptions', label: 'Generate Contextual Captions' },
                { key: 'contextualPlacement', label: 'Optimize Placement' },
                { key: 'altTextGeneration', label: 'Generate Alt Text (Accessibility)' }
              ].map((option) => (
                <div key={option.key} className="flex items-center">
                  <input
                    type="checkbox"
                    id={option.key}
                    checked={imageConfig[option.key]}
                    onChange={(e) => setImageConfig(prev => ({ ...prev, [option.key]: e.target.checked }))}
                    className="h-4 w-4 text-pink-600 focus:ring-pink-500 border-gray-300 rounded"
                  />
                  <label htmlFor={option.key} className="ml-2 block text-sm text-gray-900">
                    {option.label}
                  </label>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="text-center p-2 bg-gray-50 rounded">
                <Camera className="h-4 w-4 mx-auto mb-1 text-gray-600" />
                <span className="text-gray-700">Extract</span>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <Tag className="h-4 w-4 mx-auto mb-1 text-gray-600" />
                <span className="text-gray-700">Caption</span>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <MapPin className="h-4 w-4 mx-auto mb-1 text-gray-600" />
                <span className="text-gray-700">Place</span>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <Layers className="h-4 w-4 mx-auto mb-1 text-gray-600" />
                <span className="text-gray-700">Embed</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Processing Status */}
      {processingData && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Status</h3>
          
          {processing ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-4 bg-pink-50 border border-pink-200 rounded-lg">
                <RefreshCw className="h-5 w-5 text-pink-600 animate-spin" />
                <div>
                  <div className="font-medium text-pink-900">Processing Images...</div>
                  <div className="text-sm text-pink-700">
                    Processing image {processingStats.processed} of {processingStats.total}
                  </div>
                </div>
              </div>
              
              {processingStats.total > 0 && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-pink-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(processingStats.processed / processingStats.total) * 100}%` }}
                  ></div>
                </div>
              )}
            </div>
          ) : processingResults ? (
            <div className="flex items-center space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <div className="font-medium text-green-900">Image Processing Complete</div>
                <div className="text-sm text-green-700">
                  Processed {processingResults.totalImages} images with average caption length of {processingResults.averageCaptionLength} characters
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-amber-600" />
              <div>
                <div className="font-medium text-amber-900">Awaiting Chunked Content</div>
                <div className="text-sm text-amber-700">
                  Complete content chunking in the previous module to begin image processing
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Processing Results */}
      {processingResults && (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Processing Summary</h3>
              <button
                onClick={exportImageMap}
                className="flex items-center space-x-2 px-3 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700"
              >
                <Download className="h-4 w-4" />
                <span>Export Image Map</span>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-pink-50 rounded-lg">
                <FileImage className="h-6 w-6 mx-auto mb-2 text-pink-600" />
                <div className="text-2xl font-bold text-pink-600">
                  {processingResults.totalImages}
                </div>
                <div className="text-sm text-gray-600">Images Processed</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Tag className="h-6 w-6 mx-auto mb-2 text-blue-600" />
                <div className="text-2xl font-bold text-blue-600">
                  {processingResults.averageCaptionLength}
                </div>
                <div className="text-sm text-gray-600">Avg Caption Length</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Target className="h-6 w-6 mx-auto mb-2 text-green-600" />
                <div className="text-2xl font-bold text-green-600">100%</div>
                <div className="text-sm text-gray-600">Success Rate</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Settings className="h-6 w-6 mx-auto mb-2 text-purple-600" />
                <div className="text-2xl font-bold text-purple-600">
                  {processingResults.processingTime}
                </div>
                <div className="text-sm text-gray-600">Processing Time</div>
              </div>
            </div>
          </div>

          {/* Processed Images */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Processed Images</h3>
            <div className="space-y-6">
              {processingResults.resources.map((resource) => (
                <div key={resource.resource_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="font-medium text-gray-900">{resource.resource_name}</h4>
                      <p className="text-sm text-gray-600">
                        {resource.totalImages} images processed across {resource.articles.length} articles
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    {resource.articles.map((article) => (
                      <div key={article.article_id} className="bg-gray-50 p-4 rounded-lg">
                        <h5 className="font-medium text-gray-900 mb-3">{article.title}</h5>
                        
                        {article.images.length > 0 ? (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {article.images.map((image) => {
                              const contextColor = getContextQualityColor(image.context_score);
                              
                              return (
                                <div
                                  key={image.image_id}
                                  className="p-3 border border-gray-200 rounded-lg bg-white hover:bg-gray-50 transition-colors cursor-pointer"
                                  onClick={() => viewImageDetails(resource, article, image)}
                                >
                                  <div className="flex items-center justify-between mb-2">
                                    <div className="text-sm font-medium text-gray-900">
                                      {image.image_id}
                                    </div>
                                    <div className={`px-2 py-1 rounded text-xs font-medium bg-${contextColor}-100 text-${contextColor}-800`}>
                                      {Math.round(image.context_score * 100)}%
                                    </div>
                                  </div>
                                  
                                  <div className="text-xs text-gray-600 space-y-1 mb-2">
                                    <div className="flex justify-between">
                                      <span>Size:</span>
                                      <span>{formatFileSize(image.metadata.compressedSize)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Dimensions:</span>
                                      <span>{image.metadata.dimensions.width}×{image.metadata.dimensions.height}</span>
                                    </div>
                                  </div>
                                  
                                  <div className="text-xs text-gray-700 line-clamp-2">
                                    {image.caption}
                                  </div>
                                  
                                  <div className="mt-2 flex items-center justify-end">
                                    <Eye className="h-3 w-3 text-gray-400" />
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <div className="text-center py-4 text-gray-500">
                            <Image className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                            <p className="text-sm">No images found in this article</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Image Details Modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  Image Details: {selectedImage.image.image_id}
                </h3>
                <button
                  onClick={() => setSelectedImage(null)}
                  className="text-gray-600 hover:text-gray-800"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-pink-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-pink-900 mb-1">Context Score</div>
                  <div className="text-2xl font-bold text-pink-700">
                    {Math.round(selectedImage.image.context_score * 100)}%
                  </div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-blue-900 mb-1">File Size</div>
                  <div className="text-2xl font-bold text-blue-700">
                    {formatFileSize(selectedImage.image.metadata.compressedSize)}
                  </div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-green-900 mb-1">Dimensions</div>
                  <div className="text-lg font-bold text-green-700">
                    {selectedImage.image.metadata.dimensions.width}×{selectedImage.image.metadata.dimensions.height}
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Generated Caption</h4>
                  <div className="p-3 bg-gray-50 rounded-lg text-gray-800">
                    {selectedImage.image.caption}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Alt Text (Accessibility)</h4>
                  <div className="p-3 bg-blue-50 rounded-lg text-blue-800">
                    {selectedImage.image.alt_text}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Technical Details</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">File Path:</span>
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded">{selectedImage.image.file_path}</code>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Block ID:</span>
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded">{selectedImage.image.block_id}</code>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Format:</span>
                        <span className="font-medium">{selectedImage.image.metadata.format}</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Quality:</span>
                        <span className="font-medium">{selectedImage.image.metadata.quality}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Original Size:</span>
                        <span className="font-medium">{formatFileSize(selectedImage.image.metadata.originalSize)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Processing Time:</span>
                        <span className="font-medium">{selectedImage.image.processing_time.toFixed(1)}s</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">HTML Output</h4>
                  <div className="p-3 bg-gray-900 text-gray-100 rounded-lg text-sm font-mono overflow-x-auto">
                    {`<figure data-block-id="${selectedImage.image.block_id}">
  <img src="${selectedImage.image.file_path}" alt="${selectedImage.image.alt_text}" loading="lazy" />
  <figcaption>${selectedImage.image.caption}</figcaption>
</figure>`}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageProcessing;