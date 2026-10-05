import React from 'react';
import { Bot, User, Sparkles, AlertCircle } from 'lucide-react';

export default function AIDetectorCard({ aiData }) {
  if (!aiData) return null;

  const aiProb = aiData.ai_probability !== null && aiData.ai_probability !== undefined
    ? Math.round(aiData.ai_probability * 100)
    : null;
  const humanProb = aiProb !== null ? 100 - aiProb : null;

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div className="card-title" style={{ margin: 0 }}>
          <Bot size={18} color="var(--accent-blue)" />
          <span>AI-Generated Image Probability</span>
        </div>

        {aiData.is_experimental && (
          <span style={{
            fontSize: '0.72rem',
            backgroundColor: 'rgba(2, 132, 199, 0.2)',
            color: 'var(--accent-cyan)',
            padding: '2px 8px',
            borderRadius: '4px',
            fontFamily: 'var(--font-mono)'
          }}>
            Experimental Baseline
          </span>
        )}
      </div>

      {/* Visual probability comparison bar */}
      {aiProb !== null ? (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.88rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#f87171', fontWeight: 600 }}>
              <Bot size={16} />
              <span>Synthetic / AI: {aiProb}%</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#34d399', fontWeight: 600 }}>
              <User size={16} />
              <span>Organic / Optical: {humanProb}%</span>
            </div>
          </div>

          {/* Dual progress bar */}
          <div style={{
            height: '10px',
            backgroundColor: '#10b981',
            borderRadius: '6px',
            overflow: 'hidden',
            display: 'flex',
            marginBottom: '1rem',
            border: '1px solid var(--border-subtle)'
          }}>
            <div style={{
              width: `${aiProb}%`,
              backgroundColor: '#ef4444',
              transition: 'width 0.8s ease-in-out'
            }} />
          </div>

          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.45, marginBottom: '0.75rem' }}>
            {aiData.explanation}
          </p>

          {aiData.metrics && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
              gap: '0.5rem',
              backgroundColor: 'var(--bg-secondary)',
              padding: '0.6rem',
              borderRadius: '6px',
              fontSize: '0.72rem',
              color: 'var(--text-dim)',
              fontFamily: 'var(--font-mono)'
            }}>
              <div>Laplacian Var: <strong style={{ color: 'var(--text-main)' }}>{aiData.metrics.laplacian_variance}</strong></div>
              <div>Saturation Mean: <strong style={{ color: 'var(--text-main)' }}>{aiData.metrics.saturation_mean}</strong></div>
              <div>Gradient Ratio: <strong style={{ color: 'var(--text-main)' }}>{aiData.metrics.gradient_ratio}</strong></div>
            </div>
          )}
        </div>
      ) : (
        <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
          {aiData.explanation || 'AI detector metric unavailable.'}
        </div>
      )}
    </div>
  );
}
