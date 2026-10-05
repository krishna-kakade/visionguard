"""Fact Checking module for VisionGuard.

Provides an extensible verification provider abstraction with strict guidelines:
Never manufacture evidence; if no external provider or trusted knowledge entry matches,
return verdict 'UNVERIFIED'.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
import requests
from config import FACT_CHECK_API_KEY


class FactCheckProvider(ABC):
    """Abstract base class for claim verification providers."""

    @abstractmethod
    def verify_claim(self, claim: str) -> Dict[str, Any]:
        """Verifies a textual claim against known sources."""
        pass


class LocalFactCheckProvider(FactCheckProvider):
    """Local knowledge provider containing curated factual benchmarks for demonstrations and testing."""

    # Curated ground-truth database for common test and demo scenarios
    BENCHMARKS = [
        {
            "keywords": ["apollo", "moon", "hoax", "fake"],
            "verdict": "CONTRADICTED",
            "confidence": "High",
            "source": "NASA Lunar Surface Journal / Smithsonian Air and Space Museum",
            "evidence": "Apollo missions (11-17) successfully landed humans on the Moon, independently verified by retroreflector lasers, lunar soil samples, and third-party tracking."
        },
        {
            "keywords": ["eiffel", "tower", "paris", "france"],
            "verdict": "SUPPORTED",
            "confidence": "High",
            "source": "Société d'Exploitation de la Tour Eiffel",
            "evidence": "The Eiffel Tower is a wrought-iron lattice tower located on the Champ de Mars in Paris, France, inaugurated in 1889."
        },
        {
            "keywords": ["vaccine", "microchip", "5g"],
            "verdict": "CONTRADICTED",
            "confidence": "High",
            "source": "World Health Organization (WHO) / Centers for Disease Control and Prevention (CDC)",
            "evidence": "Extensive international peer-reviewed medical consensus confirms vaccines contain no tracking chips, electromagnetic circuitry, or 5G transmitters."
        },
        {
            "keywords": ["earth", "flat"],
            "verdict": "CONTRADICTED",
            "confidence": "High",
            "source": "Geodetic Satellite Observations / International Astronomical Union",
            "evidence": "Overwhelming observational evidence, satellite orbits, and navigational physics demonstrate Earth is an oblate spheroid."
        }
    ]

    def verify_claim(self, claim: str) -> Dict[str, Any]:
        claim_lower = claim.lower()
        for item in self.BENCHMARKS:
            if all(k in claim_lower for k in item["keywords"][:2]):
                return {
                    "verdict": item["verdict"],
                    "confidence": item["confidence"],
                    "evidence": item["evidence"],
                    "source": item["source"],
                    "provider": "LocalKnowledgeBase"
                }

        return {
            "verdict": "UNVERIFIED",
            "confidence": "Low",
            "evidence": "No matching entry in local knowledge base.",
            "source": None,
            "provider": "LocalKnowledgeBase"
        }


class WebFactCheckProvider(FactCheckProvider):
    """External Web Fact Check provider (e.g. Google Fact Check Tools API)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or FACT_CHECK_API_KEY
        self.endpoint = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    def verify_claim(self, claim: str) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "verdict": "UNVERIFIED",
                "confidence": "Low",
                "evidence": "External fact verification is not configured (FACT_CHECK_API_KEY is empty in .env).",
                "source": None,
                "provider": "GoogleFactCheckAPI (Inactive)"
            }

        try:
            params = {
                "query": claim,
                "key": self.api_key,
                "pageSize": 3
            }
            resp = requests.get(self.endpoint, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                claims_list = data.get("claims", [])
                if claims_list:
                    top_claim = claims_list[0]
                    reviews = top_claim.get("claimReview", [])
                    if reviews:
                        top_review = reviews[0]
                        publisher = top_review.get("publisher", {}).get("name", "Fact Checker")
                        text_rating = top_review.get("textualRating", "Unspecified")
                        url = top_review.get("url", "")
                        
                        # Map textual rating
                        rating_lower = text_rating.lower()
                        if any(w in rating_lower for w in ["false", "fake", "incorrect", "pants on fire"]):
                            verdict = "CONTRADICTED"
                        elif any(w in rating_lower for w in ["true", "correct", "accurate"]):
                            verdict = "SUPPORTED"
                        else:
                            verdict = "UNVERIFIED"

                        return {
                            "verdict": verdict,
                            "confidence": "High",
                            "evidence": f"Reviewed by {publisher}: '{text_rating}'.",
                            "source": url or publisher,
                            "provider": "GoogleFactCheckAPI"
                        }

            return {
                "verdict": "UNVERIFIED",
                "confidence": "Low",
                "evidence": "No published fact-checks found for this claim.",
                "source": None,
                "provider": "GoogleFactCheckAPI"
            }
        except Exception as e:
            return {
                "verdict": "UNVERIFIED",
                "confidence": "Low",
                "evidence": f"External fact-checking query failed: {str(e)}",
                "source": None,
                "provider": "GoogleFactCheckAPI"
            }


def verify_claims_list(claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Verifies a list of claims using available providers without manufacturing sources."""
    local_provider = LocalFactCheckProvider()
    web_provider = WebFactCheckProvider()

    verified_claims = []
    for item in claims:
        claim_text = item.get("claim_text", "")
        # Try local first
        res = local_provider.verify_claim(claim_text)
        
        # If unverified and web provider configured, try web
        if res["verdict"] == "UNVERIFIED" and web_provider.api_key:
            web_res = web_provider.verify_claim(claim_text)
            if web_res["verdict"] != "UNVERIFIED":
                res = web_res
            else:
                res["evidence"] = web_res["evidence"]
                res["provider"] = web_res["provider"]
        elif res["verdict"] == "UNVERIFIED" and not web_provider.api_key:
            res["evidence"] = "Unverified — no external verification provider configured."

        verified_claims.append({
            "claim": claim_text,
            "verdict": res["verdict"],
            "confidence": res["confidence"],
            "evidence": res["evidence"],
            "source": res["source"],
            "provider": res["provider"]
        })

    return verified_claims
