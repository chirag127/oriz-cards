/*
 * /cards.json — full data dump as a static endpoint, served at the site root.
 * The footer's `data → download as JSON` link points here. CC BY 4.0.
 */
import type { APIRoute } from 'astro'
import rawCards from '../../data/cards.json'

export const GET: APIRoute = () =>
  new Response(JSON.stringify(rawCards), {
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Content-Disposition': 'inline; filename="oriz-cards.json"',
      'Cache-Control': 'public, max-age=3600',
    },
  })
