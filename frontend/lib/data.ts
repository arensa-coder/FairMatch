export const fair = {
  name: "Henry Street Settlement Spring Job Fair",
  date: "Thursday, May 15, 2026",
  time: "10:00 AM – 2:00 PM",
  location: "Henry Street Settlement, 265 Henry St, New York, NY 10002",
  hostOrg: "Henry Street Settlement",
};

export const hostStats = {
  employersCommitted: 14,
  candidatesRsvp: 52,
  resumesUploaded: 38,
  avgMatchesPerCandidate: 3.6,
  avgMatchScore: 74,
  matchesReviewed: 134,
  matchesPending: 53,
};

export interface Job {
  id: string;
  title: string;
  employer: string;
  industry: string;
  pay: string;
  type: "Full-Time" | "Part-Time" | "Temp-to-Hire";
  location: string;
  description: string;
  requirements: string[];
  matchScore?: number;
}

export const jobs: Job[] = [
  {
    id: "j1",
    title: "Customer Service Representative",
    employer: "NYC Health + Hospitals",
    industry: "Healthcare",
    pay: "$19–$22/hr",
    type: "Full-Time",
    location: "Manhattan, NY",
    description:
      "Greet patients and visitors, answer inquiries, and support administrative staff at a busy community health center.",
    requirements: ["HS diploma or GED", "Bilingual (English/Spanish) preferred", "Customer service experience a plus"],
    matchScore: 88,
  },
  {
    id: "j2",
    title: "Warehouse Associate",
    employer: "Amazon Logistics",
    industry: "Logistics",
    pay: "$20/hr",
    type: "Full-Time",
    location: "Bronx, NY",
    description:
      "Pick, pack, and ship customer orders in a fast-paced fulfillment center. No experience required — full training provided.",
    requirements: ["Ability to lift 50 lbs", "Reliable transportation", "Flexible schedule"],
    matchScore: 81,
  },
  {
    id: "j3",
    title: "Home Health Aide",
    employer: "VNS Health",
    industry: "Healthcare",
    pay: "$18.50/hr",
    type: "Full-Time",
    location: "Brooklyn, NY",
    description:
      "Provide personal care and daily living assistance to elderly and disabled clients in their homes across the five boroughs.",
    requirements: ["HHA or PCA certification (training available)", "Compassionate, patient demeanor", "Bilingual a plus"],
    matchScore: 79,
  },
  {
    id: "j4",
    title: "Building Maintenance Technician",
    employer: "BRT Realty Trust",
    industry: "Property Management",
    pay: "$24–$28/hr",
    type: "Full-Time",
    location: "Queens, NY",
    description:
      "Perform preventive and corrective maintenance on residential apartment buildings including plumbing, electrical, and HVAC.",
    requirements: ["2+ years maintenance experience", "EPA 608 certification preferred", "Valid driver's license"],
    matchScore: 72,
  },
  {
    id: "j5",
    title: "Retail Sales Associate",
    employer: "Burlington Coat Factory",
    industry: "Retail",
    pay: "$17/hr",
    type: "Part-Time",
    location: "Lower East Side, NY",
    description:
      "Assist customers, maintain merchandise displays, and operate POS systems in a high-volume retail environment.",
    requirements: ["Friendly, outgoing personality", "Flexible weekend availability", "Retail or cash-handling experience a plus"],
    matchScore: 68,
  },
  {
    id: "j6",
    title: "Food Service Worker",
    employer: "NYC Department of Education",
    industry: "Food Service",
    pay: "$18.11/hr",
    type: "Full-Time",
    location: "Manhattan, NY",
    description:
      "Prepare and serve meals to K-12 students in NYC public school cafeterias. City benefits and union membership included.",
    requirements: ["Food handler certification (provided)", "Ability to stand for extended periods", "No experience required"],
    matchScore: 65,
  },
  {
    id: "j7",
    title: "Data Entry Clerk",
    employer: "MetroPlusHealth",
    industry: "Healthcare Administration",
    pay: "$20–$23/hr",
    type: "Full-Time",
    location: "Midtown, NY",
    description:
      "Accurately input and maintain member data in health plan systems. Hybrid schedule available after 90-day probation period.",
    requirements: ["Typing 45 WPM+", "Strong attention to detail", "MS Office proficiency"],
    matchScore: 62,
  },
  {
    id: "j8",
    title: "Security Officer",
    employer: "Allied Universal",
    industry: "Security",
    pay: "$19/hr",
    type: "Full-Time",
    location: "Various NYC locations",
    description:
      "Monitor premises, patrol assigned areas, and respond to emergencies at commercial and residential sites across the city.",
    requirements: ["NYS Security Guard license (training supported)", "Clean background check", "Physical fitness"],
    matchScore: 58,
  },
  {
    id: "j9",
    title: "Early Childhood Assistant Teacher",
    employer: "Henry Street Settlement",
    industry: "Education / Social Services",
    pay: "$21–$24/hr",
    type: "Full-Time",
    location: "Lower East Side, NY",
    description:
      "Support lead teachers in Head Start and pre-K classrooms. Work with children ages 3–5 in a nurturing, community-based setting.",
    requirements: ["CDA credential or 12 college credits in ECE", "Bilingual (English/Spanish or Chinese) strongly preferred", "Patience and creativity"],
    matchScore: 55,
  },
  {
    id: "j10",
    title: "Delivery Driver",
    employer: "GreenRide Logistics",
    industry: "Transportation",
    pay: "$21/hr + tips",
    type: "Full-Time",
    location: "Brooklyn & Queens, NY",
    description:
      "Deliver packages and grocery orders to residential customers using a company vehicle. Routes assigned nightly.",
    requirements: ["Valid NYS driver's license (no major violations)", "Smartphone required", "Ability to lift 40 lbs"],
    matchScore: 51,
  },
  {
    id: "j11",
    title: "Accounts Payable Clerk",
    employer: "Montefiore Medical Center",
    industry: "Healthcare Administration",
    pay: "$22–$25/hr",
    type: "Full-Time",
    location: "Bronx, NY",
    description:
      "Process vendor invoices, reconcile accounts, and support the finance team at one of NYC's largest nonprofit hospital systems.",
    requirements: ["1+ year AP or bookkeeping experience", "QuickBooks or SAP familiarity", "Associate degree preferred"],
    matchScore: 48,
  },
  {
    id: "j12",
    title: "Bilingual Case Manager Assistant",
    employer: "Catholic Charities NYC",
    industry: "Social Services",
    pay: "$20/hr",
    type: "Full-Time",
    location: "Lower East Side, NY",
    description:
      "Assist case managers in supporting immigrant and low-income families navigate housing, benefits, and social services.",
    requirements: ["Fluent Spanish required", "Empathy and cultural competency", "Bachelor's preferred but not required"],
    matchScore: 44,
  },
];

