"""
Deploy agent guidelines to Claude Code
- Workflows → .claude/commands/ or ~/.claude/commands/
- Language skills → .claude/skills/ or ~/.claude/skills/
- Rules → CLAUDE.md (merged from rules/)
"""

import sys
import json
from pathlib import Path


def get_user_claude_dir():
    return Path.home() / ".claude"


def get_project_claude_dir():
    return Path(".claude")


def create_command_files(commands_dir):
    """Create command files from workflows/"""
    source_dir = Path("workflows")
    if not source_dir.exists():
        print(f"Warning: {source_dir} not found, skipping command files")
        return

    count = 0
    for md_file in source_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        output_name = md_file.stem.lower() + ".md"
        output_path = commands_dir / output_name

        # Extract description from frontmatter if present
        description = f"{md_file.stem.replace('-', ' ').title()} workflow"
        if content.startswith("---"):
            for line in content.split("\n")[1:]:
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip()
                    break

        command_content = f"---\ndescription: {description}\n---\n\n{content}"
        output_path.write_text(command_content, encoding="utf-8")

        print(f"  ✓ {output_name}")
        count += 1

    print(f"\nCreated {count} command files")


def create_skill_files(skills_dir, languages):
    """Create skill files from skills/"""
    lang_config = {
        "csharp": {
            "folder": "skills/csharp",
            "extensions": [".cs", ".csproj", ".sln"],
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
            "extensions": [".cpp", ".hpp", ".h", ".cc", ".cxx"],
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
            "extensions": [".py", "pyproject.toml", "requirements*.txt"],
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
            "extensions": [".jsx", ".tsx", ".js", ".ts", "package.json"],
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

        # Copy SKILL.md as the entrypoint
        skill_md = lang_dir / "SKILL.md"
        if skill_md.exists():
            skill_dir = skills_dir / lang_key
            skill_dir.mkdir(parents=True, exist_ok=True)

            # Copy SKILL.md
            content = skill_md.read_text(encoding="utf-8")
            (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

            # Copy topic files
            for filename in config["files"]:
                file_path = lang_dir / filename
                if file_path.exists():
                    file_content = file_path.read_text(encoding="utf-8")
                    (skill_dir / filename).write_text(file_content, encoding="utf-8")

            print(
                f"  ✓ skills/{lang_key}/ (SKILL.md + {len(config['files'])} topic files)"
            )
            count += 1

    print(f"\nCreated {count} language skills")


def create_global_claude_md(target_file):
    """Create CLAUDE.md from rules/"""
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

    sections = []
    sections.append("# Development Guidelines\n")
    sections.append(
        "> Universal coding standards. These rules apply to all languages and projects.\n"
    )

    for filepath_str in rule_files:
        filepath = Path(filepath_str)
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8").strip()
            section_name = filepath.stem.replace("-", " ").title()
            sections.append(f"\n---\n\n# {section_name}\n\n{content}")

    if len(sections) <= 2:
        print("Warning: No rule files found")
        return

    merged_content = "\n".join(sections)
    target_file.write_text(merged_content, encoding="utf-8")

    file_size = target_file.stat().st_size / 1024
    print(f"  ✓ CLAUDE.md ({file_size:.1f} KB)")


def create_settings_json(target_file, languages):
    """Create settings.json with PostToolUse hooks"""
    hooks_config = {
        "permissions": {
            "deny": [
                "Read(./.env)",
                "Read(./.env.*)",
                "Read(./secrets/**)",
                "Read(./config/credentials.json)",
            ]
        }
    }

    if languages:
        hooks_config["hooks"] = {"PostToolUse": {}}

        validation_commands = {
            "csharp": {
                "Write(*.cs)": "dotnet format --verify-no-changes --include $FILE"
            },
            "cpp": {
                "Write(*.cpp)": "cppcheck --enable=warning,style,performance,portability --error-exitcode=1 $FILE",
                "Write(*.hpp)": "cppcheck --enable=warning,style,performance,portability --error-exitcode=1 $FILE",
                "Write(*.h)": "cppcheck --enable=warning,style,performance,portability --error-exitcode=1 $FILE",
            },
            "python": {
                "Write(*.py)": "ruff check $FILE && ruff format --check $FILE && mypy $FILE"
            },
            "react": {
                "Write(*.jsx)": "prettier --check $FILE && eslint $FILE",
                "Write(*.tsx)": "prettier --check $FILE && eslint $FILE && tsc --noEmit",
                "Write(*.js)": "prettier --check $FILE && eslint $FILE",
                "Write(*.ts)": "prettier --check $FILE && eslint $FILE && tsc --noEmit",
            },
        }

        for lang in languages:
            lang_key = lang.lower()
            if lang_key in validation_commands:
                for pattern, command in validation_commands[lang_key].items():
                    ext = pattern.split("(")[1].split(")")[0].replace("*.", "")
                    hook_name = f"{lang_key}_{ext}_validation"
                    hooks_config["hooks"]["PostToolUse"][hook_name] = {pattern: command}

    settings_json = json.dumps(hooks_config, indent=2)
    target_file.write_text(settings_json, encoding="utf-8")
    print("  ✓ settings.json")


def main():
    print("\n" + "=" * 60)
    print("Claude Code Deployment")
    print("=" * 60 + "\n")

    if len(sys.argv) < 2:
        print("Usage: python deploy_to_claude.py <target> [languages...]")
        print("\nTargets:")
        print("  user     - Deploy to user-level (~/.claude/)")
        print("  project  - Deploy to project-level (.claude/)")
        print("\nLanguages: csharp, cpp, python, react")
        print("\nExamples:")
        print("  python deploy_to_claude.py user")
        print("  python deploy_to_claude.py project csharp python")
        sys.exit(1)

    target = sys.argv[1].lower()
    languages = [arg.lower() for arg in sys.argv[2:]] if len(sys.argv) > 2 else []

    if target not in ["user", "project"]:
        print(f"Error: Invalid target '{target}'. Use 'user' or 'project'")
        sys.exit(1)

    if target == "user":
        claude_dir = get_user_claude_dir()
        print(f"Deploying to user-level: {claude_dir}")
    else:
        claude_dir = get_project_claude_dir()
        print(f"Deploying to project-level: {claude_dir}")

    if languages:
        print(f"Including languages: {', '.join(languages)}")
    else:
        print("No specific languages (global guidelines only)")

    claude_dir.mkdir(parents=True, exist_ok=True)
    commands_dir = claude_dir / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    skills_dir = claude_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("Phase 1: Creating Command Files (from workflows/)")
    print("=" * 60)
    create_command_files(commands_dir)

    print("\n" + "=" * 60)
    print("Phase 2: Creating CLAUDE.md (from rules/)")
    print("=" * 60)
    create_global_claude_md(claude_dir / "CLAUDE.md")

    if languages:
        print("\n" + "=" * 60)
        print("Phase 3: Creating Language Skills")
        print("=" * 60)
        create_skill_files(skills_dir, languages)

    if target == "project":
        print("\n" + "=" * 60)
        print("Phase 4: Creating Configuration Files")
        print("=" * 60)
        create_settings_json(claude_dir / "settings.json", languages)

    print("\n" + "=" * 60)
    print("✓ Claude Code Deployment Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
