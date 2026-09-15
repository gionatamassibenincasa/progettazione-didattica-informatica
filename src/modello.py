from typing import Optional, List, Dict, Union, Any
from pydantic import BaseModel, Field, ValidationInfo, model_validator
from pathlib import Path
import yaml

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

class Verifica(BaseModel):
    tipo: str
    numero: Union[int, str]
    strumenti: str
    
class UFC(BaseModel):
    numero: Union[int, str]
    descrizione: str
    periodo: str
    competenze_disciplinari: List[VoceDidattica] = Field(default_factory=list)
    abilita: List[VoceDidattica] = Field(default_factory=list)
    conoscenze: List[VoceDidattica] = Field(default_factory=list)
    competenze_civica: List[VoceDidattica] = Field(default_factory=list)
    verifiche: List[Verifica] = Field(default_factory=list)
    
    @model_validator(mode="before")
    @classmethod
    def resolve_external_file(cls, data: dict, info: ValidationInfo) -> dict:
        """
        Risolve i riferimenti a file esterni tramite la chiave "$ref".
        """
        if isinstance(data, dict) and "$ref" in data:
            base_dir = Path.cwd()
            if info.context and "base_dir" in info.context:
                base_dir = Path(info.context["base_dir"])
            file_rel = Path(data.pop("$ref"))
            file_path = (base_dir / file_rel).resolve()
            print(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                base_data = yaml.safe_load(f)
            # Merge: le chiavi esplicite in data sovrascrivono quelle del file base
            base_data.update(data)
            return base_data
        return data

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