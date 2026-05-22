"""
src/classify/aggregator.py
Agrega sinal de regras + similaridade (+ opcional Perspective) em um score final.
"""

from typing import List, Tuple, Optional

def aggregate_risk(
    rule_hits: List[str],
    semantic_score: float,
    thresholds: dict,
    perspective_sexual: Optional[float] = None,
    perspective_weight: float = 0.4
) -> Tuple[float, str]:
    """
    Calcula um score simples e decide label.
    - thresholds: precisa conter similarity, rule_weight, semantic_weight, decision
    - perspective_sexual: se houver, agrega com um peso (ajustável)
    """
    rule_weight = float(thresholds.get("rule_weight", 0.6))
    semantic_weight = float(thresholds.get("semantic_weight", 0.6))
    sim_threshold = float(thresholds.get("similarity", 0.55))
    decision = float(thresholds.get("decision", 0.9))

    rules_component = rule_weight if rule_hits else 0.0
    semantic_component = semantic_weight if semantic_score >= sim_threshold else 0.0

    final_score = rules_component + semantic_component

    if perspective_sexual is not None:
        final_score += perspective_sexual * float(perspective_weight)

    if final_score >= decision:
        label = "suspeito"
    elif final_score >= (decision * 0.6):
        label = "atencao"
    else:
        label = "ok"

    return final_score, label
