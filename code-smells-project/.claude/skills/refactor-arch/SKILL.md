---
name: refactor-arch
description: Analyzes a backend codebase of any language/framework, audits it against a catalog of architecture, security and quality anti-patterns (severity CRITICAL/HIGH/MEDIUM/LOW with exact file:line), and refactors it to the MVC pattern while validating that the application still boots and its endpoints still respond. Use when the user asks to audit, review the architecture of, or refactor a legacy API/backend to MVC, or invokes /refactor-arch.
---

# refactor-arch — Automated Architecture Audit & MVC Refactoring

You are a senior software architect. You run **three sequential phases** on the project in the current working directory. The skill is technology-agnostic: all stack-specific knowledge lives in the reference files, never assume a stack before Phase 1 detects it.

## Reference files (load on demand)

| File | Use it in | Content |
|---|---|---|
| `references/project-analysis.md` | Phase 1 | Heuristics to detect language, framework, database, domain and current architecture |
| `references/anti-patterns-catalog.md` | Phase 2 | Anti-patterns, detection signals, severity, deprecated-API table |
| `references/report-template.md` | Phase 2 | Exact format of the audit report |
| `references/mvc-guidelines.md` | Phase 3 | Target MVC layers, responsibilities, dependency rules, target layouts per stack |
| `references/refactoring-playbook.md` | Phase 3 | Concrete before/after transformations for each anti-pattern |

Read the file for a phase **before** starting that phase. Do not skip the references.

## Ground rules

1. **Never modify, create or delete project files before the user confirms at the end of Phase 2.** Phases 1 and 2 are strictly read-only (the only allowed write is saving the report, and only if the user asks for it or a `reports/` path is given).
2. Report real evidence only: every finding needs the **exact file and line range** you actually read. Re-open the file to confirm line numbers; never estimate.
3. **Preserve the external contract**: same routes, HTTP methods, status codes and response JSON shapes, same CLI/boot command. The only allowed contract changes are security/correctness fixes catalogued in Phase 2 (e.g. stop returning password hashes, remove a remote-SQL endpoint). List every such change in the Phase 3 summary.
4. Do not add heavy dependencies. Prefer the standard library / what the framework already ships (e.g. `werkzeug.security`, Node `crypto.scrypt`). If a dependency must be added, update the manifest (`requirements.txt`, `package.json`).
5. Print the banners exactly as shown below so output is predictable and parseable.

---

## PHASE 1 — Project Analysis (read-only)

