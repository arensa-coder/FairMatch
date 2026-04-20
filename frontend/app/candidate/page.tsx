"use client";

import Link from "next/link";
import { useState } from "react";
import { demoCandidate, fair, type Job } from "@/lib/data";

const INDUSTRIES = ["All", "Healthcare", "Logistics", "Retail", "Social Services", "Education / Social Services", "Food Service", "Security", "Transportation", "Property Management", "Healthcare Administration"];

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 80 ? "#16A34A" : score >= 65 ? "var(--blue)" : "#9CA3AF";
  const bg = score >= 80 ? "#DCFCE7" : score >= 65 ? "#EFF6FF" : "#F3F4F6";
  return (
    <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: bg, color }}>
      {score}% match
    </span>
  );
}

function JobCard({ job, saved, onSave }: { job: Job; saved: boolean; onSave: () => void }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden transition-all hover:shadow-md">
      <div className="p-5">
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-base leading-snug" style={{ color: "var(--dark)", fontFamily: "var(--font-playfair)" }}>
              {job.title}
            </h3>
            <p className="text-sm font-medium mt-0.5" style={{ color: "var(--blue)" }}>{job.employer}</p>
          </div>
          {job.matchScore && <ScoreBadge score={job.matchScore} />}
        </div>

        <div className="flex flex-wrap gap-2 mb-3 text-xs" style={{ color: "#6B7280" }}>
          <span>{job.pay}</span>
          <span>·</span>
          <span>{job.type}</span>
          <span>·</span>
          <span>{job.location}</span>
        </div>

        <p className="text-sm leading-relaxed" style={{ color: "#4B5563" }}>
          {expanded ? job.description : job.description.slice(0, 100) + "…"}
        </p>

        {expanded && (
          <div className="mt-3">
            <p className="text-xs font-semibold uppercase tracking-wide mb-1.5" style={{ color: "#9CA3AF" }}>Requirements</p>
            <ul className="space-y-1">
              {job.requirements.map((r) => (
                <li key={r} className="text-sm flex gap-2" style={{ color: "#4B5563" }}>
                  <span style={{ color: "var(--gold)" }}>•</span> {r}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="px-5 pb-4 flex gap-2">
        <button
          onClick={() => setExpanded((e) => !e)}
          className="flex-1 py-2 rounded-xl text-sm font-medium border border-gray-200 hover:bg-gray-50 transition-colors"
          style={{ color: "#6B7280" }}
        >
          {expanded ? "Show less" : "Learn more"}
        </button>
        <button
          onClick={onSave}
          className="flex-1 py-2 rounded-xl text-sm font-semibold transition-all"
          style={
            saved
              ? { background: "var(--gold)", color: "#fff" }
              : { background: "var(--gold-light)", color: "var(--dark)" }
          }
        >
          {saved ? "★ Saved" : "☆ Save"}
        </button>
      </div>
    </div>
  );
}

export default function CandidatePage() {
  const [saved, setSaved] = useState<Set<string>>(new Set());
  const [industry, setIndustry] = useState("All");
  const jobs = demoCandidate.matchedJobs;

  const toggle = (id: string) => {
    setSaved((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const filtered = industry === "All" ? jobs : jobs.filter((j) => j.industry === industry);
  const uniqueIndustries = ["All", ...Array.from(new Set(jobs.map((j) => j.industry)))];

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)" }}>
      {/* Nav */}
      <nav className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <svg width="28" height="28" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="22,3 40,38 4,38" fill="#5B8ED6" opacity="0.9"/>
            <polygon points="22,12 34,38 10,38" fill="#B8D9E8" opacity="0.8"/>
            <polygon points="16,24 28,24 22,38" fill="#D4AF6A"/>
          </svg>
          <span className="font-bold" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>FairMatch</span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/candidate/checkin"
            className="text-sm px-4 py-2 rounded-xl font-semibold text-white transition-all hover:opacity-90"
            style={{ background: "var(--henry)" }}
          >
            Fair Day Check-In
          </Link>
          <Link href="/" className="text-xs px-3 py-1.5 rounded-full border border-gray-200 hover:bg-gray-50 transition-colors" style={{ color: "#6B7280" }}>
            Sign Out
          </Link>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">

        {/* Welcome */}
        <div>
          <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
            Hi, {demoCandidate.name.split(" ")[0]} 👋
          </h1>
          <p className="text-sm mt-1" style={{ color: "#6B7280" }}>
            Here are your top job matches for the{" "}
            <span className="font-medium" style={{ color: "var(--henry)" }}>Henry Street Spring Job Fair</span>
            {" "}on {fair.date}.
          </p>
        </div>

        {/* Fair Info Banner */}
        <div className="rounded-2xl p-4 flex items-center justify-between gap-4 border"
          style={{ background: "var(--blue-light)", borderColor: "#93C5FD20" }}>
          <div>
            <p className="text-sm font-semibold" style={{ color: "var(--dark)" }}>{fair.date} · {fair.time}</p>
            <p className="text-xs mt-0.5" style={{ color: "#4B5563" }}>{fair.location}</p>
          </div>
          <Link
            href="/candidate/checkin"
            className="text-xs font-semibold px-3 py-2 rounded-xl whitespace-nowrap text-white"
            style={{ background: "var(--blue)" }}
          >
            Day-of QR →
          </Link>
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
          {uniqueIndustries.map((ind) => (
            <button
              key={ind}
              onClick={() => setIndustry(ind)}
              className="whitespace-nowrap text-xs px-3 py-1.5 rounded-full font-medium transition-all flex-shrink-0"
              style={
                industry === ind
                  ? { background: "var(--blue)", color: "#fff" }
                  : { background: "#fff", color: "#6B7280", border: "1px solid #E5E7EB" }
              }
            >
              {ind}
            </button>
          ))}
        </div>

        {/* Job Count */}
        <p className="text-xs font-medium" style={{ color: "#9CA3AF" }}>
          {filtered.length} match{filtered.length !== 1 ? "es" : ""} · {saved.size} saved
        </p>

        {/* Job Cards */}
        <div className="space-y-4">
          {filtered.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              saved={saved.has(job.id)}
              onSave={() => toggle(job.id)}
            />
          ))}
        </div>

      </div>
    </div>
  );
}
