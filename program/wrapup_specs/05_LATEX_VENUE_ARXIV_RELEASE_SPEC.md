# LaTeX, PDF, Venue, arXiv, and Artifact Specification

## 1. Do not use the generic article template as the submission template

A generic document beginning with `\documentclass{article}` plus `geometry`, custom fonts, and custom margins is acceptable for a private report, but it is **not reliable for venue submission**. Use the current official venue template without modifying margins, fonts, spacing, heading sizes, or page geometry.

Build common content in shared section files and separate top-level wrappers:

```text
paper/
  sections/
    abstract.tex
    introduction.tex
    related_work.tex
    method.tex
    data.tex
    experiments.tex
    results.tex
    analysis.tex
    limitations.tex
    ethics.tex
    conclusion.tex
  tables/generated/
  figures/generated/
  references.bib
  macros.tex
  venue/main.tex
  arxiv/main.tex
```

Never fork the prose into two diverging versions. Wrapper differences should be identity, disclosure placement, metadata, and venue-specific required sections.

## 2. P1 TMLR wrapper

Clone the current official TMLR style repository. Begin from its `main.tex`. The core form is:

```tex
\documentclass[10pt]{article}
\usepackage{tmlr} % anonymous review
% \usepackage[preprint]{tmlr}  % identified arXiv version
% \usepackage[accepted]{tmlr}  % accepted camera ready only

\input{macros.tex}
\usepackage{hyperref}
\usepackage{url}

\title{ToolMorph: Testing and Restoring Semantic Interface Invariance in Tool-Using Agents}

\author{...} % hidden automatically in anonymous mode; populated for preprint
\def\month{MM}
\def\year{YYYY}
\def\openreview{\url{https://openreview.net/forum?id=XXXX}}

\begin{document}
\maketitle
\input{sections/abstract}
...
\bibliography{references}
\bibliographystyle{tmlr}
\appendix
...
\end{document}
```

Rules:

- use official `tmlr.sty` and `tmlr.bst`;
- do not edit the style file;
- anonymous review uses `\usepackage{tmlr}`;
- arXiv uses `[preprint]`;
- only accepted camera-ready uses `[accepted]`;
- include the required first-page LLM/AI-assistance footnote in a manner compatible with anonymity and current TMLR policy;
- keep main content near or below 12 pages when possible because longer papers can review more slowly, but never omit necessary evidence merely to hit an arbitrary length.

## 3. P2 FSE 2027 wrapper

Use the current ACM `acmart` template and the FSE-required class:

```tex
\documentclass[acmsmall,screen,review,anonymous]{acmart}

\setcopyright{none} % only if the official review template/instructions permit; verify current sample
\acmConference[FSE 2027]{ACM International Conference on the Foundations of Software Engineering}{2027}{...}

\begin{document}
\title{CrossCheck: When Does Heterogeneous Model Review Improve Coding-Agent Patches?}
\author{Anonymous Author(s)}
\begin{abstract}
\input{sections/abstract}
\end{abstract}
\keywords{coding agents, code review, software testing, large language models}
\maketitle
...
\section{Data Availability}
An anonymized replication package is provided ...
\bibliographystyle{ACM-Reference-Format}
\bibliography{references}
\end{document}
```

Do not blindly copy metadata commands; start from the latest official `sample-acmsmall-conf.tex` and the FSE CFP. Required current constraints include:

- `acmsmall,screen,review,anonymous`;
- single-column review layout;
- at most 18 pages for text/figures plus 4 reference pages for initial submission;
- heavy double-anonymous review;
- a `Data Availability` section after the Conclusion;
- complete disclosure of generative-AI-created content under current ACM policy;
- no author-revealing repository link in the anonymized paper/package.

For an identified arXiv version, create a separate wrapper that removes `review,anonymous`, restores author metadata, and adds the public repository link. Do not make the arXiv version say “submitted to FSE.”

## 4. P3 TACL wrapper

Download the current official files from TACL:

```text
tacl2021v1.sty
acl_natbib.bst
tacl2021v1-template.tex
```

Begin from the official template and preserve all layout settings. Do not approximate the style with `geometry` or an ACL conference template.

Maintain:

- an anonymous TACL review wrapper with no author names, affiliations, acknowledgments, identifying repository links, PDF author metadata, or revealing self-citations;
- an identified arXiv wrapper using the same section sources;
- a TACL comments-to-editor record disclosing any arXiv preprint title, URL, server, and date;
- no dual submission;
- no supplementary-material link in the review manuscript when prohibited by current TACL rules;
- anonymous text stating the intended data/code release.

If P3 is routed to ARR instead of TACL, create a separate official ACL-style wrapper, respect the eight-page long-paper content limit, mandatory Limitations section, double-column appendix rules, and Responsible NLP Checklist. Never use TACL and ARR review simultaneously.

## 5. Citation system

Use BibTeX/natbib in the form required by each venue:

