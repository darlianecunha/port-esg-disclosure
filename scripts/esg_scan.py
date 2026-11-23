#!/usr/bin/env python3
"""
esg_scan.py - Controlled-vocabulary ESG disclosure scan for port reports.

Implements the matching rules of:
  Cunha, D. R., & Pereira, N. N. (2027). Mapping ESG evolution in Brazilian
  ports: A text-mining approach to sustainability reporting. Marine Policy,
  195, 107287. https://doi.org/10.1016/j.marpol.2026.107287

Rules reproduced from the paper:
  * text and terms are lower-cased, accents removed, hyphens turned into
    spaces and punctuation stripped before matching;
  * word boundaries are enforced and a simple plural ("s") is tolerated on
    the last token of each expression;
  * longest expression first: a multi-word expression consumes its tokens
    before shorter expressions are tested, so each surface occurrence is
    counted once;
  * the two dual-assigned terms ("direitos humanos", "human rights") are
    counted once and credited to both dimensions, as in the paper.

Counts are on the full-expression basis (398 expressions), not on the
32 canonical labels used for the paper's co-occurrence networks.

The script measures how much a report talks about each ESG dimension. It
does not measure performance, and frequency alone cannot tell a commitment
from a risk disclaimer.

Usage:
  python3 esg_scan.py REPORT.pdf [MORE.pdf | FOLDER ...] --out results/
  python3 esg_scan.py reports/ --include-nl --out results/

Text extraction uses `pdftotext` (Poppler) when available, otherwise pypdf.
Scanned (image-only) PDFs need OCR first.
"""

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
VOCAB_DIR = os.path.join(HERE, "..", "vocabulary")
DEFAULT_VOCAB = os.path.join(VOCAB_DIR, "esg_vocabulary_pt_en.csv")
NL_VOCAB = os.path.join(VOCAB_DIR, "esg_vocabulary_nl_experimental.csv")

DIMENSIONS = [
    "Governance",
    "Operational Efficiency and Safety",
    "Climate Change and Energy Transition",
    "Social Responsibility and Stakeholder Engagement",
    "Port-City and Environmental Interface",
]

LOW_TEXT_WORDS_PER_PAGE = 50


# --- normalisation and patterns (same logic as the paper's pipeline) -------

def normalize_text(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[-–—−‑]", " ", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def plural_friendly_pattern(norm_term: str) -> str:
    tokens = norm_term.split()
    if not tokens:
        return ""
    escaped = [re.escape(t) for t in tokens]
    if not tokens[-1].endswith("s"):
        escaped[-1] += "s?"
    return r"(?<!\w)" + r"\s+".join(escaped) + r"(?!\w)"


# --- vocabulary --------------------------------------------------------------

def load_vocabulary(paths):
    """Return a list of entries grouped by normalised term:
    [{'norm', 'pattern', 'terms': [(dimension, language, term), ...]}]"""
    grouped = {}
    for path in paths:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                dim = row["dimension"].strip()
                if dim not in DIMENSIONS:
                    sys.exit(f"Unknown dimension '{dim}' in {path}")
                term = row["term"].strip()
                norm = normalize_text(term)
                if not norm:
                    continue
                entry = grouped.setdefault(norm, {"norm": norm, "terms": []})
                entry["terms"].append((dim, row["language"].strip(), term))
    entries = list(grouped.values())
    for e in entries:
        e["pattern"] = re.compile(plural_friendly_pattern(e["norm"]))
    # longest expression first: more tokens, then more characters
    entries.sort(key=lambda e: (-len(e["norm"].split()), -len(e["norm"])))
    return entries


# --- text extraction -------------------------------------------------------

def extract_text(pdf_path):
    """Return (text, pages)."""
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", "-q", pdf_path, "-"],
                             capture_output=True, text=True, errors="ignore")
        text = out.stdout
        pages = text.count("\f") or 1
        if text.strip():
            return text, pages
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("Install Poppler (pdftotext) or `pip install pypdf`.")
    reader = PdfReader(pdf_path)
    texts = [(p.extract_text() or "") for p in reader.pages]
    return "\n".join(texts), len(reader.pages)


# --- counting --------------------------------------------------------------

def scan(text, entries):
    """Longest-first matching. Returns {norm_term: count} and word count."""
    work = normalize_text(text)
    words = len(work.split())
    counts = {}
    for e in entries:
        hits = e["pattern"].findall(work)
        if hits:
            counts[e["norm"]] = len(hits)
            # consume matched tokens so shorter expressions cannot reuse them
            work = e["pattern"].sub(lambda m: " " * len(m.group(0)), work)
    return counts, words


def collect_pdfs(inputs):
    pdfs = []
    for p in inputs:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                pdfs += [os.path.join(root, f) for f in sorted(files)
                         if f.lower().endswith(".pdf")]
        elif p.lower().endswith(".pdf"):
            pdfs.append(p)
    return pdfs


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="PDF files or folders")
    ap.add_argument("--out", default="esg_results", help="output folder")
    ap.add_argument("--vocab", default=DEFAULT_VOCAB,
                    help="validated PT/EN vocabulary (default)")
    ap.add_argument("--include-nl", action="store_true",
                    help="add the experimental Dutch terms (not validated)")
    ap.add_argument("--vosviewer-corpus", action="store_true",
                    help="write normalised text, one document per line, for "
                         "VOSviewer 'Create map based on text data'")
    args = ap.parse_args()

    vocab_paths = [args.vocab] + ([NL_VOCAB] if args.include_nl else [])
    entries = load_vocabulary(vocab_paths)
    pdfs = collect_pdfs(args.inputs)
    if not pdfs:
        sys.exit("No PDF found.")
    os.makedirs(args.out, exist_ok=True)

    doc_rows, term_rows, corpus = [], [], []
    for pdf in pdfs:
        name = os.path.basename(pdf)
        text, pages = extract_text(pdf)
        counts, words = scan(text, entries)
        dim_totals = defaultdict(int)
        for e in entries:
            c = counts.get(e["norm"], 0)
            dims = sorted({d for d, _, _ in e["terms"]})
            for d in dims:
                dim_totals[d] += c
            for d, lang, term in e["terms"]:
                term_rows.append({"document": name, "dimension": d,
                                  "language": lang, "term": term, "count": c,
                                  "dual_assigned": "yes" if len(dims) > 1 else ""})
        total = sum(dim_totals[d] for d in DIMENSIONS)
        row = {"document": name, "pages": pages, "words": words,
               "low_text_warning": "yes" if words / max(pages, 1) < LOW_TEXT_WORDS_PER_PAGE else ""}
        for d in DIMENSIONS:
            row[f"{d} | count"] = dim_totals[d]
            row[f"{d} | per 10k words"] = round(dim_totals[d] / words * 1e4, 2) if words else 0
            row[f"{d} | share %"] = round(dim_totals[d] / total * 100, 1) if total else 0
        doc_rows.append(row)
        if args.vosviewer_corpus:
            corpus.append(normalize_text(text))
        flag = "  [low text: scanned PDF?]" if row["low_text_warning"] else ""
        print(f"{name}: {pages} pages, {words} words, {total} matches{flag}")

    def write(fname, rows):
        with open(os.path.join(args.out, fname), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    write("dimensions_by_document.csv", doc_rows)
    write("terms_by_document.csv", term_rows)
    if corpus:
        with open(os.path.join(args.out, "vosviewer_corpus.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(corpus) + "\n")
    print(f"Results written to {args.out}/")


if __name__ == "__main__":
    main()
