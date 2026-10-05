import React from 'react';
import { FileText, Cpu, Copy, Radio, CheckCircle, AlertCircle, HelpCircle } from 'lucide-react';

const ICONS = {
  metadata: FileText,
  ela: Cpu,
  copy_move: Copy,
  frequency: Radio,
};

export default function ForensicCard({ type, title, data }) {
  const IconComponent = ICONS[type] || FileText;

  if (!data) return null;

  const isSuccess = data.status === 'success';
  const isUnavailable = data.status === 'unavailable';
  const score = data.score !== null && data.score !== undefined ? data.score : null;

  let badgeColor = 'var(--text-dim)';
  let badgeBg = 'rgba(100, 116, 139, 0.15)';
  let statusText = 'Unavailable';

  if (isSuccess) {
    if (score !== null && score >= 70) {
      badgeColor = 'var(--status-authentic)';
      badgeBg = 'rgba(16, 185, 129, 0.15)';
      statusText = 'Consistent';
    } else if (score !== null && score >= 45) {
      badgeColor = 'var(--status-suspicious)';
      badgeBg = 'rgba(245, 158, 11, 0.15)';
      statusText = 'Anomalous';
    } else {
      badgeColor = 'var(--status-fake)';
      badgeBg = 'rgba(239, 68, 68, 0.15)';
      statusText = 'Suspicious';
    }
  }

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{
            padding: '6px',
            borderRadius: '6px',
            backgroundColor: 'rgba(2, 132, 199, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <IconComponent size={18} color="var(--accent-blue)" />
          </div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff' }}>{title}</h4>
        </div>

        <span style={{
          fontSize: '0.75rem',
          fontWeight: 600,
          color: badgeColor,
          backgroundColor: badgeBg,
          padding: '2px 8px',
          borderRadius: '4px',
          fontFamily: 'var(--font-mono)'
        }}>
          {statusText}
        </span>
      </div>

      {/* Metric details */}
      <div style={{
        display: 'flex',
        alignItems: 'baseline',
        gap: '0.75rem',
        marginBottom: '0.75rem',
        paddingBottom: '0.75rem',
        borderBottom: '1px solid var(--border-subtle)'
      }}>
        {score !== null ? (
          <>
            <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', fontFamily: 'var(--font-mono)' }}>
              {Math.round(score)}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/ 100</span>
          </>
        ) : (
          <span style={{ fontSize: '1rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
            N/A
          </span>
        )}
        <span style={{
          fontSize: '0.75rem',
          color: 'var(--text-dim)',
          marginLeft: 'auto'
        }}>
          Confidence: <span style={{ color: 'var(--text-muted)' }}>{data.confidence || 'low'}</span>
        </span>
      </div>

      {/* Explanation text */}
      <p style={{
        fontSize: '0.82rem',
        color: 'var(--text-muted)',
        lineHeight: 1.45,
        flexGrow: 1
      }}>
        {data.explanation}
      </p>

      {/* Additional properties badge row */}
      {type === 'metadata' && (
        <div style={{ marginTop: '0.75rem', display: 'flex', flexWrap: 'wrap', gap: '0.4rem', fontSize: '0.72rem' }}>
          {data.camera_make && (
            <span style={{ backgroundColor: 'var(--bg-secondary)', padding: '2px 6px', borderRadius: '4px', color: 'var(--accent-cyan)' }}>
              Camera: {data.camera_make}
            </span>
          )}
          {data.software && (
            <span style={{ backgroundColor: 'var(--bg-secondary)', padding: '2px 6px', borderRadius: '4px', color: '#f59e0b' }}>
              Software: {data.software}
            </span>
          )}
          <span style={{ backgroundColor: 'var(--bg-secondary)', padding: '2px 6px', borderRadius: '4px', color: 'var(--text-dim)' }}>
            EXIF: {data.has_exif ? 'Present' : 'Stripped'}
          </span>
        </div>
      )}

      {type === 'copy_move' && data.match_count !== undefined && (
        <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
          Matched vectors: <strong style={{ color: 'var(--text-main)' }}>{data.match_count}</strong> | Clusters: <strong style={{ color: 'var(--text-main)' }}>{data.suspicious_clusters || 0}</strong>
        </div>
      )}

      {type === 'ela' && data.anomaly_ratio !== undefined && (
        <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
          Anomaly Ratio: <strong style={{ color: 'var(--text-main)' }}>{data.anomaly_ratio}</strong> | Max Diff: <strong style={{ color: 'var(--text-main)' }}>{data.max_difference}</strong>
        </div>
      )}
    </div>
  );
}
