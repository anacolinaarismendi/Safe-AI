"use client";

import React from "react";
import { useLanguage } from "@/context/LanguageContext";
import { ArrowRight, ShieldCheck, Zap, Activity, CheckCircle2 } from "lucide-react";

export const Hero: React.FC = () => {
  const { t } = useLanguage();

  return (
    <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden bg-gradient-to-b from-medical-softBlue via-white to-white">
      {/* Subtle Background Glow & Grid */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-sky-200/40 blur-[120px] rounded-full" />
        <div className="absolute top-40 right-10 w-[300px] h-[300px] bg-emerald-200/30 blur-[100px] rounded-full" />
        <svg
          className="absolute inset-0 w-full h-full opacity-10"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <pattern
              id="hero-tech-grid"
              width="48"
              height="48"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 48 0 L 0 0 0 48"
                fill="none"
                stroke="#1E3A8A"
                strokeWidth="0.8"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#hero-tech-grid)" />
        </svg>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        {/* Top Floating Badge */}
        <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-blue-100/90 border border-blue-200/80 shadow-sm mb-8 backdrop-blur-sm">
          <span className="flex h-2 w-2 rounded-full bg-sky-600 animate-pulse" />
          <span className="text-xs font-bold text-medical-blue tracking-wide uppercase">
            {t.hero.badge}
          </span>
        </div>

        {/* Main Title */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-medical-navy tracking-tight max-w-4xl mx-auto leading-[1.15]">
          {t.hero.titleStart}{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-medical-blue via-sky-600 to-emerald-600">
            {t.hero.titleHighlight}
          </span>{" "}
          {t.hero.titleEnd}
        </h1>

        {/* Subtitle */}
        <p className="mt-6 max-w-2xl mx-auto text-lg sm:text-xl text-gray-600 leading-relaxed">
          {t.hero.subtitle}
        </p>

        {/* Action Buttons */}
        <div className="mt-10 max-w-md mx-auto sm:max-w-none flex flex-col sm:flex-row justify-center gap-4">
          <a
            href="https://silent-goats-throw.loca.lt"
            target="_blank"
            className="inline-flex items-center justify-center px-8 py-4 text-base font-bold rounded-full text-white bg-medical-blue hover:bg-medical-darkBlue transition-all shadow-lg shadow-blue-900/25 hover:shadow-xl hover:-translate-y-0.5 group"
          >
            <span>{t.hero.ctaPrimary}</span>
            <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
          </a>
          <a
            href="#solucion"
            className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold rounded-full text-gray-700 bg-white hover:bg-gray-50 border border-gray-200 transition-all shadow-sm hover:shadow hover:-translate-y-0.5"
          >
            <Activity className="w-4 h-4 mr-2 text-sky-600" />
            <span>{t.hero.ctaSecondary}</span>
          </a>
        </div>

        {/* Trust Stats Bar in Glassmorphic Container */}
        <div className="mt-16 pt-8 border-t border-gray-100 max-w-3xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="flex flex-col items-center p-4 rounded-2xl bg-white/70 backdrop-blur-sm border border-gray-100 shadow-sm">
            <div className="flex items-center gap-1.5 text-medical-blue font-extrabold text-2xl sm:text-3xl">
              <ShieldCheck className="w-6 h-6 text-sky-600" />
              <span>{t.hero.stat1Number}</span>
            </div>
            <span className="text-xs text-gray-500 font-medium mt-1">
              {t.hero.stat1Label}
            </span>
          </div>

          <div className="flex flex-col items-center p-4 rounded-2xl bg-white/70 backdrop-blur-sm border border-gray-100 shadow-sm">
            <div className="flex items-center gap-1.5 text-emerald-600 font-extrabold text-2xl sm:text-3xl">
              <Zap className="w-6 h-6 text-emerald-500" />
              <span>{t.hero.stat2Number}</span>
            </div>
            <span className="text-xs text-gray-500 font-medium mt-1">
              {t.hero.stat2Label}
            </span>
          </div>

          <div className="flex flex-col items-center p-4 rounded-2xl bg-white/70 backdrop-blur-sm border border-gray-100 shadow-sm">
            <div className="flex items-center gap-1.5 text-medical-navy font-extrabold text-2xl sm:text-3xl">
              <CheckCircle2 className="w-6 h-6 text-medical-blue" />
              <span>{t.hero.stat3Number}</span>
            </div>
            <span className="text-xs text-gray-500 font-medium mt-1">
              {t.hero.stat3Label}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};
