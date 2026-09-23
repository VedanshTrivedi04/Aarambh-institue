import { LandingPageBundle, PublicEnquiryPayload, PublicEnquiryResponse } from "@/types/landing";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const FALLBACK_LANDING_DATA: LandingPageBundle = {
  contact: {
    name: "Aarambh Institute",
    tagline: "Step Toward Success",
    established_year: 2015,
    city: "Indore, Madhya Pradesh",
    full_address: "8 Shantinath Puri, Hawa Bangla, Near Sai Mandir, Indore, Madhya Pradesh",
    primary_phone: "88397-14081",
    secondary_phone: "79097-14081",
    whatsapp_number: "88397-14081",
    email: "aarambhinstitute09@gmail.com",
    website_domain: "aarambhinstitute.com",
    google_maps_url: "https://maps.app.goo.gl/T2m2g9b8tjVMCDqL9",
    working_hours: "10:00 AM to 8:00 PM (Monday to Saturday)",
    boards_covered: ["MP Board", "CBSE", "ICSE"],
    classes_taught: "Class 4th to 12th, B.Com, M.Com, BBA, MBA, B.Sc",
    footer_tagline: "Education with values. Learning with joy.",
  },
  stats: {
    years_experience: "15+ Yrs",
    total_students: "2,000+",
    highest_board_score: "98.5%",
    board_pass_rate: "98%",
    faculty_count: "12+",
    batch_size_limit: "20 Students",
  },
  about: {
    title: "Transforming Academic Journeys With The Right Guidance",
    paragraphs: [
      "At Aarambh Institute, we believe that the right guidance at the right time can transform a student's academic journey.",
      "Our experienced faculty, well-researched curriculum, and student-centric approach make learning both effective and engaging.",
    ],
    director_name: "Shobhna Vyas",
    director_designation: "Founder & Academic Director",
    director_experience: "20 Years Experience",
    director_quote:
      "As a parent myself, I know what you want: safety, learning, and happiness for your child. At Aarambh Institute, you will get all three. Let's grow together.",
    award_title: "Best Coaching Institute Award, Indore 2023",
    core_values: [
      { title: "Child Safety First", desc: "Protected and encouraging learning environment" },
      { title: "Effective Learning", desc: "Proven concept-building and test techniques" },
      { title: "Joyful Environment", desc: "Education with happiness and zero fear" },
    ],
  },
  courses: [
    {
      id: "middle-school",
      category: "school",
      title: "Class 4th to 8th (Middle School)",
      subtitle: "All Subjects Comprehensive Coaching for MP Board, CBSE & ICSE",
      target: "Classes 4th, 5th, 6th, 7th & 8th",
      duration: "1 Academic Year",
      board: "MP Board / CBSE / ICSE",
      timings: "Morning 11:00 AM - 12:30 PM | Evening 5:00 PM - 6:30 PM",
      batch_size: "Strict 20 Students per batch",
      fee: "₹800/- to ₹1,000/- (Monthly)",
      badge: "Junior Foundation",
      badge_color: "bg-blue-50 text-blue-700 border-blue-200",
      features: [
        "All Subjects Covered (Maths, Science, English, Hindi, Social Science)",
        "Weekly Assessment Tests with Parent Progress Reports",
        "Printed Comprehensive Study Material & Practice Worksheets",
        "Daily Dedicated Doubt Clearing & Homework Guidance",
        "Special focus on Handwriting, Reading & Basic Mathematical Speed",
      ],
      popular: true,
    },
    {
      id: "high-school",
      category: "board",
      title: "Class 9th to 12th (Board & Entrance)",
      subtitle: "Science (PCM / PCB) & Commerce Stream Mastery for Board Exams",
      target: "Classes 9th, 10th, 11th & 12th",
      duration: "1 Academic Year",
      board: "MP Board / CBSE / ICSE",
      timings: "Morning 11:00 AM - 1:00 PM | Evening 4:00 PM - 6:00 PM",
      batch_size: "Small Batches (20 Students)",
      fee: "Student-Friendly Affordable Fees",
      badge: "Board Result Rankers",
      badge_color: "bg-red-50 text-[#c22329] border-red-200",
      features: [
        "All Core Subjects: Physics, Chemistry, Maths, Biology, Commerce & Accounts",
        "Weekly Topic Tests + Monthly Full Board Model Examination Papers",
        "Previous 10 Years Board Papers analysis and Answer-Writing Drills",
        "Special NEET & JEE Mains Foundation Concepts covered by Expert Mentors",
        "Daily 1:1 Doubt Classes with Senior HODs (15+ to 30 Yrs Experience)",
      ],
      popular: true,
    },
    {
      id: "college-degrees",
      category: "college",
      title: "College Degrees (B.Com, M.Com, BBA, MBA, B.Sc)",
      subtitle: "Specialized Higher Education & Commerce/Management Coaching",
      target: "Undergraduate & Postgraduate Students",
      duration: "Semester / Academic Year",
      board: "University Syllabus Aligned",
      timings: "Flexible Morning & Evening College Batches",
      batch_size: "Personalized Domain Batches",
      fee: "Affordable Package Rates",
      badge: "Higher Education",
      badge_color: "bg-amber-50 text-amber-800 border-amber-200",
      features: [
        "Financial Accounting, Corporate Accounting, Taxation & Costing",
        "Business Studies, Economics, Statistics & Financial Management",
        "Taught by Veteran Commerce Head Mr. Jitendra Shindey (30 Yrs Experience)",
        "University Exam Pattern Model Question Banks & Solved Papers",
        "Concept clearing for Competitive Exams (Bank PO, CA Foundation, CAT)",
      ],
      popular: false,
    },
  ],
  faculty: [
    {
      name: "Mr. Pankaj Dubey",
      subject: "Biology",
      experience: "30 Years Experience",
      highlight: "Senior Biology Expert • PMT/NEET & Board Specialist",
      specialty: "Botany, Zoology & Medical Foundation",
      initials: "PD",
      avatar_bg: "bg-emerald-50 text-emerald-800",
      subject_badge: "bg-emerald-50 text-emerald-800 border-emerald-200",
    },
    {
      name: "Mr. Jitendra Shindey",
      subject: "Commerce & Accounts",
      experience: "30 Years Experience",
      highlight: "Senior Commerce Mentor • 11th-12th, B.Com & M.Com",
      specialty: "Financial Accounting, Tax & Corporate Laws",
      initials: "JS",
      avatar_bg: "bg-blue-50 text-blue-800",
      subject_badge: "bg-blue-50 text-blue-800 border-blue-200",
    },
    {
      name: "Mrs. Shobhna Vyas",
      subject: "Maths & Science (Founder)",
      experience: "20 Years Experience",
      highlight: "Founder & Academic Director, Aarambh Institute",
      specialty: "Conceptual Mathematics & Science for 4th to 10th",
      initials: "SV",
      avatar_bg: "bg-red-50 text-[#c22329]",
      subject_badge: "bg-red-50 text-[#c22329] border-red-200",
    },
    {
      name: "Mr. Vishal Rathore",
      subject: "Mathematics",
      experience: "15 Years Experience",
      highlight: "Senior Mathematics Specialist for Board Exams",
      specialty: "Algebra, Calculus & Trigonometry Mastery",
      initials: "VR",
      avatar_bg: "bg-amber-50 text-amber-800",
      subject_badge: "bg-amber-50 text-amber-800 border-amber-200",
    },
    {
      name: "Mrs. Anita Holkar",
      subject: "Physics",
      experience: "15 Years Experience",
      highlight: "Physics Senior Educator for MP Board & CBSE",
      specialty: "Mechanics, Electricity, Optics & Numerical Clarity",
      initials: "AH",
      avatar_bg: "bg-cyan-50 text-cyan-800",
      subject_badge: "bg-cyan-50 text-cyan-800 border-cyan-200",
    },
    {
      name: "Mr. Ansh Sir",
      subject: "Chemistry, Biology, Physics",
      experience: "5 Years Experience",
      highlight: "NEET + JEE Mains Category Specialist",
      specialty: "Competitive Speed Techniques & Problem Solving",
      initials: "AS",
      avatar_bg: "bg-purple-50 text-purple-800",
      subject_badge: "bg-purple-50 text-purple-800 border-purple-200",
    },
    {
      name: "Miss Darshna Panchal",
      subject: "Business Studies & Economics",
      experience: "2 Years Experience",
      highlight: "Teaching & Institutional Management Expertise",
      specialty: "Business Management, Micro & Macro Economics",
      initials: "DP",
      avatar_bg: "bg-rose-50 text-rose-800",
      subject_badge: "bg-rose-50 text-rose-800 border-rose-200",
    },
  ],
  featured_toppers: [
    {
      name: "Prince",
      grade: "Class 12th",
      board: "MP Board",
      score: "94%",
      marks: "580 / 600",
      rank: "Rank 1st",
      year: "2023",
      subjects: "Maths: 100/100 • Physics: 99/100",
      quote: "Aarambh ne mujhe sahi direction diya aur regular practice sets ki wajah se board exam mein top rank mili.",
      initials: "PR",
      badge_color: "bg-amber-100 text-amber-900 border-amber-300",
    },
    {
      name: "Rohit Garg",
      grade: "Class 10th",
      board: "MP Board",
      score: "91%",
      marks: "Board Distinction",
      rank: "Rank 2nd",
      year: "2024",
      subjects: "Maths & Physics Topper",
      quote: "Proud to be an Aarambhian! The teachers personally cleared every doubt before the exams.",
      initials: "RG",
      badge_color: "bg-blue-100 text-blue-900 border-blue-300",
    },
    {
      name: "Payal Sharma",
      grade: "Class 10th",
      board: "MP Board",
      score: "89%",
      marks: "Board Distinction",
      rank: "Rank 3rd",
      year: "2024",
      subjects: "Maths & Chemistry Distinction",
      quote: "Aarambh didn't just teach me, it transformed me. Concepts were made crystal clear.",
      initials: "PS",
      badge_color: "bg-emerald-100 text-emerald-900 border-emerald-300",
    },
  ],
  all_toppers: [
    { name: "Prince", class_name: "12th", board: "MP Board", score: "94%", year: "2023", highlight: "Rank 1st (Maths 100/100)" },
    { name: "Rohit Garg", class_name: "10th", board: "MP Board", score: "91%", year: "2024", highlight: "Rank 2nd" },
    { name: "Payal Sharma", class_name: "10th", board: "MP Board", score: "89%", year: "2024", highlight: "Rank 3rd" },
    { name: "Neha Yadav", class_name: "10th", board: "MP Board", score: "89%", year: "2023", highlight: "Distinction" },
    { name: "Nupur", class_name: "10th", board: "CBSE", score: "89%", year: "2023", highlight: "Distinction" },
    { name: "Monika", class_name: "12th", board: "CBSE", score: "85%", year: "2024", highlight: "Distinction" },
    { name: "Ritika Sarothiya", class_name: "10th", board: "CBSE", score: "85%", year: "2025", highlight: "Distinction" },
    { name: "Nishtha Jain", class_name: "10th", board: "MP Board", score: "83%", year: "2025", highlight: "First Division" },
    { name: "Shrishti Yadav", class_name: "9th", board: "MP Board", score: "A Grade", year: "2025", highlight: "Class Topper" },
    { name: "Vanshika Yadav", class_name: "7th", board: "MP Board", score: "A Grade", year: "2025", highlight: "Class Topper" },
    { name: "Atharva Choudhary", class_name: "8th", board: "CBSE", score: "A Grade", year: "2025", highlight: "School Star" },
  ],
  testimonials: [
    {
      name: "Dhruvika",
      class_info: "Class 6th",
      year: "2023",
      role: "Parent Review",
      review: "Aarambh Institute ke teachers bahut dedicated hain. Mere bachche ke marks aur confidence dono mein kaafi improvement hua hai. Hum institute ki teaching aur guidance se bahut santusht hain.",
    },
    {
      name: "Yashika",
      class_info: "Class 7th",
      year: "2024",
      role: "Student Review",
      review: "Aarambh Institute mein padhai ka environment bahut positive hai. Teachers har topic ko simple aur interesting tareeke se samjhate hain, jis se padhai aasan lagti hai.",
    },
    {
      name: "Vaishnavi Patel",
      class_info: "Class 10th (Boards)",
      year: "2025",
      role: "Student Review",
      review: "Regular tests, personal attention aur progress updates ki wajah se humein performance ka poora pata rehta hai. Aarambh Institute sach mein students ke future ko lekar serious hai.",
    },
    {
      name: "Rishabh Bhargav",
      class_info: "Class 11th (Science)",
      year: "2025",
      role: "Student Review",
      review: "Yahan mujhe padhai ke saath motivation bhi milta hai. Teachers hamesha support karte hain aur doubts ko turant solve karte hain.",
    },
    {
      name: "Gourav Sarothiya",
      class_info: "Class 10th (Boards)",
      year: "2024",
      role: "Student Review",
      review: "Best guidance for academic success! Highly recommended for all board students in Indore.",
    },
  ],
  usps: [
    { number: 1, title: "Expert Faculty", description: "Highly qualified and experienced teachers with up to 30 years of dedicated teaching legacy." },
    { number: 2, title: "Personalised Attention", description: "Strict small batch sizes of 20 students to ensure individual guidance and better interaction." },
    { number: 3, title: "Result Oriented Approach", description: "Consistent record of excellent results in board examinations (98.5% highest scorer)." },
    { number: 4, title: "Comprehensive Study Material & Regular Tests", description: "Notes, practice sets, and return modules designed for all levels with weekly feedback." },
    { number: 5, title: "Supportive Learning Environment", description: "Encouraging atmosphere that builds confidence, eliminates fear, and motivates students to excel." },
    { number: 6, title: "Student-Friendly Fee Structure", description: "Quality education at an affordable and transparent price starting from ₹800/mo." },
  ],
  notices: [
    {
      date: "24 March 2026",
      title: "Weekly Board Mock Test Series (Sunday Batch)",
      desc: "Mandatory for Class 10th and 12th students. Timings: 11:00 AM to 1:00 PM. Answer sheet evaluation will be handed over to parents on Wednesday.",
      priority: "High Priority",
      color: "bg-red-50 text-[#c22329] border-red-200",
    },
    {
      date: "20 March 2026",
      title: "New Academic Session (2026-27) Admissions Open",
      desc: "Classes 4th to 12th & Degree programs. Limited 20 seats per batch. Avail early bird fee benefits at Hawa Bangla campus.",
      priority: "Admission Alert",
      color: "bg-blue-50 text-blue-700 border-blue-200",
    },
    {
      date: "15 March 2026",
      title: "Doubt Clearing Clinic with HODs",
      desc: "Special extra classes every evening from 6:00 PM to 7:00 PM for physics numericals and organic chemistry reactions.",
      priority: "Academic",
      color: "bg-amber-50 text-amber-800 border-amber-200",
    },
  ],
  holidays: [
    { holiday: "Mahavir Jayanti", date: "April 2026", status: "Holiday" },
    { holiday: "Good Friday / Ambedkar Jayanti", date: "April 2026", status: "Holiday" },
    { holiday: "Summer Break (Junior Batches Only)", date: "May 15 - May 25, 2026", status: "Special Timings" },
    { holiday: "Independence Day & Raksha Bandhan", date: "August 2026", status: "Celebration" },
    { holiday: "Ganesh Chaturthi / Anant Chaturdashi", date: "September 2026", status: "Holiday" },
    { holiday: "Dussehra & Diwali Break", date: "October / November 2026", status: "Festival Break" },
  ],
  materials: [
    {
      title: "Class 10th Maths All Formulas Booklet",
      target_class: "Class 10th (MP Board / CBSE)",
      pages: "18 Pages",
      size: "2.4 MB PDF",
      downloads: "1,240+ Downloads",
      author: "Mrs. Shobhna Vyas & Mr. Vishal Rathore",
      badge: "Most Popular",
      badge_color: "bg-red-50 text-[#c22329] border-red-200",
    },
    {
      title: "Class 12th Physics Quick Revision & Derivations",
      target_class: "Class 12th Science",
      pages: "26 Pages",
      size: "3.8 MB PDF",
      downloads: "980+ Downloads",
      author: "Mrs. Anita Holkar",
      badge: "Board Essential",
      badge_color: "bg-blue-50 text-blue-700 border-blue-200",
    },
    {
      title: "Class 12th Biology Diagram Compendium & Labels",
      target_class: "Class 12th & PMT/NEET",
      pages: "32 Pages",
      size: "5.1 MB PDF",
      downloads: "1,450+ Downloads",
      author: "Mr. Pankaj Dubey (30 Yrs Exp)",
      badge: "NEET Ready",
      badge_color: "bg-emerald-50 text-emerald-700 border-emerald-200",
    },
    {
      title: "Class 11th & 12th Commerce Accounting Proformas",
      target_class: "Commerce & B.Com",
      pages: "22 Pages",
      size: "2.9 MB PDF",
      downloads: "890+ Downloads",
      author: "Mr. Jitendra Shindey (30 Yrs Exp)",
      badge: "Commerce Star",
      badge_color: "bg-amber-50 text-amber-800 border-amber-200",
    },
    {
      title: "Class 4th to 8th Vedic Maths & Mental Calculation Tricks",
      target_class: "Junior Section",
      pages: "14 Pages",
      size: "1.8 MB PDF",
      downloads: "620+ Downloads",
      author: "Aarambh Junior Academic Cell",
      badge: "Speed Maths",
      badge_color: "bg-purple-50 text-purple-700 border-purple-200",
    },
    {
      title: "MP Board & CBSE 2026 Model Solved Question Paper",
      target_class: "All High School Batches",
      pages: "40 Pages",
      size: "4.5 MB PDF",
      downloads: "2,100+ Downloads",
      author: "Aarambh Faculty Panel",
      badge: "Official Model",
      badge_color: "bg-rose-50 text-rose-700 border-rose-200",
    },
  ],
};

