# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Python system that generates department teaching-plan documents (`.docx`) from structured YAML data. It renders a Word template using `docxtpl`/Jinja2, with data validated by Pydantic models and IDE-time validated via a JSON Schema. Supports batch generation of multiple documents from one config file.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Requires Python 3.10+. Key deps: `docxtpl` (Jinja2-based DOCX templating), `pydantic` (data validation), `pyyaml`, `python-docx`, `jsonref` (resolves `$ref` pointers in the data YAML before validation).

## Commands

Generate documents using the default batch config (`config/documenti.yaml`):
```bash
python src/genera_doc.py
```

Generate using a different config file:
```bash
python src/genera_doc.py config/config_personalizzato.yaml
```

Validate a data YAML file against the Pydantic model without rendering (useful before debugging template issues):
```bash
python -c "import sys, yaml; sys.path.insert(0, 'src'); from modello import ProgrammazioneData; data = ProgrammazioneData(**yaml.safe_load(open('data/programmazione_3_sia.yaml')))"
```

Inspect which table cells in a `.docx` template still contain unresolved Jinja2 tags (`{{` / `{%`) — useful when a template edit broke rendering:
```bash
python -c "
import docx
doc = docx.Document('templates/TEMPLATE_MOD_INS_01_B REV.02 Programm. Dipart. Triennio.docx')
for i, table in enumerate(doc.tables):
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            if '{%' in cell.text or '{{' in cell.text:
                print(f'Tabella {i} [riga {r_idx}, colonna {c_idx}]: {cell.text.strip()}')
"
```

There is no test suite, linter, or build step in this repo — correctness is verified by running the generator against real data/template files and checking the output `.docx`.

## Architecture / data pipeline

```
config/documenti.yaml  →  src/genera_doc.py  →  data/*.yaml + templates/*.docx  →  output/*.docx
                              │
                              ▼
                        src/modello.py (Pydantic validation)
```

- **`config/documenti.yaml`**: batch job list. Each entry has `data_filepath`, `template_filepath`, and optional `output_filename`. All paths in a job entry are resolved *relative to the config file's own directory* (see `risolvi_percorso` in `genera_doc.py`), not relative to the CWD.
- **`data/*.yaml`**: the actual teaching-plan content (UFCs, competencies, frameworks). Validated against `schemas/schema_programmazione.json` live in VS Code (via the `# yaml-language-server: $schema=...` header line) and against `src/modello.py` at runtime.
- **`src/modello.py`**: Pydantic models defining the data shape — `ProgrammazioneData` → `UFC` → `VoceDidattica` (a single competency/skill/knowledge entry) and `UFC.verifiche: List[Verifica]` (`Verifica` = `{tipo, numero, strumenti}`, `tipo` ∈ Scritto/Orale/Pratico). `VoceDidattica` accepts either a plain string or a structured object (a `model_validator(mode='before')` coerces a bare string into `{"testo": ...}`), and exposes `formatted_text`, which renders the bullet, the `[★ Minimo]` badge (from `is_minimo`), and framework reference codes (e.g. `CINI_INF:ALG-01`) into the single string that ends up in a Word table cell.
- **`src/genera_doc.py`**: orchestration. `carica_jobs()` reads and validates the batch config into `DocumentoJob` objects; `genera_documento()` loads a data file's raw YAML, resolves any `$ref` pointers via `jsonref.replace_refs` (using a custom `yaml_loader` so refs can point at external YAML files, not just JSON), then validates it with `ProgrammazioneData`. It flattens each UFC's list fields (competenze_disciplinari, abilita, conoscenze, competenze_civica) into newline-joined `formatted_text` strings and each UFC's `verifiche` into a list of `{tipo, numero, strumenti}` dicts, then renders the template via `docxtpl` (`.docx`) or `jinja2.Template` (`.md`). `output_filename` defaults to `<data_stem>_generato.docx` when omitted.
- **`templates/*.docx`**: the Word templates. Must follow strict `docxtpl` conventions — see below. Templates: `TEMPLATE_MOD_INS_01_B REV.02 Programm. Dipart. Triennio.docx` (classi 3ª-5ª, `classe` values `TERZA`/`QUARTA`/`QUINTA`), `MOD_INS_01_A REV.02 Programm. Dipart. Biennio.docx` (classi 1ª-2ª, `classe` values `PRIMA`/`SECONDA`; no `SIA` row, since that articolazione only starts in the secondo biennio), and `TEMPLATE_Triennio_valutazione.docx` (currently used only for the SIA job in `config/documenti.yaml`; same 9-column layout). All three share the identical 9-column UFC table layout and `indirizzo` checkbox values. `templates/template_md_triennio.md` is a Jinja2 (non-docx) template for Markdown output, rendered via plain `jinja2.Template` rather than `docxtpl`.
- **`schemas/schema_programmazione.json`**: JSON Schema mirroring `modello.py`, used only for editor-time autocomplete/validation, not enforced at runtime.
- **`docs/riferimenti/`**: human reference material only (ministerial guidelines, framework documents, target/comparison docs) — never read by any script. Safe to add files here without affecting the pipeline.

## DOCX template conventions (critical, easy to break)

The teaching-plan table in the template is a 9-column table iterated over `ufcs`. Editing the template in Word is error-prone because Word can split a single Jinja tag across multiple XML `<w:r>` runs, which breaks rendering (use the "inspect tags" command above to check after any manual edit).

- Row 2, first cell: `{%tr for ufc in ufcs %}` — **no space** after `%`, or Jinja2 raises `TemplateSyntaxError: Encountered unknown tag 'tr'`.
- Row 3 (9 columns, one field each, in order): `ufc.numero`, `ufc.descrizione`, `ufc.periodo`, `ufc.competenze_disciplinari`, `ufc.abilita`, `ufc.conoscenze`, `ufc.competenze_civica`, then the last two columns each contain a nested `{% for v in ufc.verifiche %}...{% endfor %}` loop: `{{ v.tipo }} {{ v.numero }}` in column 8, `{{ v.strumenti }}` in column 9. (Older revisions used flat `ufc.verifiche_num`/`ufc.verifiche_strumenti` string fields — these no longer exist on `UFC`; a data file that still sets them will validate silently, since Pydantic ignores unknown fields by default, but the corresponding cells will render empty. Always use the `verifiche: [{tipo, numero, strumenti}]` list form.)
- Row 4, first cell: `{%tr endfor %}` — again no space after `%`.
- Header checkboxes use inline conditionals, e.g. `{% if classe == 'TERZA' %}▣{% else %}☐{% endif %} TERZA` and the analogous pattern keyed on `indirizzo`. Recognized `indirizzo` values that light up a checkbox: `AFM`, `SIA`, `SCIENTIFICO` (corso base), `SCIENTIFICO_CAMBRIDGE`, `SCIENTIFICO_SCIENZE_APPLICATE`, `SCIENTIFICO_INFORMATICA`. Other values (e.g. `LICEO LINGUISTICO`, `TURISTICO`) are accepted but have no checkbox in the template — those rows are plain labels.

When adding a new field to `UFC`/`VoceDidattica`, update in lockstep: `src/modello.py`, the context dict built in `genera_documento()`, `schemas/schema_programmazione.json`, and the template's table cells.
