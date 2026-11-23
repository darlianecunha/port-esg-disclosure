# Example: Port of Koper, Sustainability Report 2018

Source report (public, published by Luka Koper d.d.; not redistributed here):
https://www.luka-kp.si/wp-content/uploads/2021/06/TRAJNOSTNO-POROCILO-2018_-ANG_26_04_2019_-OBJAVLJENO.pdf

Command:

```bash
python3 scripts/esg_scan.py Koper_2018_Sustainability_Report.pdf --out examples/koper_2018
```

Result (validated PT/EN vocabulary, full-expression basis; 168 pages, 45,859 words):

| ESG dimension | Matches | Per 10k words | Share |
|---|---:|---:|---:|
| Governance | 514 | 112.1 | 40.4% |
| Operational Efficiency and Safety | 258 | 56.3 | 20.3% |
| Climate Change and Energy Transition | 48 | 10.5 | 3.8% |
| Social Responsibility and Stakeholder Engagement | 192 | 41.9 | 15.1% |
| Port-City and Environmental Interface | 259 | 56.5 | 20.4% |

How to read it: the report gives far more space to governance and reporting
frameworks than to climate and energy transition, the same governance-over-climate
pattern found in Brazilian ports. Two checks before drawing conclusions:

- "GRI" alone accounts for 169 Governance matches, most of them from the GRI
  content index. Rerunning without the index pages, or reading the share
  without that term, is a fair robustness test.
- "noise" (155 matches) dominates the port-city dimension; the term list in
  `terms_by_document.csv` shows which expressions drive each total.

This is a single report used to demonstrate the tool. It is not a comparison
between ports and says nothing about Koper's actual performance.
