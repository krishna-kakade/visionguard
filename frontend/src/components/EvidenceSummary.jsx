import React from 'react';
import { HelpCircle, Download, FileJson, AlertTriangle } from 'lucide-react';
import { getReportUrl } from '../api/api';

export default function EvidenceSummary({ analysisId, finalSummary, evidenceBullets, limitations }) {
  const pdfUrl = getReportUrl(analysisId, 'pdf');
  const jsonUrl = getReportUrl(analysisId, 'json');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Evidence Explanation Card */}
      <div className="card">
        <h4 className="card-title">
          <HelpCircle size={18} color="var(--accent-cyan)" />
          <span>Why did VisionGuard reach this result?</span>
        </h4>

        {finalSummary && (
          <p style={{
            fontSize: '0.9rem',
            color: 'var(--text-main)',
            lineHeight: 1.55,
            marginBottom: '1.25rem',
            padding: '0.85rem 1rem',
            backgroundColor: 'var(--bg-secondary)',
            borderRadius: '8px',
            borderLeft: '3px solid var(--accent-cyan)'
          }}>
            {finalSummary}
          </p>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
          {evidenceBullets && evidenceBullets.map((bullet, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.65rem', fontSize: '0.86rem', color: 'var(--text-muted)' }}>
              <span style={{ color: 'var(--accent-blue)', fontWeight: 'bold' }}>•</span>
              <span style={{ lineHeight: 1.5 }}>{bullet}</span>
            </div>
          ))}
        </div>

        {/* Download Actions */}
        <div style={{
          display: 'flex',
          gap: '1rem',
          marginTop: '1.5rem',
          paddingTop: '1.25rem',
          borderTop: '1px solid var(--border-subtle)',
          flexWrap: 'wrap'
        }}>
          <a
            href={pdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            download
            className="btn-primary"
            style={{ textDecoration: 'none', fontSize: '0.88rem', padding: '0.6rem 1.25rem' }}
          >
            <Download size={16} />
            <span>Download Forensic PDF Report</span>
          </a>

          <a
            href={jsonUrl}
            target="_blank"
            rel="noopener noreferrer"
            download
            className="btn-secondary"
            style={{ textDecoration: 'none', fontSize: '0.88rem', padding: '0.6rem 1.25rem' }}
          >
            <FileJson size={16} color="var(--accent-cyan)" />
            <span>Export Raw JSON Data</span>
          </a>
        </div>
      </div>

      {/* Limitations & Ethical Disclaimer (Rule 30) */}
      <div style={{
        padding: '1rem 1.25rem',
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(148, 163, 184, 0.2)',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.75rem',
        fontSize: '0.78rem',
        color: 'var(--text-dim)',
        lineHeight: 1.5
      }}>
        <AlertTriangle size={16} color="#94a3b8" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <strong style={{ color: 'var(--text-muted)' }}>Academic & Forensic Disclaimer: </strong>
          {limitations || (
            "VisionGuard provides AI-assisted forensic analysis. Results are probabilistic " +
            "and should not be treated as definitive proof of authenticity or manipulation."
          )}
        </div>
      </div>
    </div>
  );
}
