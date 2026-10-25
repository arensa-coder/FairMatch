"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import {
  appointments,
  client,
  enrollments,
  initialDocuments,
  readinessAreas,
  trainings,
  type ClientDocument,
  type DocumentType,
  type Enrollment,
  type MilestoneStatus,
  type Training,
} from "@/lib/clientData";

type Tab = "overview" | "enrollments" | "readiness" | "trainings" | "documents";

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "enrollments", label: "Enrollments" },
  { id: "readiness", label: "Career Readiness" },
  { id: "trainings", label: "Trainings" },
  { id: "documents", label: "Documents" },
];

const allMilestones = readinessAreas.flatMap((a) => a.milestones);
const readinessPct = Math.round(
  (allMilestones.filter((m) => m.status === "done").length / allMilestones.length) * 100
);
const activeEnrollments = enrollments.filter((e) => e.status === "Active");

function SectionTitle({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-4">
      <h2 className="text-xl font-bold" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
        {title}
      </h2>
      {subtitle && <p className="text-sm mt-0.5" style={{ color: "#6B7280" }}>{subtitle}</p>}
    </div>
  );
}

function ProgressBar({ value, color = "var(--blue)" }: { value: number; color?: string }) {
  return (
    <div className="h-2 rounded-full w-full" style={{ background: "#E5E7EB" }}>
      <div className="h-2 rounded-full transition-all" style={{ width: `${value}%`, background: color }} />
    </div>
  );
}

function StatusPill({ status }: { status: Enrollment["status"] }) {
  const styles = {
    Active: { background: "#DCFCE7", color: "#16A34A" },
    Completed: { background: "#EFF6FF", color: "var(--blue)" },
    Exited: { background: "#F3F4F6", color: "#6B7280" },
  }[status];
  return (
    <span className="text-xs font-bold px-2 py-0.5 rounded-full whitespace-nowrap" style={styles}>
      {status}
    </span>
  );
}

function ReadinessRing({ value, size = 120 }: { value: number; size?: number }) {
  const r = (size - 14) / 2;
  const c = 2 * Math.PI * r;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={`${value}% career ready`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#E5E7EB" strokeWidth="10" />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="var(--gold)"
        strokeWidth="10"
        strokeLinecap="round"
        strokeDasharray={c}
        strokeDashoffset={c * (1 - value / 100)}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      <text x="50%" y="50%" textAnchor="middle" dominantBaseline="central" fontSize={size / 4.5} fontWeight="700" fill="var(--dark)">
        {value}%
      </text>
    </svg>
  );
}

function EnrollmentCard({ e }: { e: Enrollment }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
      <div className="flex items-start justify-between gap-3 mb-1">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: "#9CA3AF" }}>{e.category}</p>
          <h3 className="font-bold text-base leading-snug mt-0.5" style={{ fontFamily: "var(--font-playfair)" }}>{e.program}</h3>
          <p className="text-sm mt-0.5" style={{ color: "var(--blue)" }}>{e.provider}</p>
        </div>
        <StatusPill status={e.status} />
      </div>
      <p className="text-xs mt-2" style={{ color: "#6B7280" }}>
        {e.startDate} – {e.endDate ?? "Ongoing"}
      </p>
      {e.progress !== undefined && (
        <div className="mt-3">
          <div className="flex justify-between text-xs mb-1" style={{ color: "#6B7280" }}>
            <span>Progress</span>
            <span className="font-semibold">{e.progress}%</span>
          </div>
          <ProgressBar value={e.progress} />
        </div>
      )}
      {e.nextStep && (
        <p className="text-sm mt-3 rounded-xl px-3 py-2" style={{ background: "var(--gold-light)" }}>
          <span className="font-semibold">Next: </span>{e.nextStep}
        </p>
      )}
      {e.outcome && <p className="text-sm mt-3" style={{ color: "#4B5563" }}>{e.outcome}</p>}
    </div>
  );
}

