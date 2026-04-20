import Link from "next/link";
import { fair, hostStats } from "@/lib/data";

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
      <p className="text-sm font-medium mb-1" style={{ color: "#6B7280" }}>{label}</p>
      <p className="text-3xl font-bold" style={{ color: "var(--dark)", fontFamily: "var(--font-playfair)" }}>{value}</p>
      {sub && <p className="text-xs mt-1" style={{ color: "#9CA3AF" }}>{sub}</p>}
    </div>
  );
}

export default function HostDashboard() {
  const matchProgress = Math.round(
    (hostStats.matchesReviewed / (hostStats.matchesReviewed + hostStats.matchesPending)) * 100
  );

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)" }}>
      {/* Top Nav */}
      <nav className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <svg width="32" height="32" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="22,3 40,38 4,38" fill="#5B8ED6" opacity="0.9"/>
            <polygon points="22,12 34,38 10,38" fill="#B8D9E8" opacity="0.8"/>
            <polygon points="16,24 28,24 22,38" fill="#D4AF6A"/>
          </svg>
          <span className="font-bold text-lg" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
            FairMatch
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-semibold" style={{ color: "var(--henry)" }}>Henry Street Settlement</p>
            <p className="text-xs" style={{ color: "#9CA3AF" }}>Host Organization</p>
          </div>
          <Link href="/" className="text-xs px-3 py-1.5 rounded-full border border-gray-200 hover:bg-gray-50 transition-colors" style={{ color: "#6B7280" }}>
            Sign Out
          </Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">

        {/* Fair Header */}
        <div className="rounded-2xl p-6 text-white" style={{ background: "var(--henry)" }}>
          <div className="flex items-start justify-between flex-wrap gap-4">
            <div>
              <p className="text-sm font-medium opacity-80 mb-1 uppercase tracking-wide">Upcoming Fair</p>
              <h1 className="text-2xl font-bold mb-2" style={{ fontFamily: "var(--font-playfair)" }}>
                {fair.name}
              </h1>
              <p className="text-sm opacity-90">{fair.date} · {fair.time}</p>
              <p className="text-sm opacity-80 mt-0.5">{fair.location}</p>
            </div>
            <span className="text-xs bg-white/20 rounded-full px-3 py-1 font-medium">25 days away</span>
          </div>
        </div>

        {/* Fair Stats */}
        <section>
          <h2 className="text-lg font-bold mb-4" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
            Fair Overview
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <StatCard
              label="Employers Committed"
              value={hostStats.employersCommitted}
              sub="confirmed participants"
            />
            <StatCard
              label="Candidates RSVP'd"
              value={hostStats.candidatesRsvp}
              sub="registered attendees"
            />
            <StatCard
              label="Resumes Uploaded"
              value={hostStats.resumesUploaded}
              sub={`${Math.round((hostStats.resumesUploaded / hostStats.candidatesRsvp) * 100)}% of RSVP'd candidates`}
            />
          </div>
        </section>

        {/* Match Progress */}
        <section>
          <h2 className="text-lg font-bold mb-4" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
            Match Progress
          </h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <StatCard
              label="Avg Matches per Candidate"
              value={hostStats.avgMatchesPerCandidate}
              sub="job matches generated"
            />
            <StatCard
              label="Avg Match Score"
              value={`${hostStats.avgMatchScore}%`}
              sub="across all candidates"
            />
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className="flex justify-between items-center mb-3">
              <p className="text-sm font-medium" style={{ color: "#6B7280" }}>Match Review Progress</p>
              <p className="text-sm font-bold" style={{ color: "var(--dark)" }}>
                {hostStats.matchesReviewed} / {hostStats.matchesReviewed + hostStats.matchesPending} reviewed
              </p>
            </div>
            <div className="w-full rounded-full h-3" style={{ background: "var(--gold-light)" }}>
              <div
                className="h-3 rounded-full transition-all"
                style={{ width: `${matchProgress}%`, background: "var(--gold)" }}
              />
            </div>
            <div className="flex justify-between mt-2">
              <p className="text-xs" style={{ color: "#9CA3AF" }}>
                {hostStats.matchesPending} matches still pending review
              </p>
              <p className="text-xs font-semibold" style={{ color: "var(--gold)" }}>{matchProgress}% complete</p>
            </div>
          </div>
        </section>

        {/* Check In CTA */}
        <section>
          <div
            className="rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4"
            style={{ background: "var(--blue-light)" }}
          >
            <div>
              <h3 className="text-lg font-bold mb-1" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
                Fair Day Check-In
              </h3>
              <p className="text-sm" style={{ color: "#4B5563" }}>
                Mark candidates as arrived and track attendance in real time.
              </p>
            </div>
            <Link
              href="/host/checkin"
              className="whitespace-nowrap px-6 py-3 rounded-xl font-semibold text-white text-sm transition-all hover:opacity-90 hover:shadow-md"
              style={{ background: "var(--blue)" }}
            >
              Start Check-In →
            </Link>
          </div>
        </section>

      </div>
    </div>
  );
}
