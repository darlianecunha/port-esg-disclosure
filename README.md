# port-esg-disclosure

**Controlled-vocabulary ESG disclosure scan for port and maritime sustainability reports, packaged as an AI agent skill (SKILL.md) and a standalone Python script.**

It measures how a report distributes its disclosure across five ESG dimensions, using the validated 398-term Portuguese/English vocabulary of a peer-reviewed study, and points out the expressions that drive each total and the ones that never appear.

## Source study

> Cunha, D. R., & Pereira, N. N. (2027). Mapping ESG evolution in Brazilian ports: A text-mining approach to sustainability reporting. *Marine Policy*, 195, 107287. https://doi.org/10.1016/j.marpol.2026.107287

The vocabulary was built from GRI, EcoPorts, SASB, ESPO and the ANTAQ Environmental Performance Index (IDA), and validated by two independent coders (90.7% agreement, Cohen's kappa 0.88) and by LDA topic modelling.

## The five ESG dimensions

| Dimension | Expressions (PT + EN) | Indicative ESRS topics |
|---|---:|---|
| Governance | 74 | ESRS 2, G1 |
| Operational Efficiency and Safety | 67 | S1 (health and safety) |
| Climate Change and Energy Transition | 87 | E1 |
| Social Responsibility and Stakeholder Engagement | 76 | S1, S2, S3, S4 |
| Port-City and Environmental Interface | 94 | E2, E3, E4, E5, S3 |

## Quick start

```bash
git clone https://github.com/darlianecunha/port-esg-disclosure
cd port-esg-disclosure
pip install pypdf            # only if Poppler's pdftotext is not installed
python3 scripts/esg_scan.py path/to/reports/ --out results/
```

Outputs:

- `dimensions_by_document.csv`: count, matches per 10,000 words and share per dimension
- `terms_by_document.csv`: count per expression, with language and dual-assignment flag
- `vosviewer_corpus.txt` (with `--vosviewer-corpus`): one normalised document per line for VOSviewer

## Use as an agent skill

Copy the folder into your agent's skills directory (for Claude Code: `~/.claude/skills/port-esg-disclosure/`). The agent reads `SKILL.md`, runs the scanner on the reports you provide and explains the distribution, the drivers and the silences.

## Example

`examples/koper_2018/` applies the scanner to the Port of Koper Sustainability Report 2018 (public report, linked, not redistributed).

## Repository structure

```
port-esg-disclosure/
├── SKILL.md                                   # agent instructions
├── scripts/esg_scan.py                        # scanner (no mandatory dependencies)
├── vocabulary/
│   ├── esg_vocabulary_pt_en.csv               # validated vocabulary, 398 expressions
│   ├── esg_vocabulary_nl_experimental.csv     # 88 Dutch terms, not validated
│   └── esrs_crosswalk.csv                     # indicative dimension-to-ESRS mapping
└── examples/koper_2018/
```

## Limits

- Frequency measures emphasis, not performance; it cannot separate commitments from risk disclaimers.
- The vocabulary was validated on Brazilian reports (2018-2024). Use on other countries is methodologically comparable, not calibrated.
- The Dutch terms and the ESRS crosswalk are the author's extensions and were not part of the validated study.
- Scanned PDFs need OCR first.

## Related tools

- [PDFWords](https://github.com/darlianecunha/textmining): open word co-occurrence networks for VOSviewer

## How to cite

Please cite the source study above. A software citation with DOI will be added on the first Zenodo release.

## Author

**Darliane Ribeiro Cunha, PhD**, researcher in sustainability governance, environmental analytics and port decarbonisation.
[ORCID 0000-0003-2548-1237](https://orcid.org/0000-0003-2548-1237)

## Licence

Code: MIT. Vocabulary files: CC BY 4.0. See `LICENSE`.
