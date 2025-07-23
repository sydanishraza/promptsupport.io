import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Camera,
  Video,
  Monitor,
  Square,
  Circle,
  Pause,
  Play,
  StopCircle,
  Settings,
  Download,
  Upload,
  X,
  Maximize,
  Minimize,
  Mic,
  MicOff,
  Volume2,
  VolumeX
} from 'lucide-react';

const SnipAndRecord = ({ isOpen, onClose, onCapture }) => {
  const [captureMode, setCaptureMode] = useState('screenshot'); // 'screenshot' or 'video'
  const [captureArea, setCaptureArea] = useState('screen'); // 'screen', 'window', 'region'
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [includeMicrophone, setIncludeMicrophone] = useState(true);
  const [includeSystemAudio, setIncludeSystemAudio] = useState(true);
  const [includeWebcam, setIncludeWebcam] = useState(false);
  const [webcamPosition, setWebcamPosition] = useState('bottom-right');
  const [outputFormat, setOutputFormat] = useState('mp4');
  const [capturedMedia, setCapturedMedia] = useState(null);
  const [fileName, setFileName] = useState('');
  
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);

  // Start screen recording
  const startRecording = useCallback(async () => {
    try {
      const constraints = {
        video: {
          mediaSource: captureArea === 'screen' ? 'screen' : 'window',
          width: { ideal: 1920 },
          height: { ideal: 1080 },
          frameRate: { ideal: 30, max: 60 }
        },
        audio: includeSystemAudio
      };

      const stream = await navigator.mediaDevices.getDisplayMedia(constraints);
      
      // Add microphone if enabled
      if (includeMicrophone) {
        const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioTracks = audioStream.getAudioTracks();
        audioTracks.forEach(track => stream.addTrack(track));
      }

      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9'
      });
      
      const chunks = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'video/webm' });
        setCapturedMedia({
          type: 'video',
          blob,
          url: URL.createObjectURL(blob),
          duration: recordingDuration
        });
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
        setIsRecording(false);
        setRecordingDuration(0);
      };
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(1000); // Collect data every second
      setIsRecording(true);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Failed to start recording. Please ensure you grant screen recording permissions.');
    }
  }, [captureArea, includeMicrophone, includeSystemAudio, recordingDuration]);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  }, [isRecording]);

  // Take screenshot
  const takeScreenshot = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { mediaSource: 'screen' }
      });
      
      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();
      
      video.addEventListener('loadedmetadata', () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        canvas.toBlob((blob) => {
          setCapturedMedia({
            type: 'image',
            blob,
            url: URL.createObjectURL(blob)
          });
          
          // Stop the stream
          stream.getTracks().forEach(track => track.stop());
        }, 'image/png');
      });
      
    } catch (error) {
      console.error('Error taking screenshot:', error);
      alert('Failed to take screenshot. Please ensure you grant screen capture permissions.');
    }
  }, []);

  // Format recording duration
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Save captured media
  const saveMedia = useCallback(async () => {
    if (!capturedMedia || !fileName) return;
    
    try {
      // For demo purposes, we'll process with Knowledge Engine
      const formData = new FormData();
      
      if (capturedMedia.type === 'video') {
        formData.append('file', capturedMedia.blob, `${fileName}.webm`);
      } else {
        formData.append('file', capturedMedia.blob, `${fileName}.png`);
      }
      
      formData.append('metadata', JSON.stringify({
        source: 'snip_and_record',
        capture_type: capturedMedia.type,
        capture_area: captureArea,
        created_at: new Date().toISOString(),
        duration: capturedMedia.duration || 0
      }));

      // Process with Knowledge Engine
      if (onCapture) {
        await onCapture(formData);
      }
      
      // Reset state
      setCapturedMedia(null);
      setFileName('');
      onClose();
      
    } catch (error) {
      console.error('Error saving media:', error);
      alert('Failed to save media. Please try again.');
    }
  }, [capturedMedia, fileName, captureArea, onCapture, onClose]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Snip and Record</h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
            >
              <X size={20} />
            </button>
          </div>

          <div className="p-6">
            {/* Capture Mode Selection */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Capture Mode</h3>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setCaptureMode('screenshot')}
                  className={`p-4 rounded-lg border-2 transition-colors ${
                    captureMode === 'screenshot'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Camera className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                  <p className="font-medium">Screenshot</p>
                  <p className="text-sm text-gray-600">Capture a single image</p>
                </button>
                
                <button
                  onClick={() => setCaptureMode('video')}
                  className={`p-4 rounded-lg border-2 transition-colors ${
                    captureMode === 'video'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Video className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                  <p className="font-medium">Screen Recording</p>
                  <p className="text-sm text-gray-600">Record screen activity</p>
                </button>
              </div>
            </div>

            {/* Capture Area Selection */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Capture Area</h3>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'screen', label: 'Entire Screen', icon: Monitor },
                  { value: 'window', label: 'Application Window', icon: Square },
                  { value: 'region', label: 'Select Region', icon: Maximize }
                ].map(({ value, label, icon: Icon }) => (
                  <button
                    key={value}
                    onClick={() => setCaptureArea(value)}
                    className={`p-3 rounded-lg border text-center transition-colors ${
                      captureArea === value
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300 text-gray-700'
                    }`}
                  >
                    <Icon className="w-5 h-5 mx-auto mb-1" />
                    <p className="text-sm font-medium">{label}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Video Recording Options */}
            {captureMode === 'video' && (
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Recording Options</h3>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={includeMicrophone}
                      onChange={(e) => setIncludeMicrophone(e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <Mic className="w-4 h-4 ml-3 mr-2 text-gray-600" />
                    <span className="text-sm">Include microphone audio</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={includeSystemAudio}
                      onChange={(e) => setIncludeSystemAudio(e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <Volume2 className="w-4 h-4 ml-3 mr-2 text-gray-600" />
                    <span className="text-sm">Include system audio</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={includeWebcam}
                      onChange={(e) => setIncludeWebcam(e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <Camera className="w-4 h-4 ml-3 mr-2 text-gray-600" />
                    <span className="text-sm">Picture-in-picture webcam overlay</span>
                  </label>
                </div>
              </div>
            )}

            {/* Recording Controls */}
            {isRecording && (
              <div className="mb-6 p-4 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-red-800 font-medium">Recording</span>
                    <span className="text-red-700 font-mono">{formatDuration(recordingDuration)}</span>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setIsPaused(!isPaused)}
                      className="p-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200"
                    >
                      {isPaused ? <Play size={16} /> : <Pause size={16} />}
                    </button>
                    <button
                      onClick={stopRecording}
                      className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                    >
                      <StopCircle size={16} />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Captured Media Preview */}
            {capturedMedia && (
              <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
                <h3 className="text-lg font-medium text-green-900 mb-3">Captured Media</h3>
                <div className="flex items-center space-x-4">
                  {capturedMedia.type === 'video' ? (
                    <video
                      src={capturedMedia.url}
                      controls
                      className="w-32 h-20 rounded object-cover"
                    />
                  ) : (
                    <img
                      src={capturedMedia.url}
                      alt="Captured screenshot"
                      className="w-32 h-20 rounded object-cover"
                    />
                  )}
                  <div className="flex-1">
                    <input
                      type="text"
                      value={fileName}
                      onChange={(e) => setFileName(e.target.value)}
                      placeholder="Enter file name..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                    />
                    <p className="text-sm text-green-700">
                      {capturedMedia.type === 'video' 
                        ? `Duration: ${formatDuration(capturedMedia.duration || 0)}`
                        : 'Screenshot captured successfully'
                      }
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-between">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Cancel
              </button>
              
              <div className="flex space-x-3">
                {capturedMedia ? (
                  <button
                    onClick={saveMedia}
                    disabled={!fileName}
                    className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Process with Knowledge Engine
                  </button>
                ) : (
                  <>
                    {captureMode === 'screenshot' ? (
                      <button
                        onClick={takeScreenshot}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
                      >
                        <Camera className="w-4 h-4 mr-2" />
                        Take Screenshot
                      </button>
                    ) : (
                      <button
                        onClick={isRecording ? stopRecording : startRecording}
                        className={`px-6 py-2 rounded-lg flex items-center ${
                          isRecording
                            ? 'bg-red-600 text-white hover:bg-red-700'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                      >
                        {isRecording ? (
                          <>
                            <StopCircle className="w-4 h-4 mr-2" />
                            Stop Recording
                          </>
                        ) : (
                          <>
                            <Circle className="w-4 h-4 mr-2" />
                            Start Recording
                          </>
                        )}
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default SnipAndRecord;