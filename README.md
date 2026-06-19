# oriz-cards

> India card intelligence — 750 credit, debit, and prepaid card profiles. Lives at [cards.oriz.in](https://cards.oriz.in).

Static catalog and comparison UI for cards issued in India: Amex, Axis, AU SFB, Bandhan, BoB, BoM, Canara, CUB, DCB, Dhanlaxmi, ESAF, Federal, HDFC, HSBC, ICICI, IDBI, IDFC, Indian Bank, IndusInd, IOB, J&K Bank, Karnataka Bank, Kotak, KVB, PNB, PSB, RBL, Saraswat, SBI, SIB, StanChart, TMB, UCO, Union, Yes Bank.

Card data lives in `data/cards/{credit,debit,prepaid}/<bank>/*.json` — open data, MIT-licensed, contributions welcome.

Part of the [oriz](https://github.com/chirag127/oriz) family of static sites. Shared sign-in across `*.oriz.in` via Firebase Authentication. Shared design system via [`@chirag127/oriz-ui`](https://github.com/chirag127/oriz-ui).

## Develop

```bash
pnpm install
npx envpact-cli@0.2.0    # pulls .env from the shared envpact source
pnpm dev
```

The dev server boots at http://localhost:4321.

## Build + deploy

```bash
pnpm build               # Astro static build → dist/
pnpm deploy              # wrangler deploy → Cloudflare Pages
```

The Cloudflare project is `oriz-cards`; the custom domain `cards.oriz.in` is bound through the dashboard. See `wrangler.toml`.

## Stack

- [Astro 6](https://astro.build) (static output, `format: 'directory'`)
- [React 19](https://react.dev) for the small interactive islands (search, theme switch, account)
- [Tailwind v4](https://tailwindcss.com) via `@tailwindcss/vite`
- [Firebase Auth + Firestore](https://firebase.google.com) for the shared `oriz-app` project
- [`@chirag127/oriz-ui`](https://github.com/chirag127/oriz-ui) for shared components and tokens
- [Biome](https://biomejs.dev) for lint + format
- Hosted on [Cloudflare Pages](https://pages.cloudflare.com)

## License

Code: MIT. Card data: CC BY 4.0. See `LICENSE` (TBD).
