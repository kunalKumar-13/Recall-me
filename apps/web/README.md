# Recall — landing page

The marketing site for Recall, a local-first continuity
operating system.

Stack:

- **Next.js 14** (app router)
- **Tailwind CSS** for styling
- **Framer Motion** for restrained, cinematic motion
- **TypeScript** end-to-end

## Run locally

```bash
cd web
npm install
npm run dev
```

Then open <http://localhost:3000>.

## Build

```bash
npm run build
npm run start
```

## Deploy to Vercel

```bash
npx vercel
```

The project is zero-config for Vercel — push to a Git remote and import,
or run `vercel` from inside `web/`.

## Structure

```
web/
├── app/
│   ├── layout.tsx        # root layout, metadata, font
│   ├── page.tsx          # composes the sections
│   ├── globals.css       # Tailwind base + atmospheric styles
│   └── components/
│       ├── AmbientBackground.tsx   # floating accent orbs
│       ├── Logo.tsx                # the R-on-purple identity
│       ├── Nav.tsx                 # transparent → blur on scroll
│       ├── Hero.tsx                # headline + cinematic mockup
│       ├── LauncherMockup.tsx      # static recreation of the launcher
│       ├── Problem.tsx             # three-line statement
│       ├── Features.tsx            # 6-cell grid
│       ├── Privacy.tsx             # private-by-design slab
│       ├── BuiltForThinkers.tsx    # audience pills
│       ├── FinalCTA.tsx            # closing section
│       └── Footer.tsx              # minimal footer
├── tailwind.config.ts
├── postcss.config.mjs
├── next.config.mjs
└── tsconfig.json
```

## Design tokens

The palette mirrors the desktop app so the website and the launcher feel
like the same product:

| Token | Hex |
|---|---|
| `bg` | `#0a0b0f` |
| `accent` | `#8b9bff` |
| `accentSoft` | `#3b4566` |
| `highlight` | `#cdd2e0` |

Plus utility classes `.text-gradient` (white → 70% white) and
`.text-gradient-accent` (accent → highlight) for headline emphasis.

## Motion

All entrance animations use `[0.16, 1, 0.3, 1]` (a calm cubic bezier),
durations 0.7–1.2 s, `whileInView` with `once: true` so nothing replays
on scroll-back. The hero mockup floats on a 9-second loop. No flashy
gimmicks; the page should feel quiet.
