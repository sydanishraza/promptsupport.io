import React, { useState } from 'react';

const RefinedEngineTest = () => {
    const [file, setFile] = useState(null);
    const [files, setFiles] = useState([]);
    const [textContent, setTextContent] = useState('');
    const [processing, setProcessing] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [engineVersion, setEngineVersion] = useState('refined_2.0');
    const [analytics, setAnalytics] = useState(null);

    const getEndpoints = () => {
        if (engineVersion === 'advanced_2.1') {
            return {
                upload: '/api/content/upload-advanced',
                process: '/api/content/process-advanced',
                batch: '/api/content/upload-batch-advanced',
                analytics: '/api/content/analytics/advanced'
            };
        }
        return {
            upload: '/api/content/upload-refined',
            process: '/api/content/process-refined'
        };
    };

    const handleFileUpload = async () => {
        if (!file) {
            setError('Please select a file');
            return;
        }

        setProcessing(true);
        setError(null);
        setResults(null);

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('metadata', JSON.stringify({
                title: file.name,
                processing_mode: engineVersion
            }));

            const endpoints = getEndpoints();
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}${endpoints.upload}`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                setResults(data);
            } else {
                setError(data.detail || 'Upload failed');
            }
        } catch (err) {
            setError(`Network error: ${err.message}`);
        } finally {
            setProcessing(false);
        }
    };

    const handleBatchUpload = async () => {
        if (!files || files.length === 0) {
            setError('Please select multiple files for batch processing');
            return;
        }

        if (engineVersion !== 'advanced_2.1') {
            setError('Batch processing is only available with Advanced Engine v2.1');
            return;
        }

        setProcessing(true);
        setError(null);
        setResults(null);

        try {
            const formData = new FormData();
            for (let file of files) {
                formData.append('files', file);
            }
            formData.append('metadata', JSON.stringify({
                batch_processing: true,
                processing_mode: engineVersion
            }));

            const endpoints = getEndpoints();
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}${endpoints.batch}`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                setResults(data);
            } else {
                setError(data.detail || 'Batch upload failed');
            }
        } catch (err) {
            setError(`Network error: ${err.message}`);
        } finally {
            setProcessing(false);
        }
    };

    const handleTextProcess = async () => {
        if (!textContent.trim()) {
            setError('Please enter some text content');
            return;
        }

        setProcessing(true);
        setError(null);
        setResults(null);

        try {
            const endpoints = getEndpoints();
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}${endpoints.process}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: textContent,
                    metadata: {
                        title: 'Text Input',
                        processing_mode: engineVersion
                    }
                })
            });

            const data = await response.json();

            if (response.ok) {
                setResults(data);
            } else {
                setError(data.detail || 'Processing failed');
            }
        } catch (err) {
            setError(`Network error: ${err.message}`);
        } finally {
            setProcessing(false);
        }
    };

    const fetchAnalytics = async () => {
        if (engineVersion !== 'advanced_2.1') {
            setError('Analytics are only available with Advanced Engine v2.1');
            return;
        }

        try {
            const endpoints = getEndpoints();
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}${endpoints.analytics}`);
            const data = await response.json();

            if (response.ok) {
                setAnalytics(data);
            } else {
                setError('Failed to fetch analytics');
            }
        } catch (err) {
            setError(`Analytics error: ${err.message}`);
        }
    };

    return (
        <div className="max-w-6xl mx-auto p-6 bg-white rounded-lg shadow-lg">
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">
                    🚀 Refined PromptSupport Engine - Phase 2
                </h2>
                <p className="text-gray-600">
                    Test both Refined Engine v2.0 and Advanced Engine v2.1 with enhanced features
                </p>
            </div>

            {/* Engine Version Selection */}
            <div className="mb-8 p-4 bg-blue-50 rounded-lg">
                <h3 className="text-lg font-semibold mb-4">🔧 Select Engine Version</h3>
                <div className="space-y-3">
                    <label className="flex items-center space-x-3">
                        <input
                            type="radio"
                            value="refined_2.0"
                            checked={engineVersion === 'refined_2.0'}
                            onChange={(e) => setEngineVersion(e.target.value)}
                            className="form-radio"
                        />
                        <div>
                            <span className="font-medium">Refined Engine v2.0</span>
                            <p className="text-sm text-gray-600">Basic refined processing with strict source fidelity</p>
                        </div>
                    </label>
                    <label className="flex items-center space-x-3">
                        <input
                            type="radio"
                            value="advanced_2.1"
                            checked={engineVersion === 'advanced_2.1'}
                            onChange={(e) => setEngineVersion(e.target.value)}
                            className="form-radio"
                        />
                        <div>
                            <span className="font-medium">🚀 Advanced Engine v2.1</span>
                            <span className="ml-2 px-2 py-1 text-xs font-semibold bg-purple-500 text-white rounded-full">NEW</span>
                            <p className="text-sm text-gray-600">Enhanced analysis, parallel processing, batch support, analytics</p>
                        </div>
                    </label>
                </div>
            </div>

            {/* Single File Upload Section */}
            <div className="mb-8">
                <h3 className="text-lg font-semibold mb-4">📄 Single File Upload Test</h3>
                <div className="space-y-4">
                    <div>
                        <input
                            type="file"
                            accept=".docx,.pdf,.txt,.md"
                            onChange={(e) => setFile(e.target.files[0])}
                            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                    </div>
                    <button
                        onClick={handleFileUpload}
                        disabled={processing || !file}
                        className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                        {processing ? 'Processing...' : `Upload & Process with ${engineVersion === 'advanced_2.1' ? 'Advanced Engine v2.1' : 'Refined Engine v2.0'}`}
                    </button>
                </div>
            </div>

            {/* Batch Processing Section - Only for Advanced Engine */}
            {engineVersion === 'advanced_2.1' && (
                <div className="mb-8 p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <h3 className="text-lg font-semibold mb-4">📦 Batch Processing Test (Advanced v2.1 Only)</h3>
                    <div className="space-y-4">
                        <div>
                            <input
                                type="file"
                                multiple
                                accept=".docx,.pdf,.txt,.md"
                                onChange={(e) => setFiles(Array.from(e.target.files))}
                                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                            />
                            {files.length > 0 && (
                                <p className="text-sm text-gray-600 mt-2">
                                    Selected {files.length} files: {files.map(f => f.name).join(', ')}
                                </p>
                            )}
                        </div>
                        <button
                            onClick={handleBatchUpload}
                            disabled={processing || files.length === 0}
                            className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                        >
                            {processing ? 'Processing Batch...' : `Batch Process ${files.length} Files`}
                        </button>
                    </div>
                </div>
            )}

            {/* Text Input Section */}
            <div className="mb-8">
                <h3 className="text-lg font-semibold mb-4">📝 Direct Text Input Test</h3>
                <div className="space-y-4">
                    <div>
                        <textarea
                            value={textContent}
                            onChange={(e) => setTextContent(e.target.value)}
                            placeholder="Enter your content here to test the refined engine..."
                            rows={8}
                            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>
                    <button
                        onClick={handleTextProcess}
                        disabled={processing || !textContent.trim()}
                        className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                        {processing ? 'Processing...' : `Process Text with ${engineVersion === 'advanced_2.1' ? 'Advanced Engine v2.1' : 'Refined Engine v2.0'}`}
                    </button>
                </div>
            </div>

            {/* Analytics Section - Only for Advanced Engine */}
            {engineVersion === 'advanced_2.1' && (
                <div className="mb-8 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <h3 className="text-lg font-semibold mb-4">📊 Processing Analytics (Advanced v2.1 Only)</h3>
                    <button
                        onClick={fetchAnalytics}
                        className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                        Fetch Processing Analytics
                    </button>
                </div>
            )}

            {/* Analytics Results */}
            {analytics && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
                    <h3 className="text-lg font-semibold text-green-800 mb-4">📊 Advanced Engine Analytics</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="bg-white p-3 rounded border">
                            <h4 className="font-semibold">Processing Stats</h4>
                            <p>Total Processed: {analytics.total_processed}</p>
                            <p>Avg Time: {analytics.average_processing_time?.toFixed(2)}s</p>
                            <p>Avg Speed: {analytics.average_chars_per_second?.toFixed(0)} chars/sec</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                            <h4 className="font-semibold">Database Stats</h4>
                            <p>Advanced Articles: {analytics.database_stats?.advanced_refined_articles}</p>
                            <p>Refined Articles: {analytics.database_stats?.refined_articles}</p>
                            <p>Total Articles: {analytics.database_stats?.total_articles}</p>
                        </div>
                        <div className="bg-white p-3 rounded border">
                            <h4 className="font-semibold">Approaches Used</h4>
                            {analytics.processing_approaches && Object.entries(analytics.processing_approaches).map(([approach, count]) => (
                                <p key={approach}>{approach}: {count}</p>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Processing Results */}
            {results && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
                    <h3 className="text-lg font-semibold text-green-800 mb-4">✅ Processing Results</h3>
                    <div className="space-y-2 text-sm">
                        <p><strong>Engine:</strong> {results.engine_used}</p>
                        <p><strong>Success:</strong> {results.success ? 'Yes' : 'No'}</p>
                        
                        {/* Batch Results */}
                        {results.batch_id && (
                            <>
                                <p><strong>Batch ID:</strong> {results.batch_id}</p>
                                <p><strong>Files Processed:</strong> {results.files_processed}</p>
                                <p><strong>Files Successful:</strong> {results.files_successful}</p>
                                <p><strong>Total Articles Created:</strong> {results.total_articles_created}</p>
                            </>
                        )}
                        
                        {/* Single File/Text Results */}
                        {!results.batch_id && (
                            <>
                                <p><strong>Articles Created:</strong> {results.articles_created}</p>
                                {results.filename && (
                                    <p><strong>Filename:</strong> {results.filename}</p>
                                )}
                                {results.content_extracted && (
                                    <p><strong>Content Extracted:</strong> {results.content_extracted} characters</p>
                                )}
                            </>
                        )}
                        
                        <p><strong>Message:</strong> {results.message}</p>
                        
                        {/* Processing Analytics */}
                        {results.processing_analytics && (
                            <div className="mt-4 p-3 bg-white rounded border">
                                <h4 className="font-semibold">⚡ Performance Metrics</h4>
                                <p>Processing Time: {results.processing_analytics.processing_time?.toFixed(2)}s</p>
                                <p>Speed: {results.processing_analytics.chars_per_second?.toFixed(0)} chars/sec</p>
                                {results.processing_analytics.confidence_average && (
                                    <p>Avg Confidence: {(results.processing_analytics.confidence_average * 100)?.toFixed(1)}%</p>
                                )}
                            </div>
                        )}
                    </div>
                    
                    {/* Individual Articles */}
                    {results.articles && results.articles.length > 0 && (
                        <div className="mt-4">
                            <h4 className="font-semibold text-green-800 mb-2">Generated Articles:</h4>
                            <div className="space-y-2">
                                {results.articles.map((article, index) => (
                                    <div key={index} className="bg-white p-3 rounded border">
                                        <p><strong>Title:</strong> {article.title}</p>
                                        <p><strong>Type:</strong> {article.article_type}</p>
                                        <p><strong>Content Length:</strong> {article.content_length} characters</p>
                                        {article.confidence_score && (
                                            <p><strong>Confidence:</strong> {(article.confidence_score * 100).toFixed(1)}%</p>
                                        )}
                                        {article.processing_approach && (
                                            <p><strong>Approach:</strong> {article.processing_approach}</p>
                                        )}
                                        {article.content_type && (
                                            <p><strong>Content Type:</strong> {article.content_type}</p>
                                        )}
                                        <p><strong>ID:</strong> {article.id}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    
                    {/* Batch Results Detail */}
                    {results.results && results.results.length > 0 && (
                        <div className="mt-4">
                            <h4 className="font-semibold text-green-800 mb-2">Batch Processing Results:</h4>
                            <div className="space-y-2 max-h-64 overflow-y-auto">
                                {results.results.map((result, index) => (
                                    <div key={index} className={`p-3 rounded border ${result.success ? 'bg-green-50' : 'bg-red-50'}`}>
                                        <p><strong>File:</strong> {result.filename}</p>
                                        <p><strong>Status:</strong> {result.success ? '✅ Success' : '❌ Failed'}</p>
                                        {result.success ? (
                                            <>
                                                <p>Articles Created: {result.articles_created}</p>
                                                <p>Content Extracted: {result.content_extracted} chars</p>
                                            </>
                                        ) : (
                                            <p className="text-red-600">Error: {result.error}</p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Error Section */}
            {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
                    <h3 className="text-lg font-semibold text-red-800 mb-2">❌ Error</h3>
                    <p className="text-red-700">{error}</p>
                </div>
            )}

            {/* Processing Indicator */}
            {processing && (
                <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
                    <div className="flex items-center space-x-3">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                        <p className="text-blue-800">
                            Processing with {engineVersion === 'advanced_2.1' ? 'Advanced Engine v2.1' : 'Refined Engine v2.0'}...
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RefinedEngineTest;