# React Static Analysis

## Tools

- **Biome** — Linter + formatter (preferred)
- **ESLint** — Linter for JS/TS (legacy, if configured)
- **Prettier** — Formatter (legacy, if configured)
- **TypeScript** — Type checker

## Commands

```bash
# Preferred: Biome (lint + format in one tool)
pnpm exec biome check --write $FILE

# Before committing
pnpm exec biome check src/ && pnpm exec tsc --noEmit

# Legacy: ESLint + Prettier (if project uses them)
npx eslint $FILE --fix && npx prettier --write $FILE && npx tsc --noEmit
```

## .eslintrc.json

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "plugins": ["react", "react-hooks", "jsx-a11y", "@typescript-eslint"],
  "settings": { "react": { "version": "detect" } },
  "rules": {
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "@typescript-eslint/no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/no-explicit-any": "warn",
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "prefer-const": "error",
    "no-var": "error"
  }
}
```

## .prettierrc

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "arrowParens": "avoid"
}
```

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "isolatedModules": true,
    "noEmit": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Inline Suppression

```javascript
// eslint-disable-next-line no-console
console.log('debug');

// prettier-ignore
const matrix = [[1,2],[3,4]];
```
