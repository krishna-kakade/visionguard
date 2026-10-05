import React from 'react';
import UploadZone from '../components/UploadZone';
import { Eye, Shield, Cpu, Binary, Search, FileCheck } from 'lucide-react';

export default function Home({ onStartAnalysis, isAnalyzing, onTriggerDemo }) {
  return (
    <div style={{ padding: '3rem 0 5rem' }}>
      <div className="container">
        {/* Upload Hero */}
        <UploadZone
          onStartAnalysis={onStartAnalysis}
          isAnalyzing={isAnalyzing}
          onTriggerDemo={onTriggerDemo}
        />

        {/* Multimodal Methodology Pillars */}
        <div style={{ marginTop: '5rem' }}>
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
              Multimodal Forensic Verification Framework
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto' }}>
              VisionGuard combines low-level pixel analysis, frequency spectrum forensics,
              and semantic verification into an explainable decision engine.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.5rem'
          }}>
            <div className="card">
              <div style={{
                padding: '8px',
                borderRadius: '8px',
                backgroundColor: 'rgba(2, 132, 199, 0.15)',
                display: 'inline-flex',
                marginBottom: '1rem'
              }}>
                <Cpu size={20} color="var(--accent-cyan)" />
              </div>
              <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#fff', marginBottom: '0.4rem' }}>
                Error Level Analysis (ELA)
              </h4>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                Computes localized compression differentials against controlled JPEG recompression to expose digital splicing and composite edits.
              </p>
            </div>

            <div className="card">
              <div style={{
                padding: '8px',
                borderRadius: '8px',
                backgroundColor: 'rgba(2, 132, 199, 0.15)',
                display: 'inline-flex',
                marginBottom: '1rem'
              }}>
                <Binary size={20} color="var(--accent-blue)" />
              </div>
              <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#fff', marginBottom: '0.4rem' }}>
                2D Fourier FFT Forensics
              </h4>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                Analyzes frequency domain magnitude spectra to detect anomalous periodic spikes and synthetic GAN/diffusion checkerboard upsampling artifacts.
              </p>
            </div>

            <div className="card">
              <div style={{
                padding: '8px',
                borderRadius: '8px',
                backgroundColor: 'rgba(2, 132, 199, 0.15)',
                display: 'inline-flex',
                marginBottom: '1rem'
              }}>
                <Search size={20} color="#a855f7" />
              </div>
              <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#fff', marginBottom: '0.4rem' }}>
                OCR & Claim Fact-Checking
              </h4>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                Extracts embedded visual text and runs named entity recognition (NER) to cross-reference assertions against verifiable factual databases.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
