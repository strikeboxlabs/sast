# Develop and test a rule

Use this reference to encode a recurring source defect or diagnose a rule regression. Inputs are the source idiom, language, expected unsafe condition, and at least one nearby safe variant. First distinguish a structural API check from a claim about untrusted data reaching that API.

## Pattern rule and paired tests

The package includes `assets/rules/python-shell-enabled.yaml` and `assets/rules/python-shell-enabled.py`. Set `skill_dir` to the installed folder containing this SKILL.md; it is independent of the source checkout. The rule reports two Python subprocess APIs when their `shell` argument is literally true. It requests review of that API choice; it does not establish that an attacker controls the command.

```bash
# Set skill_dir to this installed skill folder; do not execute the Python fixture.
semgrep scan --test --metrics=off --disable-version-check \
  "$skill_dir/assets/rules"
```

The paired test annotations mark expected matches with `ruleid:` and expected nonmatches with `ok:` immediately above the relevant line. Keep test and rule basenames aligned. A passing result proves only the annotated cases under that engine. The fixture is static input and must not be imported or run.

For a project-specific rule, copy the pair into the task's rules directory, change the rule ID and assumptions, and add expected matches and nonmatches before applying it broadly. Use `// ruleid: actual-rule-id` and `// ok: actual-rule-id` for C# fixtures. Prefer the annotated test runner so unexpected matches and missed expectations fail the check; a plain scan plus a result count does not assert the annotations. Report the expectations actually checked for each rule. A fixture for one rule does not validate the other rules in a combined configuration.

Distinguish expected matches from unsafe examples: a structural concatenation rule may intentionally match trusted constants, so a positive fixture need not represent injection. Test aliases, keyword ordering and wrappers where the actual source needs them. A check that passes these tests may still miss a different wrapper or report unrelated APIs.

If the annotated runner cannot execute, preserve that failure. A local fixture scan with explicit assertions comparing rule IDs and source locations to all expected matches/nonmatches can provide a narrower check. Record that method and its limits; do not label a raw match count as a passing annotated test.

If a newly written rule is invalid, use the installed validator to distinguish YAML/schema failure from a valid pattern matching the wrong node. The validation mode may retrieve lint rules; it is not an offline guarantee:

```bash
# Set rules to the new rule file or directory.
semgrep scan --validate --config "$rules" --metrics=off --disable-version-check
```

## Diagnose matching before blaming the engine

`metavariable-regex` is left anchored: it attempts a match at the start of the captured text. A regex for a substring needs to account for the prefix, for example `.*Prelude` rather than `Prelude` when that word is inside a captured call expression. Quotes are part of a captured string literal. An expression not starting with `+` should not match a bare `\+` regex; that alone is not an engine defect. Structural patterns are often clearer for operators. See the [documented operator semantics](https://docs.semgrep.dev/writing-rules/rule-syntax#metavariable-regex).

For a surprising nonmatch, first inspect the captured value and isolate the pattern from its filters in a harmless static fixture. For C# assignment statements, check the complete statement form including the semicolon; distinguish a syntactically accepted pattern from one that matches the intended node. Confirm the installed CLI options with help instead of repeatedly trying guessed flags. Keep diagnostic outputs separate and change one relevant condition at a time. Record an unresolved limitation if a minimal case remains unexplained; do not turn an unverified explanation into a reusable engine restriction.

## When taint tracking is the right model

Use `mode: taint` when the bug depends on a value moving from an identified input to a sensitive operation. Specify `pattern-sources` and `pattern-sinks`; narrow them to the actual data-bearing expression/argument. Add sanitizers only after verifying that they establish the required invariant for that sink. Escaping for one context is not automatically safe in another.

Begin with a same-function positive flow and a safe control. Add a case where the apparent sanitizer validates the wrong value, plus a case where the value crosses a wrapper if that matters to the request. Read the installed edition's dataflow limitations before claiming that a nonmatch across files/functions proves safety. If a test cannot be represented faithfully, retain the limitation rather than weakening the unsafe case until it passes.

When results are surprising, inspect source/sink matching independently, then propagation and sanitization. Review rule findings manually before proposing a CI gate. Deliver the rule, regression inputs, actual test outcome, assumptions, and known gaps. Source fixes and rule suppressions are separate deliverables.

Primary references: [rule tests](https://docs.semgrep.dev/writing-rules/testing-rules), [taint analysis](https://docs.semgrep.dev/writing-rules/data-flow/taint-mode/overview), and [pattern syntax](https://docs.semgrep.dev/writing-rules/pattern-syntax).
