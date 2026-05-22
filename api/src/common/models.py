"""
src/common/models.py
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any

@dataclass
class CommentRecord:

    platform: str                       
    source_id: str                     
    comment_id: str                     
    author: Optional[str]               
    text: str                          
    preprocessed: str                   
    rule_hits: List[str]               
    semantic_score: float               
    perspective_sexual: Optional[float] 
    final_score: float                  
    classification: str                
    extras: Dict[str, Any]              

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict (útil para persistir)."""
        return asdict(self)
 