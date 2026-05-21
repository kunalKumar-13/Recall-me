import {
  loadCohorts,
  loadFeedback,
  loadHealth,
  loadMeta,
  loadRelease,
  loadTimeline,
  loadTraction,
  loadTrust,
} from "../lib/data";
import { AlphaCohorts } from "../components/AlphaCohorts";
import { FeedbackRoom } from "../components/FeedbackRoom";
import { FounderTimeline } from "../components/FounderTimeline";
import { HealthOverview } from "../components/HealthOverview";
import { ReleaseRoom } from "../components/ReleaseRoom";
import { TractionRoom } from "../components/TractionRoom";
import { TrustRoom } from "../components/TrustRoom";

/**
 * The control-room page. One server component, eight sections,
 * every data row sourced from a JSON file the founder placed in
 * `apps/admin/data/`. Nothing fetched from anywhere else, by
 * construction.
 *
 * The order is the 30-second read: health first, traction second,
 * cohorts third, release fourth, trust fifth, feedback sixth,
 * timeline last. A founder who opens this and stops after the
 * first two sections still leaves knowing whether the product is
 * alive.
 */
export default async function Page() {
  const [
    health, traction, cohorts, release, trust, feedback, timeline, meta,
  ] = await Promise.all([
    loadHealth(),
    loadTraction(),
    loadCohorts(),
    loadRelease(),
    loadTrust(),
    loadFeedback(),
    loadTimeline(),
    loadMeta(),
  ]);

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Recall — control room</h1>
          <div className="page-subtitle">
            local-first · no server · no auth · no telemetry
          </div>
        </div>
        <div className="page-subtitle">
          generated {meta.generated_at ?? "—"}
        </div>
      </header>

      <Section title="1 · Health overview" aside="six cards · current state">
        <HealthOverview cards={health} />
      </Section>

      <Section title="2 · Traction" aside="30-day trend per metric">
        <TractionRoom series={traction} />
      </Section>

      <Section title="3 · Alpha cohorts" aside="manual roster">
        <AlphaCohorts cohorts={cohorts} />
      </Section>

      <Section title="4 · Release" aside="what ships, what blocks it">
        <ReleaseRoom release={release} />
      </Section>

      <Section title="5 · Trust" aside="recoveries shown / accepted / silenced">
        <TrustRoom cards={trust} />
      </Section>

      <Section title="6 · Feedback" aside="manual import only">
        <FeedbackRoom items={feedback} />
      </Section>

      <Section title="7 · Founder timeline" aside="phase done %">
        <FounderTimeline phases={timeline} />
      </Section>

      <footer className="footer">
        <span>
          data: <code>apps/admin/data/</code> &middot; refresh with{" "}
          <code>merge_stats.py</code> + <code>pull_release_stats.py</code>
        </span>
        <span>{meta.source_note ?? ""}</span>
      </footer>
    </main>
  );
}

function Section({
  title, aside, children,
}: {
  title: string;
  aside?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="section">
      <div className="section-header">
        <span className="section-title">{title}</span>
        {aside ? <span className="section-aside">— {aside}</span> : null}
      </div>
      {children}
    </section>
  );
}
