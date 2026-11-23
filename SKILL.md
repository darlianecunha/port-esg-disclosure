---
name: port-esg-disclosure
description: Measure how a port or maritime company's sustainability, ESG or annual report distributes its disclosure across five ESG dimensions, using a validated 398-term Portuguese/English vocabulary (Marine Policy, 2027), with an experimental Dutch extension and an indicative ESRS crosswalk. Use when asked to analyse, compare or benchmark port sustainability reports, ESG disclosure, or reporting gaps.
---

# Port ESG Disclosure Scan

Quantifies **what a port report talks about**, not how well the port performs.
Method and vocabulary come from a peer-reviewed study:

> Cunha, D. R., & Pereira, N. N. (2027). Mapping ESG evolution in Brazilian ports:
> A text-mining approach to sustainability reporting. *Marine Policy*, 195, 107287.
> https://doi.org/10.1016/j.marpol.2026.107287

## The five ESG dimensions

1. Governance
2. Operational Efficiency and Safety
3. Climate Change and Energy Transition
4. Social Responsibility and Stakeholder Engagement
5. Port-City and Environmental Interface

The vocabulary (`vocabulary/esg_vocabulary_pt_en.csv`) holds 398 expressions
(236 PT, 162 EN), built from GRI, EcoPorts, SASB, ESPO and the ANTAQ IDA and
validated by two independent coders (90.7% agreement, Cohen's kappa 0.88).

## When to use

- The user provides one or more port, terminal or shipping-company reports
  (PDF) and asks what they emphasise, what they leave out, or how they compare.
- The user asks for an ESG or CSRD-style disclosure gap check on a port report.
- The user wants a reproducible, citable method rather than an ad hoc reading.

## How to run

1. Check the reports are text PDFs. Scanned PDFs need OCR first; the script flags
   documents with fewer than 50 words per page.
2. Run the scanner (Python 3.9+, `pdftotext` from Poppler or `pip install pypdf`):

   ```bash
   python3 scripts/esg_scan.py <pdf files or folder> --out results/
   ```

   Options:
   - `--include-nl` adds 88 experimental Dutch terms (see limits below).
   - `--vosviewer-corpus` writes one normalised document per line for
     VOSviewer's "Create map based on text data".
3. Read `results/dimensions_by_document.csv` (count, per 10k words, share per
   dimension) and `results/terms_by_document.csv` (count per expression).

## How to report the results

Give the user, in this order:

1. **Distribution:** a table of the five dimensions with share and per-10k-word
   intensity. Use per-10k-word figures when comparing reports of different length.
2. **Drivers:** the 3 to 5 expressions behind each large total. A single term can
   dominate (for example "GRI" from a content index, or "noise").
3. **Silences:** relevant expressions with zero matches, especially in Climate
   Change and Energy Transition (scope 1/2/3, GHG inventory, shore power,
   targets). Absence of a term is a prompt to check the text, not proof of absence.
4. **ESRS view (optional):** map dimensions to ESRS topics with
   `vocabulary/esrs_crosswalk.csv`, stating that the crosswalk is indicative.
5. **Next check:** suggest reading the passages behind the key counts before
   drawing any conclusion.

## Matching rules (do not change silently)

- Lower-case, accents removed, hyphens to spaces, punctuation stripped.
- Word boundaries enforced; a simple plural "s" is tolerated on the last token.
- Longest expression first: multi-word expressions consume their tokens, so
  "climate change adaptation" is not also counted as "adaptation".
- "direitos humanos" and "human rights" are counted once and credited to both
  Governance and Social Responsibility, as in the paper.
- Counts use the full-expression basis (398 expressions), not the 32 canonical
  labels used for the paper's co-occurrence networks.

## Limits to state to the user

- Frequency measures emphasis, not performance or truthfulness. It cannot tell a
  commitment from a risk disclaimer; read the context before judging.
- The PT/EN vocabulary was validated on Brazilian reports (2018-2024). Results
  for other countries are comparable in method, not calibrated.
- The Dutch list is an unvalidated extension by the author. Report it separately
  or flag any figure that depends on it.
- The ESRS crosswalk is the author's indicative mapping, not part of the study.
- Reports in other languages (Spanish, French, German, Italian) are only covered
  through the English and Portuguese terms they contain.
