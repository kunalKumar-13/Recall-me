/**
 * Recall admin — Next.js config.
 *
 * The control room is local-first: there is no server hosting it,
 * no auth, no remote data fetch. Run `next dev` for the founder's
 * own machine, or `next build && next start` for an internal LAN
 * dashboard. No public deploy, no analytics, no telemetry.
 */
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // The page reads JSON from `apps/admin/data/` via Node fs at
  // server-component render time. No external image hosts.
  images: { unoptimized: true },
};

export default nextConfig;
