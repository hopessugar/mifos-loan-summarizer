"""
Audit Trail Service

Logs every loan analysis to a JSON Lines file for regulatory compliance.
Each entry contains:
- Timestamp
- Contract hash (SHA-256 of input text — NOT the text itself)
- Provider used
- Risk score output
- Processing time
- Security warnings

Audit logs are append-only and rotated daily.
"""

import json
import hashlib
import datetime
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Audit log directory — inside the container, mount as a volume in production
AUDIT_DIR = Path("/app/audit_logs")


def _ensure_audit_dir():
    """Create audit directory if it doesn't exist."""
    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        logger.warning(f"Cannot create audit directory {AUDIT_DIR}. Audit logging disabled.")
        return False
    return True


def hash_contract(text: str) -> str:
    """Generate SHA-256 hash of contract text for traceability without storing PII."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def log_analysis(
    contract_text: str,
    provider: str,
    risk_score: Optional[float],
    processing_time_ms: int,
    warnings: list[str],
    entities_found: int = 0,
    language: str = 'en',
    source: str = 'text',  # 'text' or 'fineract'
):
    """Log an analysis event to the daily audit file.
    
    Args:
        contract_text: The raw contract text (hashed, not stored)
        provider: LLM provider name
        risk_score: Calculated risk score (0-10)
        processing_time_ms: Total processing time in milliseconds
        warnings: List of security/validation warnings
        entities_found: Number of entities successfully extracted
        language: Analysis language (en/hi)
        source: Input source (text paste or fineract product)
    """
    if not _ensure_audit_dir():
        return

    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "contract_hash": hash_contract(contract_text),
        "contract_length": len(contract_text),
        "provider": provider,
        "language": language,
        "source": source,
        "risk_score": risk_score,
        "entities_found": entities_found,
        "processing_time_ms": processing_time_ms,
        "warning_count": len(warnings),
        "warnings": warnings[:10],  # Cap at 10 to prevent log bloat
    }

    log_file = AUDIT_DIR / f"audit_{datetime.date.today().isoformat()}.jsonl"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.debug(f"Audit entry written: {entry['contract_hash'][:12]}...")
    except Exception as e:
        logger.error(f"Failed to write audit entry: {e}")
