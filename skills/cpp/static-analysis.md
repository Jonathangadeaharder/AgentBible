# C++ Static Analysis

## Tool: Cppcheck

```bash
# After editing
cppcheck --enable=all --suppress-xml --inline-suppr $FILE

# Before committing
git diff --cached --name-only --diff-filter=ACM \
  | grep -E '\.(cpp|hpp|h|cc)$' \
  | xargs cppcheck --enable=all --suppress-xml --inline-suppr --error-exitcode=1
```

## Suppression File (.cppcheck)

```xml
<?xml version="1.0"?>
<suppressions>
  <suppress>
    <id>unmatchedSuppression</id>
    <fileName>*</fileName>
  </suppress>
  <suppress><fileName>external/*</fileName></suppress>
  <suppress><fileName>vendor/*</fileName></suppress>
  <suppress><fileName>third_party/*</fileName></suppress>
</suppressions>
```

## Inline Suppression

```cpp
// cppcheck-suppress uninitvar
int x;
use(x);
```

## Check Categories

All enabled with `--enable=all`:

| Category | Description |
|----------|-------------|
| `error` | Errors (always on) |
| `warning` | Warnings |
| `style` | Style issues |
| `performance` | Performance suggestions |
| `portability` | Portability issues |
| `information` | Config info |
