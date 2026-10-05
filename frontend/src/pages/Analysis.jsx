import React from 'react';
import AnalysisProgress from '../components/AnalysisProgress';
import ScoreCard from '../components/ScoreCard';
import ForensicCard from '../components/ForensicCard';
import SuspiciousRegions from '../components/SuspiciousRegions';
import AIDetectorCard from '../components/AIDetectorCard';
import OCRPanel from '../components/OCRPanel';
import ClaimsPanel from '../components/ClaimsPanel';
import EvidenceSummary from '../components/EvidenceSummary';
import { ArrowLeft, Clock, FileText } from 'lucide-react';

export default function Analysis({ analysisData, isAnalyzing, currentStep, onReset }) {
  if (isAnalyzing || !analysisData || analysisData.status === 'processing') {
    return (
      <div className="container" style={{ padding: '3rem 0' }}>
        <AnalysisProgress
          currentStep={currentStep}
          status={analysisData?.status || 'processing'}
          errorMessage={analysisData?.error_message}
        />
      </div>
    );
  }

  const modules = analysisData.modules_results || {};

  return (
    <div className="container" style={{ padding: '2rem 0 5rem' }}>
      {/* Back button and Record Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '1.5rem',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <button
          onClick={onReset}
          className="btn-secondary"
          style={{ padding: '0.45rem 1rem', fontSize: '0.85rem' }}
        >
          <ArrowLeft size={16} />
          <span>Back to Upload</span>
        </button>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          fontSize: '0.8rem',
          color: 'var(--text-dim)',
          fontFamily: 'var(--font-mono)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <FileText size={14} color="var(--accent-blue)" />
            <span>{analysisData.original_filename}</span>
          </div>
          <span>•</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Clock size={14} />
            <span>ID: {analysisData.id?.slice(0, 12)}...</span>
          </div>
        </div>
      </div>

      {/* Main Analysis Dashboard Layout */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {/* Section 1: Overall Trust Score & Transparent Contribution */}
        <ScoreCard
          score={analysisData.overall_score}
          status={analysisData.authenticity_status}
          confidence={analysisData.confidence}
          breakdown={analysisData.score_breakdown}
          isDemo={analysisData.is_demo}
        />

        {/* Section 2: Multimodal Visual Artifact Comparator */}
        <SuspiciousRegions
          analysisId={analysisData.id}
          artifacts={analysisData.artifacts}
        />

        {/* Section 3: Core Forensic Cards Grid (Metadata, ELA, CopyMove, Frequency) */}
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', marginBottom: '1rem' }}>
            Forensic Modality Breakdown
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.25rem'
          }}>
            <ForensicCard
              type="metadata"
              title="EXIF & Provenance"
              data={modules.metadata}
            />
            <ForensicCard
              type="ela"
              title="Error Level Analysis"
              data={modules.ela}
            />
            <ForensicCard
              type="copy_move"
              title="Copy-Move Clones"
              data={modules.copy_move}
            />
            <ForensicCard
              type="frequency"
              title="Fourier Spectrum (FFT)"
              data={modules.frequency}
            />
          </div>
        </div>

        {/* Section 4: AI Detector Baseline */}
        <AIDetectorCard aiData={modules.ai_detector} />

        {/* Section 5: Text & Claims Verification */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.5rem'
        }}>
          <OCRPanel
            ocrData={modules.ocr}
            artifactUrl={analysisData.artifacts?.ocr}
          />
          <ClaimsPanel
            claims={modules.claims_verification}
          />
        </div>

        {/* Section 6: Explainable Evidence Synthesis & Report Export */}
        <EvidenceSummary
          analysisId={analysisData.id}
          finalSummary={analysisData.final_summary}
          evidenceBullets={analysisData.evidence_bullets}
          limitations={analysisData.limitations}
        />
      </div>
    </div>
  );
}
