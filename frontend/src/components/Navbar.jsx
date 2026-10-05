import React from 'react';
import { Shield, Activity, Sparkles, RefreshCw } from 'lucide-react';

export default function Navbar({ healthStatus, onTriggerDemo, isAnalyzing, onReset }) {
  const isOnline = healthStatus?.status === 'ok';

  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      backgroundColor: 'rgba(13, 21, 39, 0.85)',
      backdropFilter: 'blur(12px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      padding: '0.85rem 0'
    }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {/* Brand */}
        <div 
          onClick={onReset}
          style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}
        >
          <div style={{
            background: 'linear-gradient(135deg, #0284c7 0%, #00f0ff 100%)',
            padding: '8px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(0, 240, 255, 0.3)'
          }}>
            <Shield size={24} color="#070c18" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '0.04em', color: '#fff' }}>
                VISION<span style={{ color: 'var(--accent-cyan)' }}>GUARD</span>
              </h1>
              <span style={{
                fontSize: '0.65rem',
                backgroundColor: 'rgba(2, 132, 199, 0.2)',
                color: 'var(--accent-blue)',
                padding: '2px 6px',
                borderRadius: '4px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 600
              }}>v1.0</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Explainable Visual Fact-Checking Assistant
            </p>
          </div>
        </div>

        {/* Right actions & Health indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Health status indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '20px',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.78rem',
            fontFamily: 'var(--font-mono)'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: isOnline ? 'var(--status-authentic)' : 'var(--status-fake)',
              boxShadow: isOnline ? '0 0 8px #10b981' : '0 0 8px #ef4444'
            }} />
            <span style={{ color: isOnline ? '#e2e8f0' : '#f87171' }}>
              {isOnline ? 'Core: Online' : 'Core: Offline'}
            </span>
          </div>

          {/* Demo Mode Button (Rule 48) */}
          <button
            onClick={onTriggerDemo}
            disabled={isAnalyzing}
            className="btn-secondary"
            title="Load sample precomputed forensic investigation"
            style={{
              borderColor: 'rgba(168, 85, 247, 0.4)',
              color: '#d8b4fe'
            }}
          >
            <Sparkles size={16} color="#c084fc" />
            <span>Load Demo Case</span>
          </button>

          {/* New investigation reset */}
          <button
            onClick={onReset}
            className="btn-secondary"
            title="Start new analysis"
          >
            <RefreshCw size={15} />
            <span>New Scan</span>
          </button>
        </div>
      </div>
    </header>
  );
}
