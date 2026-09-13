---
name: feedback-flag-dont-implement-open-questions
description: "In study docs, don't bake an unresolved design decision into a concrete schema/spec even as a \"proposed default\" — flag it as open and wait for confirmation."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 945e2199-ad5f-451c-8102-3b6c36fec3b1
  modified: 2026-09-13T13:34:11.291Z
---

When a study doc raises something as an open question, don't also
silently commit to that decision elsewhere in the same doc (e.g. in a
model/schema table) before the user has actually confirmed it — even if
the choice is presented as "my proposed default."

**Why:** In [[project_digital_cafe]]'s first study doc
(`doc/study/0001-digital-cafe-mvp.md`), `CartItem` was given
`unique_together = ("user", "product")` directly in the model table —
which locks in "merge quantities on duplicate add-to-cart" at the schema
level — while the same doc's Open Questions section still listed that
exact behavior as unresolved. The user's own answer turned out to match
(merge is correct), but they explicitly called out that the schema
shouldn't have encoded the decision before it was confirmed, even in a
draft/study doc that produces no code.

**How to apply:** In study/plan docs (or any pre-implementation design
artifact), open questions should stay purely descriptive in every
section of the doc, not just their own subsection — no table row,
snippet, or diagram elsewhere in the same doc should presuppose one
answer as settled. State the proposed default in prose in the open
question itself, but leave the schema/spec generic or explicitly marked
"pending" until the user confirms. This applies at CLAUDE.md's "study"
workflow step specifically, and likely to any other planning-stage
artifact in this project.
