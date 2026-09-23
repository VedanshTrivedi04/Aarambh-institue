export interface InstituteContactInfo {
  name: string;
  tagline: string;
  established_year: number;
  city: string;
  full_address: string;
  primary_phone: string;
  secondary_phone: string;
  whatsapp_number: string;
  email: string;
  website_domain: string;
  google_maps_url: string;
  working_hours: string;
  boards_covered: string[];
  classes_taught: string;
  footer_tagline: string;
}

export interface HeroStats {
  years_experience: string;
  total_students: string;
  highest_board_score: string;
  board_pass_rate: string;
  faculty_count: string;
  batch_size_limit: string;
}

export interface AboutSectionData {
  title: string;
  paragraphs: string[];
  director_name: string;
  director_designation: string;
  director_experience: string;
  director_quote: string;
  award_title: string;
  core_values: Array<{ title: string; desc: string }>;
}

export interface CourseItem {
  id: string;
  category: string;
  title: string;
  subtitle: string;
  target: string;
  duration: string;
  board: string;
  timings: string;
  batch_size: string;
  fee: string;
  badge: string;
  badge_color: string;
  features: string[];
  popular: boolean;
}

export interface FacultyMember {
  name: string;
  subject: string;
  experience: string;
  highlight: string;
  specialty: string;
  initials: string;
  avatar_bg: string;
  subject_badge: string;
}

export interface TopperStudent {
  name: string;
  grade: string;
  board: string;
  score: string;
  marks: string;
  rank: string;
  year: string;
  subjects: string;
  quote: string;
  initials: string;
  badge_color: string;
}

export interface StudentRollItem {
  name: string;
  class_name: string;
  board: string;
  score: string;
  year: string;
  highlight: string;
}

export interface TestimonialItem {
  name: string;
  class_info: string;
  year: string;
  review: string;
  role: string;
}

export interface UspFeature {
  number: number;
  title: string;
  description: string;
}

export interface NoticeItem {
  date: string;
  title: string;
  desc: string;
  priority: string;
  color: string;
}

export interface HolidayItem {
  holiday: string;
  date: string;
  status: string;
}

export interface StudyMaterialItem {
  title: string;
  target_class: string;
  pages: string;
  size: string;
  downloads: string;
  author: string;
  badge: string;
  badge_color: string;
}

export interface LandingPageBundle {
  contact: InstituteContactInfo;
  stats: HeroStats;
  about: AboutSectionData;
  courses: CourseItem[];
  faculty: FacultyMember[];
  featured_toppers: TopperStudent[];
  all_toppers: StudentRollItem[];
  testimonials: TestimonialItem[];
  usps: UspFeature[];
  notices: NoticeItem[];
  holidays: HolidayItem[];
  materials: StudyMaterialItem[];
}

export interface PublicEnquiryPayload {
  student_name: string;
  parent_name: string;
  phone: string;
  email?: string;
  target_class: string;
  stream?: string;
  remarks?: string;
}

export interface PublicEnquiryResponse {
  id: string;
  student_name: string;
  parent_name: string;
  phone: string;
  message: string;
}
