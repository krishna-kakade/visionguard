import React, { useState, useRef } from 'react';
import { UploadCloud, AlertCircle, FileCheck, ArrowRight, Sparkles } from 'lucide-react';

export default function UploadZone({ onStartAnalysis, isAnalyzing, onTriggerDemo }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [imageMeta, setImageMeta] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const inputRef = useRef(null);

  const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp'];
  const MAX_SIZE_MB = 10;

  const handleFile = (file) => {
    setErrorMsg(null);
    if (!file) return;

    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setErrorMsg(`Unsupported file type '${ext}'. Please upload JPG, PNG, or WEBP.`);
      return;
    }

    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setErrorMsg(`File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds maximum limit of 10MB.`);
      return;
    }

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    const img = new Image();
    img.onload = () => {
      setImageMeta({
        width: img.naturalWidth,
        height: img.naturalHeight,
        sizeMb: (file.size / (1024 * 1024)).toFixed(2),
      });
    };
    img.src = objectUrl;
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyzeClick = () => {
    if (!selectedFile) return;
    onStartAnalysis(selectedFile);
  };

  return (
    <div style={{ maxWidth: '820px', margin: '0 auto', textAlign: 'center' }}>
      {/* Hero section */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{
          fontSize: '2.5rem',
          fontWeight: 700,
          color: 'var(--text-main)',
          letterSpacing: '-0.02em',
          lineHeight: 1.25,
          marginBottom: '0.75rem'
        }}>
          Analyze. Verify. Understand.
        </h2>
        <p style={{ fontSize: '1rem', color: 'var(--text-muted)', maxWidth: '640px', margin: '0 auto' }}>
          Multimodal forensic investigation assistant for detecting digital tampering,
          splicing, recompression discrepancies, AI-generation traces, and unverified textual claims.
        </p>
      </div>

      {/* Upload Drag & Drop Container */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !selectedFile && inputRef.current?.click()}
        style={{
          border: `2px dashed ${dragActive ? 'var(--accent-blue)' : selectedFile ? '#3b82f6' : 'var(--border-subtle)'}`,
          backgroundColor: dragActive ? 'rgba(59, 130, 246, 0.04)' : 'var(--bg-card)',
          borderRadius: '8px',
          padding: selectedFile ? '2rem' : '3.5rem 2rem',
          cursor: selectedFile ? 'default' : 'pointer',
          transition: 'border-color 0.15s ease, background-color 0.15s ease',
          position: 'relative'
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.webp"
          style={{ display: 'none' }}
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />

        {!selectedFile ? (
          <div>
            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '6px',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.25rem',
              border: '1px solid rgba(59, 130, 246, 0.2)'
            }}>
              <UploadCloud size={28} color="var(--accent-blue)" />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              Drag & Drop your image here, or <span style={{ color: 'var(--accent-blue)', textDecoration: 'underline' }}>Browse File</span>
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginBottom: '1.5rem' }}>
              Supported formats: JPG · JPEG · PNG · WEBP (Max 10 MB)
            </p>

            {/* Quick Demo button */}
            <div style={{ display: 'inline-flex', gap: '0.75rem' }}>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); onTriggerDemo(); }}
                className="btn-secondary"
                style={{ fontSize: '0.82rem', padding: '0.45rem 1rem' }}
              >
                <Sparkles size={14} color="var(--accent-blue)" />
                <span>Or load sample precomputed case</span>
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '1.25rem'
            }}>
              {/* Image preview */}
              <div style={{
                position: 'relative',
                borderRadius: '6px',
                overflow: 'hidden',
                border: '1px solid var(--border-subtle)',
                maxHeight: '320px',
                backgroundColor: '#000'
              }}>
                <img
                  src={previewUrl}
                  alt="Upload preview"
                  style={{
                    maxHeight: '320px',
                    maxWidth: '100%',
                    objectFit: 'contain',
                    display: 'block'
                  }}
                />
              </div>

              {/* File details card */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1.25rem',
                backgroundColor: 'var(--bg-secondary)',
                padding: '0.65rem 1.25rem',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
                fontSize: '0.82rem',
                color: 'var(--text-muted)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#fff', fontWeight: 600 }}>
                  <FileCheck size={16} color="var(--accent-blue)" />
                  <span style={{ maxWidth: '220px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {selectedFile.name}
                  </span>
                </div>
                {imageMeta && (
                  <>
                    <span>•</span>
                    <span>{imageMeta.width} × {imageMeta.height} px</span>
                    <span>•</span>
                    <span>{imageMeta.sizeMb} MB</span>
                  </>
                )}
                <span>•</span>
                <button
                  type="button"
                  onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}
                  style={{ color: '#ef4444', fontSize: '0.8rem', textDecoration: 'underline' }}
                >
                  Change
                </button>
              </div>

              {/* Action Button */}
              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  onClick={handleAnalyzeClick}
                  disabled={isAnalyzing}
                  className="btn-primary"
                  style={{ fontSize: '0.95rem', padding: '0.8rem 2rem' }}
                >
                  <span>Launch Forensic Analysis</span>
                  <ArrowRight size={17} />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error notification */}
      {errorMsg && (
        <div style={{
          marginTop: '1.25rem',
          backgroundColor: 'rgba(220, 38, 38, 0.1)',
          border: '1px solid rgba(220, 38, 38, 0.35)',
          color: '#fca5a5',
          padding: '0.75rem 1rem',
          borderRadius: '6px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem',
          fontSize: '0.85rem'
        }}>
          <AlertCircle size={16} color="#dc2626" />
          <span>{errorMsg}</span>
        </div>
      )}
    </div>
  );
}
