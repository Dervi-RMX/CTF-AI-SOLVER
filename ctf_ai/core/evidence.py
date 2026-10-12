"""
Módulo de Gestión e Inventario de Evidencias para CTF-AI Solver Pro
Distingue formalmente entre Hipótesis, Hechos Observados, Evidencia Confirmada,
Banderas Candidatas y Banderas Validadas para prevenir alucinaciones.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
import datetime
import uuid


class EvidenceType(str, Enum):
    """Nivel de certeza y tipología de la evidencia."""
    HYPOTHESIS = "HIPÓTESIS"                    # Conjetura preliminar no comprobada
    OBSERVED_FACT = "HECHO_OBSERVADO"           # Salida directa y medible de una herramienta
    CONFIRMED_EVIDENCE = "EVIDENCIA_CONFIRMADA" # Hallazgo corroborado y reproducible
    CANDIDATE_FLAG = "BANDERA_CANDIDATA"        # Cadena con formato flag{...} encontrada
    VERIFIED_FLAG = "BANDERA_VALIDADA"          # Bandera comprobada contra evidencias del reto


class EvidenceItem:
    """Representa una pieza discreta de evidencia o hipótesis."""

    def __init__(
        self,
        evidence_type: EvidenceType,
        description: str,
        source: str = "análisis",
        data: Any = None,
        confidence: float = 0.5,
        item_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        timestamp: Optional[str] = None,
    ):
        self.id = item_id or f"EVD-{uuid.uuid4().hex[:6].upper()}"
        self.evidence_type = (
            evidence_type if isinstance(evidence_type, EvidenceType) else EvidenceType(evidence_type)
        )
        self.description = description.strip()
        self.source = source.strip()
        self.data = data
        self.confidence = max(0.0, min(1.0, float(confidence)))
        self.tags = tags or []
        self.timestamp = timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.evidence_type.value,
            "description": self.description,
            "source": self.source,
            "data": str(self.data) if self.data is not None else None,
            "confidence": self.confidence,
            "tags": self.tags,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceItem":
        raw_type = data.get("type", EvidenceType.OBSERVED_FACT.value)
        # Normalizar si viene string
        ev_type = EvidenceType.OBSERVED_FACT
        for t in EvidenceType:
            if t.value == raw_type or t.name == raw_type:
                ev_type = t
                break

        return cls(
            evidence_type=ev_type,
            description=data.get("description", ""),
            source=data.get("source", "historial"),
            data=data.get("data"),
            confidence=data.get("confidence", 0.5),
            item_id=data.get("id"),
            tags=data.get("tags", []),
            timestamp=data.get("timestamp"),
        )

    def __repr__(self) -> str:
        return f"[{self.id}|{self.evidence_type.value}] {self.description} (conf: {self.confidence:.2f})"


class EvidenceInventory:
    """Inventario centralizado de evidencias recolectadas durante un reto."""

    def __init__(self):
        self.items: List[EvidenceItem] = []

    def add(
        self,
        evidence_type: EvidenceType,
        description: str,
        source: str = "análisis",
        data: Any = None,
        confidence: float = 0.5,
        tags: Optional[List[str]] = None,
    ) -> EvidenceItem:
        """Añade una nueva evidencia o hipótesis al inventario."""
        item = EvidenceItem(
            evidence_type=evidence_type,
            description=description,
            source=source,
            data=data,
            confidence=confidence,
            tags=tags,
        )
        self.items.append(item)
        return item

    def get_by_type(self, ev_type: EvidenceType) -> List[EvidenceItem]:
        """Filtra evidencias por tipo."""
        return [i for i in self.items if i.evidence_type == ev_type]

    def get_hypotheses(self) -> List[EvidenceItem]:
        return self.get_by_type(EvidenceType.HYPOTHESIS)

    def get_observed_facts(self) -> List[EvidenceItem]:
        return self.get_by_type(EvidenceType.OBSERVED_FACT)

    def get_confirmed_evidence(self) -> List[EvidenceItem]:
        return self.get_by_type(EvidenceType.CONFIRMED_EVIDENCE)

    def get_candidate_flags(self) -> List[EvidenceItem]:
        return self.get_by_type(EvidenceType.CANDIDATE_FLAG)

    def get_verified_flags(self) -> List[EvidenceItem]:
        return self.get_by_type(EvidenceType.VERIFIED_FLAG)

    def promote_to_verified(self, flag_str: str, reason: str = "Validación comprobada") -> Optional[EvidenceItem]:
        """Promueve una bandera candidata a bandera validada con evidencia comprobada."""
        for item in self.items:
            if item.evidence_type == EvidenceType.CANDIDATE_FLAG and flag_str.strip() in item.description:
                item.evidence_type = EvidenceType.VERIFIED_FLAG
                item.confidence = 1.0
                item.description += f" [VALIDADA: {reason}]"
                return item

        # Si no existía como candidata previa, registrar directamente como validada
        return self.add(
            evidence_type=EvidenceType.VERIFIED_FLAG,
            description=f"{flag_str} [VALIDADA: {reason}]",
            source="validador",
            confidence=1.0,
        )

    def get_summary(self) -> str:
        """Genera un resumen textual formateado del estado de evidencias."""
        lines = [
            f"Total de evidencias registradas: {len(self.items)}",
            f"  - Hipótesis activas: {len(self.get_hypotheses())}",
            f"  - Hechos observados: {len(self.get_observed_facts())}",
            f"  - Evidencias confirmadas: {len(self.get_confirmed_evidence())}",
            f"  - Banderas candidatas: {len(self.get_candidate_flags())}",
            f"  - Banderas validadas: {len(self.get_verified_flags())}",
        ]
        return "\n".join(lines)

    def add_candidate_flag(self, flag_str: str, source: str = "análisis") -> EvidenceItem:
        return self.add(
            evidence_type=EvidenceType.CANDIDATE_FLAG,
            description=f"Bandera candidata detectada: {flag_str}",
            source=source,
            data={"flag": flag_str},
            confidence=0.85,
        )

    def verify_flag(self, flag_str: str, corroborating_fact: str = "") -> bool:
        item = self.promote_to_verified(flag_str, reason=corroborating_fact)
        return item is not None

    def get_verified_flag(self) -> Optional[str]:
        verified = self.get_verified_flags()
        if verified:
            import re
            m = re.search(r"(?:flag|ctf|picoctf|htb|thm)\{[^}]+\}", verified[0].description, re.IGNORECASE)
            return m.group(0) if m else verified[0].description
        return None

    def to_dict_list(self) -> List[Dict[str, Any]]:
        return [item.to_dict() for item in self.items]

    def to_list(self) -> List[Dict[str, Any]]:
        return self.to_dict_list()

    @classmethod
    def from_list(cls, data_list: List[Dict[str, Any]]) -> "EvidenceInventory":
        inv = cls()
        inv.load_from_dict_list(data_list)
        return inv

    def load_from_dict_list(self, data_list: List[Dict[str, Any]]) -> None:
        self.items = [EvidenceItem.from_dict(d) for d in data_list]
