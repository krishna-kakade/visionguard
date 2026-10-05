import React from 'react';
import { CheckCircle2, XCircle, HelpCircle, ExternalLink, ShieldAlert } from 'lucide-react';

export default function ClaimsPanel({ claims }) {
  if (!claims || claims.length === 0) {
    return (
      <div className="card">
        <h4 className="card-title">
          <ShieldAlert size={18} color="var(--accent-blue)" />
          <span>Factual Claim Verification</span>
        </h4>
        <div style={{
          padding: '1.5rem',
          textAlign: 'center',
          backgroundColor: 'var(--bg-secondary)',
          borderRadius: '8px',
          border: '1px dashed var(--border-subtle)',
          color: 'var(--text-dim)',
          fontSize: '0.85rem'
        }}>
          No factual claims were identified in the image text to verify.
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h4 className="card-title">
        <ShieldAlert size={18} color="var(--accent-cyan)" />
        <span>Factual Claim Verification ({claims.length})</span>
      </h4>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {claims.map((item, idx) => {
          const verdict = item.verdict || 'UNVERIFIED';
          
          let verdictClass = 'badge-neutral';
          let VerdictIcon = HelpCircle;

          if (verdict === 'SUPPORTED') {
            verdictClass = 'badge-authentic';
            VerdictIcon = CheckCircle2;
          } else if (verdict === 'CONTRADICTED') {
            verdictClass = 'badge-fake';
            VerdictIcon = XCircle;
          }

          return (
            <div
              key={idx}
              style={{
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: '1rem'
              }}
            >
              {/* Claim header & verdict badge */}
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', marginBottom: '0.5rem' }}>
                <p style={{ fontSize: '0.92rem', fontWeight: 600, color: '#fff', lineHeight: 1.4 }}>
                  "{item.claim}"
                </p>
                <span className={`badge ${verdictClass}`} style={{ flexShrink: 0 }}>
                  <VerdictIcon size={14} />
                  <span>{verdict}</span>
                </span>
              </div>

              {/* Evidence statement */}
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.5rem', lineHeight: 1.45 }}>
                {item.evidence || 'No corroborating evidence found.'}
              </p>

              {/* Provider & Source */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-dim)', paddingTop: '0.4rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                <span>Provider: <strong style={{ color: 'var(--text-muted)' }}>{item.provider || 'Local Knowledge'}</strong></span>
                {item.source && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--accent-cyan)' }}>
                    <span>Source: {item.source}</span>
                    <ExternalLink size={12} />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
