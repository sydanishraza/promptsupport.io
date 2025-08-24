import React, { useState, useEffect } from 'react';
import { HTMLContent } from './PrismCodeBlock';

const ReviewDashboard = () => {
    const [runs, setRuns] = useState([]);
    const [selectedRun, setSelectedRun] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [statusFilter, setStatusFilter] = useState('all');
    const [summaryStats, setSummaryStats] = useState({});
    const [reviewerName, setReviewerName] = useState('Human Reviewer');

    useEffect(() => {
        fetchRunsForReview();
    }, [statusFilter]);

    const fetchRunsForReview = async () => {
        try {
            setLoading(true);
            const filterParam = statusFilter !== 'all' ? `?status=${statusFilter}` : '';
            const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/review/runs${filterParam}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch runs: ${response.status}`);
            }
            
            const data = await response.json();
            setRuns(data.runs || []);
            setSummaryStats(data.summary || {});
            setError(null);
        } catch (err) {
            console.error('Error fetching runs for review:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchRunDetails = async (runId) => {
        try {
            const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/review/runs/${runId}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch run details: ${response.status}`);
            }
            
            const runDetails = await response.json();
            setSelectedRun(runDetails);
        } catch (err) {
            console.error('Error fetching run details:', err);
            setError(err.message);
        }
    };

    const approveAndPublish = async (runId) => {
        try {
            const formData = new FormData();
            formData.append('run_id', runId);
            formData.append('reviewer_name', reviewerName);
            formData.append('review_notes', 'Approved via Review Dashboard');

            const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/review/approve`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Failed to approve run: ${response.status}`);
            }

            const result = await response.json();
            alert(`✅ Run approved and published successfully! ${result.articles_published} articles published.`);
            
            // Refresh runs list
            fetchRunsForReview();
            setSelectedRun(null);
        } catch (err) {
            console.error('Error approving run:', err);
            alert(`❌ Error approving run: ${err.message}`);
        }
    };

    const rejectRun = async (runId, rejectionReason, reviewNotes, suggestedActions) => {
        try {
            const formData = new FormData();
            formData.append('run_id', runId);
            formData.append('rejection_reason', rejectionReason);
            formData.append('reviewer_name', reviewerName);
            formData.append('review_notes', reviewNotes);
            formData.append('suggested_actions', suggestedActions);

            const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/review/reject`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Failed to reject run: ${response.status}`);
            }

            const result = await response.json();
            alert(`❌ Run rejected successfully. ${result.articles_updated} articles marked as partial.`);
            
            // Refresh runs list
            fetchRunsForReview();
            setSelectedRun(null);
        } catch (err) {
            console.error('Error rejecting run:', err);
            alert(`❌ Error rejecting run: ${err.message}`);
        }
    };

    const rerunSelectedSteps = async (runId, selectedSteps, rerunReason) => {
        try {
            const formData = new FormData();
            formData.append('run_id', runId);
            formData.append('selected_steps', JSON.stringify(selectedSteps));
            formData.append('reviewer_name', reviewerName);
            formData.append('rerun_reason', rerunReason);

            const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/review/rerun`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Failed to rerun steps: ${response.status}`);
            }

            const result = await response.json();
            alert(`🔄 Selected steps re-run completed: ${result.rerun_steps.join(', ')}`);
            
            // Refresh run details
            fetchRunDetails(runId);
        } catch (err) {
            console.error('Error rerunning steps:', err);
            alert(`❌ Error rerunning steps: ${err.message}`);
        }
    };

    const getBadgeColor = (status) => {
        switch (status) {
            case 'excellent': return 'bg-green-100 text-green-800 border-green-200';
            case 'good': return 'bg-blue-100 text-blue-800 border-blue-200';
            case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            default: return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'pending_review': return 'bg-yellow-100 text-yellow-800';
            case 'approved': return 'bg-green-100 text-green-800';
            case 'rejected': return 'bg-red-100 text-red-800';
            case 'published': return 'bg-blue-100 text-blue-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 p-6">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                        <p className="mt-4 text-gray-600">Loading runs for review...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">V2 Engine Review Dashboard</h1>
                    <p className="text-gray-600">Human-in-the-loop quality assurance for content processing</p>
                </div>

                {/* Summary Statistics */}
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
                    <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-gray-900">{summaryStats.total_runs || 0}</div>
                        <div className="text-sm text-gray-600">Total Runs</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-yellow-600">{summaryStats.pending_review || 0}</div>
                        <div className="text-sm text-gray-600">Pending Review</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-green-600">{summaryStats.approved || 0}</div>
                        <div className="text-sm text-gray-600">Approved</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-red-600">{summaryStats.rejected || 0}</div>
                        <div className="text-sm text-gray-600">Rejected</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-blue-600">{Math.round(summaryStats.approval_rate || 0)}%</div>
                        <div className="text-sm text-gray-600">Approval Rate</div>
                    </div>
                </div>

                {/* Controls */}
                <div className="bg-white p-4 rounded-lg shadow mb-6">
                    <div className="flex flex-wrap items-center gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Status:</label>
                            <select 
                                value={statusFilter} 
                                onChange={(e) => setStatusFilter(e.target.value)}
                                className="border border-gray-300 rounded-md px-3 py-2 text-sm"
                            >
                                <option value="all">All Runs</option>
                                <option value="pending_review">Pending Review</option>
                                <option value="approved">Approved</option>
                                <option value="rejected">Rejected</option>
                                <option value="published">Published</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Reviewer Name:</label>
                            <input
                                type="text"
                                value={reviewerName}
                                onChange={(e) => setReviewerName(e.target.value)}
                                className="border border-gray-300 rounded-md px-3 py-2 text-sm w-40"
                                placeholder="Your name"
                            />
                        </div>
                        <div className="ml-auto">
                            <button
                                onClick={fetchRunsForReview}
                                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
                            >
                                Refresh
                            </button>
                        </div>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                        <strong>Error:</strong> {error}
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Runs List */}
                    <div className="bg-white rounded-lg shadow">
                        <div className="p-4 border-b border-gray-200">
                            <h2 className="text-lg font-semibold text-gray-900">Processing Runs ({runs.length})</h2>
                        </div>
                        <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                            {runs.length === 0 ? (
                                <div className="p-4 text-center text-gray-500">
                                    No runs found for the selected filter.
                                </div>
                            ) : (
                                runs.map((run) => (
                                    <div 
                                        key={run.run_id} 
                                        className={`p-4 cursor-pointer hover:bg-gray-50 ${selectedRun?.run_id === run.run_id ? 'bg-blue-50 border-l-4 border-blue-500' : ''}`}
                                        onClick={() => fetchRunDetails(run.run_id)}
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <div className="text-sm font-medium text-gray-900">
                                                Run: {run.run_id.slice(-8)}
                                            </div>
                                            <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(run.review_status)}`}>
                                                {run.review_status.replace('_', ' ')}
                                            </div>
                                        </div>
                                        <div className="text-xs text-gray-500 mb-2">
                                            {new Date(run.processing_timestamp).toLocaleString()}
                                        </div>
                                        <div className="text-sm text-gray-700 mb-2">
                                            {run.articles.count} articles • {Math.round(run.articles.total_content_length / 1000)}k chars
                                        </div>
                                        {/* Quality Badges */}
                                        <div className="flex flex-wrap gap-1">
                                            {Object.entries(run.badges || {}).map(([key, badge]) => (
                                                <span 
                                                    key={key}
                                                    className={`px-2 py-1 rounded text-xs border ${getBadgeColor(badge.status)}`}
                                                    title={badge.tooltip}
                                                >
                                                    {key}: {badge.value}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Run Details Panel */}
                    <div className="bg-white rounded-lg shadow">
                        {selectedRun ? (
                            <RunDetailsPanel 
                                run={selectedRun}
                                onApprove={approveAndPublish}
                                onReject={rejectRun}
                                onRerun={rerunSelectedSteps}
                                reviewerName={reviewerName}
                            />
                        ) : (
                            <div className="p-8 text-center">
                                <div className="text-gray-400 mb-4">
                                    <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                </div>
                                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Run to Review</h3>
                                <p className="text-gray-500">Click on a run from the list to view detailed information and take review actions.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

const RunDetailsPanel = ({ run, onApprove, onReject, onRerun, reviewerName }) => {
    const [activeTab, setActiveTab] = useState('overview');
    const [showRejectModal, setShowRejectModal] = useState(false);
    const [showRerunModal, setShowRerunModal] = useState(false);

    const tabs = [
        { id: 'overview', name: 'Overview', icon: '📊' },
        { id: 'articles', name: 'Articles', icon: '📄' },
        { id: 'media', name: 'Media', icon: '🖼️' },
        { id: 'diagnostics', name: 'Diagnostics', icon: '🔍' }
    ];

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between mb-2">
                    <h2 className="text-lg font-semibold text-gray-900">
                        Run Details: {run.run_id.slice(-8)}
                    </h2>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(run.review_status)}`}>
                        {run.review_status.replace('_', ' ')}
                    </div>
                </div>
                <div className="text-sm text-gray-500">
                    Processed: {new Date(run.processing_timestamp).toLocaleString()}
                </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`py-2 px-4 text-sm font-medium border-b-2 ${
                                activeTab === tab.id
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            {tab.icon} {tab.name}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-y-auto p-4">
                {activeTab === 'overview' && <OverviewTab run={run} />}
                {activeTab === 'articles' && <ArticlesTab run={run} />}
                {activeTab === 'media' && <MediaTab run={run} />}
                {activeTab === 'diagnostics' && <DiagnosticsTab run={run} />}
            </div>

            {/* Action Buttons */}
            {run.review_status === 'pending_review' && (
                <div className="p-4 border-t border-gray-200 bg-gray-50">
                    <div className="flex gap-2">
                        <button
                            onClick={() => onApprove(run.run_id)}
                            className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700"
                        >
                            ✅ Approve & Publish
                        </button>
                        <button
                            onClick={() => setShowRejectModal(true)}
                            className="flex-1 bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700"
                        >
                            ❌ Reject
                        </button>
                        <button
                            onClick={() => setShowRerunModal(true)}
                            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
                        >
                            🔄 Re-run Steps
                        </button>
                    </div>
                </div>
            )}

            {/* Reject Modal */}
            {showRejectModal && (
                <RejectModal
                    run={run}
                    onClose={() => setShowRejectModal(false)}
                    onReject={onReject}
                />
            )}

            {/* Rerun Modal */}
            {showRerunModal && (
                <RerunModal
                    run={run}
                    onClose={() => setShowRerunModal(false)}
                    onRerun={onRerun}
                />
            )}
        </div>
    );
};

const OverviewTab = ({ run }) => {
    const getBadgeColor = (status) => {
        switch (status) {
            case 'excellent': return 'bg-green-100 text-green-800 border-green-200';
            case 'good': return 'bg-blue-100 text-blue-800 border-blue-200';
            case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            default: return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    return (
        <div className="space-y-6">
            {/* Quality Badges */}
            <div>
                <h3 className="text-md font-medium text-gray-900 mb-3">Quality Metrics</h3>
                <div className="grid grid-cols-2 gap-3">
                    {Object.entries(run.badges || {}).map(([key, badge]) => (
                        <div key={key} className={`p-3 rounded-lg border ${getBadgeColor(badge.status)}`}>
                            <div className="flex items-center justify-between">
                                <div className="text-sm font-medium capitalize">{key.replace('_', ' ')}</div>
                                <div className="text-lg font-bold">{badge.value}</div>
                            </div>
                            <div className="text-xs mt-1" title={badge.tooltip}>
                                {badge.tooltip}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Articles Summary */}
            <div>
                <h3 className="text-md font-medium text-gray-900 mb-3">Content Summary</h3>
                <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span className="font-medium">Articles:</span> {run.articles.count}
                        </div>
                        <div>
                            <span className="font-medium">Total Length:</span> {Math.round(run.articles.total_content_length / 1000)}k chars
                        </div>
                    </div>
                    <div className="mt-3">
                        <span className="font-medium text-sm">Article Titles:</span>
                        <ul className="mt-1 text-sm text-gray-600">
                            {run.articles.titles.slice(0, 3).map((title, index) => (
                                <li key={index} className="truncate">• {title}</li>
                            ))}
                            {run.articles.titles.length > 3 && (
                                <li className="text-gray-400">... and {run.articles.titles.length - 3} more</li>
                            )}
                        </ul>
                    </div>
                </div>
            </div>

            {/* Processing Results */}
            <div>
                <h3 className="text-md font-medium text-gray-900 mb-3">Processing Pipeline Results</h3>
                <div className="space-y-2">
                    {Object.entries(run.processing_results || {}).map(([step, result]) => (
                        <div key={step} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <div className="text-sm font-medium capitalize">{step.replace('_', ' ')}</div>
                            <div className={`px-2 py-1 rounded text-xs ${
                                result.status === 'passed' || result.status === 'success' 
                                    ? 'bg-green-100 text-green-800' 
                                    : result.status === 'not_available'
                                    ? 'bg-gray-100 text-gray-600'
                                    : 'bg-yellow-100 text-yellow-800'
                            }`}>
                                {result.status || 'Unknown'}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

const ArticlesTab = ({ run }) => {
    const [selectedArticle, setSelectedArticle] = useState(null);

    return (
        <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">Generated Articles ({run.articles.count})</h3>
            
            {run.articles.articles_data && run.articles.articles_data.length > 0 ? (
                <div className="space-y-3">
                    {run.articles.articles_data.map((article, index) => (
                        <div key={article.id || index} className="border rounded-lg p-4 hover:bg-gray-50">
                            <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium text-gray-900">{article.title}</h4>
                                <button
                                    onClick={() => setSelectedArticle(selectedArticle === article.id ? null : article.id)}
                                    className="text-blue-600 text-sm hover:text-blue-700"
                                >
                                    {selectedArticle === article.id ? 'Hide Preview' : 'Show Preview'}
                                </button>
                            </div>
                            <div className="text-sm text-gray-600 mb-2">
                                Length: {article.content ? article.content.length : 0} characters
                            </div>
                            <div className="text-sm text-gray-500">
                                Status: {article.status || 'draft'} • Created: {new Date(article.created_at).toLocaleDateString()}
                            </div>
                            
                            {selectedArticle === article.id && (
                                <div className="mt-4 border-t pt-4">
                                    <div className="max-h-96 overflow-y-auto bg-white p-4 border rounded">
                                        <div 
                                            className="prose prose-sm max-w-none"
                                            dangerouslySetInnerHTML={{ __html: article.content || '<p>No content available</p>' }}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            ) : (
                <div className="text-center py-8 text-gray-500">
                    No articles available for preview.
                </div>
            )}
        </div>
    );
};

const MediaTab = ({ run }) => {
    return (
        <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">Media Library</h3>
            
            <div className="bg-gray-50 p-4 rounded-lg text-center">
                <div className="text-gray-400 mb-2">
                    <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                </div>
                <p className="text-gray-600">Media preview will be available in future updates</p>
                <p className="text-sm text-gray-500 mt-1">
                    Media count: {run.media ? run.media.count : 0}
                </p>
            </div>
        </div>
    );
};

const DiagnosticsTab = ({ run }) => {
    return (
        <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">Processing Diagnostics</h3>
            
            <div className="space-y-4">
                {Object.entries(run.processing_results || {}).map(([step, result]) => (
                    <div key={step} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-gray-900 capitalize">{step.replace('_', ' ')}</h4>
                            <span className={`px-2 py-1 rounded text-xs ${
                                result.status === 'passed' || result.status === 'success' 
                                    ? 'bg-green-100 text-green-800' 
                                    : result.status === 'not_available'
                                    ? 'bg-gray-100 text-gray-600'
                                    : 'bg-yellow-100 text-yellow-800'
                            }`}>
                                {result.status || 'Unknown'}
                            </span>
                        </div>
                        <div className="text-sm text-gray-600">
                            <pre className="whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

const RejectModal = ({ run, onClose, onReject }) => {
    const [rejectionReason, setRejectionReason] = useState('quality_issues');
    const [reviewNotes, setReviewNotes] = useState('');
    const [suggestedActions, setSuggestedActions] = useState('');

    const rejectionReasons = [
        { value: 'quality_issues', label: 'Quality Issues' },
        { value: 'incomplete_content', label: 'Incomplete Content' },
        { value: 'factual_errors', label: 'Factual Errors' },
        { value: 'formatting_problems', label: 'Formatting Problems' },
        { value: 'missing_sections', label: 'Missing Sections' },
        { value: 'redundancy_issues', label: 'Redundancy Issues' },
        { value: 'coverage_insufficient', label: 'Coverage Insufficient' },
        { value: 'fidelity_low', label: 'Fidelity Low' },
        { value: 'style_violations', label: 'Style Violations' },
        { value: 'other', label: 'Other' }
    ];

    const handleReject = () => {
        onReject(run.run_id, rejectionReason, reviewNotes, suggestedActions);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Reject Processing Run</h3>
                
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Rejection Reason:
                        </label>
                        <select
                            value={rejectionReason}
                            onChange={(e) => setRejectionReason(e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                        >
                            {rejectionReasons.map(reason => (
                                <option key={reason.value} value={reason.value}>
                                    {reason.label}
                                </option>
                            ))}
                        </select>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Review Notes:
                        </label>
                        <textarea
                            value={reviewNotes}
                            onChange={(e) => setReviewNotes(e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                            rows="3"
                            placeholder="Detailed feedback about the issues..."
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Suggested Actions:
                        </label>
                        <textarea
                            value={suggestedActions}
                            onChange={(e) => setSuggestedActions(e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                            rows="2"
                            placeholder="What should be done to address these issues..."
                        />
                    </div>
                </div>
                
                <div className="flex gap-2 mt-6">
                    <button
                        onClick={onClose}
                        className="flex-1 border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm hover:bg-gray-50"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleReject}
                        className="flex-1 bg-red-600 text-white px-4 py-2 rounded-md text-sm hover:bg-red-700"
                    >
                        Reject Run
                    </button>
                </div>
            </div>
        </div>
    );
};

const RerunModal = ({ run, onClose, onRerun }) => {
    const [selectedSteps, setSelectedSteps] = useState([]);
    const [rerunReason, setRerunReason] = useState('');

    const availableSteps = [
        { value: 'validation', label: 'Validation', description: 'Re-run content validation checks' },
        { value: 'qa', label: 'Quality Assurance', description: 'Re-run cross-article QA analysis' },
        { value: 'adjustment', label: 'Adaptive Adjustment', description: 'Re-run length balancing and optimization' },
        { value: 'publishing', label: 'Publishing', description: 'Re-run publishing flow and content library update' },
        { value: 'versioning', label: 'Versioning', description: 'Re-run versioning and diff analysis' }
    ];

    const toggleStep = (step) => {
        setSelectedSteps(prev => 
            prev.includes(step) 
                ? prev.filter(s => s !== step)
                : [...prev, step]
        );
    };

    const handleRerun = () => {
        if (selectedSteps.length === 0) {
            alert('Please select at least one step to re-run.');
            return;
        }
        onRerun(run.run_id, selectedSteps, rerunReason);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Re-run Processing Steps</h3>
                
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Select Steps to Re-run:
                        </label>
                        <div className="space-y-2">
                            {availableSteps.map(step => (
                                <div key={step.value} className="flex items-start">
                                    <input
                                        type="checkbox"
                                        id={step.value}
                                        checked={selectedSteps.includes(step.value)}
                                        onChange={() => toggleStep(step.value)}
                                        className="mt-1 mr-3"
                                    />
                                    <div>
                                        <label htmlFor={step.value} className="text-sm font-medium text-gray-900 cursor-pointer">
                                            {step.label}
                                        </label>
                                        <p className="text-xs text-gray-600">{step.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Reason for Re-run:
                        </label>
                        <textarea
                            value={rerunReason}
                            onChange={(e) => setRerunReason(e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                            rows="3"
                            placeholder="Why are these steps being re-run..."
                        />
                    </div>
                </div>
                
                <div className="flex gap-2 mt-6">
                    <button
                        onClick={onClose}
                        className="flex-1 border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm hover:bg-gray-50"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleRerun}
                        className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
                    >
                        Re-run Selected Steps
                    </button>
                </div>
            </div>
        </div>
    );
};

// Helper function for status colors (moved outside component to avoid re-definition)
const getStatusColor = (status) => {
    switch (status) {
        case 'pending_review': return 'bg-yellow-100 text-yellow-800';
        case 'approved': return 'bg-green-100 text-green-800';
        case 'rejected': return 'bg-red-100 text-red-800';
        case 'published': return 'bg-blue-100 text-blue-800';
        default: return 'bg-gray-100 text-gray-800';
    }
};

export default ReviewDashboard;