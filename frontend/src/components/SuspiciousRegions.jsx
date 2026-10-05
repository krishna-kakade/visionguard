import React, { useState } from 'react';
import { Eye, Layers, ZoomIn } from 'lucide-react';
import { getArtifactUrl } from '../api/api';

const TABS = [
  { key: 'original', label: 'Original Source', desc: 'Normalized input image' },
  { key: 'ela', label: 'Error Level Analysis', desc: 'JPEG recompression differential pattern' },
  { key: 'copy_move', label: 'Copy-Move Vectors', desc: 'Duplicated keypoints and spatial translation vectors' },
  { key: 'frequency', label: '2D FFT Spectrum', desc: 'Fourier frequency magnitude spectrum heatmap' },
  { key: 'ocr', label: 'OCR Overlays', desc: 'Detected textual bounding boxes' }
];

export default function SuspiciousRegions({ analysisId, artifacts }) {
  const [activeTab, setActiveTab] = useState('original');
  const [isZoomed, setIsZoomed] = useState(false);

  if (!artifacts) return null;

  // Determine current image URL
  const getImageUrl = (key) => {
    if (key === 'original') {
      return getArtifactUrl(analysisId, artifacts.original ? artifacts.original.split(/[\\/]/).pop() : 'original');
    }
    if (key === 'ela' && artifacts.ela) {
      return getArtifactUrl(analysisId, 'ela.png');
    }
    if (key === 'copy_move' && artifacts.copy_move) {
      return getArtifactUrl(analysisId, 'copy_move.png');
    }
    if (key === 'frequency' && artifacts.frequency) {
      return getArtifactUrl(analysisId, 'frequency.png');
    }
    if (key === 'ocr' && artifacts.ocr) {
      return getArtifactUrl(analysisId, 'ocr_annotated.png');
    }
    return null;
  };

  const currentUrl = getImageUrl(activeTab);
  const activeTabObj = TABS.find((t) => t.key === activeTab);

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div className="card-title" style={{ margin: 0 }}>
          <Layers size={18} color="var(--accent-cyan)" />
          <span>Multimodal Forensic Artifact Comparator</span>
        </div>

        {/* Tab buttons */}
        <div style={{
          display: 'flex',
          backgroundColor: 'var(--bg-secondary)',
          padding: '3px',
          borderRadius: '8px',
          border: '1px solid var(--border-subtle)',
          flexWrap: 'wrap',
          gap: '2px'
        }}>
          {TABS.map((tab) => {
            const hasArtifact = (tab.key === 'original') || Boolean(artifacts[tab.key]);
            const isSelected = activeTab === tab.key;

            return (
              <button
                key={tab.key}
                type="button"
                disabled={!hasArtifact}
                onClick={() => { setActiveTab(tab.key); setIsZoomed(false); }}
                style={{
                  padding: '0.35rem 0.75rem',
                  borderRadius: '6px',
                  fontSize: '0.78rem',
                  fontWeight: isSelected ? 600 : 400,
                  backgroundColor: isSelected ? 'var(--bg-card)' : 'transparent',
                  color: isSelected ? 'var(--accent-cyan)' : hasArtifact ? 'var(--text-muted)' : 'var(--text-dim)',
                  boxShadow: isSelected ? '0 2px 8px rgba(0,0,0,0.3)' : 'none',
                  border: isSelected ? '1px solid var(--border-subtle)' : '1px solid transparent',
                  opacity: hasArtifact ? 1 : 0.4,
                  cursor: hasArtifact ? 'pointer' : 'not-allowed',
                  transition: 'all 0.15s'
                }}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Description of active forensic layer */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
        marginBottom: '0.75rem'
      }}>
        <span>{activeTabObj?.desc}</span>
        {currentUrl && (
          <button
            type="button"
            onClick={() => setIsZoomed(!isZoomed)}
            style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--accent-blue)', fontSize: '0.75rem' }}
          >
            <ZoomIn size={13} />
            <span>{isZoomed ? 'Fit to View' : 'Zoom 100%'}</span>
          </button>
        )}
      </div>

      {/* Artifact Viewer Frame */}
      <div style={{
        position: 'relative',
        backgroundColor: '#050811',
        borderRadius: '8px',
        border: '1px solid var(--border-subtle)',
        minHeight: '340px',
        maxHeight: isZoomed ? 'none' : '480px',
        overflow: 'auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem'
      }}>
        {currentUrl ? (
          <img
            src={currentUrl}
            alt={activeTabObj?.label}
            style={{
              maxWidth: isZoomed ? 'none' : '100%',
              maxHeight: isZoomed ? 'none' : '440px',
              objectFit: 'contain',
              display: 'block',
              borderRadius: '4px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
            }}
          />
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-dim)' }}>
            <p>Artifact not available for this forensic modality.</p>
          </div>
        )}
      </div>
    </div>
  );
}
