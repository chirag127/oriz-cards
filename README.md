# Oriz Financial Cards

> India financial card intelligence — credit, debit, prepaid, travel/forex, corporate, and business card profiles for every major Indian issuer, with a static catalog and comparison UI.

**Live at**: <https://financial-cards.oriz.in> · **Status**: production

## What this is

A free, searchable directory of every financial card issued in India — Amex, Axis, AU SFB, Bandhan, BoB, BoM, Canara, CUB, DCB, Dhanlaxmi, ESAF, Federal, HDFC, HSBC, ICICI, IDBI, IDFC, Indian Bank, IndusInd, IOB, J&K Bank, Karnataka Bank, Kotak, KVB, PNB, PSB, RBL, Saraswat, SBI, SIB, StanChart, TMB, UCO, Union, Yes Bank, plus wallets and fintechs (Paytm, etc.). Card data lives as JSON under `data/cards/{credit,debit,prepaid,travel,corporate,business}/<bank>/`.

## Card categories covered

- **Credit** — 750+ profiles (live)
- **Debit** — sample seeded; expanding
- **Prepaid** — sample seeded; expanding
- **Travel / Forex** — sample seeded; expanding
- **Corporate / Business** — sample seeded; expanding
- Extensible: `student`, `metal`, `virtual` tiers covered by schema

Schema is maximal — see `src/content/cards/schema.ts`.

## Per-feature inventory

| Feature | Status |
| --- | --- |
| Card directory + detail pages (`credit/[issuer]/[slug]`) | live |
| `cards.json` data endpoint | live |
| Account / sign-in (shared) | live |
| Legal pages (privacy, terms, cookies, disclaimer, grievance) | live |
| Debit + prepaid + travel + corporate detail routes | WIP |
| Side-by-side card comparison | planned |

## App-specific env vars

None beyond the family-wide set at `templates/.env.example`.

## Local dev

```bash
# from the workspace root (c:/D/oriz)
pnpm -F @chirag127/oriz-financial-cards-app dev
```

## Knowledge

See [`./knowledge/`](./knowledge/) for app-specific decisions, runbooks, and services. Family rules / decisions / architecture live at the master repo's [`knowledge/`](../../../../knowledge/).

## License

MIT License. See master [`LICENSE`](../../../../LICENSE) — same terms across the family.
