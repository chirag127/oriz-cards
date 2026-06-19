import type { APIRoute } from 'astro'
import { SITE_CONFIG } from '~/lib/siteConfig'

export const GET: APIRoute = () =>
  new Response(
    `User-agent: *\nAllow: /\nSitemap: ${SITE_CONFIG.origin}/sitemap-index.xml\n`,
    { headers: { 'Content-Type': 'text/plain; charset=utf-8' } },
  )
