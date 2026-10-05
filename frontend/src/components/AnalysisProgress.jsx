import React from 'react';
import { CheckCircle2, Loader2, Circle, AlertCircle } from 'lucide-react';

const STAGES = [
  { key: 'upload', label: 'Image uploaded and validated' },
  { key: 'preprocessing', label: 'Preprocessing & Normalization' },
  { key: 'metadata', label: 'Metadata & EXIF analysis' },
  { key: 'ela', label: 'Error Level Analysis (ELA)' },
  { key: 'copy_move', label: 'Copy-move forgery detection' },
  { key: 'frequency', label: 'Frequency domain (FFT) analysis' },
  { key: 'ai_detector', label: 'AI image detection baseline' },
  { key: 'ocr', label: 'OCR & Text extraction' },
  { key: 'nlp', label: 'NLP & Claim extraction' },
  { key: 'fact_check', label: 'Fact verification matching' },
  { key: 'decision', label: 'Decision engine synthesis' },
  { key: 'reports', label: 'Generating PDF & JSON reports' },
];

export default function AnalysisProgress({ currentStep, status, errorMessage }) {
  // Determine current active stage index
  const stepLower = (currentStep || '').toLowerCase();
  
  let activeIndex = 0;
  if (stepLower.includes('preprocess')) activeIndex = 1;
  else if (stepLower.includes('metadata')) activeIndex = 2;
  else if (stepLower.includes('error level') || stepLower.includes('ela')) activeIndex = 3;
  else if (stepLower.includes('copy-move') || stepLower.includes('copy_move')) activeIndex = 4;
  else if (stepLower.includes('frequency')) activeIndex = 5;
  else if (stepLower.includes('ai')) activeIndex = 6;
  else if (stepLower.includes('ocr')) activeIndex = 7;
  else if (stepLower.includes('nlp') || stepLower.includes('claim')) activeIndex = 8;
  else if (stepLower.includes('fact')) activeIndex = 9;
  else if (stepLower.includes('decision') || stepLower.includes('synthesis')) activeIndex = 10;
  else if (stepLower.includes('report')) activeIndex = 11;
  else if (status === 'completed') activeIndex = 12;

  const isFailed = status === 'failed';

  return (
    <div style={{ maxWidth: '640px', margin: '2rem auto' }} className="card">
      <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
        <div style={{
          display: 'inline-flex',
          padding: '12px',
          borderRadius: '50%',
          backgroundColor: isFailed ? 'rgba(239, 68, 68, 0.15)' : 'rgba(2, 132, 199, 0.15)',
          marginBottom: '1rem',
          border: `1px solid ${isFailed ? 'rgba(239, 68, 68, 0.4)' : 'rgba(2, 132, 199, 0.4)'}`
        }}>
          {isFailed ? (
            <AlertCircle size={32} color="#ef4444" />
          ) : (
            <Loader2 size={32} color="var(--accent-cyan)" className="pulse" style={{ animation: 'spin 1.5s linear infinite' }} />
          )}
        </div>
        <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: '#fff', marginBottom: '0.25rem' }}>
          {isFailed ? 'Investigation Halted' : 'Forensic Investigation in Progress'}
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {isFailed ? (errorMessage || 'An error occurred during analysis.') : `Current stage: ${currentStep || 'Initializing pipeline...'}`}
        </p>
      </div>

      {/* Progress Timeline List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {STAGES.map((stage, idx) => {
          const isDone = idx < activeIndex || status === 'completed';
          const isCurrent = idx === activeIndex && status !== 'completed' && !isFailed;
          const isPending = idx > activeIndex && !isFailed;

          return (
            <div
              key={stage.key}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.85rem',
                padding: '0.6rem 0.85rem',
                borderRadius: '8px',
                backgroundColor: isCurrent ? 'rgba(2, 132, 199, 0.12)' : 'transparent',
                border: isCurrent ? '1px solid rgba(2, 132, 199, 0.3)' : '1px solid transparent',
                transition: 'all 0.2s'
              }}
            >
              {isDone ? (
                <CheckCircle2 size={18} color="var(--status-authentic)" />
              ) : isCurrent ? (
                <div style={{ width: '18px', height: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <div style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--accent-cyan)',
                    boxShadow: '0 0 10px var(--accent-cyan)'
                  }} />
                </div>
              ) : (
                <Circle size={18} color="var(--border-subtle)" />
              )}

              <span style={{
                fontSize: '0.9rem',
                fontWeight: isCurrent ? 600 : 400,
                color: isDone ? 'var(--text-main)' : isCurrent ? 'var(--accent-cyan)' : 'var(--text-dim)',
                fontFamily: isCurrent ? 'var(--font-mono)' : 'inherit'
              }}>
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
