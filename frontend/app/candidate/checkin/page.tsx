"use client";

import Link from "next/link";
import { demoCandidate, fair } from "@/lib/data";
import { useState } from "react";

function QRPlaceholder() {
  const cells = Array.from({ length: 21 * 21 }, (_, i) => {
    const row = Math.floor(i / 21);
    const col = i % 21;
    const isFinderCorner =
      (row < 7 && col < 7) ||
      (row < 7 && col > 13) ||
      (row > 13 && col < 7);
    const isRandom = Math.random() > 0.55;
    return isFinderCorner || isRandom;
  });

  return (
    <div className="inline-block p-4 bg-white rounded-2xl shadow-md">
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(21, 10px)",
          gap: "1px",
        }}
      >
        {cells.map((filled, i) => (
          <div
            key={i}
            style={{
              width: 10,
              height: 10,
              background: filled ? "#2C3340" : "#fff",
              borderRadius: 1,
            }}
          />
        ))}
      </div>
    </div>
  );
}

export default function CandidateCheckin() {
  const [checkedIn, setCheckedIn] = useState(false);

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "var(--bg)" }}>
      {/* Nav */}
      <nav className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
        <Link href="/candidate" className="text-sm flex items-center gap-1 hover:opacity-70 transition-opacity" style={{ color: "var(--blue)" }}>
          ← My Matches
        </Link>
        <p className="text-sm font-semibold" style={{ color: "var(--dark)", fontFamily: "var(--font-playfair)" }}>Check-In</p>
      </nav>

      <div className="flex-1 flex flex-col items-center justify-center px-4 py-10 space-y-8 text-center">

        {!checkedIn ? (
          <>
            {/* Identity Card */}
            <div className="w-full max-w-sm bg-white rounded-2xl shadow-md p-6 border border-gray-100">
              <div
                className="w-16 h-16 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-3"
                style={{ background: "var(--blue)" }}
              >
                {demoCandidate.name.split(" ").map((n) => n[0]).join("")}
              </div>
              <h2 className="text-xl font-bold mb-0.5" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
                {demoCandidate.name}
              </h2>
              <p className="text-sm" style={{ color: "#6B7280" }}>Job Seeker · FairMatch ID #{demoCandidate.id}</p>
            </div>

            {/* QR Code */}
            <div className="flex flex-col items-center gap-3">
              <p className="text-sm font-medium" style={{ color: "#6B7280" }}>
                Show this to the check-in desk
              </p>
              <QRPlaceholder />
              <p className="text-xs font-mono px-3 py-1 rounded-full" style={{ background: "var(--gold-light)", color: "var(--dark)" }}>
                FM-2026-{demoCandidate.id.toUpperCase()}-HSS
              </p>
            </div>

            {/* Fair Details */}
            <div className="w-full max-w-sm rounded-2xl p-5 text-left" style={{ background: "var(--blue-light)" }}>
              <p className="text-xs font-semibold uppercase tracking-wide mb-3" style={{ color: "var(--blue)" }}>Fair Details</p>
              <div className="space-y-2 text-sm" style={{ color: "var(--dark)" }}>
                <div className="flex gap-2">
                  <span>📅</span>
                  <span>{fair.date} · {fair.time}</span>
                </div>
                <div className="flex gap-2">
                  <span>📍</span>
                  <span>{fair.location}</span>
                </div>
                <div className="flex gap-2">
                  <span>💼</span>
                  <span>{demoCandidate.matchedJobs.length} job matches waiting for you</span>
                </div>
              </div>
            </div>

            {/* Simulate check-in */}
            <button
              onClick={() => setCheckedIn(true)}
              className="w-full max-w-sm py-4 rounded-2xl font-bold text-white text-base transition-all hover:opacity-90 hover:shadow-lg"
              style={{ background: "var(--henry)" }}
            >
              Simulate Scan ✓
            </button>
          </>
        ) : (
          <>
            {/* Success State */}
            <div
              className="w-24 h-24 rounded-full flex items-center justify-center text-4xl mx-auto"
              style={{ background: "#DCFCE7" }}
            >
              ✓
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-2" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
                You&apos;re checked in!
              </h2>
              <p className="text-sm" style={{ color: "#6B7280" }}>
                Welcome to the {fair.hostOrg} Job Fair, {demoCandidate.name.split(" ")[0]}.
              </p>
            </div>

            <div className="w-full max-w-sm rounded-2xl p-5" style={{ background: "var(--gold-light)" }}>
              <p className="text-sm font-semibold mb-2" style={{ color: "var(--dark)" }}>Your check-in time</p>
              <p className="text-2xl font-bold" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
                {new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </p>
              <p className="text-xs mt-1" style={{ color: "#6B7280" }}>{fair.date}</p>
            </div>

            <Link
              href="/candidate"
              className="w-full max-w-sm block py-4 rounded-2xl font-bold text-white text-center text-base transition-all hover:opacity-90"
              style={{ background: "var(--blue)" }}
            >
              View My Matches →
            </Link>

            <button
              onClick={() => setCheckedIn(false)}
              className="text-xs underline"
              style={{ color: "#9CA3AF" }}
            >
              Reset demo
            </button>
          </>
        )}
      </div>
    </div>
  );
}
