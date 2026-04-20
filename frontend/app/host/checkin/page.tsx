"use client";

import Link from "next/link";
import { useState } from "react";
import { candidates, fair, type Candidate } from "@/lib/data";

const BARRIER_COLORS: Record<string, string> = {
  Housing: "#F59E0B",
  Transportation: "#3B82F6",
  Childcare: "#8B5CF6",
  Language: "#EC4899",
};

function BarrierTag({ label }: { label: string }) {
  const color = BARRIER_COLORS[label] ?? "#6B7280";
  return (
    <span
      className="text-xs px-2 py-0.5 rounded-full font-medium"
      style={{ background: color + "18", color }}
    >
      {label}
    </span>
  );
}

export default function CheckInPage() {
  const [checkedIn, setCheckedIn] = useState<Set<string>>(new Set());
  const [search, setSearch] = useState("");

  const filtered = candidates.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  const toggle = (id: string) => {
    setCheckedIn((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const arrivedCount = checkedIn.size;

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)" }}>
      {/* Nav */}
      <nav className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/host" className="text-sm flex items-center gap-1 hover:opacity-70 transition-opacity" style={{ color: "var(--blue)" }}>
            ← Dashboard
          </Link>
        </div>
        <div className="text-right hidden sm:block">
          <p className="text-sm font-semibold" style={{ color: "var(--henry)" }}>Henry Street Settlement</p>
          <p className="text-xs" style={{ color: "#9CA3AF" }}>Fair Day Check-In</p>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold mb-1" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
            Candidate Check-In
          </h1>
          <p className="text-sm" style={{ color: "#6B7280" }}>{fair.date} · {fair.location}</p>
        </div>

        {/* Live Counter */}
        <div className="rounded-2xl p-5 text-white flex items-center justify-between" style={{ background: "var(--henry)" }}>
          <div>
            <p className="text-sm opacity-80 uppercase tracking-wide font-medium">Arrived Today</p>
            <p className="text-4xl font-bold mt-1" style={{ fontFamily: "var(--font-playfair)" }}>
              {arrivedCount} <span className="text-xl font-normal opacity-70">/ {candidates.length}</span>
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm opacity-80">Not yet arrived</p>
            <p className="text-2xl font-bold mt-1">{candidates.length - arrivedCount}</p>
          </div>
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Search by name…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:border-transparent"
          style={{ "--tw-ring-color": "var(--blue)" } as React.CSSProperties}
        />

        {/* Candidate List */}
        <div className="space-y-3">
          {filtered.map((c: Candidate) => {
            const arrived = checkedIn.has(c.id);
            return (
              <div
                key={c.id}
                className="bg-white rounded-2xl p-4 flex items-center gap-4 shadow-sm border transition-all"
                style={{ borderColor: arrived ? "var(--henry)" : "#F3F4F6" }}
              >
                {/* Avatar */}
                <div
                  className="w-11 h-11 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
                  style={{ background: arrived ? "var(--henry)" : "var(--blue-light)", color: arrived ? "#fff" : "var(--blue)" }}
                >
                  {c.name.split(" ").map((n) => n[0]).join("")}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="font-semibold text-sm" style={{ color: "var(--dark)" }}>{c.name}</p>
                    {c.resumeUploaded && (
                      <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "#DCFCE7", color: "#16A34A" }}>
                        Resume ✓
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                    <span className="text-xs" style={{ color: "#9CA3AF" }}>{c.matchCount} matches</span>
                    {c.barriers.map((b) => <BarrierTag key={b} label={b} />)}
                  </div>
                </div>

                <button
                  onClick={() => toggle(c.id)}
                  className="flex-shrink-0 px-4 py-2 rounded-xl text-sm font-semibold transition-all"
                  style={
                    arrived
                      ? { background: "var(--henry)", color: "#fff" }
                      : { background: "#F3F4F6", color: "#6B7280" }
                  }
                >
                  {arrived ? "✓ Arrived" : "Check In"}
                </button>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
