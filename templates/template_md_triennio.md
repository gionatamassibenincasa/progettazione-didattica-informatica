# Programmazione Didattica: {{ dipartimento }}

**Ordinamento:** {{ ordinamento }}  
**Indirizzo:** {{ indirizzo }}  
**Classe:** {{ classe }}  

---

## Framework di competenza e altri riferimenti

{% for id, fw in frameworks.items() %}
* **{{ fw.nome }}**: [{{ fw.url }}]({{ fw.url }})
{% endfor %}

---

## U.F.C. - UNITA’ FORMATIVE CERTIFICABILI


{% for ufc in ufcs %}
### {% if ufc.numero is string and ufc.numero.startswith('ITP') %}Laboratorio {{ ufc.numero }}{% else %} UFC {{ ufc.numero }}{% endif %}: {{ ufc.descrizione }}

#### Periodo di realizzazione
{{ ufc.periodo }}

#### Competenze disciplinari
{% for comp in ufc.competenze_disciplinari %}
- {{ comp.testo }}{% if comp.is_minimo %} **[Obiettivo Minimo]**{% endif %}
  {%- if comp.riferimenti %}
    {%- for ref in comp.riferimenti %} `[{{ ref.framework_id }}: {{ ref.codice }}]`{% endfor %}
  {%- endif %}
{% endfor %}

#### Abilità
{% for ab in ufc.abilita %}
- {{ ab.testo }}{% if ab.is_minimo %} *(Minimo)*{% endif %}
  {%- if ab.riferimenti %}
    {%- for ref in ab.riferimenti %} `[{{ ref.framework_id }}: {{ ref.codice }}]`{% endfor %}
  {%- endif %}
{% endfor %}

#### Conoscenze (contenuti)
{% for con in ufc.conoscenze %}
- {{ con.testo }}{% if con.is_minimo %} *(Minimo)*{% endif %}
  {%- if con.riferimenti %}
    {%- for ref in con.riferimenti %} `[{{ ref.framework_id }}: {{ ref.codice }}]`{% endfor %}
  {%- endif %}
{% endfor %}

{% if ufc.competenze_civica %}
#### Competenze dell'Educazione Civica
{% for comp in ufc.competenze_civica %}
- {{ comp.testo }}{% if comp.is_minimo %} **[Obiettivo Minimo]**{% endif %}
  {%- if comp.riferimenti %}
    {%- for ref in comp.riferimenti %} `[{{ ref.framework_id }}: {{ ref.codice }}]`{% endfor %}
  {%- endif %}
{% endfor %}
{% endif %}

{% if ufc.verifiche %}
#### Verifiche

| Tipo | Numero | Strumenti |
| :--- | :--- | :--- | {% for verifica in ufc.verifiche %}
| {{ verifica.tipo }} | {{ verifica.numero | replace('\n', ', ') }} | {{ verifica.strumenti | replace('\n', ', ') }} | {% endfor %}
{% endif %}

---
{% endfor %}