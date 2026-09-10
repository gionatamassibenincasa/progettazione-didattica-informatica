from typing import Optional, List, Dict, Union, Any
from pydantic import BaseModel, Field, model_validator

class FrameworkMetadata(BaseModel):
    nome: str
    versione: Optional[str] = None
    url: Optional[str] = None

class FrameworkRef(BaseModel):
    framework_id: str
    codice: str

class VoceDidattica(BaseModel):
    testo: str
    is_minimo: bool = False
    riferimenti: List[FrameworkRef] = Field(default_factory=list)

    # Coercizione automatica: se nel YAML c'è una semplice stringa, la converte in VoceDidattica
    @model_validator(mode='before')
    @classmethod
    def parse_string_to_voce(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"testo": value}
        return value

    @property
    def formatted_text(self) -> str:
        """Restituisce una riga formattata per la cella Word."""
        parts = [f"• {self.testo}"]
        
        if self.is_minimo:
            parts.append(" [★ Minimo]")
            
        if self.riferimenti:
            refs_str = ", ".join([f"{r.framework_id}:{r.codice}" for r in self.riferimenti])
            parts.append(f" ({refs_str})")
            
        return "".join(parts)

class UFC(BaseModel):
    numero: Union[int, str]
    descrizione: str
    periodo: str
    competenze_disciplinari: List[VoceDidattica] = Field(default_factory=list)
    abilita: List[VoceDidattica] = Field(default_factory=list)
    conoscenze: List[VoceDidattica] = Field(default_factory=list)
    competenze_civica: List[VoceDidattica] = Field(default_factory=list)
    verifiche_num: str = ""
    verifiche_strumenti: str = ""

class ProgrammazioneData(BaseModel):
    frameworks: Dict[str, FrameworkMetadata] = Field(default_factory=dict)
    dipartimento: str
    ordinamento: str
    indirizzo: str
    classe: str
    ufcs: List[UFC]

class DocumentoJob(BaseModel):
    data_filepath: str
    template_filepath: str
    output_filename: Optional[str] = None

class ConfigDocumenti(BaseModel):
    documenti: List[DocumentoJob]