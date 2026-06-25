# Human Authorship, AI Assistance, and Final Sign-Off

## 1. Do not make a false disclosure

Do not write that Claude/Codex were used only for grammar if they also assisted with literature discovery, code generation, experiment orchestration, debugging, statistical scripts, tables, or prose. The disclosure must match the actual workflow.

Do not overcorrect by saying the models originated the scientific claims if the human principal investigator selected, approved, audited, and takes responsibility for them. Authorship is based on genuine human intellectual responsibility and accountability, not on who typed the first draft.

## 2. Baseline truthful disclosure text

Adapt this to each venue and to the actual record:

> Generative AI tools, including Anthropic Claude Code and OpenAI Codex, were used as assistive tools for literature discovery, code generation, experiment orchestration, debugging, statistical scripting, internal review, and prose drafting. The human author selected and approved the research questions, experimental designs, inclusion and exclusion rules, interpretations, and final scientific claims; reviewed the key raw outputs and generated analyses; verified the cited sources; and assumes full responsibility for the work. No model was listed as an author or treated as ground truth. Reported tables and figures were generated from auditable experiment ledgers and deterministic analysis scripts.

Modify any clause that is not literally true. For example, do not say every citation was human-verified until the human has actually completed that audit.

## 3. Venue placement

- **TMLR:** include the explicit first-page footnote required by current TMLR policy; preserve anonymity while accurately identifying the class of tools and scope of assistance.
- **FSE/ACM:** fully disclose generative-AI-created content under current ACM authorship policy. Include a non-identifying disclosure in the anonymous manuscript where required and a complete Acknowledgments disclosure in the identified version.
- **ARR/ACL:** complete the Responsible NLP Checklist accurately and describe writing/coding assistance in Acknowledgments/README as required.
- **TACL:** follow current ACL/TACL ethics and authorship rules; include a transparent disclosure in the appropriate non-identifying location and complete any editorial metadata honestly.
- **arXiv:** include the identified disclosure in the manuscript or a clearly visible reproducibility/acknowledgment statement.

## 4. Human intellectual contribution record

Create `HUMAN_CONTRIBUTION_RECORD.md` with dated entries for:

- initial research ideas and motivations;
- acceptance/rejection of candidate hypotheses;
- dataset/oracle design decisions;
- primary endpoint and kill-gate approval;
- interpretation of key failures/counterexamples;
- changes made after red-team review;
- final claim approval;
- authorship and venue decisions.

This is not performative paperwork. It should truthfully document human control and responsibility.

## 5. Human verification checklist

The final human author must personally:

1. Read each manuscript from beginning to end.
2. Open every cited source and verify the citation ledger.
3. Inspect all primary tables against generated files and ledger records.
4. Inspect a stratified sample of at least 10% of raw traces plus every major failure category and every excluded case.
5. Verify that no method accesses sealed labels or gold outputs.
6. Review task/data licenses and redistribution terms.
7. Approve the exact author list, order, affiliations, conflicts, funding, and acknowledgments.
8. Approve the AI-assistance disclosure as factually complete.
9. Approve limitations, ethics, and broader-impact statements.
10. Verify anonymity of review PDFs and artifacts.
11. Verify there is no overlapping archival submission.
12. Choose the arXiv license and check metadata.
13. Perform the final external submission/posting action.

Claude must not mark these steps complete merely because it thinks they are likely complete. It may prepare evidence and checklists; the human marks them.

## 6. Submission decision rubric

### `SUBMIT_READY`

All of the following:

- core claim survives confirmatory controls;
- method is end-to-end and no-gold where claimed;
- strongest baseline is fairly implemented;
- held-out generalization exists;
- uncertainty is reported;
- novelty survives a current-date audit;
- independent reproduction passes;
- paper and artifact pass venue rules;
- human signs all required checks.

### `ARXIV_ONLY`

- coherent, useful, and reproducible result;
- claims are honest and bounded;
- one or more top-tier requirements remain unmet;
- posting now would not mislead readers or permanently anchor a false central claim.

### `HOLD`

- promising direction but missing required evidence/resources/annotation;
- no pressure to post a weak PDF.

### `KILL`

- claim falsified or contribution subsumed;
- result irreparably confounded;
- full study is not worth the expected resource cost.

## 7. Final handoff from Claude

Claude's final report must not say “submitted.” It must say one of:

- `READY FOR HUMAN SUBMISSION TO [VENUE]`;
- `READY FOR HUMAN ARXIV REVIEW/POSTING`;
- `HOLD — [BLOCKERS]`;
- `KILL — [EVIDENCE]`.

For each paper, provide the exact local paths to:

- review PDF;
- arXiv PDF;
- source archives;
- anonymous artifact;
- public artifact draft;
- decision memo;
- human sign-off checklist;
- checksums.
