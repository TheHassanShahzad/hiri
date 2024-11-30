import React, { useRef, useState, useEffect } from 'react';
import axios from 'axios';
import useDeviceType from '../hooks/useDeviceType';
import '../styles/LiveVideoStream.css';

function LiveVideoStream() {
  const deviceType = useDeviceType();
  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [chunkInterval, setChunkInterval] = useState(1000);
  const api_endpoint = 'https://api.yourpartners.com/upload-video';
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isAudioOn, setIsAudioOn] = useState(false)

  const startWebcam = async () => {
    try {
      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera access not supported by browser');
      }

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

  const startAudio = async () => {
    try {
      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Audio access not supported by browser');
      }

      // Mobile-specific constraints
      const constraints = {
        audio: true // Set to true only if you need audio
      };

      console.log('Requesting audio:', constraints);

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      setIsAudioOn(true);
      setError(null);
    } catch (err) {
      console.error('Audio error:', err);
    }
  };

  
  const stopAudio = () => {
    if (audioRef.current?.srcObject) {
      if (isStreaming) {
        stopStreaming();
      }
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsAudioOn(false);
    }
  };
  /*
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
  }; */


  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        stopStreaming();
      }
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
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
          onClick={startWebcam} 
          disabled={isCameraOn}
          className={deviceType}
        >
          Start Camera
        </button>
        <button 
          onClick={stopWebcam} 
          disabled={!isCameraOn}
        >
          Stop Camera
        </button>
        <button 
          onClick={startAudio} 
          disabled={isAudioOn}
          className={deviceType}
        >
          Start Audio
        </button>

        <button 
          onClick={startStreaming} 
          disabled={isStreaming || !isCameraOn}
          className={isStreaming ? 'streaming' : ''}
        >
          Start Streaming
        </button>
        <button 
          onClick={stopStreaming} 
          disabled={!isStreaming}
        >
          Stop Streaming
        </button>
      </div>

      {isStreaming && (
        <div className="streaming-indicator">
          Live Streaming
          <span className="streaming-dot"></span>
        </div>
      )}

      {isAudioOn && (
        <h2 className='audio-recording'>
          Audio is currently recording
        </h2>
      )}


    </div>

  );
}

export default LiveVideoStream;
