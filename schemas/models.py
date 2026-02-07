from __future__ import annotations

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator



Speaker = Literal["agent", "customer"]


class Turn(BaseModel):
    """
    One dialogue turn in a conversation.
    """
    model_config = ConfigDict(extra="forbid")  # reject unknown keys (deterministic)

    turn_id: int = Field(..., ge=1, description="Turn index starting from 1")
    speaker: Speaker = Field(..., description="agent or customer")
    text: str = Field(..., min_length=1, description="Verbatim text for the turn")
    timestamp: Optional[str] = Field(None, description="Optional timestamp string")

    @field_validator("text")
    @classmethod
    def clean_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Turn.text cannot be empty")
        return v


class Conversation(BaseModel):
    """
    Normalized conversation used for Task 1 and Task 2.
    """
    model_config = ConfigDict(extra="forbid")

    call_id: str = Field(..., min_length=1, description="Unique conversation ID")
    outcome: str = Field(..., min_length=1, description="Outcome label (e.g., escalation, complaint)")
    domain: Optional[str] = Field(None, description="Optional domain (if available in dataset)")
    intent: Optional[str] = Field(None, description="Optional intent (if available in dataset)")
    reason_for_call: Optional[str] = Field(None, description="Optional reason (if available)")
    turns: List[Turn] = Field(..., min_length=1, description="Ordered list of turns")

    @field_validator("call_id", "outcome", "domain", "intent", "reason_for_call")
    @classmethod
    def strip_strings(cls, v):
        if v is None:
            return v
        return str(v).strip()

    @field_validator("outcome")
    @classmethod
    def normalize_outcome(cls, v: str) -> str:
        v = v.strip().lower()
        return v

    @field_validator("turns")
    @classmethod
    def validate_turn_order(cls, turns: List[Turn]) -> List[Turn]:
        """
        Deterministic ordering guarantees for temporal / causal reasoning.
        """
        ids = [t.turn_id for t in turns]
        if ids != sorted(ids):
            raise ValueError("turn_id values must be sorted in increasing order")
        if ids[0] != 1:
            raise ValueError("turn_id must start at 1")
        # Optional but recommended: enforce contiguous turn IDs
        for i, tid in enumerate(ids, start=1):
            if tid != i:
                raise ValueError("turn_id must be contiguous starting from 1")
        return turns


# =========================
# Evidence Schemas (Task 1)
# =========================

class EvidenceSpan(BaseModel):
    """
    A supporting evidence span: must be traceable to a specific call + turn.
    This enables IDRecall and Faithfulness evaluation.
    """
    model_config = ConfigDict(extra="forbid")

    call_id: str = Field(..., min_length=1, description="Evidence call ID")
    turn_id: int = Field(..., ge=1, description="Evidence turn ID")
    speaker: Speaker = Field(..., description="agent or customer")
    text: str = Field(..., min_length=1, description="Verbatim evidence text")
    factor: str = Field(..., min_length=1, description="Causal factor label")

    @field_validator("call_id", "text", "factor")
    @classmethod
    def strip_fields(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Evidence fields cannot be empty")
        return v

    @field_validator("factor")
    @classmethod
    def normalize_factor(cls, v: str) -> str:
        return v.strip().lower()


class CausalFactor(BaseModel):
    """
    Interpretable causal factor with linked evidence.
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Factor name, e.g., customer_frustration")
    description: str = Field(..., min_length=1, description="Human-readable explanation of the factor")
    evidence: List[EvidenceSpan] = Field(default_factory=list, description="Supporting evidence spans")
    strength: float = Field(0.0, ge=0.0, le=1.0, description="Optional confidence/strength score")

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip().lower()


class CausalExplanation(BaseModel):
    """
    Structured Task 1 output:
    - outcome
    - call_ids analyzed
    - factors with evidence
    - causal chain (ordered)
    - human summary
    """
    model_config = ConfigDict(extra="forbid")

    outcome: str = Field(..., min_length=1, description="Target outcome event")
    call_ids: List[str] = Field(..., min_length=1, description="Call IDs used for explanation")
    factors: List[CausalFactor] = Field(default_factory=list, description="Causal factors (interpretable)")
    causal_chain: List[str] = Field(default_factory=list, description="Ordered causal steps")
    summary: str = Field(..., min_length=1, description="Readable explanation grounded in evidence")

    @field_validator("outcome")
    @classmethod
    def normalize_outcome(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("call_ids")
    @classmethod
    def unique_call_ids(cls, v: List[str]) -> List[str]:
        cleaned = [x.strip() for x in v if x and x.strip()]
        if not cleaned:
            raise ValueError("call_ids cannot be empty")
        # preserve order while ensuring uniqueness
        seen = set()
        uniq = []
        for cid in cleaned:
            if cid not in seen:
                uniq.append(cid)
                seen.add(cid)
        return uniq


# =========================
# Deterministic Context State (Task 2)
# =========================

class ContextState(BaseModel):
    """
    Explicit deterministic memory for multi-turn interaction (Task 2).
    This object is stored after Task 1 and reused across follow-ups.
    """
    model_config = ConfigDict(extra="forbid")

    version: int = Field(..., ge=1, description="Context version, increments when re-initialized")
    active_outcome: str = Field(..., min_length=1, description="Outcome being analyzed")
    active_call_ids: List[str] = Field(..., min_length=1, description="Pinned call IDs from Task 1")
    explanation: CausalExplanation = Field(..., description="Pinned Task 1 explanation output")

    # Evidence is pinned to prevent drift across follow-ups (faithfulness)
    pinned_evidence: List[EvidenceSpan] = Field(default_factory=list)

    # Deterministic history of the user interaction (optional but good for auditing)
    query_history: List[Dict[str, Any]] = Field(default_factory=list)

    @field_validator("active_outcome")
    @classmethod
    def normalize_active_outcome(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("active_call_ids")
    @classmethod
    def validate_active_call_ids(cls, v: List[str]) -> List[str]:
        cleaned = [x.strip() for x in v if x and x.strip()]
        if not cleaned:
            raise ValueError("active_call_ids cannot be empty")
        return cleaned

    def pin_evidence_from_explanation(self) -> "ContextState":
        """
        Convenience method to pin evidence spans from explanation factors.
        Call once after creating ContextState.
        """
        ev: List[EvidenceSpan] = []
        for factor in self.explanation.factors:
            ev.extend(factor.evidence)
        self.pinned_evidence = ev
        return self
