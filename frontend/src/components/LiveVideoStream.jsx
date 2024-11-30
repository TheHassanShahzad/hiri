import React, { useRef, useState, useEffect } from 'react';
import axios from 'axios';
import useDeviceType from '../hooks/useDeviceType';
import '../styles/LiveVideoStream.css';

function LiveVideoStream() {
  const deviceType = useDeviceType();
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [chunkInterval, setChunkInterval] = useState(1000);
  const api_endpoint = 'https://api.yourpartners.com/upload-video';
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isAudioOn, setIsAudioOn] = useState(false)
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef(null);
  const [transcriptData, setTranscriptData] = useState([]);
  const sessionIdRef = useRef(Date.now());
  const [interimTranscript, setInterimTranscript] = useState('');

  const startWebcam = async () => {
    try {
      // Check if getUserMedia is supported


      // Mobile-specific constraints
      const constraints = {
        video: deviceType === 'mobile' ? {
          facingMode: { exact: 'environment' }, // Force back camera
          width: { ideal: 720 },
          height: { ideal: 1280 }
        } : {
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false // Set to true only if you need audio
      };

      console.log('Requesting camera with constraints:', constraints);

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      if (!videoRef.current) {
        throw new Error('Video element not found');
      }

      videoRef.current.srcObject = stream;
      setIsCameraOn(true);
      setError(null);
    } catch (err) {
      console.error('Camera error:', err);
      // More descriptive error messages
      if (err.name === 'NotAllowedError') {
        setError('Camera access denied. Please allow camera access and try again.');
      } else if (err.name === 'NotFoundError') {
        setError('No camera found. Please check your device.');
      } else if (err.name === 'NotReadableError') {
        setError('Camera is in use by another application.');
      } else {
        setError(`Camera error: ${err.message || 'Unknown error'}`);
      }
    }
  };
  
  const stopWebcam = () => {
    if (videoRef.current?.srcObject) {
      if (isStreaming) {
        stopStreaming();
      }
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsCameraOn(false);
    }
  };  
  const startStreaming = () => {
    if (!videoRef.current?.srcObject) {
      setError('No camera access');
      return;
    }

    try {
      const stream = videoRef.current.srcObject;
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp8,opus',
        videoBitsPerSecond: 1000000 // 1 Mbps
      });

      mediaRecorder.ondataavailable = async (event) => {
        if (event.data && event.data.size > 0) {
          const chunk = event.data;
          sendChunkToServer(chunk);
        }
      };

      // Request data every 1 second
      mediaRecorder.start(chunkInterval);
      mediaRecorderRef.current = mediaRecorder;
      setIsStreaming(true);
    } catch (err) {
      setError("Error starting stream: " + err.message);
      console.error("Streaming error:", err);
    }
  };

  const stopStreaming = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsStreaming(false);
    }
  };

  const sendChunkToServer = async (chunk) => {
    try {
      const formData = new FormData();
      formData.append('video_chunk', chunk);
      
      // Add timestamp or chunk number if needed
      formData.append('timestamp', Date.now().toString());

      await axios.post('api_endpoint', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          // Add any other required headers
          // 'Authorization': `Bearer ${token}`,
        },
      });

    } catch (err) {
      console.error('Error sending chunk:', err);
      // Don't stop streaming on individual chunk errors
      // But you might want to show some indication of network issues
    }
  };

  const sendTranscriptToServer = async (text) => {
    try {
      console.log('\n📤 Sending to server:', text);
      await axios.post('api_endpoint/transcript', {
        text,
        sessionId: sessionIdRef.current,
        timestamp: new Date().toISOString()
      });
      console.log('✅ Sent successfully');
    } catch (err) {
      console.error('❌ Error sending transcript:', err);
    }
  };

  const startAudio = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Audio access not supported by browser');
      }

      const constraints = {
        audio: true
      };

      console.log('Requesting audio:', constraints);

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      // Start speech recognition
      if ('webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
          let finalTranscript = '';
          let currentInterim = '';

          // Process results
          for (let i = 0; i < event.results.length; i++) {
            const result = event.results[i];
            if (result.isFinal) {
              const transcriptText = result[0].transcript;
              finalTranscript += transcriptText + ' ';
              // Send final result
              sendTranscriptToServer(transcriptText);
            } else {
              // Collect interim results
              currentInterim += result[0].transcript;
            }
          }

          // Update interim transcript and send to server
          if (currentInterim !== interimTranscript) {
            setInterimTranscript(currentInterim);
            sendTranscriptToServer(currentInterim);
          }

          // Update displayed transcript
          setTranscript(finalTranscript + currentInterim);
        };

        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          setError('Speech recognition error: ' + event.error);
        };

        recognition.start();
        recognitionRef.current = recognition;
      } else {
        console.warn('Speech recognition not supported');
      }
      
      setIsAudioOn(true);
      setError(null);
    } catch (err) {
      console.error('Audio error:', err);
      setError('Audio error: ' + err.message);
    }
  };

  const stopAudio = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsAudioOn(false);
  };

  const captureAndSendImage = async () => {
    try {
      if (!videoRef.current) {
        throw new Error('Video element not found');
      }

      // Create a canvas element
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;

      // Draw the current video frame to canvas
      const context = canvas.getContext('2d');
      context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

      // Convert canvas to blob
      const blob = await new Promise(resolve => {
        canvas.toBlob(resolve, 'image/jpeg', 0.8);
      });

      // Create FormData and append image
      const formData = new FormData();
      formData.append('thumbnail', blob, `thumbnail_${Date.now()}.jpg`);
      formData.append('sessionId', sessionIdRef.current);
      formData.append('timestamp', new Date().toISOString());

      // Send to server
      await axios.post('api_endpoint/thumbnail', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

    } catch (err) {
      console.error('Error capturing thumbnail:', err);
      setError('Failed to capture thumbnail');
    }
  };

  const handleToggleAll = async () => {
    if (isCameraOn || isAudioOn || isStreaming) {
      stopWebcam();
      stopAudio();
    } else {
      await startWebcam();
      // Wait a brief moment for video to initialize
      setTimeout(async () => {
        await captureAndSendImage();
        await startAudio();
        startStreaming();
      }, 1000);
    }
  };

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        stopStreaming();
      }
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  return (
    <div className={`stream-container ${deviceType}`}>
      {error && (
        <div className={`error-message ${deviceType}`}>
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}
      
      <video 
        ref={videoRef} 
        autoPlay 
        playsInline
        muted
        className={`video-preview ${deviceType}`}
      />

      <div className={`controls ${deviceType}`}>
        <button 
          onClick={handleToggleAll}
          className={`${isCameraOn ? 'active' : ''} ${isStreaming ? 'streaming' : ''}`}
        >
          {isCameraOn || isAudioOn || isStreaming ? 'Stop Streaming' : 'Start Streaming'}
        </button>
      </div>

      {isStreaming && (
        <div className="streaming-indicator">
          Live Streaming
          <span className="streaming-dot"></span>
        </div>
      )}

      {isAudioOn && (
        <div className='audio-recording'>
          <h2>Audio is currently recording</h2>
          <div className='transcript'>
            <div className='final-transcript'>{transcript}</div>
            <div className='interim-transcript'>{interimTranscript}</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LiveVideoStream;
