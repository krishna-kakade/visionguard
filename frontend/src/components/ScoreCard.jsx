import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle, HelpCircle, Info } from 'lucide-react';

export default function ScoreCard({ score, status, confidence, breakdown, isDemo }) {
  // Determine color theme based on status
  let statusBadgeClass = 'badge-neutral';
  let StatusIcon = HelpCircle;
  let ringColor = '#475569';

  if (status === 'Likely Authentic') {
    statusBadgeClass = 'badge-authentic';
    StatusIcon = ShieldCheck;
    ringColor = '#16a34a';
  } else if (status === 'Potentially Suspicious') {
    statusBadgeClass = 'badge-suspicious';
    StatusIcon = AlertTriangle;
    ringColor = '#d97706';
  } else if (status === 'Highly Suspicious') {
    statusBadgeClass = 'badge-fake';
    StatusIcon = ShieldAlert;
    ringColor = '#dc2626';
  }

  const safeScore = score !== null && score !== undefined ? Math.round(score) : '—';
  const strokeDashoffset = score !== null && score !== undefined ? 283 - (283 * score) / 100 : 283;

  return (
    <div className="card" style={{ position: 'relative', overflow: 'hidden' }}>
      {isDemo && (
        <div style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
        }}>
          <span className="badge badge-demo">DEMO RESULT</span>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem', alignItems: 'center' }}>
        {/* Left: Circular gauge */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          <div style={{ position: 'relative', width: '170px', height: '170px' }}>
            <svg style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }} viewBox="0 0 100 100">
              {/* Background circle */}
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="var(--border-subtle)"
                strokeWidth="6"
              />
              {/* Progress circle */}
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke={ringColor}
                strokeWidth="6"
                strokeDasharray="283"
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                style={{ transition: 'stroke-dashoffset 0.8s ease-in-out' }}
              />
            </svg>

            {/* Inner text */}
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <span style={{ fontSize: '2.4rem', fontWeight: 700, color: '#fff', lineHeight: 1, fontFamily: 'var(--font-mono)' }}>
                {safeScore}
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                / 100
              </span>
            </div>
          </div>

          <div style={{ marginTop: '1.25rem' }}>
            <div style={{ marginBottom: '0.5rem' }}>
              <span className={`badge ${statusBadgeClass}`} style={{ fontSize: '0.85rem', padding: '0.3rem 0.85rem' }}>
                <StatusIcon size={15} />
                <span>{status || 'Evaluating...'}</span>
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
              Confidence Level: <strong style={{ color: 'var(--text-main)' }}>{confidence || 'Low'}</strong>
            </p>
          </div>
        </div>

        {/* Right: Transparent Contribution Breakdown */}
        <div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Info size={16} color="var(--accent-blue)" />
            <span>Transparent Score Weighting</span>
          </h4>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.85rem' }}>
            Weights dynamically normalize across active modules to ensure reliable overall scoring.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {breakdown && Object.entries(breakdown).map(([key, item]) => (
              <div
                key={key}
                style={{
                  backgroundColor: 'var(--bg-secondary)',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '4px',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '0.8rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>{item.name}</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-blue)' }}>
                    Score: {item.score} ({item.normalized_weight_pct}%)
                  </span>
                </div>
                {/* Progress mini bar */}
                <div style={{ height: '3px', backgroundColor: 'var(--bg-card)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${Math.min(100, Math.max(0, item.score))}%`,
                    height: '100%',
                    backgroundColor: item.score >= 70 ? 'var(--status-authentic)' : item.score >= 45 ? 'var(--status-suspicious)' : 'var(--status-fake)',
                    borderRadius: '2px'
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