/**
 * Fetch dynamic landing page bundle from FastAPI backend.
 * Falls back to local defaults if backend is offline or starting up.
 */
export async function getLandingData(): Promise<LandingPageBundle> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/public/landing-data`, {
      next: { revalidate: 30 },
    });

    if (!res.ok) {
      console.warn(`[API] Backend returned status ${res.status}, falling back to defaults`);
      return FALLBACK_LANDING_DATA;
    }

    const data: LandingPageBundle = await res.json();
    return data;
  } catch (err) {
    console.warn("[API] Failed to reach backend, using local fallback data:", err);
    return FALLBACK_LANDING_DATA;
  }
}

/**
 * Submit website enquiry / demo registration directly to backend CRM.
 */
export async function submitPublicEnquiry(
  payload: PublicEnquiryPayload
): Promise<{ success: boolean; data?: PublicEnquiryResponse; error?: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/public/enquiries`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      return {
        success: false,
        error: errJson.detail || "Unable to submit enquiry at this time",
      };
    }

    const data: PublicEnquiryResponse = await res.json();
    return { success: true, data };
  } catch (err: any) {
    return {
      success: false,
      error: err?.message || "Network error. Please try again or contact via WhatsApp.",
    };
  }
}

/**
 * Admin CMS: Fetch all customizable public page configurations
 */
