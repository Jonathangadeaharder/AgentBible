---
name: react
description: React/TypeScript coding standards, patterns, and best practices. Use when writing, reviewing, or refactoring React code.
paths:
  - "**/*.jsx"
  - "**/*.tsx"
  - "**/*.ts"
  - "**/*.js"
  - "**/package.json"
compatibility: "React 18+, TypeScript 5+"
allowed-tools: Bash(pnpm *) Bash(npx *) Bash(tsc *) Bash(vitest *) Bash(playwright *)
---

# React Skill

Covers React/TypeScript development standards: clean code, component patterns, testing, static analysis, concurrency, and data fetching.

## Topic Files

| File | Contents |
|------|----------|
| `clean-code.md` | Naming, hooks, props, ES6+, performance, styling |
| `patterns.md` | Composition, Custom Hooks, Context Provider |
| `testing.md` | Jest + React Testing Library, mocking, timeouts |
| `static-analysis.md` | ESLint + Prettier + TypeScript config |
| `parallel.md` | React 18 concurrent, Web Workers, Suspense |
| `ipc.md` | Fetch/Axios, WebSockets, Context state management |

## Quick Reference

| Convention | Rule |
|------------|------|
| Components | `PascalCase` |
| Props | `camelCase` |
| Event handlers | `handle` prefix (`handleClick`) |
| Boolean props | `is`/`has`/`should` prefix |
| Constants | `UPPER_SNAKE_CASE` |
| Files | Match component name (`UserProfile.tsx`) |

## Key Tools

- **Package manager**: pnpm (not npm/yarn)
- **Linter**: ESLint + Biome
- **Formatter**: Prettier
- **Type checker**: TypeScript (`tsc --noEmit`)
- **Testing**: Vitest (not Jest)
- **E2E**: Playwright
