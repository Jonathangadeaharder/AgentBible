"""
Deploy agent guidelines to GitHub Copilot
Creates .prompt.md files from workflows/ and .instructions.md from skills/
"""

import os
import sys
from pathlib import Path


def get_target_dir():
    """Get VS Code User prompts directory"""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        # Fallback for macOS/Linux
        home = Path.home()
        if sys.platform == "darwin":
            return (
                home / "Library" / "Application Support" / "Code" / "User" / "prompts"
            )
        else:
            return home / ".config" / "Code" / "User" / "prompts"
    return Path(appdata) / "Code" / "User" / "prompts"


def create_prompt_files(target_dir):
    """Copy workflow files as .prompt.md with frontmatter"""
    workflows_dir = Path("workflows")
    if not workflows_dir.exists():
        print(f"Warning: {workflows_dir} not found, skipping workflow files")
        return

    count = 0
    for md_file in workflows_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        output_name = md_file.stem.lower() + ".prompt.md"
        output_path = target_dir / output_name

        prompt_content = f"---\nmode: agent\n---\n\n{content}"
        output_path.write_text(prompt_content, encoding="utf-8")

        print(f"  ✓ {output_name}")
        count += 1

    print(f"\nCreated {count} prompt files")


def create_instruction_files(target_dir, languages):
    """Create language-specific instruction files from skills/"""
    lang_config = {
        "csharp": {
            "folder": "skills/csharp",
            "output": "csharp.instructions.md",
            "applyTo": "['.cs', '.csproj', '.sln']",
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
            "output": "cpp.instructions.md",
            "applyTo": "['.cpp', '.hpp', '.h', '.cc', '.cxx', 'CMakeLists.txt']",
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
            "output": "python.instructions.md",
            "applyTo": "['.py', 'pyproject.toml', 'requirements*.txt']",
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
            "output": "react.instructions.md",
            "applyTo": "['.jsx', '.tsx', '.js', '.ts', 'package.json']",
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
            continue

        config = lang_config[lang_key]
        lang_dir = Path(config["folder"])

        if not lang_dir.exists():
            print(f"Warning: {lang_dir} not found, skipping {lang_key}")
            continue

        sections = []
        for filename in config["files"]:
            file_path = lang_dir / filename
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8").strip()
                sections.append(content)

        if not sections:
            continue

        output_path = target_dir / config["output"]
        merged_content = "\n\n---\n\n".join(sections)
        instruction_content = (
            f"---\napplyTo: {config['applyTo']}\n---\n\n{merged_content}"
        )
        output_path.write_text(instruction_content, encoding="utf-8")

        print(f"  ✓ {config['output']}")
        count += 1

    print(f"\nCreated {count} instruction files")


def create_global_instructions(target_dir):
    """Create global instructions file from rules/"""
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
    for filepath_str in rule_files:
        filepath = Path(filepath_str)
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8").strip()
            sections.append(content)

    if not sections:
        print("Warning: No rule files found")
        return

    output_path = target_dir / "global.instructions.md"
    merged_content = "\n\n---\n\n".join(sections)
    instruction_content = f"---\napplyTo: '**/*'\n---\n\n{merged_content}"
    output_path.write_text(instruction_content, encoding="utf-8")

    print("  ✓ global.instructions.md")
    print("\nCreated global instructions file")


def main():
    print("\n" + "=" * 60)
    print("GitHub Copilot Deployment")
    print("=" * 60 + "\n")

    languages = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.lower() in ["csharp", "cpp", "python", "react"]:
                languages.append(arg.lower())
    else:
        languages = ["csharp", "cpp", "python", "react"]

    print(f"Including languages: {', '.join(languages)}\n")

    target_dir = get_target_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"Target: {target_dir}\n")

    print("Creating prompt files...")
    create_prompt_files(target_dir)

    print("\nCreating global instructions...")
    create_global_instructions(target_dir)

    print("\nCreating language-specific instructions...")
    create_instruction_files(target_dir, languages)

    print("\n" + "=" * 60)
    print("✓ Deployment complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