1. Read `references/project-analysis.md`.
2. Inventory the project: list source files (ignore `node_modules`, `.venv`, `venv`, `__pycache__`, `.git`, build output, `.claude`, lock files, binary files, `*.db`). Count source files and approximate lines of code.
3. Detect, using the heuristics file: **language**, **framework + version** (from the manifest), **dependencies**, **database / persistence** (engine, tables/models, how connections are created), **application domain** (infer from routes, tables, model names), **entry point** and how to boot it, and **current architecture** (layers present, where each responsibility lives).
4. Record the list of all **HTTP endpoints** (method + path) by reading the route definitions. You will need it for the Phase 3 validation and for the contract-preservation rule.
5. Print:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language + runtime version if known>
Framework:     <framework + version>
Dependencies:  <main runtime dependencies>
Domain:        <one-line domain description>
Architecture:  <current architecture in one sentence>
Source files:  <N> files analyzed (~<L> lines)
DB tables:     <tables/models, or "n/a">
Entry point:   <file + boot command>
Endpoints:     <count> (<METHOD /path>, ...)
================================
```

---

## PHASE 2 — Architecture Audit (read-only)

1. Read `references/anti-patterns-catalog.md` and `references/report-template.md`.
2. Read **every** source file fully. For each anti-pattern in the catalog, check its detection signals (use search for fast triage, then open the code to confirm and capture exact lines). Also check the **deprecated APIs** table for the detected stack.
3. Classify each confirmed finding with the catalog's severity (scale: CRITICAL / HIGH / MEDIUM / LOW). If one anti-pattern occurs in many places, produce **one finding** listing the main occurrences (`file:lines` for each) rather than dozens of duplicates; when occurrences are in clearly different modules and have different impact, split them.
4. Order findings **CRITICAL → HIGH → MEDIUM → LOW**. Within a severity keep a stable order (security first, then architecture, then quality).
5. Generate the report in the exact format of `references/report-template.md`. Minimum bar: if you find fewer than 5 findings, you have not read carefully enough — re-scan with the catalog before reporting.
6. If the user passed a destination for the report (e.g. `reports/audit-project-N.md`), save it there. This is the only file you may write in this phase.
7. **STOP and ask for confirmation.** Print exactly:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Wait for the answer. If the user answers anything other than an explicit yes, end the run without touching any project file.

---

## PHASE 3 — MVC Refactoring (only after explicit confirmation)

1. Read `references/mvc-guidelines.md` and `references/refactoring-playbook.md`.
2. **Capture a behavioural baseline before changing code**: boot the original application (see Phase 1 entry point; pick a free port if the default is taken, e.g. macOS AirPlay occupies 5000) and call every endpoint recorded in Phase 1, saving status codes and response shapes. Use a fresh/seeded database.
3. Design the target structure from the guidelines (adapt the layout to the stack's conventions; keep the original boot command working). Present the planned tree in one short block.
4. **Apply every CRITICAL recommendation in full.** Before refactoring, build a checklist from the Phase 2 report: one line per CRITICAL finding, split into one item per clause of its `Description`/`Recommendation` and per file/route/secret it lists (e.g. AP-04 → one item per unprotected write route plus the ownership rule; AP-05 → hash *and* token; AP-01 → every secret). A CRITICAL is "done" only when **all** its items are implemented; implementing only the part that is easiest (e.g. admin-only deletes while `DELETE /tasks/<id>` or `PUT /users/<id>` stay anonymous) is a failure. Keep it open while refactoring (step 5) and tick items only after validation (step 6). Do not rely on the catalog pattern alone — the report text is the source of truth. If an item is impossible without a contract decision, ask the user instead of silently dropping it.
5. Refactor in this order, running a syntax/boot check after each step:
   1. Configuration module — move every hardcoded secret/setting to env-driven config (playbook P1).
   2. Database/connection layer and **Models** — parameterized queries / ORM, no global connection, schema + seed isolated (P2, P5, P9, P13).
   3. **Services / utils** — external integrations (e-mail, payment, notifications), password hashing, shared helpers (P6, P10).
   4. **Controllers** — request flow, validation and business rules, no SQL, no framework-agnostic leaks (P4, P14, P15).
   5. **Views/Routes** — only route → controller wiring (P3).
   6. **Error handling middleware** — centralized handler, no leaking of internals (P7).
   7. **Composition root** — a small entry file that wires config, DB, routes and middlewares (P5).
   8. Replace deprecated APIs and clean low-severity items (P11–P13). Remove dead code and unused imports.
   9. Remove or protect dangerous endpoints, authenticate every write route and enforce ownership (P8 A+B+C) and delete the old monolithic files that were replaced.
6. **Validate** (mandatory, never skip, never claim success without running it):
   - Install dependencies if the manifest changed, then **boot the application** and confirm it starts without errors.
   - Call **every endpoint recorded in Phase 1** against the refactored app and compare with the baseline: same status codes and same response shapes (except the documented security/correctness changes).
   - **Verify the CRITICAL checklist item by item with real requests**, not by reading code: for authentication/authorization findings send the negative cases (no token → 401, non-owner token → 403, owner/admin token → success) for **every** write route, including password/role changes on another user (e.g. anonymous `PUT /users/<admin id>` with a new password must fail). Update the smoke/baseline scripts so they authenticate where needed.
   - Re-run the catalog against the new code (search for the detection signals: string-concatenated SQL, hardcoded secrets, `debug=True`, global state, fat controllers, deprecated calls) and confirm **zero CRITICAL/HIGH remain**.
   - If anything fails, fix and re-run the validation. Do not finish with a failing validation; if something cannot be fixed, report it explicitly as a known issue.
7. Print:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<tree>

## Contract changes (security/correctness only)
- <change and reason>   (or "none")

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly (<N>/<N>)
  ✓ CRITICAL checklist: <k>/<k> items implemented and verified (<AP-id: item>, ...)
  ✓ Zero CRITICAL/HIGH anti-patterns remaining
  ✗ <anything that failed, with detail>   (omit if everything passed)
================================
```

## Quality bar for the final result

- Config extracted, no secrets in source; models own all data access; controllers own the flow; routes only wire; one central error handler; a clear entry point.
- No behavioural regression on the original endpoints.
- Code comments only where the logic is non-obvious; keep the language/naming conventions of the original project (e.g. Portuguese domain names stay Portuguese).
