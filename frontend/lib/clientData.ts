// Static demo data for the workforce development client portal.

export const client = {
  id: "c1",
  name: "Maria Santos",
  clientId: "WD-204817",
  program: "Henry Street Settlement Workforce Development",
  careerCoach: {
    name: "Denise Okafor",
    title: "Career Coach",
    email: "dokafor@henrystreet.org",
    phone: "(212) 555-0148",
  },
  interestAreas: ["Healthcare", "Healthcare Administration", "Customer Service"],
  memberSince: "Nov 2025",
};

export type EnrollmentStatus = "Active" | "Completed" | "Exited";

export interface Enrollment {
  id: string;
  program: string;
  provider: string;
  category: string;
  status: EnrollmentStatus;
  startDate: string;
  endDate?: string;
  progress?: number;
  nextStep?: string;
  outcome?: string;
}

export const enrollments: Enrollment[] = [
  {
    id: "e1",
    program: "Medical Administrative Assistant Training",
    provider: "Henry Street Settlement · Career Pathways",
    category: "Occupational Training",
    status: "Active",
    startDate: "Sep 8, 2026",
    endDate: "Dec 12, 2026",
    progress: 58,
    nextStep: "Week 8: Medical billing & coding basics — Tue, Oct 27, 6:00 PM",
  },
  {
    id: "e2",
    program: "WIOA Adult Career Services",
    provider: "NYC Workforce1 Career Center",
    category: "Career Services",
    status: "Active",
    startDate: "Aug 12, 2026",
    progress: 70,
    nextStep: "Coaching check-in with Denise — Thu, Oct 29, 11:00 AM",
  },
  {
    id: "e3",
    program: "Job Placement & Retention Services",
    provider: "Henry Street Settlement",
    category: "Employment Services",
    status: "Active",
    startDate: "Oct 1, 2026",
    progress: 20,
    nextStep: "Mock interview session — Mon, Nov 2, 2:00 PM",
  },
  {
    id: "e4",
    program: "Financial Coaching",
    provider: "Henry Street Settlement · Financial Empowerment",
    category: "Supportive Services",
    status: "Completed",
    startDate: "Feb 3, 2026",
    endDate: "May 28, 2026",
    outcome: "Completed 6 sessions · Built monthly budget",
  },
  {
    id: "e5",
    program: "Digital Literacy Basics",
    provider: "NYPL TechConnect",
    category: "Foundational Skills",
    status: "Completed",
    startDate: "Nov 10, 2025",
    endDate: "Jan 16, 2026",
    outcome: "Certificate earned · Northstar Digital Literacy",
  },
  {
    id: "e6",
    program: "Intermediate ESL",
    provider: "Henry Street Settlement · Adult Education",
    category: "Foundational Skills",
    status: "Exited",
    startDate: "Nov 17, 2025",
    endDate: "Feb 20, 2026",
    outcome: "Exited early to begin Digital Literacy track",
  },
];

export type MilestoneStatus = "done" | "in-progress" | "todo";

export interface Milestone {
  id: string;
  label: string;
  status: MilestoneStatus;
  date?: string;
  detail?: string;
}

export interface ReadinessArea {
  id: string;
  name: string;
  milestones: Milestone[];
}

export const readinessAreas: ReadinessArea[] = [
  {
    id: "assess",
    name: "Assessment & Planning",
    milestones: [
      { id: "m1", label: "Intake & eligibility", status: "done", date: "Aug 12, 2026" },
      { id: "m2", label: "Career interest inventory", status: "done", date: "Aug 19, 2026" },
      { id: "m3", label: "Basic skills assessment (TABE)", status: "done", date: "Aug 26, 2026" },
      { id: "m4", label: "Individual employment plan", status: "done", date: "Sep 2, 2026" },
    ],
  },
  {
    id: "tools",
    name: "Job Search Tools",
    milestones: [
      { id: "m5", label: "Resume reviewed by coach", status: "done", date: "Sep 30, 2026" },
      { id: "m6", label: "Cover letter template", status: "in-progress", detail: "Draft uploaded · awaiting feedback" },
      { id: "m7", label: "LinkedIn profile", status: "todo", detail: "Workshop on Nov 5" },
      { id: "m8", label: "Two professional references", status: "todo" },
    ],
  },
  {
    id: "skills",
    name: "Workplace Skills",
    milestones: [
      { id: "m9", label: "Digital literacy certificate", status: "done", date: "Jan 16, 2026" },
      { id: "m10", label: "Workplace communication workshop", status: "done", date: "Oct 7, 2026" },
      { id: "m11", label: "Mock interview", status: "todo", detail: "Scheduled Nov 2" },
    ],
  },
  {
    id: "creds",
    name: "Credentials",
    milestones: [
      { id: "m12", label: "CPR / First Aid", status: "done", date: "Oct 3, 2026" },
      { id: "m13", label: "Medical Administrative Assistant (CMAA)", status: "in-progress", detail: "Exam after course ends in Dec" },
    ],
  },
];

export interface Appointment {
  id: string;
  title: string;
  when: string;
  where: string;
}

export const appointments: Appointment[] = [
  { id: "a1", title: "Medical billing & coding class", when: "Tue, Oct 27 · 6:00 PM", where: "265 Henry St, Room 204" },
  { id: "a2", title: "Coaching check-in with Denise", when: "Thu, Oct 29 · 11:00 AM", where: "Video call" },
  { id: "a3", title: "Mock interview session", when: "Mon, Nov 2 · 2:00 PM", where: "265 Henry St, Career Lab" },
];

