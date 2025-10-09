
## Frontend Development README

This directory contains the Next.js frontend for the project. The instructions below show how to run the development server, build for production, and use tooling included in the app (ESLint, Tailwind CSS, formatters).

### Prerequisites
- Node.js 18+ recommended (check with `node -v`)
- npm (bundled with Node) or yarn

### Install dependencies

```powershell
npm install
```

### Run development server

```powershell
npm run dev
```

Open http://localhost:3000 in your browser. The Next.js dev server supports HMR (hot module replacement) so edits update immediately.

Entry points
- App routes: `app/`
- Main page: `app/page.js` (or `pages/index.js`)

### Build for production

```powershell
npm run build
npm run start    # to run the built app locally
```

Notes about the Next.js build process
- `npm run build` runs Next.js's build step which compiles and optimizes pages, generates server-side bundles, and prepares static assets.
- By default Next will perform code-splitting and optimization for production.
- Environment variables for build/runtime should go in a `.env.local` file (do NOT commit secrets). See `next.config.js` for any custom build-time configuration.

### ESLint

This project includes ESLint configuration (if present). To run linter:

```powershell
npm run lint
```

Common commands you might see in `package.json`:
- `lint` — runs ESLint and reports problems
- `lint:fix` — runs ESLint with `--fix` to automatically correct simple issues

### Tailwind CSS

Tailwind is configured via `tailwind.config.js` and PostCSS. Typical commands do not change — Tailwind's utility classes are available in JSX/TSX and will be processed at build time.