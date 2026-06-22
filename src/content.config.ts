/**
 * Astro 5+ content collections config.
 *
 * Loads every JSON under `data/cards/<type>/<bank>/<card>.json` into the
 * `cards` collection. Files live OUTSIDE `src/` (at the repo root) so they
 * can be linted/processed/scraped without going through Astro's pipeline.
 *
 * Adding a new card category (debit, prepaid, travel, corporate, ...) is
 * just a matter of dropping JSON files into the right subdir — the glob
 * loader picks them up on the next build.
 *
 * Schema is the maximal `cardSchema` in `./content/cards/schema.ts`.
 */

import { defineCollection } from 'astro:content'
import { glob } from 'astro/loaders'
import { cardSchema } from './content/cards/schema'

const cards = defineCollection({
  loader: glob({
    pattern: '**/*.json',
    // `base` is resolved relative to the project root (the dir containing
    // astro.config.mjs), so the catalog at `data/cards/**` is reachable.
    base: './data/cards',
  }),
  schema: cardSchema,
})

export const collections = { cards }
