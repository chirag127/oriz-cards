# Oriz Financial Cards

> India financial-card intelligence — credit, debit, prepaid, travel/forex, corporate, and business card profiles for every major Indian issuer, with a static catalog and comparison UI.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/chirag127/oriz-cards)](https://github.com/chirag127/oriz-cards/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/chirag127/oriz-cards)](https://github.com/chirag127/oriz-cards/commits/main)
[![CI](https://github.com/chirag127/oriz-cards/actions/workflows/ci.yml/badge.svg)](https://github.com/chirag127/oriz-cards/actions/workflows/ci.yml)
[![Astro](https://img.shields.io/badge/Astro-6-BC52EE?logo=astro&logoColor=white)](https://astro.build/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev/)

## What it is / why it exists

There's no single free place to look up, filter, and compare every financial card issued in India — the data is scattered across bank sites, aggregators, and paywalled comparison portals. Oriz Financial Cards is a static, searchable directory of credit, debit, prepaid, travel/forex, corporate, and business cards from every major Indian issuer. Card data lives as versioned JSON under `data/cards/`, so the catalog is transparent, forkable, and deploys to Cloudflare Pages at $0.

## Links

- **Live site:** [financial-cards.oriz.in](https://financial-cards.oriz.in) (canonical, Cloudflare Pages)
- **GitHub Pages mirror:** [chirag127.github.io/oriz-cards](https://chirag127.github.io/oriz-cards/)
- **Repo:** [github.com/chirag127/oriz-cards](https://github.com/chirag127/oriz-cards)

⭐ If this is useful, please **star the repo** — it helps others find it.

## Architecture

```mermaid
flowchart TD
  A[data/cards/*.json<br/>per issuer, per category] --> B[Astro content collection<br/>schema.ts validation]
  B --> C[static build<br/>astro build]
  C --> D[card directory<br/>+ detail routes]
  C --> E[cards.json<br/>data endpoint]
  F[@chirag127/astro-shell<br/>astro-chrome / astro-data] --> C
  G[React 19 islands] --> D
  H[Clerk<br/>optional, gates paid only] -.-> G
  I[Firebase<br/>optional] -.-> G
  C --> J[Cloudflare Pages<br/>financial-cards.oriz.in]
  C --> K[GitHub Pages mirror]
```

## Features

- Searchable directory of Indian financial cards — Amex, Axis, AU SFB, BoB, Canara, Federal, HDFC, HSBC, ICICI, IDFC, IndusInd, Kotak, PNB, RBL, SBI, StanChart, Yes Bank, plus wallets/fintechs.
- Card categories: **credit** (750+ profiles, live), **debit / prepaid / travel-forex / corporate / business** (seeded, expanding). Schema also covers `student`, `metal`, `virtual` tiers.
- Detail pages per card (`credit/[issuer]/[slug]`) + a `cards.json` data endpoint.
- Card data as versioned JSON under `data/cards/{credit,debit,prepaid,travel,corporate,business}/<bank>/` — transparent and forkable.
- **Public content reads without auth** — Clerk gates only paid/account features (fleet SSO rule).
- Optional AI polish that degrades gracefully if unavailable.
- Full test matrix: Vitest (unit) + Playwright (e2e) + Biome (lint/format).

## Tech stack

- **Framework:** Astro 6 · React 19 · Tailwind CSS 4
- **Shared:** `@chirag127/astro-shell`, `@chirag127/astro-chrome`, `@chirag127/astro-data`, `@chirag127/astro-test-utils`
- **Auth/data (optional):** Clerk (`@clerk/clerk-react`) · Firebase
- **Tooling:** Biome · Vitest (+ v8 coverage) · Playwright · Wrangler · `pnpm@10`, Node ≥22.12
- **Hosting:** Cloudflare Pages (deploy via Wrangler) + GitHub Pages mirror

## Repo structure

```
src/                     # Astro pages, React islands, content collections
  content/cards/schema.ts   # maximal card schema
data/cards/              # per-issuer, per-category card JSON  (the catalog)
data/cards/debit/pnb/    # PNB debit catalog — scraped from pnb.bank.in/card-index.html
                         #   pdf/           benefit PDFs per card
                         #   manifest.json  scrape output (tab text + pdf mapping)
                         #   scrape_pnb_cards.py / build_pnb_cards.py  (repo root)
knowledge/               # app-specific decisions, runbooks, services

## PNB debit-catalog pipeline

`scrape_pnb_cards.py` fetches [pnb.bank.in/card-index.html](https://pnb.bank.in/card-index.html),
resolves each card tab's benefits PDF (direct `uploadfile/` link → "Benefits Cured with
Card" fid → shared RuPay contactless doc), downloads them into
`data/cards/debit/pnb/pdf/`, and writes `manifest.json`. `build_pnb_cards.py` parses
that manifest into schema-compliant per-card JSONs and upgrades `data/cards.json`.
Re-run both to refresh (idempotent).
tests/                   # vitest + playwright
astro.config.mjs         # shell() → financial-cards.oriz.in
wrangler.toml            # Cloudflare Pages deploy config
.github/workflows/       # ci · codeql · megalinter · scorecard · gh-pages mirrors
```

## Quick start

```bash
pnpm i                 # install (Node >=22.12)
pnpm dev               # local dev server
pnpm build             # static build
pnpm preview           # preview the build
pnpm test              # unit tests (vitest)
pnpm test:e2e          # e2e tests (playwright)
pnpm lint              # biome check
pnpm deploy            # wrangler deploy to Cloudflare Pages
```

> On Windows, if a `pnpm` build crashes on the missing `@esbuild/win32-x64` binary, use `npm install --legacy-peer-deps && npm run build`.

## Configuration

Env vars are drawn from the family-wide `.env.example` (names only — never commit values). App-relevant keys:

| Env var | Purpose |
| --- | --- |
| `PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk publishable key (browser-safe) — gates paid/account features only |
| `PUBLIC_FIREBASE_API_KEY` | Firebase web config (client) |
| `PUBLIC_FIREBASE_AUTH_DOMAIN` | Firebase auth domain (`auth.oriz.in`) |
| `PUBLIC_FIREBASE_PROJECT_ID` | Firebase project id |
| `PUBLIC_FIREBASE_APP_ID` | Firebase app id |
| `PUBLIC_BASE_PATH` | Base path override (e.g. `/oriz-cards/` for the GH Pages mirror) |
| `CLOUDFLARE_API_TOKEN` | Cloudflare Pages deploy (CI/deploy only) |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account for deploy |

`PUBLIC_*` are client-only by convention; secret keys are server/deploy-only and never prefixed `PUBLIC_`.

## Part of the oriz family

One of ~80 [oriz](https://blog.oriz.in) sites. Read how the fleet is built solo at [blog.oriz.in](https://blog.oriz.in).

**Cost:** $0 on the Cloudflare free tier.

## Security

No secrets in the repo; sops+age vault (Doppler upstream). `PUBLIC_*` vars are client-only; secret keys live in GitHub org secrets / Cloudflare / Firebase runtime config. Never expose a `PUBLIC_*_SECRET`.

## Contributing

Issues and PRs welcome. Add or correct a card by editing the JSON under `data/cards/` (validated against `schema.ts`). Terse, conventional commits. This site has its own visual identity — reuse `@chirag127/*` for mechanism only, not another site's look.

## Status

Production. Credit catalog live (750+); debit/prepaid/travel/corporate/business expanding; side-by-side comparison planned.

## Changelog

Conventional commits are the changelog.

## Disclaimer

General information, not investment advice. Card details, fees, and reward structures change — always verify with the issuer before applying.

## License

MIT © 2026 Chirag Singhal — see [LICENSE](LICENSE).

## Author

Chirag Singhal · chirag@oriz.in