export interface Candidate {
  id: string;
  name: string;
  email: string;
  checkedIn: boolean;
  resumeUploaded: boolean;
  barriers: string[];
  matchCount: number;
  avgScore: number;
  status: "matched" | "pending" | "reviewing";
}

export const candidates: Candidate[] = [
  { id: "c1", name: "Maria Santos", email: "m.santos@email.com", checkedIn: false, resumeUploaded: true, barriers: ["Housing"], matchCount: 4, avgScore: 76, status: "matched" },
  { id: "c2", name: "James Williams", email: "jwilliams@email.com", checkedIn: false, resumeUploaded: true, barriers: [], matchCount: 5, avgScore: 82, status: "matched" },
  { id: "c3", name: "Yolanda Chen", email: "ychen@email.com", checkedIn: false, resumeUploaded: false, barriers: ["Transportation"], matchCount: 3, avgScore: 69, status: "reviewing" },
  { id: "c4", name: "Devon Okafor", email: "dokafor@email.com", checkedIn: false, resumeUploaded: true, barriers: ["Childcare"], matchCount: 4, avgScore: 71, status: "matched" },
  { id: "c5", name: "Rosa Reyes", email: "rreyes@email.com", checkedIn: false, resumeUploaded: true, barriers: ["Housing", "Childcare"], matchCount: 2, avgScore: 64, status: "pending" },
  { id: "c6", name: "Marcus Thompson", email: "mthompson@email.com", checkedIn: false, resumeUploaded: true, barriers: [], matchCount: 5, avgScore: 88, status: "matched" },
  { id: "c7", name: "Aisha Patel", email: "apatel@email.com", checkedIn: false, resumeUploaded: false, barriers: ["Transportation"], matchCount: 3, avgScore: 73, status: "reviewing" },
  { id: "c8", name: "Luis Hernandez", email: "lhernandez@email.com", checkedIn: false, resumeUploaded: true, barriers: [], matchCount: 4, avgScore: 79, status: "matched" },
  { id: "c9", name: "Tamika Brown", email: "tbrown@email.com", checkedIn: false, resumeUploaded: true, barriers: ["Housing"], matchCount: 3, avgScore: 67, status: "pending" },
  { id: "c10", name: "Ivan Petrov", email: "ipetrov@email.com", checkedIn: false, resumeUploaded: false, barriers: ["Language"], matchCount: 2, avgScore: 61, status: "reviewing" },
];

export const demoCandidate = {
  id: "c1",
  name: "Maria Santos",
  fairDate: "Thursday, May 15, 2026",
  fairTime: "10:00 AM – 2:00 PM",
  location: "265 Henry St, New York, NY 10002",
  matchedJobs: jobs.slice(0, 5),
};
