import argparse
import sys
from pathlib import Path
from typing import List, Optional
import yaml
from docxtpl import DocxTemplate
from modello import ProgrammazioneData, DocumentoJob, ConfigDocumenti

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def genera_documento(data_filepath: str, template_filepath: str, output_filename: Optional[str] = None) -> Path:
    """Genera un singolo documento DOCX a partire da un file dati YAML e un template DOCX."""
    data_path = Path(data_filepath)
    template_path = Path(template_filepath)

    if not data_path.exists():
        raise FileNotFoundError(f"File dati non trovato: {data_filepath}")
    if not template_path.exists():
        raise FileNotFoundError(f"File template non trovato: {template_filepath}")

    if not output_filename:
        output_filename = f"{data_path.stem}_generato.docx"
    output_path = Path(output_filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Caricamento e validazione del file dati YAML
    with open(data_path, "r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

    data = ProgrammazioneData(**raw_data)

    # 2. Preparazione contesto per docxtpl
    context = {
        "dipartimento": data.dipartimento,
        "ordinamento": data.ordinamento,
        "indirizzo": data.indirizzo,
        "classe": data.classe,
        "frameworks": data.frameworks,
        "ufcs": []
    }

    for ufc in data.ufcs:
        context["ufcs"].append({
            "numero": ufc.numero,
            "descrizione": ufc.descrizione,
            "periodo": ufc.periodo,
            "competenze_disciplinari": "\n".join([v.formatted_text for v in ufc.competenze_disciplinari]),
            "abilita": "\n".join([v.formatted_text for v in ufc.abilita]),
            "conoscenze": "\n".join([v.formatted_text for v in ufc.conoscenze]),
            "competenze_civica": "\n".join([v.formatted_text for v in ufc.competenze_civica]),
            "verifiche_num": ufc.verifiche_num,
            "verifiche_strumenti": ufc.verifiche_strumenti,
        })

    # 3. Rendering con docxtpl
    doc = DocxTemplate(str(template_path))
    doc.render(context)
    doc.save(str(output_path))
    print(f"✅ Generato: '{output_path}' da '{data_path}' (template: '{template_path}')")
    return output_path


def risolvi_percorso(filepath: str, config_path: Path) -> Path:
    """Risolvi un percorso di job rispetto alla directory della configurazione."""
    path = Path(filepath)
    return path if path.is_absolute() else (config_path.parent / path).resolve()


def carica_jobs(config_filepath: str) -> List[DocumentoJob]:
    """Carica l'elenco dei job di generazione da un file YAML di configurazione."""
    config_path = Path(config_filepath)
    if not config_path.exists():
        raise FileNotFoundError(f"File di configurazione non trovato: {config_filepath}")

    with open(config_path, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)

    if isinstance(raw_config, dict) and "documenti" in raw_config:
        config = ConfigDocumenti(**raw_config)
        return config.documenti
    elif isinstance(raw_config, list):
        return [DocumentoJob(**item) for item in raw_config]
    elif isinstance(raw_config, dict) and "data_filepath" in raw_config:
        return [DocumentoJob(**raw_config)]
    else:
        raise ValueError(
            f"Formato non riconosciuto nel file '{config_filepath}'. "
            "Attesa una lista di job o una chiave 'documenti'."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Generatore automatizzato di programmazioni didattiche DOCX da file YAML."
    )
    parser.add_argument(
        "config",
        nargs="?",
        default=PROJECT_ROOT / "config" / "documenti.yaml",
        help="Percorso del file YAML di configurazione (default: 'config/documenti.yaml')."
    )

    args = parser.parse_args()
    config_path = Path(args.config)

    try:
        jobs = carica_jobs(str(config_path))
        print(f"Elaborazione di {len(jobs)} documento/i da '{config_path}'...")
        for job in jobs:
            genera_documento(
                data_filepath=str(risolvi_percorso(job.data_filepath, config_path)),
                template_filepath=str(risolvi_percorso(job.template_filepath, config_path)),
                output_filename=(
                    str(risolvi_percorso(job.output_filename, config_path))
                    if job.output_filename
                    else None
                ),
            )
        print("Tutti i documenti sono stati generati con successo!")
    except Exception as exc:
        print(f"❌ Errore durante la generazione: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()