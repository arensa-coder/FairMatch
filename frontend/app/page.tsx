import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4" style={{ background: "var(--bg)" }}>
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-3 mb-4">
          <svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="22,3 40,38 4,38" fill="#5B8ED6" opacity="0.9"/>
            <polygon points="22,12 34,38 10,38" fill="#B8D9E8" opacity="0.8"/>
            <polygon points="16,24 28,24 22,38" fill="#D4AF6A"/>
          </svg>
          <h1 className="text-4xl font-bold tracking-tight" style={{ fontFamily: "var(--font-playfair)", color: "var(--dark)" }}>
            FairMatch
          </h1>
        </div>
        <p className="text-base" style={{ color: "#6B7280" }}>
          Smarter job fair matching — powered by{" "}
          <span style={{ color: "var(--blue)" }} className="font-medium">Arensa Consulting</span>
        </p>
      </div>

      <div className="w-full max-w-md space-y-4">
        <p className="text-center text-xs font-semibold uppercase tracking-widest mb-6" style={{ color: "#9CA3AF" }}>
          Sign in as
        </p>

        <Link href="/host" className="block w-full">
          <div
            className="rounded-2xl p-6 text-center transition-all hover:scale-[1.02] hover:shadow-lg cursor-pointer border-2 bg-white"
            style={{ borderColor: "var(--henry)" }}
          >
            <div className="text-3xl mb-2">🏢</div>
            <h2 className="text-xl font-bold mb-1" style={{ color: "var(--henry)", fontFamily: "var(--font-playfair)" }}>
              Host Organization
            </h2>
            <p className="text-sm" style={{ color: "#6B7280" }}>
              Manage your fair, review matches, check in candidates
            </p>
          </div>
        </Link>

        <Link href="/candidate" className="block w-full">
          <div
            className="rounded-2xl p-6 text-center transition-all hover:scale-[1.02] hover:shadow-lg cursor-pointer border-2 bg-white"
            style={{ borderColor: "var(--blue)" }}
          >
            <div className="text-3xl mb-2">👤</div>
            <h2 className="text-xl font-bold mb-1" style={{ color: "var(--blue)", fontFamily: "var(--font-playfair)" }}>
              Job Seeker
            </h2>
            <p className="text-sm" style={{ color: "#6B7280" }}>
              Browse your matched jobs and check in on fair day
            </p>
          </div>
        </Link>
      </div>

      <p className="mt-12 text-xs" style={{ color: "#9CA3AF" }}>
        Demo · Henry Street Settlement Spring Job Fair 2026
      </p>
    </main>
  );
}