export async function fetchAdminCmsContent(): Promise<{
  success: boolean;
  pages?: Record<string, any>;
  last_updated?: string;
  error?: string;
}> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/cms/content`, {
      cache: "no-store",
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return { success: false, error: err.detail || "Failed to load CMS content" };
    }

    const data = await res.json();
    return { success: true, pages: data.pages, last_updated: data.last_updated };
  } catch (err: any) {
    return { success: false, error: err?.message || "Network error fetching CMS content" };
  }
}

/**
 * Admin CMS: Update a specific public page's configuration
 */
export async function updateAdminCmsSection(
  pageSlug: string,
  data: any,
  title?: string
): Promise<{ success: boolean; data?: any; error?: string }> {
  try {
    const { getAuthToken } = await import("@/lib/auth");
    const token = getAuthToken();
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/cms/content/${pageSlug}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        title: title || pageSlug.replace("_", " ").toUpperCase(),
        data,
        updated_by: "ADMIN_EDITOR",
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return { success: false, error: err.detail || `Failed to update ${pageSlug}` };
    }

    const resJson = await res.json();
    return { success: true, data: resJson };
  } catch (err: any) {
    return { success: false, error: err?.message || `Network error updating ${pageSlug}` };
  }
}

/**
 * Admin CMS: Reset page(s) to institute canonical defaults
 */
export async function resetAdminCmsDefaults(
  pageSlug?: string
): Promise<{ success: boolean; message?: string; error?: string }> {
  try {
    const { getAuthToken } = await import("@/lib/auth");
    const token = getAuthToken();
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/cms/content/reset`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ page_slug: pageSlug || null }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return { success: false, error: err.detail || "Failed to reset content" };
    }

    const resJson = await res.json();
    return { success: true, message: resJson.message };
  } catch (err: any) {
    return { success: false, error: err?.message || "Network error resetting content" };
  }
}
