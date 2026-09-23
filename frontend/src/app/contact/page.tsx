import React from "react";
import Link from "next/link";
import { getLandingData } from "@/lib/api";
import AdmissionsForm from "@/components/landing/AdmissionsForm";
import {
  MapPin,
  Phone,
  Mail,
  Clock,
  ExternalLink,
  MessageCircle,
  Navigation,
  CheckCircle2,
  Building,
  Sparkles,
} from "lucide-react";

export const metadata = {
  title: "Contact Us & Campus Location | Aarambh Institute Indore",
  description:
    "Visit Aarambh Institute at 8 Shantinath Puri, Hawa Bangla, Near Sai Mandir, Indore. Call 88397-14081 / 79097-14081 or message on WhatsApp for coaching admissions.",
};

export default async function ContactPage() {
  const data = await getLandingData();
  const contact = data.contact;

  return (
    <div className="bg-[#f8fafd] text-slate-900 pb-20">
      {/* Page Header */}
      <section className="relative bg-gradient-to-b from-white via-slate-50 to-[#f8fafd] border-b border-slate-200/80 pt-10 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-4">
            <Link href="/" className="hover:text-[#c22329] transition-colors">
              Home
            </Link>
            <span>/</span>
            <span className="text-[#c22329]">Contact Us</span>
          </div>

          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-bold uppercase tracking-wider">
              <MapPin className="w-3.5 h-3.5" />
              <span>Campus Visit & Inquiries</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
              Get In Touch & Visit <br />
              <span className="text-[#c22329]">Our Indore Campus</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
              Have questions about batches, fees, or want to meet our teachers? Visit our Hawa Bangla center or call our academic counselors.
            </p>
          </div>
        </div>
      </section>

      {/* Main Contact Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Card 1: Address & Location */}
          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-center text-[#c22329]">
                <MapPin className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Campus Address</h3>
              <p className="text-sm text-slate-600 leading-relaxed font-medium">
                {contact.full_address}
              </p>
              <div className="text-xs text-slate-500 bg-slate-50 p-3 rounded-xl border border-slate-100">
                <strong>Landmark:</strong> Near Sai Mandir, easily accessible from CAT Road, Rajendra Nagar & Silicon City.
              </div>
            </div>

            <a
              href={contact.google_maps_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-caramel-gold inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-bold text-xs shadow-md"
            >
              <Navigation className="w-4 h-4" />
              <span>Open In Google Maps</span>
            </a>
          </div>

          {/* Card 2: Phone & WhatsApp */}
          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700">
                <Phone className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Helpline Numbers</h3>
              <div className="space-y-2 pt-1 text-sm font-semibold">
                <div className="flex items-center gap-2 text-slate-800">
                  <span className="text-slate-500 text-xs w-20">Primary:</span>
                  <a
                    href={`tel:+91${contact.primary_phone.replace(/\D/g, "")}`}
                    className="hover:text-[#c22329] transition-colors"
                  >
                    {contact.primary_phone}
                  </a>
                </div>
                <div className="flex items-center gap-2 text-slate-800">
                  <span className="text-slate-500 text-xs w-20">Secondary:</span>
                  <a
                    href={`tel:+91${contact.secondary_phone.replace(/\D/g, "")}`}
                    className="hover:text-[#c22329] transition-colors"
                  >
                    {contact.secondary_phone}
                  </a>
                </div>
                <div className="flex items-center gap-2 text-slate-800">
                  <span className="text-slate-500 text-xs w-20">WhatsApp:</span>
                  <a
                    href={`https://wa.me/91${contact.whatsapp_number.replace(/\D/g, "")}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-emerald-700 hover:underline"
                  >
                    {contact.whatsapp_number}
                  </a>
                </div>
              </div>
            </div>

            <a
              href={`https://wa.me/91${contact.whatsapp_number.replace(/\D/g, "")}?text=Hello%20Aarambh%20Institute%2C%20I%20want%20to%20know%20about%20admissions.`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-bold text-xs bg-emerald-600 hover:bg-emerald-700 text-white shadow-md transition-colors"
            >
              <MessageCircle className="w-4 h-4" />
              <span>Chat On WhatsApp</span>
            </a>
          </div>

          {/* Card 3: Email & Hours */}
          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-800">
                <Clock className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Visiting Hours & Email</h3>
              <div className="space-y-3 pt-1 text-xs">
                <div>
                  <span className="font-semibold text-slate-500">Working Hours:</span>
                  <p className="text-slate-900 font-bold text-sm mt-0.5">
                    {contact.working_hours}
                  </p>
                </div>
                <div>
                  <span className="font-semibold text-slate-500">Official Email:</span>
                  <p className="text-[#c22329] font-semibold text-sm mt-0.5">
                    <a href={`mailto:${contact.email}`}>{contact.email}</a>
                  </p>
                </div>
                <div>
                  <span className="font-semibold text-slate-500">Official Website:</span>
                  <p className="text-slate-900 font-bold text-sm mt-0.5">
                    {contact.website_domain}
                  </p>
                </div>
              </div>
            </div>

            <a
              href={`mailto:${contact.email}`}
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-bold text-xs bg-slate-900 hover:bg-slate-800 text-white shadow-md transition-colors"
            >
              <Mail className="w-4 h-4" />
              <span>Send An Email</span>
            </a>
          </div>
        </div>
      </section>

      {/* Online Callback & Inquiry Form */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="mb-8 text-center max-w-2xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-black text-slate-900">
            Request A Callback From Our Academic Counselor
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 mt-2">
            Fill out your details below and our team will contact you within 2 business hours.
          </p>
        </div>

        <AdmissionsForm />
      </div>
    </div>
  );
}
