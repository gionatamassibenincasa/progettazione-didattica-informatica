# Programmazione Didattica DOCX Generator

Sistema di generazione automatizzata per i documenti di programmazione didattica di dipartimento (formato DOCX), basato su **Python**, **`docxtpl`**, **YAML**, **JSON Schema** e **Pydantic**.

Il sistema permette di compilare i dati della programmazione in un formato testuale semplice e strutturato (YAML), con validazione sintattica in tempo reale nell'IDE e validazione dei dati a runtime prima del popolamento del modello Microsoft Word (`.docx`). Supporta inoltre l'elaborazione batch di più documenti tramite un file di configurazione centrale.

---

## Architecture & Data Pipeline

```text
┌────────────────────────────────────────────────────────┐
│             config/documenti.yaml                      │ ◄── File di configurazione batch
│ (data_filepath, template_filepath, [output_filename])  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌─────────────────────────┐   ┌──────────────────────────┐
│data/programmazione_3_sia│   │schemas/schema_programmaz. │ ◄── Validazione IDE (VS Code)
└────────────┬────────────┘   └──────────────────────────┘
             │
             ▼
┌─────────────────────────┐
│    src/modello.py       │ ◄── Validazione Pydantic (Strong Typing)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   src/genera_doc.py     │ ◄── Pipeline di rendering Jinja2/docxtpl
└────────────┬────────────┘
             │ + templates/TEMPLATE_MOD_INS_01_B REV.02 Programm. Dipart. Triennio.docx
             ▼
┌─────────────────────────┐
│output/MOD_INS_01_B_...  │ ◄── File Word (.docx) finale compilato a 9 colonne
└─────────────────────────┘
```

---

## Struttura del Progetto

```text
.
├── config/
│   └── documenti.yaml                                     # Configurazione batch dei documenti da produrre
├── data/
│   └── programmazione_3_sia.yaml                          # File dati YAML di esempio (classe 3^ SIA)
├── docs/
│   └── riferimenti/
│       └── Target_3_SIA.docx                              # Documento di riferimento target
├── output/                                                # Documenti DOCX generati
├── schemas/
│   └── schema_programmazione.json                         # JSON Schema per autocompletamento e validazione IDE
├── src/
│   ├── genera_doc.py                                      # Script Python di orchestrazione, parsing e rendering
│   └── modello.py                                         # Modelli Pydantic (Strong Typing a runtime)
├── templates/
│   ├── TEMPLATE_MOD_INS_01_B REV.02 Programm. Dipart. Triennio.docx
│   └── TEMPLATE_MOD_INS_01_B REV.02 Programm. Dipart. Triennio-err.docx
├── README.md                                              # Documentazione di progetto
└── requirements.txt                                       # Dipendenze Python
```

---

## Requisiti e Installazione

### Prerequisites
* **Python 3.10+**
* **VS Code** con estensione **YAML (Red Hat)** consigliata per l'autocompletamento.

### Ambiente virtuale
Creare e attivare un ambiente virtuale locale prima di installare le dipendenze:

```bash
python -m venv .venv
source .venv/bin/activate
```

Su Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### Installazione Dipendenze
```bash
pip install -r requirements.txt
# oppure con uv:
uv pip install -r requirements.txt
```

Dipendenze principali:
* `docxtpl`: motore di template per documenti DOCX basato su Jinja2.
* `pydantic`: validazione e coercizione tipizzata dei dati.
* `pyyaml`: parser per file YAML.
* `python-docx`: manipolazione avanzata del formato OpenXML DOCX.

---

## Configurazione Batch (`config/documenti.yaml`)

Il file di configurazione permette di definire uno o più documenti da produrre contemporaneamente. Ciascuna voce contiene:
* `data_filepath` (*obbligatorio*): percorso del file YAML contenente i dati della programmazione.
* `template_filepath` (*obbligatorio*): percorso del modello Word (`.docx`).
* `output_filename` (*opzionale*): nome del file DOCX generato. Se non specificato, viene generato automaticamente nella forma `<nome_file_dati>_generato.docx`.