- narrative: `\citet{key}`;
- parenthetical: `\citep{key}`;
- multiple sources: `\citep{key1,key2}`;
- never cite a raw URL in place of a scholarly reference;
- include DOI and arXiv/eprint fields where appropriate;
- use title case/bracing carefully for model names and acronyms;
- deduplicate preprint and published versions; cite the archival version where it exists.

Create `citation_ledger.csv` columns:

```text
bibkey,title,authors,year,venue,doi_or_arxiv,primary_source_url,
claim_supported,source_location,verified_by_human,verified_date,
retraction_checked,notes
```

The Citation Auditor must:

1. open every source;
2. check every metadata field;
3. verify the cited sentence is supported;
4. detect citations to superseded versions;
5. run duplicate-key and unused-reference checks;
6. flag any bibliography item generated only from model memory.

## 6. Figure and table standards

- Prefer vector PDF figures generated by scripts.
- Use fonts embedded in the PDF.
- Make figures readable in grayscale and for common color-vision deficiencies.
- Use no decorative 3D charts.
- Show raw or paired distributions when sample size permits, not only bars.
- Include uncertainty visually.
- Every figure has a concise self-contained caption stating sample/unit and interval type.
- Every table states unit, direction, uncertainty, and whether values are exploratory or confirmatory.
- Use `booktabs`; avoid vertical lines.
- Do not shrink text below venue rules.
- Do not put a figure on TACL's final first page if current final-production rules forbid it.

## 7. Compilation pipeline

Use a clean TeX Live environment matching arXiv support, preferably TeX Live 2025 unless a venue template requires otherwise.

Commands:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex
latexmk -c
```

Run:

- `chktex` with a documented suppression file;
- unresolved citation/reference scan;
- `pdftotext` scan for `??`, `TODO`, `FIXME`, `Anonymous` in identified version, author names in anonymous version, and accidental prompt text;
- `pdfinfo` metadata audit;
- `pdffonts` to reject Type 3/unembedded fonts;
- overfull/underfull box audit;
- page-count check;
- link check;
- spelling/grammar check that does not alter technical meaning;
- clean-container rebuild and PDF checksum.

No source package may contain:

- `.aux`, `.log`, `.out`, `.synctex`, editor backups;
- private notes or comments;
- prompt transcripts;
- secrets/tokens;
- local absolute paths;
- author metadata in anonymous packages;
- unused figures/data;
- reviewer simulations or confidential memos.

## 8. Abstract construction

Write the abstract last, in one paragraph unless venue rules say otherwise. It must contain:

1. problem and why it matters;
2. exact gap;
3. method/dataset;
4. study scale described truthfully;
5. principal result with an effect and uncertainty when space permits;
6. bounded conclusion.

Never write `state-of-the-art` without a complete and fair comparison. Never include a number not generated by the final analysis script.

## 9. arXiv packaging

arXiv prefers TeX source when TeX exists. Build a minimal source archive containing:

- top-level `main.tex`;
- used section files;
- `references.bib` and/or correct `.bbl` as required;
- required venue/style files when redistribution is allowed;
- used figure files;
- used macro files;
- no extraneous outputs or private comments.

Requirements:

- safe ASCII filenames with consistent case;
- one clear top-level TeX file;
- compile in a clean TeX Live 2025 container;
- inspect arXiv-generated PDF, not only local PDF;
- verify title, abstract, authors, categories, comments, and license manually;
- do not use `\today` if a rebuild-changing date is undesirable;
- ensure all code/data links are already public and resolve;
- human chooses the permanent arXiv license;
- human presses submit.

Suggested categories, subject to human confirmation:

- P1: primary `cs.AI` or `cs.LG` based on final emphasis;
- P2: primary `cs.SE`, optional `cs.AI` cross-list;
- P3: primary `cs.CL`, optional `cs.AI` cross-list.

Do not post a preprint merely to create the appearance of completion. Recommend arXiv only when the paper is internally coherent, citation-audited, and unlikely to require a reversal of its central claim.

## 10. Anonymous versus public artifacts

### Anonymous package

- scrub git history or create a clean export;
- remove usernames, emails, organization names, GitHub URLs, local paths, model account IDs, and author-linked DOI/Zenodo metadata;
- use neutral repository/project identifiers;
- include exact reproduction instructions;
- test all links for identity leakage;
- zip and hash.

### Public package draft

- author identities and real repository URL;
- LICENSE and data licenses selected/approved by human;
- CITATION.cff;
- release notes;
- frozen tag;
- checksums;
- code of conduct/security notice as relevant;
- artifact DOI plan, if later desired;
- no secrets or redistributable-prohibited data.

## 11. Final PDF quality gate

A paper is not deliverable until:

- compilation has zero errors and no unresolved references;
- page limit and anonymity pass;
- all fonts are embedded;
- figures are legible at 100%;
- all main values match `RESULTS_MANIFEST.json`;
- every citation passes the ledger audit;
- Limitations/Ethics/Data Availability/AI disclosure are present as required;
- independent reproducer can regenerate all main tables and figures;
- Reviewer 2's fatal concerns are resolved or explicitly limit the claim.
