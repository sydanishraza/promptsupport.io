import React, { useState } from 'react';

const RefinedEngineTest = () => {
    const [file, setFile] = useState(null);
    const [textContent, setTextContent] = useState('');
    const [processing, setProcessing] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);

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
                processing_mode: 'refined_engine'
            }));

            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/content/upload-refined`, {
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

    const handleTextProcess = async () => {
        if (!textContent.trim()) {
            setError('Please enter some text content');
            return;
        }

        setProcessing(true);
        setError(null);
        setResults(null);

        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/content/process-refined`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: textContent,
                    metadata: {
                        title: 'Text Input',
                        processing_mode: 'refined_engine'
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

    return (
        <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">
                    🆕 Refined PromptSupport Engine v2.0 
                </h2>
                <p className="text-gray-600">
                    Test the new refined engine with strict source fidelity and optimized granularity
                </p>
            </div>

            {/* File Upload Section */}
            <div className="mb-8">
                <h3 className="text-lg font-semibold mb-4">📄 File Upload Test</h3>
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
                        {processing ? 'Processing...' : 'Upload & Process with Refined Engine'}
                    </button>
                </div>
            </div>

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
                        {processing ? 'Processing...' : 'Process Text with Refined Engine'}
                    </button>
                </div>
            </div>

            {/* Results Section */}
            {results && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
                    <h3 className="text-lg font-semibold text-green-800 mb-4">✅ Processing Results</h3>
                    <div className="space-y-2 text-sm">
                        <p><strong>Engine:</strong> {results.engine_used}</p>
                        <p><strong>Success:</strong> {results.success ? 'Yes' : 'No'}</p>
                        <p><strong>Articles Created:</strong> {results.articles_created}</p>
                        {results.filename && (
                            <p><strong>Filename:</strong> {results.filename}</p>
                        )}
                        {results.content_extracted && (
                            <p><strong>Content Extracted:</strong> {results.content_extracted} characters</p>
                        )}
                        <p><strong>Message:</strong> {results.message}</p>
                    </div>
                    
                    {results.articles && results.articles.length > 0 && (
                        <div className="mt-4">
                            <h4 className="font-semibold text-green-800 mb-2">Generated Articles:</h4>
                            <div className="space-y-2">
                                {results.articles.map((article, index) => (
                                    <div key={index} className="bg-white p-3 rounded border">
                                        <p><strong>Title:</strong> {article.title}</p>
                                        <p><strong>Type:</strong> {article.article_type}</p>
                                        <p><strong>Content Length:</strong> {article.content_length} characters</p>
                                        <p><strong>ID:</strong> {article.id}</p>
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
                        <p className="text-blue-800">Processing with Refined Engine v2.0...</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RefinedEngineTest;