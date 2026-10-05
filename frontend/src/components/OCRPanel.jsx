import React, { useState } from 'react';
import { Type, Copy, Check, FileQuestion } from 'lucide-react';

export default function OCRPanel({ ocrData, artifactUrl }) {
  const [copied, setCopied] = useState(false);

  if (!ocrData) return null;

  const hasText = Boolean(ocrData.text && ocrData.text.trim().length > 0);

  const handleCopy = () => {
    if (ocrData.text) {
      navigator.clipboard.writeText(ocrData.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div className="card-title" style={{ margin: 0 }}>
          <Type size={18} color="var(--accent-cyan)" />
          <span>Optical Character Recognition (OCR)</span>
        </div>

        {hasText && (
          <button
            onClick={handleCopy}
            className="btn-secondary"
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
          >
            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
            <span>{copied ? 'Copied' : 'Copy Text'}</span>
          </button>
        )}
      </div>

      {hasText ? (
        <div>
          <div style={{
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '8px',
            padding: '1rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.88rem',
            color: '#e2e8f0',
            lineHeight: 1.6,
            maxHeight: '160px',
            overflowY: 'auto',
            whiteSpace: 'pre-wrap'
          }}>
            {ocrData.text}
          </div>

          <div style={{ display: 'flex', gap: '1.25rem', marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <span>Engine: <strong style={{ color: '#fff' }}>{ocrData.engine || 'Standard'}</strong></span>
            <span>Confidence: <strong style={{ color: '#fff' }}>{ocrData.confidence || 0}%</strong></span>
            <span>Boxes detected: <strong style={{ color: '#fff' }}>{ocrData.boxes_count || 0}</strong></span>
          </div>
        </div>
      ) : (
        <div style={{
          padding: '1.5rem',
          textAlign: 'center',
          backgroundColor: 'var(--bg-secondary)',
          borderRadius: '8px',
          border: '1px dashed var(--border-subtle)',
          color: 'var(--text-dim)'
        }}>
          <FileQuestion size={24} style={{ margin: '0 auto 0.5rem', opacity: 0.5 }} />
          <p style={{ fontSize: '0.85rem' }}>{ocrData.explanation || 'No textual content was detected in this image.'}</p>
        </div>
      )}
    </div>
  );
}
