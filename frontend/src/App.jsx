import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Analysis from './pages/Analysis';
import { checkHealth, uploadAndAnalyze, getAnalysisStatus, getAnalysisDetails, triggerDemoMode } from './api/api';

export default function App() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [analysisId, setAnalysisId] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);

  const pollIntervalRef = useRef(null);

  // 1. Initial health check on mount
  useEffect(() => {
    const fetchHealth = async () => {
      const res = await checkHealth();
      setHealthStatus(res);
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // 2. Poll for pipeline status updates while analyzing
  useEffect(() => {
    if (isAnalyzing && analysisId) {
      pollIntervalRef.current = setInterval(async () => {
        try {
          const statusRes = await getAnalysisStatus(analysisId);
          setCurrentStep(statusRes.current_step);

          if (statusRes.status === 'completed') {
            clearInterval(pollIntervalRef.current);
            const fullDetails = await getAnalysisDetails(analysisId);
            setAnalysisData(fullDetails);
            setIsAnalyzing(false);
          } else if (statusRes.status === 'failed') {
            clearInterval(pollIntervalRef.current);
            setIsAnalyzing(false);
            setErrorMessage(statusRes.error_message || 'Pipeline analysis failed.');
            setAnalysisData({
              status: 'failed',
              error_message: statusRes.error_message
            });
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 1000);
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [isAnalyzing, analysisId]);

  // 3. User initiates new image upload
  const handleStartAnalysis = async (file) => {
    try {
      setErrorMessage(null);
      setIsAnalyzing(true);
      setCurrentStep('Uploading image to VisionGuard...');
      setAnalysisData(null);

      const res = await uploadAndAnalyze(file);
      setAnalysisId(res.id);
      setCurrentStep(res.current_step || 'Processing started');
    } catch (err) {
      setIsAnalyzing(false);
      const detail = err.response?.data?.detail || err.message || 'Upload failed.';
      setErrorMessage(detail);
      alert(`Upload error: ${detail}`);
    }
  };

  // 4. Demo Mode trigger (Rule 48)
  const handleTriggerDemo = async () => {
    try {
      setErrorMessage(null);
      setIsAnalyzing(false);
      const demoResult = await triggerDemoMode();
      setAnalysisId(demoResult.id);
      setAnalysisData(demoResult);
      setCurrentStep('Completed');
    } catch (err) {
      alert(`Demo mode error: ${err.message}`);
    }
  };

  // 5. Reset to home / new scan
  const handleReset = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }
    setAnalysisId(null);
    setAnalysisData(null);
    setIsAnalyzing(false);
    setCurrentStep('');
    setErrorMessage(null);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        healthStatus={healthStatus}
        onTriggerDemo={handleTriggerDemo}
        isAnalyzing={isAnalyzing}
        onReset={handleReset}
      />

      <main style={{ flexGrow: 1 }}>
        {!analysisId && !isAnalyzing ? (
          <Home
            onStartAnalysis={handleStartAnalysis}
            isAnalyzing={isAnalyzing}
            onTriggerDemo={handleTriggerDemo}
          />
        ) : (
          <Analysis
            analysisData={analysisData}
            isAnalyzing={isAnalyzing}
            currentStep={currentStep}
            onReset={handleReset}
          />
        )}
      </main>

      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        backgroundColor: 'var(--bg-secondary)',
        padding: '1.25rem 0',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-dim)'
      }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <strong>VISIONGUARD</strong> — Explainable Multimodal Forensics & Fact Verification
          </div>
          <div>
            Built with React · FastAPI · OpenCV · PIL · spaCy
          </div>
        </div>
      </footer>
    </div>
  );
}