I percorsi dei job sono relativi alla directory del file di configurazione.

### Esempio `config/documenti.yaml`:
```yaml
documenti:
  - data_filepath: "../data/programmazione_3_sia.yaml"
    template_filepath: "../templates/TEMPLATE_MOD_INS_01_B REV.02 Programm. Dipart. Triennio.docx"
    output_filename: "../output/MOD_INS_01_B_REV.02_Generato.docx"
```

---

## Configurazione IDE (VS Code)

Per abilitare l'autocompletamento, il suggerimento dei campi e la segnalazione degli errori nei file YAML in tempo reale:

1. Installa l'estensione **YAML** di Red Hat in VS Code.
2. Assicurati che l'intestazione dei tuoi file `.yaml` contenga la direttiva dello schema:
   ```yaml
   # yaml-language-server: $schema=../schemas/schema_programmazione.json
   ```

---

## Modello dei Dati e Framework Supportati

Il sistema supporta il tracciamento strutturato degli obiettivi didattici:
* **Obiettivi Minimi**: flag `is_minimo: true/false` per identificare le competenze/abilità necessarie al raggiungimento della sufficienza (renderizzate con badge `[★ Minimo]`).
* **Mappatura Multi-Framework**: ogni voce può riferirsi a uno o più framework esterni (es. `DIGCOMP_3.0`, `CINI_INF`).
* **Flessibilità Voci**: ogni competenza/abilità/conoscenza può essere un oggetto dettagliato o una semplice stringa testuale.

### Esempio di Struttura Dati YAML (`data/programmazione_3_sia.yaml`)
```yaml
# yaml-language-server: $schema=../schemas/schema_programmazione.json

frameworks:
  DIGCOMP_3.0:
    nome: "Digital Competence Framework for Citizens (DigComp 3.0/2.2)"
    url: "https://joint-research-centre.ec.europa.eu/digcomp_en"
  CINI_INF:
    nome: "Indicazioni Nazionali per l'Insegnamento dell'Informatica - Consorzio CINI"
    url: "https://www.consorzio-cini.it/images/Proposta-Indicazioni-Nazionali-Informatica-Scuola-numerata.pdf"

dipartimento: "INFORMATICA"
ordinamento: "TECNICO ECONOMICO"
indirizzo: "SIA"
classe: "TERZA"

ufcs:
  - numero: 1
    descrizione: "Progettazione degli algoritmi (cap. 3)"
    periodo: "Settembre-Dicembre"
    competenze_disciplinari:
      - testo: "Acquisire il concetto di algoritmo."
        is_minimo: true
        riferimenti:
          - framework_id: "CINI_INF"
            codice: "ALG-01"
    abilita:
      - testo: "Utilizzare la pseudocodifica e i diagrammi a blocchi per rappresentare gli algoritmi."
        is_minimo: true
        riferimenti:
          - framework_id: "CINI_INF"
            codice: "ALG-02"
          - framework_id: "DIGCOMP_3.0"
            codice: "3.4"
    conoscenze:
      - testo: "Le strutture di controllo ed il Teorema di Böhm-Jacopini."
        is_minimo: true
        riferimenti:
          - framework_id: "CINI_INF"
            codice: "ALG-K02"
    competenze_civica:
      - testo: "Gestire dati, informazioni e contenuti digitali"
        is_minimo: true
        riferimenti:
          - framework_id: "DIGCOMP_3.0"
            codice: "1.3"
    verifiche_num: "1 scritta/pratica\n1 quiz"
    verifiche_strumenti: "Questionari\nVerifiche orali\nFlowgorithm"
```

---

## Regole di Struttura del Template DOCX (`docxtpl`)

Per consentire la corretta iterazione delle righe della tabella UFC preservando la suddivisione a **9 colonne**, il template Microsoft Word deve rispettare rigorosamente le convenzioni di `docxtpl`:

