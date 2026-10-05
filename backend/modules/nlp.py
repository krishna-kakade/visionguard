"""Natural Language Processing and Claim Extraction module for VisionGuard.

Uses spaCy to process OCR-extracted or user-submitted text, identifying named entities
(PERSON, ORG, GPE, DATE, EVENT) and parsing factual claims for verification.
"""

from typing import Dict, Any, List
import re

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        nlp = spacy.blank("en")
except ImportError:
    nlp = None


def clean_text(raw_text: str) -> str:
    """Removes irregular OCR artifacts and extra whitespace."""
    if not raw_text:
        return ""
    text = re.sub(r'[\r\n\t]+', ' ', raw_text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def extract_claims_and_entities(text: str) -> Dict[str, Any]:
    """Analyzes text to extract structured entities and candidate claims."""
    cleaned = clean_text(text)
    if not cleaned:
        return {
            "status": "success",
            "text": "",
            "entities": [],
            "claims": [],
            "explanation": "No textual content to analyze."
        }

    if nlp is None:
        # Regex-based fallback if spacy not available
        sentences = [s.strip() for s in re.split(r'[.!?]+', cleaned) if len(s.strip()) > 5]
        return {
            "status": "partial",
            "text": cleaned,
            "entities": [],
            "claims": [{"claim_text": s, "subject": "Unknown", "entities": []} for s in sentences],
            "explanation": "spaCy unavailable; performed basic sentence segmentation."
        }

    doc = nlp(cleaned)

    # 1. Named Entity Extraction
    target_labels = {"PERSON", "ORG", "GPE", "DATE", "EVENT", "NORP", "MONEY"}
    entities: List[Dict[str, str]] = []
    
    for ent in doc.ents:
        if ent.label_ in target_labels:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })

    # 2. Claim Extraction
    # Filter sentences that have subject-verb-object structures or significant length
    claims: List[Dict[str, Any]] = []
    for sent in doc.sents:
        sent_text = sent.text.strip()
        if len(sent_text) < 8:
            continue

        # Check for verbal predicate
        has_verb = any(token.pos_ in {"VERB", "AUX"} for token in sent)
        sent_ents = [ent.text for ent in sent.ents if ent.label_ in target_labels]

        # Extract root verb and subject if parsed
        subj = None
        for token in sent:
            if "subj" in token.dep_:
                subj = token.text
                break

        if has_verb:
            claims.append({
                "claim_text": sent_text,
                "subject": subj or "Unspecified",
                "entities": sent_ents,
                "has_named_entities": len(sent_ents) > 0
            })

    # If no structured sentences with verbs were found, treat whole snippet as candidate claim
    if not claims and len(cleaned) > 5:
        claims.append({
            "claim_text": cleaned,
            "subject": "General",
            "entities": [e["text"] for e in entities],
            "has_named_entities": len(entities) > 0
        })

    return {
        "status": "success",
        "text": cleaned,
        "entities": entities,
        "claims": claims,
        "claims_count": len(claims),
        "explanation": f"Identified {len(entities)} named entities and {len(claims)} candidate claims for fact verification."
    }
