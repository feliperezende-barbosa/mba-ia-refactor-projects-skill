# Audit Report Template (Phase 2)

Generate the report **exactly** in this structure. Replace everything in `<angle brackets>`. Language of descriptions: the user's language (Portuguese or English); keep headings and severity tags in English.

````markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project folder name>
Stack:   <Language> + <Framework> <version>
Files:   <N> analyzed | ~<L> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <AP-id> <Short title>
File: <path>:<start>-<end>   (add `, <path>:<lines>` for further occurrences)
Description: <what is wrong, referencing the real code (name, value, function)>
Impact: <concrete consequence for security/maintainability/performance>
Recommendation: <concrete fix, referencing the playbook pattern, e.g. "Use parameterized queries (P2)">

### [CRITICAL] ...

### [HIGH] ...

### [MEDIUM] ...

### [LOW] ...

================================
Total: <N> findings
================================
````

## Rules

1. **Order**: all CRITICAL first, then HIGH, MEDIUM, LOW.
2. **Every finding must contain** `File` with exact line numbers (`file.py:42` or `file.py:10-35`), `Description`, `Impact`, `Recommendation`. No finding without a file and lines.
3. **Line numbers must be verified** by reading the file; for multi-location findings list the main occurrences (up to ~4) separated by commas.
4. The summary counts must match the number of findings by severity, and `Total` must equal their sum.
5. Include a finding for **deprecated APIs** whenever any is present (AP-17); if none exist, add a line `Deprecated APIs: none detected` right after the summary.
6. Minimum 5 findings, containing at least one CRITICAL or HIGH. If you cannot reach that, re-read the sources with the catalog before reporting.
7. Titles use the catalog name (e.g. "SQL Injection"), optionally followed by the specific symptom.
8. The report ends with the confirmation prompt (outside the report block):

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Example finding

```markdown
### [CRITICAL] AP-02 SQL Injection
File: models.py:28-33, models.py:111-113, models.py:272-282
Description: Queries are built by concatenating request data (`"... WHERE email = '" + email + "'"`), including the login query.
Impact: An attacker can bypass authentication (`' OR '1'='1`) and read or destroy any table.
Recommendation: Use parameterized queries (`cursor.execute("... WHERE email = ?", (email,))`) — playbook P2.
```
