"""Report generator service for VisionGuard.

Generates structured JSON exports and comprehensive forensic PDF reports
with visual artifacts, breakdown tables, evidence summaries, and limitations.
"""

from pathlib import Path
from typing import Dict, Any
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.units import inch

from config import REPORTS_DIR


def generate_json_report(analysis_data: Dict[str, Any], output_path: Path) -> Path:
    """Saves complete forensic analysis data to JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis_data, f, indent=2, default=str)
    return output_path


def generate_pdf_report(analysis_data: Dict[str, Any], output_path: Path) -> Path:
    """Generates a professional forensic PDF report using ReportLab."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )
    subhead_style = ParagraphStyle(
        'DocSubhead',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        leftIndent=15,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=3
    )
    limitations_style = ParagraphStyle(
        'Limitations',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748b"),
        italic=True
    )

    story = []

    # Title & Banner
    story.append(Paragraph("VISIONGUARD", header_style))
    story.append(Paragraph("Explainable Visual Fact-Checking & Multimodal Forensics Report", subhead_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=12))

    # Overview Metadata Table
    status_label = analysis_data.get("authenticity_status", "Insufficient Evidence")
    overall_score = analysis_data.get("overall_score")
    score_display = f"{overall_score:.0f} / 100" if overall_score is not None else "N/A"
    
    status_color = colors.HexColor("#16a34a") if status_label == "Likely Authentic" else (
        colors.HexColor("#ea580c") if status_label == "Potentially Suspicious" else colors.HexColor("#dc2626")
    )

    meta_table_data = [
        [Paragraph("<b>Analysis ID:</b>", body_style), Paragraph(str(analysis_data.get("id")), body_style),
         Paragraph("<b>Overall Trust Score:</b>", body_style), Paragraph(f"<b>{score_display}</b>", body_style)],
        [Paragraph("<b>File Name:</b>", body_style), Paragraph(str(analysis_data.get("original_filename")), body_style),
         Paragraph("<b>Authenticity Status:</b>", body_style), Paragraph(f"<b>{status_label}</b>", body_style)],
        [Paragraph("<b>Date:</b>", body_style), Paragraph(str(analysis_data.get("created_at")), body_style),
         Paragraph("<b>Confidence Level:</b>", body_style), Paragraph(str(analysis_data.get("confidence", "Medium")), body_style)]
    ]

    t_meta = Table(meta_table_data, colWidths=[1.3*inch, 2.2*inch, 1.4*inch, 2.1*inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # Executive Summary
    story.append(Paragraph("Executive Summary", h2_style))
    story.append(Paragraph(analysis_data.get("final_summary", "No summary generated."), body_style))
    story.append(Spacer(1, 8))

    # Key Evidence & Findings
    evidence_bullets = analysis_data.get("evidence_bullets", [])
    if evidence_bullets:
        story.append(Paragraph("Forensic Evidence Breakdown", h2_style))
        for bullet in evidence_bullets:
            story.append(Paragraph(f"• {bullet}", bullet_style))
        story.append(Spacer(1, 10))

    # Score Contribution Breakdown Table
    breakdown = analysis_data.get("score_breakdown", {})
    if breakdown:
        story.append(Paragraph("Transparent Component Weighting", h2_style))
        table_rows = [
            [Paragraph("<b>Forensic Module</b>", body_style),
             Paragraph("<b>Raw Score</b>", body_style),
             Paragraph("<b>Norm Weight</b>", body_style),
             Paragraph("<b>Confidence</b>", body_style),
             Paragraph("<b>Finding Summary</b>", body_style)]
        ]
        for key, row in breakdown.items():
            table_rows.append([
                Paragraph(row.get("name", key), body_style),
                Paragraph(f"{row.get('score', 'N/A')}", body_style),
                Paragraph(f"{row.get('normalized_weight_pct', 0)}%", body_style),
                Paragraph(row.get("confidence", "Medium").capitalize(), body_style),
                Paragraph(row.get("explanation", "")[:120] + "...", body_style)
            ])

        t_breakdown = Table(table_rows, colWidths=[1.5*inch, 0.8*inch, 0.9*inch, 0.9*inch, 2.9*inch])
        t_breakdown.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_breakdown)
        story.append(Spacer(1, 12))

    # Visual Artifacts Section (Original vs ELA vs Frequency)
    artifacts = analysis_data.get("artifacts", {})
    if artifacts:
        story.append(Paragraph("Forensic Visual Artifacts", h2_style))
        art_items = []
        for art_key in ["original", "ela", "frequency", "copy_move"]:
            art_path = artifacts.get(art_key)
            if art_path and Path(art_path).exists():
                try:
                    rl_img = RLImage(art_path, width=1.65*inch, height=1.65*inch)
                    label = art_key.replace("_", " ").upper()
                    art_items.append([rl_img, Paragraph(f"<para align='center'><b>{label}</b></para>", body_style)])
                except Exception:
                    pass

        if art_items:
            img_row = [item[0] for item in art_items]
            label_row = [item[1] for item in art_items]
            col_width = (7.0 / len(art_items)) * inch
            t_images = Table([img_row, label_row], colWidths=[col_width]*len(art_items))
            t_images.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(t_images)
            story.append(Spacer(1, 10))

    # OCR and Claim Verification
    modules_res = analysis_data.get("modules_results", {})
    ocr_data = modules_res.get("ocr", {})
    claims_list = modules_res.get("claims_verification", [])
    
    if ocr_data.get("text") or claims_list:
        story.append(Paragraph("Text Extraction & Fact Verification", h2_style))
        if ocr_data.get("text"):
            story.append(Paragraph(f"<b>Extracted Text:</b> <i>\"{ocr_data['text'][:250]}\"</i>", body_style))
            story.append(Spacer(1, 4))
        
        if claims_list:
            for c in claims_list:
                v = c.get("verdict", "UNVERIFIED")
                v_color = "#16a34a" if v == "SUPPORTED" else ("#dc2626" if v == "CONTRADICTED" else "#64748b")
                story.append(Paragraph(
                    f"• <b>Claim:</b> {c.get('claim')} | <font color='{v_color}'><b>[{v}]</b></font> ({c.get('confidence')} Confidence)<br/>"
                    f"  <b>Evidence:</b> {c.get('evidence')}",
                    bullet_style
                ))
            story.append(Spacer(1, 6))

    # Limitations & Academic Disclaimer
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=6))
    limitations = analysis_data.get("limitations", (
        "VisionGuard provides AI-assisted forensic analysis. Results are probabilistic "
        "and should not be treated as definitive proof of authenticity or manipulation."
    ))
    story.append(Paragraph(f"<b>Notice & Limitations:</b> {limitations}", limitations_style))

    doc.build(story)
    return output_path
