# C# Static Analysis

## Tools

- **dotnet format** — Code formatting (built into .NET SDK 6.0+)
- **Roslyn Analyzers** — Code quality (built into compiler)

## Commands

```bash
# After editing
dotnet format --verify-no-changes --include $FILE

# Before committing
dotnet format --verify-no-changes
```

## .editorconfig

```ini
root = true

[*.cs]
indent_size = 4
tab_width = 4
end_of_line = crlf

dotnet_sort_system_directives_first = true
csharp_style_var_for_built_in_types = true:suggestion
csharp_prefer_braces = true:warning
csharp_style_namespace_declarations = file_scoped:warning
```

## Directory.Build.props

```xml
<Project>
  <PropertyGroup>
    <EnableNETAnalyzers>true</EnableNETAnalyzers>
    <AnalysisMode>Recommended</AnalysisMode>
    <AnalysisLevel>latest</AnalysisLevel>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <LangVersion>latest</LangVersion>
  </PropertyGroup>
</Project>
```

## Inline Suppression

```csharp
#pragma warning disable CA1031
try { DoWork(); }
catch (Exception ex) { Log(ex); }
#pragma warning restore CA1031
```

## Per-file Suppression

```ini
[Tests/**/*.cs]
dotnet_diagnostic.CA1707.severity = none
```