export interface Training {
  id: string;
  title: string;
  provider: string;
  interestArea: string;
  format: "In person" | "Online" | "Hybrid";
  schedule: string;
  duration: string;
  startDate: string;
  cost: string;
  credential?: string;
  seatsLeft: number;
  description: string;
}

export const trainings: Training[] = [
  {
    id: "t1",
    title: "Patient Care Technician",
    provider: "Henry Street Settlement · Career Pathways",
    interestArea: "Healthcare",
    format: "In person",
    schedule: "Mon–Thu, 9:00 AM – 1:00 PM",
    duration: "14 weeks",
    startDate: "Jan 11, 2027",
    cost: "Free for eligible clients",
    credential: "NHA Certified Patient Care Technician",
    seatsLeft: 6,
    description: "Hands-on training in phlebotomy, EKG, and patient care with a clinical externship at a partner hospital.",
  },
  {
    id: "t2",
    title: "Home Health Aide Certification",
    provider: "VNS Health Training Institute",
    interestArea: "Healthcare",
    format: "In person",
    schedule: "Mon–Fri, 9:00 AM – 3:00 PM",
    duration: "3 weeks",
    startDate: "Nov 16, 2026",
    cost: "Free · paid stipend",
    credential: "NYS Home Health Aide",
    seatsLeft: 3,
    description: "State-approved HHA program with a job offer for graduates who meet hiring requirements.",
  },
  {
    id: "t3",
    title: "Medical Billing & Coding",
    provider: "LaGuardia Community College",
    interestArea: "Healthcare Administration",
    format: "Hybrid",
    schedule: "Tue & Thu evenings",
    duration: "16 weeks",
    startDate: "Feb 2, 2027",
    cost: "ITA voucher eligible",
    credential: "AAPC Certified Professional Coder",
    seatsLeft: 12,
    description: "Learn ICD-10 and CPT coding, insurance claims, and electronic health records software.",
  },
  {
    id: "t4",
    title: "Electronic Health Records Specialist",
    provider: "Per Scholas",
    interestArea: "Healthcare Administration",
    format: "Online",
    schedule: "Self-paced + weekly live session",
    duration: "8 weeks",
    startDate: "Dec 7, 2026",
    cost: "Free",
    credential: "NHA Certified EHR Specialist",
    seatsLeft: 20,
    description: "Manage patient records, scheduling, and documentation in Epic-style EHR systems.",
  },
  {
    id: "t5",
    title: "Customer Service Excellence",
    provider: "NYC Workforce1 Career Center",
    interestArea: "Customer Service",
    format: "In person",
    schedule: "Wed, 10:00 AM – 2:00 PM",
    duration: "4 weeks",
    startDate: "Nov 11, 2026",
    cost: "Free",
    credential: "NRF Customer Service & Sales",
    seatsLeft: 9,
    description: "Build de-escalation, phone, and front-desk skills employers look for in patient-facing roles.",
  },
  {
    id: "t6",
    title: "Bilingual Call Center Representative",
    provider: "Grace Institute",
    interestArea: "Customer Service",
    format: "Hybrid",
    schedule: "Mon–Fri, 9:30 AM – 12:30 PM",
    duration: "10 weeks",
    startDate: "Jan 4, 2027",
    cost: "Free",
    seatsLeft: 4,
    description: "Spanish/English call center training with job placement support at health insurers and city agencies.",
  },
  {
    id: "t7",
    title: "OSHA-30 Construction Safety",
    provider: "Building Skills NY",
    interestArea: "Construction",
    format: "In person",
    schedule: "Sat, 8:00 AM – 4:00 PM",
    duration: "4 weeks",
    startDate: "Nov 7, 2026",
    cost: "Free",
    credential: "OSHA-30 + SST card",
    seatsLeft: 15,
    description: "Required safety certification for most NYC construction sites.",
  },
  {
    id: "t8",
    title: "IT Support Fundamentals",
    provider: "Per Scholas",
    interestArea: "Technology",
    format: "Hybrid",
    schedule: "Mon–Fri, 9:00 AM – 4:00 PM",
    duration: "15 weeks",
    startDate: "Jan 19, 2027",
    cost: "Free",
    credential: "CompTIA A+",
    seatsLeft: 8,
    description: "Troubleshoot hardware, software, and networks and prepare for the CompTIA A+ exam.",
  },
];

export type DocumentType = "Resume" | "Cover Letter" | "Certificate" | "Other";

export interface ClientDocument {
  id: string;
  name: string;
  type: DocumentType;
  uploaded: string;
  size: string;
  sharedWithCoach: boolean;
  note?: string;
  url?: string;
}

export const initialDocuments: ClientDocument[] = [
  {
    id: "d1",
    name: "Maria_Santos_Resume_Healthcare.pdf",
    type: "Resume",
    uploaded: "Sep 30, 2026",
    size: "142 KB",
    sharedWithCoach: true,
    note: "Reviewed by Denise",
  },
  {
    id: "d2",
    name: "Maria_Santos_Resume_General.docx",
    type: "Resume",
    uploaded: "Aug 20, 2026",
    size: "38 KB",
    sharedWithCoach: false,
  },
  {
    id: "d3",
    name: "Cover_Letter_Front_Desk.docx",
    type: "Cover Letter",
    uploaded: "Oct 21, 2026",
    size: "24 KB",
    sharedWithCoach: true,
    note: "Awaiting feedback",
  },
  {
    id: "d4",
    name: "CPR_First_Aid_Card.pdf",
    type: "Certificate",
    uploaded: "Oct 3, 2026",
    size: "310 KB",
    sharedWithCoach: true,
  },
];