### Tabella UFC (Tabella 1 a 9 Colonne)
1. **Riga apertura ciclo (Riga 2)**:
   - Prima cella: `{%tr for ufc in ufcs %}` (tassativamente **senza spazio** dopo `%`).
   - L'intera riga XML viene rimossa da `docxtpl` e trasformata nell'apertura del ciclo Jinja2.
2. **Riga modello dei dati (Riga 3 - 9 colonne distinte)**:
   - Colonna 0: `{{ ufc.numero }}`
   - Colonna 1: `{{ ufc.descrizione }}`
   - Colonna 2: `{{ ufc.periodo }}`
   - Colonna 3: `{{ ufc.competenze_disciplinari }}`
   - Colonna 4: `{{ ufc.abilita }}`
   - Colonna 5: `{{ ufc.conoscenze }}`
   - Colonna 6: `{{ ufc.competenze_civica }}`
   - Colonna 7: `{{ ufc.verifiche_num }}`
   - Colonna 8: `{{ ufc.verifiche_strumenti }}`
3. **Riga chiusura ciclo (Riga 4)**:
   - Prima cella: `{%tr endfor %}` (tassativamente **senza spazio** dopo `%`).
   - L'intera riga XML viene rimossa da `docxtpl` e trasformata nella chiusura del ciclo Jinja2.

### Tabella Intestazione e Checkbox (Tabella 0)
I checkbox dinamici per la classe e l'indirizzo utilizzano la sintassi condizionale Jinja2:
* Classe: `{% if classe == 'TERZA' %}▣{% else %}☐{% endif %} TERZA`
* Indirizzo: `{% if indirizzo == 'SIA' %}▣{% else %}☐{% endif %}`

---

## Esecuzione e Generazione Documenti

Per generare i documenti utilizzando il file di configurazione predefinito (`config/documenti.yaml`):

```bash
python src/genera_doc.py
```

Per specificare un file di configurazione differente:

```bash
python src/genera_doc.py config/config_personalizzato.yaml
```

Lo script esegue automaticamente le seguenti operazioni per ogni voce:
1. Verifica l'esistenza dei file dati e template.
2. Legge e valida i dati con Pydantic (`ProgrammazioneData`).
3. Pre-formatta il testo (inclusi badge `[★ Minimo]` e codici dei framework).
4. Renderizza il template Word con `docxtpl` preservando formattazione, tabelle e stili.
5. Salva il documento finale all'interno del percorso specificato.

---

## Istruzioni per lo Sviluppo ed il Debugging con AGY (Google AntiGravity)

Se il progetto viene sviluppato o manutenuto tramite l'ambiente **AGY (Google AntiGravity)**, seguire le indicazioni sottostanti:

### 1. Linee Guida per AGY su Gestione File e Modelli
* **Validazione Statica Prima del Rendering**: AGY deve validare i modelli Pydantic prima di avviare il rendering:
  ```bash
  python -c "import sys, yaml; sys.path.insert(0, 'src'); from modello import ProgrammazioneData; data = ProgrammazioneData(**yaml.safe_load(open('data/programmazione_3_sia.yaml')))"
  ```
* **Integrità dei Tag XML OpenXML**: In Microsoft Word, i tag Jinja2 non devono essere spezzati su più elementi run `<w:r>` interni. In caso di modifiche manuali a modelli Word, verificare i tag con lo script di ispezione.
* **Sintassi `{%tr`**: Assicurarsi che i tag di riga della tabella usino `{%tr` senza spazi, altrimenti Jinja2 solleverà `TemplateSyntaxError: Encountered unknown tag 'tr'`.

### 2. Routine di Debugging Rapido

#### Test di Validazione Completa
```bash
python src/genera_doc.py config/documenti.yaml
```

#### Ispezione dei Tag Jinja2 nelle Tabelle
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
