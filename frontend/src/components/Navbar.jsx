import React from 'react';
import { Shield, Sparkles, RefreshCw } from 'lucide-react';

export default function Navbar({ healthStatus, onTriggerDemo, isAnalyzing, onReset }) {
  const isOnline = healthStatus?.status === 'ok';

  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      backgroundColor: 'rgba(17, 24, 39, 0.95)',
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
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            padding: '7px',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Shield size={20} color="var(--accent-blue)" strokeWidth={2.2} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h1 style={{ fontSize: '1.15rem', fontWeight: 700, letterSpacing: '0.02em', color: '#fff' }}>
                VISION<span style={{ color: 'var(--accent-blue)' }}>GUARD</span>
              </h1>
              <span style={{
                fontSize: '0.65rem',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                color: 'var(--accent-blue)',
                padding: '2px 5px',
                borderRadius: '3px',
                border: '1px solid rgba(59, 130, 246, 0.25)',
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          {/* Health status indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.45rem',
            padding: '0.3rem 0.65rem',
            borderRadius: '4px',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.76rem',
            fontFamily: 'var(--font-mono)'
          }}>
            <div style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: isOnline ? 'var(--status-authentic)' : 'var(--status-fake)'
            }} />
            <span style={{ color: isOnline ? '#cbd5e1' : '#f87171' }}>
              {isOnline ? 'System Online' : 'System Offline'}
            </span>
          </div>

          {/* Demo Mode Button */}
          <button
            onClick={onTriggerDemo}
            disabled={isAnalyzing}
            className="btn-secondary"
            title="Load sample precomputed forensic investigation"
            style={{ fontSize: '0.82rem', padding: '0.45rem 0.85rem' }}
          >
            <Sparkles size={14} color="var(--accent-blue)" />
            <span>Load Demo Case</span>
          </button>

          {/* New investigation reset */}
          <button
            onClick={onReset}
            className="btn-secondary"
            title="Start new analysis"
            style={{ fontSize: '0.82rem', padding: '0.45rem 0.85rem' }}
          >
            <RefreshCw size={14} />
            <span>New Scan</span>
          </button>
        </div>
      </div>
    </header>
  );
}
