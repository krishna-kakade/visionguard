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
    <div style={{ maxWidth: '620px', margin: '2rem auto' }} className="card">
      <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
        <div style={{
          display: 'inline-flex',
          padding: '10px',
          borderRadius: '50%',
          backgroundColor: isFailed ? 'rgba(220, 38, 38, 0.12)' : 'rgba(37, 99, 235, 0.12)',
          marginBottom: '0.85rem',
          border: `1px solid ${isFailed ? 'rgba(220, 38, 38, 0.3)' : 'rgba(37, 99, 235, 0.3)'}`
        }}>
          {isFailed ? (
            <AlertCircle size={28} color="#dc2626" />
          ) : (
            <Loader2 size={28} color="var(--accent-blue)" style={{ animation: 'spin 1.5s linear infinite' }} />
          )}
        </div>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
          {isFailed ? 'Investigation Halted' : 'Forensic Investigation in Progress'}
        </h3>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          {isFailed ? (errorMessage || 'An error occurred during analysis.') : `Current stage: ${currentStep || 'Initializing pipeline...'}`}
        </p>
      </div>

      {/* Progress Timeline List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {STAGES.map((stage, idx) => {
          const isDone = idx < activeIndex || status === 'completed';
          const isCurrent = idx === activeIndex && status !== 'completed' && !isFailed;

          return (
            <div
              key={stage.key}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.55rem 0.75rem',
                borderRadius: '4px',
                backgroundColor: isCurrent ? 'rgba(37, 99, 235, 0.08)' : 'transparent',
                border: isCurrent ? '1px solid rgba(37, 99, 235, 0.25)' : '1px solid transparent',
                transition: 'background-color 0.15s ease'
              }}
            >
              {isDone ? (
                <CheckCircle2 size={16} color="var(--status-authentic)" />
              ) : isCurrent ? (
                <div style={{ width: '16px', height: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--accent-blue)'
                  }} />
                </div>
              ) : (
                <Circle size={16} color="var(--border-subtle)" />
              )}

              <span style={{
                fontSize: '0.85rem',
                fontWeight: isCurrent ? 600 : 400,
                color: isDone ? 'var(--text-main)' : isCurrent ? 'var(--accent-blue)' : 'var(--text-dim)',
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
