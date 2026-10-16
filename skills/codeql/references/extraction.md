# Extraction, builds, and source fidelity

Use this reference for compiled languages, failed/partial extraction, or uncertainty about database provenance. Inputs are the source root and revision, installed language support, actual build configuration/dependencies, and available execution authorization. Database creation can invoke project build commands; static analysis does not make those commands passive.

## Choose extraction intentionally

Interpreted-language extraction and compiled-language build modes differ. Inspect installed language support and matching documentation before choosing `none`, `autobuild`, or a manual command. Support for no-build extraction is language/version dependent. It can reduce build prerequisites but has limits around dependencies, generated code, and framework/type knowledge. State those limits rather than claiming equivalence to a production build.

If a build is in scope, use its real compiler, dependencies, flags, and target. An incremental build that compiles nothing may give the extractor no useful units. Capture compilation during extraction, not during an earlier unrelated build. Do not run an unknown project installer/build simply because a query needs a database.

For a CMake C/C++ project that already has a configured `build` directory, this example performs a clean rebuild under CodeQL. Replace the command only with the actual authorized build for the project:

```bash
# Set repo to the source root and out to a fresh report directory outside it.
cd "$repo"
if codeql database create "$out/db-cpp" --language=cpp \
  --source-root="$repo" --command='cmake --build build --clean-first' \
  >"$out/extraction.log" 2>"$out/extraction-errors.log"; then
  extraction_status=0
else
  extraction_status=$?
fi
printf '%s\n' "$extraction_status" >"$out/extraction-status.txt"
```

After a successful creation, confirm that the expected source units and build variant were extracted. Logs and the database's diagnostic/summary queries matter: finding a directory named `db-cpp` is insufficient. If a unit is absent, check whether the compiler actually ran, whether a wrapper/cache hid it, and whether generated source or a platform branch was omitted.

## Recover without inventing coverage

| Observation | Next decision |
|---|---|
| Build/dependency failure | Preserve logs, identify the missing prerequisite, and stop that extraction. Fixing the environment/build requires its own scope; do not analyze an older database as if it belongs to this run. |
| Creation completed but expected units are missing | Check build reuse, selected target, paths, exclusions, and extractor diagnostics. Recreate in a fresh output directory after correcting the cause. |
| Creation refuses an existing non-empty database directory ("Refusing to create database ... exists and is not an empty directory") | Re-running creation does not overwrite. Use `--overwrite` for a clean re-extraction of the same source, or a fresh database directory when the failed attempt's logs and partial state must be preserved. |
| Source changed after extraction | Treat the database as a snapshot. Re-extract for conclusions about the changed source; editing files does not update a database automatically. |
| Unsupported language/platform or missing entitlement | Report the specific gap and select an available authorized tool for that source if appropriate. A different tool's results do not become CodeQL coverage. |

Keep databases and raw logs local; they can contain source. Completion is a recorded extraction outcome with expected-source evidence and any unresolved gaps. Only then proceed to a compatible language suite.

## C#/.NET evidence continuity

Read the solution/project target frameworks and any SDK selection file before judging the available SDK. A system `dotnet` that cannot build the target framework is a mismatch for that invocation, not proof that no suitable SDK exists; for .NET this fails fast with MSBuild error NETSDK1045, which names the highest framework the installed SDK supports — treat that as a toolchain fact, not a source fact. Check prior task evidence for an already prepared toolchain. Record its absolute executable path, SDK version, source root, restore state and build configuration in the handoff; use the same toolchain for comparable before/after evidence.

Distinguish application build/test evidence from CodeQL extraction evidence. A successful earlier build does not establish that CodeQL observed compilation. Conversely, a no-build database does not prove framework behavior that depends on generated code, runtime configuration or authorization policy. State the relevant missing coverage and preserve diagnostics so another worker can assess the result without repeating environment setup.

See [preparing code for analysis](https://docs.github.com/en/code-security/tutorials/customize-code-scanning/prepare-code-for-analysis) and [build modes](https://docs.github.com/en/code-security/code-scanning/creating-an-advanced-setup-for-code-scanning/codeql-code-scanning-for-compiled-languages).