function Overview({ go, requested }: { go: (t: Tab) => void; requested: Set<string> }) {
  const recommended = trainings.filter((t) => client.interestAreas.includes(t.interestArea)).slice(0, 2);
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <button onClick={() => go("enrollments")} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 text-left hover:shadow-md transition-all">
          <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: "#9CA3AF" }}>Active enrollments</p>
          <p className="text-3xl font-bold mt-1" style={{ color: "var(--blue)" }}>{activeEnrollments.length}</p>
          <p className="text-xs mt-1" style={{ color: "#6B7280" }}>{enrollments.length - activeEnrollments.length} past programs</p>
        </button>
        <button onClick={() => go("readiness")} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 text-left hover:shadow-md transition-all">
          <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: "#9CA3AF" }}>Career readiness</p>
          <p className="text-3xl font-bold mt-1" style={{ color: "var(--gold)" }}>{readinessPct}%</p>
          <p className="text-xs mt-1" style={{ color: "#6B7280" }}>
            {allMilestones.filter((m) => m.status === "done").length} of {allMilestones.length} milestones
          </p>
        </button>
        <button onClick={() => go("trainings")} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 text-left hover:shadow-md transition-all">
          <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: "#9CA3AF" }}>Trainings for you</p>
          <p className="text-3xl font-bold mt-1" style={{ color: "var(--henry)" }}>
            {trainings.filter((t) => client.interestAreas.includes(t.interestArea)).length}
          </p>
          <p className="text-xs mt-1" style={{ color: "#6B7280" }}>{requested.size} enrollment request{requested.size !== 1 ? "s" : ""} sent</p>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h3 className="font-bold mb-3" style={{ fontFamily: "var(--font-playfair)" }}>Coming up</h3>
          <ul className="space-y-3">
            {appointments.map((a) => (
              <li key={a.id} className="flex gap-3">
                <span className="mt-1.5 h-2 w-2 rounded-full flex-shrink-0" style={{ background: "var(--blue)" }} />
                <div>
                  <p className="text-sm font-semibold">{a.title}</p>
                  <p className="text-xs" style={{ color: "#6B7280" }}>{a.when} · {a.where}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h3 className="font-bold mb-3" style={{ fontFamily: "var(--font-playfair)" }}>Your career coach</h3>
          <p className="text-sm font-semibold">{client.careerCoach.name}</p>
          <p className="text-xs" style={{ color: "#6B7280" }}>{client.careerCoach.title} · {client.program}</p>
          <div className="mt-3 space-y-1 text-sm">
            <p><a className="underline" style={{ color: "var(--blue)" }} href={`mailto:${client.careerCoach.email}`}>{client.careerCoach.email}</a></p>
            <p style={{ color: "#4B5563" }}>{client.careerCoach.phone}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-bold" style={{ fontFamily: "var(--font-playfair)" }}>Recommended trainings</h3>
          <button onClick={() => go("trainings")} className="text-xs font-semibold" style={{ color: "var(--blue)" }}>See all →</button>
        </div>
        <ul className="divide-y divide-gray-100">
          {recommended.map((t) => (
            <li key={t.id} className="py-3 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="text-sm font-semibold">{t.title}</p>
                <p className="text-xs" style={{ color: "#6B7280" }}>{t.provider} · starts {t.startDate}</p>
              </div>
              <span className="text-xs whitespace-nowrap" style={{ color: "var(--henry)" }}>{t.seatsLeft} seats left</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function Enrollments() {
  const past = enrollments.filter((e) => e.status !== "Active");
  return (
    <div className="space-y-8">
      <section>
        <SectionTitle title="Active enrollments" subtitle="Programs you're participating in right now." />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {activeEnrollments.map((e) => <EnrollmentCard key={e.id} e={e} />)}
        </div>
      </section>
      <section>
        <SectionTitle title="Enrollment history" subtitle="Programs you've completed or exited." />
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <ul className="divide-y divide-gray-100">
            {past.map((e) => (
              <li key={e.id} className="p-4 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm">{e.program}</p>
                  <p className="text-xs" style={{ color: "#6B7280" }}>{e.provider}</p>
                  {e.outcome && <p className="text-xs mt-1" style={{ color: "#4B5563" }}>{e.outcome}</p>}
                </div>
                <p className="text-xs whitespace-nowrap" style={{ color: "#6B7280" }}>{e.startDate} – {e.endDate}</p>
                <StatusPill status={e.status} />
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}

const MILESTONE_ICON: Record<MilestoneStatus, { mark: string; bg: string; color: string; label: string }> = {
  done: { mark: "✓", bg: "#DCFCE7", color: "#16A34A", label: "Done" },
  "in-progress": { mark: "•", bg: "var(--gold-light)", color: "#A07A2C", label: "In progress" },
  todo: { mark: "", bg: "#F3F4F6", color: "#9CA3AF", label: "To do" },
};

function Readiness() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col sm:flex-row items-center gap-6">
        <ReadinessRing value={readinessPct} />
        <div className="flex-1 w-full">
          <h2 className="text-xl font-bold" style={{ fontFamily: "var(--font-playfair)" }}>Career readiness</h2>
          <p className="text-sm mt-0.5 mb-4" style={{ color: "#6B7280" }}>
            You&apos;re making strong progress toward your goal: <span className="font-semibold">Medical front desk / patient services</span>.
          </p>
          <div className="space-y-3">
            {readinessAreas.map((a) => {
              const done = a.milestones.filter((m) => m.status === "done").length;
              const pct = Math.round((done / a.milestones.length) * 100);
              return (
                <div key={a.id}>
                  <div className="flex justify-between text-xs mb-1" style={{ color: "#6B7280" }}>
                    <span className="font-medium">{a.name}</span>
                    <span>{done}/{a.milestones.length}</span>
                  </div>
                  <ProgressBar value={pct} color={pct === 100 ? "#16A34A" : "var(--blue)"} />
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {readinessAreas.map((a) => (
          <div key={a.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <h3 className="font-bold mb-3" style={{ fontFamily: "var(--font-playfair)" }}>{a.name}</h3>
            <ul className="space-y-3">
              {a.milestones.map((m) => {
                const s = MILESTONE_ICON[m.status];
                return (
                  <li key={m.id} className="flex gap-3 items-start">
                    <span
                      className="h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                      style={{ background: s.bg, color: s.color, border: m.status === "todo" ? "1.5px dashed #D1D5DB" : "none" }}
                      title={s.label}
                    >
                      {s.mark}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium" style={{ color: m.status === "todo" ? "#6B7280" : "var(--dark)" }}>{m.label}</p>
                      <p className="text-xs" style={{ color: "#9CA3AF" }}>{m.date ? `Completed ${m.date}` : m.detail ?? s.label}</p>
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

function TrainingCard({ t, requested, onRequest }: { t: Training; requested: boolean; onRequest: () => void }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 flex flex-col">
      <div className="flex items-start justify-between gap-3">
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: "var(--blue-light)", color: "var(--dark)" }}>
          {t.interestArea}
        </span>
        <span className="text-xs whitespace-nowrap" style={{ color: t.seatsLeft <= 5 ? "var(--henry)" : "#6B7280" }}>
          {t.seatsLeft} seats left
        </span>
      </div>
      <h3 className="font-bold text-base leading-snug mt-2" style={{ fontFamily: "var(--font-playfair)" }}>{t.title}</h3>
      <p className="text-sm" style={{ color: "var(--blue)" }}>{t.provider}</p>
      <p className="text-sm mt-2 leading-relaxed" style={{ color: "#4B5563" }}>{t.description}</p>
      <dl className="grid grid-cols-2 gap-x-3 gap-y-1.5 text-xs mt-3" style={{ color: "#6B7280" }}>
        <div><dt className="font-semibold" style={{ color: "#9CA3AF" }}>Starts</dt><dd>{t.startDate}</dd></div>
        <div><dt className="font-semibold" style={{ color: "#9CA3AF" }}>Length</dt><dd>{t.duration} · {t.format}</dd></div>
        <div className="col-span-2"><dt className="font-semibold" style={{ color: "#9CA3AF" }}>Schedule</dt><dd>{t.schedule}</dd></div>
        <div><dt className="font-semibold" style={{ color: "#9CA3AF" }}>Cost</dt><dd>{t.cost}</dd></div>
        {t.credential && <div><dt className="font-semibold" style={{ color: "#9CA3AF" }}>Credential</dt><dd>{t.credential}</dd></div>}
      </dl>
      <div className="flex-1" />
      <button
        onClick={onRequest}
        disabled={requested}
        className="mt-4 w-full py-2 rounded-xl text-sm font-semibold transition-all"
        style={requested ? { background: "#DCFCE7", color: "#16A34A" } : { background: "var(--blue)", color: "#fff" }}
      >
        {requested ? "✓ Request sent to your coach" : "Request to enroll"}
      </button>
    </div>
  );
}

function Trainings({ requested, onRequest }: { requested: Set<string>; onRequest: (id: string) => void }) {
  const [filter, setFilter] = useState<string>("My interests");
  const areas = ["My interests", ...client.interestAreas, "All trainings"];
  const shown = trainings.filter((t) =>
    filter === "All trainings" ? true : filter === "My interests" ? client.interestAreas.includes(t.interestArea) : t.interestArea === filter
  );
  return (
    <div>
      <SectionTitle title="Available trainings" subtitle="Openings that match your interest areas. Requests go to your career coach for approval." />
      <div className="flex gap-2 overflow-x-auto pb-1 mb-4 -mx-1 px-1">
        {areas.map((a) => (
          <button
            key={a}
            onClick={() => setFilter(a)}
            className="whitespace-nowrap text-xs px-3 py-1.5 rounded-full font-medium transition-all flex-shrink-0"
            style={filter === a ? { background: "var(--blue)", color: "#fff" } : { background: "#fff", color: "#6B7280", border: "1px solid #E5E7EB" }}
          >
            {a}
          </button>
        ))}
      </div>
      <p className="text-xs font-medium mb-3" style={{ color: "#9CA3AF" }}>{shown.length} training{shown.length !== 1 ? "s" : ""}</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {shown.map((t) => (
          <TrainingCard key={t.id} t={t} requested={requested.has(t.id)} onRequest={() => onRequest(t.id)} />
        ))}
      </div>
    </div>
  );
}

function formatSize(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const DOC_TYPES: DocumentType[] = ["Resume", "Cover Letter", "Certificate", "Other"];

function Documents({
  docs,
  setDocs,
}: {
  docs: ClientDocument[];
  setDocs: React.Dispatch<React.SetStateAction<ClientDocument[]>>;
}) {
  const [uploadType, setUploadType] = useState<DocumentType>("Resume");
  const [preview, setPreview] = useState<ClientDocument | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const addFiles = (files: FileList | null) => {
    if (!files) return;
    const today = new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    const added = Array.from(files).map((f, i) => ({
      id: `u${Date.now()}-${i}`,
      name: f.name,
      type: uploadType,
      uploaded: today,
      size: formatSize(f.size),
      sharedWithCoach: false,
      url: URL.createObjectURL(f),
    }));
    setDocs((prev) => [...added, ...prev]);
  };

  const remove = (id: string) => {
    setDocs((prev) => {
      const doc = prev.find((d) => d.id === id);
      if (doc?.url) URL.revokeObjectURL(doc.url);
      return prev.filter((d) => d.id !== id);
    });
  };

  const toggleShare = (id: string) =>
    setDocs((prev) => prev.map((d) => (d.id === id ? { ...d, sharedWithCoach: !d.sharedWithCoach } : d)));

  return (
    <div className="space-y-6">
      <SectionTitle title="My documents" subtitle="Keep your resumes, cover letters, and certificates in one place and choose what your coach can see." />

      <div
        className="rounded-2xl border-2 border-dashed p-6 text-center bg-white"
        style={{ borderColor: "var(--blue-light)" }}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          addFiles(e.dataTransfer.files);
        }}
      >
        <p className="text-sm font-semibold">Drag a file here, or</p>
        <div className="mt-3 flex flex-col sm:flex-row items-center justify-center gap-2">
          <label className="text-xs" style={{ color: "#6B7280" }} htmlFor="doc-type">Save as</label>
          <select
            id="doc-type"
            value={uploadType}
            onChange={(e) => setUploadType(e.target.value as DocumentType)}
            className="text-sm rounded-xl border border-gray-200 px-3 py-2 bg-white"
          >
            {DOC_TYPES.map((t) => <option key={t}>{t}</option>)}
          </select>
          <button
            onClick={() => inputRef.current?.click()}
            className="text-sm px-4 py-2 rounded-xl font-semibold text-white"
            style={{ background: "var(--blue)" }}
          >
            Choose file
          </button>
          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.txt,.png,.jpg"
            className="hidden"
            onChange={(e) => {
              addFiles(e.target.files);
              e.target.value = "";
            }}
          />
        </div>
        <p className="text-xs mt-2" style={{ color: "#9CA3AF" }}>PDF, Word, or image · Demo only: files stay in this browser tab</p>
      </div>

      {DOC_TYPES.map((type) => {
        const group = docs.filter((d) => d.type === type);
        if (group.length === 0) return null;
        return (
          <section key={type}>
            <h3 className="text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: "#9CA3AF" }}>
              {type === "Other" ? "Other" : `${type}s`} · {group.length}
            </h3>
            <ul className="bg-white rounded-2xl border border-gray-100 shadow-sm divide-y divide-gray-100">
              {group.map((d) => (
                <li key={d.id} className="p-4 flex flex-col sm:flex-row sm:items-center gap-3">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <span className="h-10 w-10 rounded-xl flex items-center justify-center text-[10px] font-bold flex-shrink-0" style={{ background: "var(--gold-light)", color: "#A07A2C" }}>
                      {d.name.split(".").pop()?.toUpperCase()}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold truncate">{d.name}</p>
                      <p className="text-xs" style={{ color: "#6B7280" }}>
                        {d.uploaded} · {d.size}{d.note ? ` · ${d.note}` : ""}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <button
                      onClick={() => toggleShare(d.id)}
                      className="text-xs px-3 py-1.5 rounded-full font-medium"
                      style={d.sharedWithCoach ? { background: "#DCFCE7", color: "#16A34A" } : { background: "#F3F4F6", color: "#6B7280" }}
                      aria-pressed={d.sharedWithCoach}
                    >
                      {d.sharedWithCoach ? "Shared with coach" : "Private"}
                    </button>
                    {d.url ? (
                      <a href={d.url} target="_blank" rel="noreferrer" className="text-xs px-3 py-1.5 rounded-full border border-gray-200 hover:bg-gray-50" style={{ color: "var(--blue)" }}>
                        View
                      </a>
                    ) : (
                      <button onClick={() => setPreview(d)} className="text-xs px-3 py-1.5 rounded-full border border-gray-200 hover:bg-gray-50" style={{ color: "var(--blue)" }}>
                        View
                      </button>
                    )}
                    <button onClick={() => remove(d.id)} className="text-xs px-3 py-1.5 rounded-full border border-gray-200 hover:bg-gray-50" style={{ color: "var(--henry)" }}>
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        );
      })}

      {preview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(44,51,64,0.5)" }} onClick={() => setPreview(null)}>
          <div className="bg-white rounded-2xl max-w-md w-full p-6" onClick={(e) => e.stopPropagation()}>
            <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: "#9CA3AF" }}>{preview.type}</p>
            <h3 className="font-bold mt-1 break-all" style={{ fontFamily: "var(--font-playfair)" }}>{preview.name}</h3>
            <div className="mt-4 rounded-xl border border-gray-100 p-4 space-y-2" style={{ background: "var(--bg)" }}>
              <div className="h-3 w-1/2 rounded" style={{ background: "#D1D5DB" }} />
              <div className="h-2 w-1/3 rounded" style={{ background: "#E5E7EB" }} />
              {[90, 80, 95, 70, 85, 60].map((w, i) => (
                <div key={i} className="h-2 rounded" style={{ width: `${w}%`, background: "#E5E7EB" }} />
              ))}
            </div>
            <p className="text-xs mt-3" style={{ color: "#6B7280" }}>Sample document: the preview is a placeholder in this demo.</p>
            <button onClick={() => setPreview(null)} className="mt-4 w-full py-2 rounded-xl text-sm font-semibold text-white" style={{ background: "var(--blue)" }}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ClientPortalPage() {
  const [tab, setTab] = useState<Tab>("overview");
  const [requested, setRequested] = useState<Set<string>>(new Set());
  const [docs, setDocs] = useState<ClientDocument[]>(initialDocuments);

  const request = (id: string) => setRequested((prev) => new Set(prev).add(id));

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)" }}>
      <nav className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <svg width="28" height="28" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="22,3 40,38 4,38" fill="#5B8ED6" opacity="0.9"/>
            <polygon points="22,12 34,38 10,38" fill="#B8D9E8" opacity="0.8"/>
            <polygon points="16,24 28,24 22,38" fill="#D4AF6A"/>
          </svg>
          <span className="font-bold" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>FairMatch</span>
          <span className="hidden sm:inline text-xs px-2 py-0.5 rounded-full" style={{ background: "var(--blue-light)" }}>Client Portal</span>
        </div>
        <Link href="/" className="text-xs px-3 py-1.5 rounded-full border border-gray-200 hover:bg-gray-50 transition-colors" style={{ color: "#6B7280" }}>
          Sign Out
        </Link>
      </nav>

      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
            Welcome back, {client.name.split(" ")[0]}
          </h1>
          <p className="text-sm mt-1" style={{ color: "#6B7280" }}>
            {client.program} · Client ID {client.clientId}
          </p>
        </div>

        <div className="flex gap-1 overflow-x-auto border-b border-gray-200 mb-6 -mx-1 px-1" role="tablist">
          {TABS.map((t) => (
            <button
              key={t.id}
              role="tab"
              aria-selected={tab === t.id}
              onClick={() => setTab(t.id)}
              className="whitespace-nowrap text-sm px-4 py-2.5 font-medium transition-colors -mb-px border-b-2"
              style={tab === t.id ? { borderColor: "var(--blue)", color: "var(--blue)" } : { borderColor: "transparent", color: "#6B7280" }}
            >
              {t.label}
            </button>
          ))}
        </div>

        {tab === "overview" && <Overview go={setTab} requested={requested} />}
        {tab === "enrollments" && <Enrollments />}
        {tab === "readiness" && <Readiness />}
        {tab === "trainings" && <Trainings requested={requested} onRequest={request} />}
        {tab === "documents" && <Documents docs={docs} setDocs={setDocs} />}
      </div>
    </div>
  );
}
