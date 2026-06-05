"""
Deploy agent guidelines to Windsurf
- Workflows → ~/.codeium/windsurf/workflows/
- Language skills → ~/.codeium/windsurf/rules/ with glob triggers
- Global rules → ~/.codeium/windsurf/rules/global_rules.md
"""

import os
import sys
from pathlib import Path


def get_windsurf_dir():
    """Get Windsurf config directory"""
    if sys.platform == "win32":
        userprofile = os.environ.get("USERPROFILE")
        if not userprofile:
            print("Error: USERPROFILE environment variable not found")
            sys.exit(1)
        return Path(userprofile) / ".codeium" / "windsurf"
    elif sys.platform == "darwin":
        return Path.home() / ".codeium" / "windsurf"
    else:
        return Path.home() / ".codeium" / "windsurf"


def create_workflow_files(workflows_dir):
    """Create workflow files from workflows/ folder"""
    source_dir = Path("workflows")
    if not source_dir.exists():
        print(f"Warning: {source_dir} not found, skipping workflow files")
        return

    count = 0
    for md_file in source_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        output_name = md_file.stem.lower() + ".md"
        output_path = workflows_dir / output_name

        # Windsurf workflow format
        workflow_content = f"---\nauto_execution_mode: 3\n---\n\n{content}"
        output_path.write_text(workflow_content, encoding="utf-8")

        print(f"  ✓ {output_name}")
        count += 1

    print(f"\nCreated {count} workflow files")


def create_language_rule_files(rules_dir, languages):
    """Create language-specific rule files from skills/"""
    lang_config = {
        "csharp": {
            "folder": "skills/csharp",
            "description": "C# development guidelines and best practices",
            "globs": ["*.cs", "*.csx", "*.csproj"],
            "files": [
                "clean-code.md",
                "patterns.md",
                "testing.md",
                "static-analysis.md",
                "parallel.md",
                "ipc.md",
            ],
        },
        "cpp": {
            "folder": "skills/cpp",
            "description": "C++ development guidelines and best practices",
            "globs": ["*.cpp", "*.hpp", "*.h", "*.cc", "*.cxx"],
            "files": [
                "clean-code.md",
                "patterns.md",
                "testing.md",
                "static-analysis.md",
                "parallel.md",
                "ipc.md",
            ],
        },
        "python": {
            "folder": "skills/python",
            "description": "Python development guidelines and best practices",
            "globs": ["*.py", "*.pyx", "*.pyi"],
            "files": [
                "clean-code.md",
                "patterns.md",
                "testing.md",
                "static-analysis.md",
                "parallel.md",
                "ipc.md",
            ],
        },
        "react": {
            "folder": "skills/react",
            "description": "React/JavaScript development guidelines and best practices",
            "globs": ["*.jsx", "*.tsx", "*.js", "*.ts", "*.mjs", "*.cjs"],
            "files": [
                "clean-code.md",
                "patterns.md",
                "testing.md",
                "static-analysis.md",
                "parallel.md",
                "ipc.md",
            ],
        },
    }

    count = 0
    for lang in languages:
        lang_key = lang.lower()
        if lang_key not in lang_config:
            print(f"Warning: Unknown language '{lang}', skipping")
            continue

        config = lang_config[lang_key]
        lang_dir = Path(config["folder"])

        if not lang_dir.exists():
            print(f"Warning: {lang_dir} not found, skipping")
            continue

        merged_content = f"# {lang_key.title()} Development Guidelines\n\n"
        for filename in config["files"]:
            file_path = lang_dir / filename
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                section_name = filename.replace(".md", "").replace("-", " ").title()
                merged_content += f"\n## {section_name}\n\n{content}\n"
                merged_content += "\n---\n\n"

        output_name = f"{lang_key}_rules.md"
        output_path = rules_dir / output_name

        globs_str = "\n".join(f"  - {glob}" for glob in config["globs"])
        rule_content = f"""---
trigger: glob
description: {config["description"]}
globs:
{globs_str}
---

{merged_content}"""

        output_path.write_text(rule_content, encoding="utf-8")
        print(f"  ✓ {output_name}")
        count += 1

    print(f"\nCreated {count} language rule files")


def create_global_rules_file(rules_dir):
    """Create global_rules.md from rules/"""
    rule_files = [
        "rules/clean-code.md",
        "rules/patterns.md",
        "rules/testing.md",
        "rules/commit.md",
        "rules/architecture.md",
        "rules/ipc.md",
        "rules/mcp.md",
        "rules/orchestration.md",
        "rules/security.md",
        "rules/memory.md",
        "rules/behaviour.md",
    ]

    combined_content = "# Global Development Guidelines\n\n"
    combined_content += (
        "> These rules apply to all programming languages and project types.\n\n"
    )

    for filepath_str in rule_files:
        file_path = Path(filepath_str)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            section_name = file_path.stem.replace("-", " ").title()
            combined_content += f"\n---\n\n# {section_name}\n\n{content}\n"
        else:
            print(f"  Warning: {filepath_str} not found, skipping")

    output_path = rules_dir / "global_rules.md"
    output_path.write_text(combined_content, encoding="utf-8")

    file_size = output_path.stat().st_size / 1024
    print(f"  ✓ global_rules.md ({file_size:.1f} KB)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy_to_windsurf.py <language1> [language2] ...")
        print("Available languages: csharp, cpp, python, react")
        sys.exit(1)

    languages = [arg.lower() for arg in sys.argv[1:]]

    print("=" * 60)
    print("Windsurf Deployment")
    print("=" * 60)

    windsurf_dir = get_windsurf_dir()
    workflows_dir = windsurf_dir / "workflows"
    rules_dir = windsurf_dir / "rules"

    workflows_dir.mkdir(parents=True, exist_ok=True)
    rules_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nWorkflows: {workflows_dir}")
    print(f"Rules: {rules_dir}")

    print("\n" + "=" * 60)
    print("Phase 1: Creating Workflow Files")
    print("=" * 60)
    create_workflow_files(workflows_dir)

    print("\n" + "=" * 60)
    print("Phase 2: Creating Language Rule Files")
    print("=" * 60)
    create_language_rule_files(rules_dir, languages)

    print("\n" + "=" * 60)
    print("Phase 3: Creating Global Rules File")
    print("=" * 60)
    create_global_rules_file(rules_dir)

    print("\n" + "=" * 60)
    print("✓ Windsurf Deployment Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
