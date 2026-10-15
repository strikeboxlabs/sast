# Compilation context and diagnostic recovery

Use this reference when `compile_commands.json` exists, conditional source matters, or diagnostics depend on includes/platform/library modeling. Inputs are the source tree, actual compilation database or known compiler settings, target variant, available Cppcheck version, and scan artifacts.

## Import real commands

Prefer an existing database produced by the intended build. A database from another branch, platform, or generated-source state can describe the wrong program. Check representative `directory`, `file`, and command/arguments entries against the current checkout. Cppcheck imports the settings; this invocation does not execute those compilation commands.

```bash
# Define compilation_db as its actual absolute path and out as a fresh directory.
if cppcheck --project="$compilation_db" \
  --enable=warning,performance,portability --xml --xml-version=2 \
  --error-exitcode=1 >"$out/progress.log" 2>"$out/findings.xml"; then
  scan_status=0
else
  scan_status=$?
fi
printf '%s\n' "$scan_status" >"$out/status.txt"
```

Confirm the expected source units appear in progress/report context. Importing a database does not include source files absent from that database. Header diagnostics depend on the translation units and configurations that include them.

If a new database is needed, generation is a separate build-system action. For CMake, `CMAKE_EXPORT_COMPILE_COMMANDS` applies to supported generators; build interceptors such as Bear execute a build to capture commands. Use the project's actual authorized process. Do not invent include paths or run an arbitrary build to make a warning disappear.

## Resolve configuration-dependent results

Without a database, supply the actual language standard, include search paths (`-I`), and defined/undefined macros (`-D`/`-U`) relevant to the source. Cppcheck's configuration exploration is not a guarantee that the production variant was analyzed. Overriding defines or increasing exploration with `--force` can change both coverage and cost; do it for a specific missing branch rather than as a ritual.

Use the relevant installed platform/library model only when it matches the project. A missing system header is not automatically a scan failure: Cppcheck can analyze incomplete code. Missing project definitions or library contracts can materially change a diagnostic, so inspect their effect before drawing a source conclusion.

For a disputed lifetime/bounds warning, reduce only the relevant code into disposable static input while retaining types, guards, ownership, and macro behavior. Compare the full-context and reduced diagnostics. A minimized nonmatch can lose the very condition being investigated; it does not disprove the full-project report.

If suppressions are requested, keep them narrow by diagnostic/location and explain the modeled invariant. Do not suppress a whole group to mask missing build context. Deliver the database/configuration identity, analyzed variant/units, raw report and status, reviewed defect condition, and any unresolved model gaps.

Primary reference: [compilation databases, preprocessor settings, and models](https://cppcheck.sourceforge.io/manual.html).
