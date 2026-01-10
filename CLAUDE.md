# AST-Grep Preference for Code Searches
Always prefer ast-grep over regular grep for structural code searches.
When searching for code patterns, functions, classes, or any structural elements in code:
- **USE**: `ast-grep` for structural code searches
- **AVOID**: Regular `grep` or text-based searches for code analysis
- **EXCEPTION**: Use regular grep only for searching non-code files (logs, documentation, configuration files)


## AST-Grep Command Structure
```bash
# Basic pattern matching
ast-grep --pattern '$PATTERN' --lang $LANGUAGE

# Search in specific directories
ast-grep --pattern '$PATTERN' --lang $LANGUAGE path/to/search/

# Output matching files only
ast-grep --pattern '$PATTERN' --lang $LANGUAGE --files-with-matches

# Show context around matches
ast-grep --pattern '$PATTERN' --lang $LANGUAGE -A 3 -B 3
```

## Common Patterns:
JavaScript/TypeScript:
- Functions: `ast-grep --pattern 'function $NAME($$$PARAMS) { $$$BODY }' --lang javascript`
- React: `ast-grep --pattern 'const $NAME = ($$$PROPS) => { $$$BODY }' --lang typescript`
- Imports: `ast-grep --pattern 'import $IMPORT from "$MODULE"' --lang javascript`

Python:
- Functions: `ast-grep --pattern 'def $NAME($$$PARAMS): $$$BODY' --lang python`
- Classes: `ast-grep --pattern 'class $NAME($$$BASES): $$$BODY' --lang python`

Go:
- Functions: `ast-grep --pattern 'func $NAME($$$PARAMS) $TYPE { $$$BODY }' --lang go`
- Structs: `ast-grep --pattern 'type $NAME struct { $$$FIELDS }' --lang go`

Rust:
- Functions: `ast-grep --pattern 'fn $NAME($$$PARAMS) -> $TYPE { $$$BODY }' --lang rust`
- Structs: `ast-grep --pattern 'struct $NAME { $$$FIELDS }' --lang rust`

NOTE: Always specify --lang parameter. Use $VAR for single matches, $$$VAR for multiple.



