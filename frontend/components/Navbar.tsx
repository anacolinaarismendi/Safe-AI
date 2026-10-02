"use client";

import React, { useState } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { Shield, Menu, X, Globe, Sparkles } from "lucide-react";
import { Language } from "@/data/translations";

export const Navbar: React.FC = () => {
  const { lang, setLang, t } = useLanguage();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const languages: { code: Language; label: string; flag: string }[] = [
    { code: "es", label: "ES", flag: "🇪🇸" },
    { code: "en", label: "EN", flag: "🇬🇧" },
    { code: "de", label: "DE", flag: "🇩🇪" },
  ];

  return (
    <nav className="fixed top-0 left-0 w-full bg-white/90 backdrop-blur-md z-50 border-b border-gray-100 transition-all shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20 items-center">
          {/* Brand Logo */}
          <a href="#" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-medical-blue to-sky-500 flex items-center justify-center text-white shadow-md shadow-blue-900/20 group-hover:scale-105 transition-transform">
              <Shield className="w-5 h-5 fill-white/20" />
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-2xl tracking-tight text-medical-navy flex items-center gap-1">
                SafeRx <span className="text-sky-600">AI</span>
              </span>
              <span className="text-[10px] text-gray-400 font-semibold tracking-wider uppercase -mt-1">
                Clinical Safety Guard
              </span>
            </div>
          </a>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-7">
            <a
              href="#problema"
              className="text-sm font-medium text-gray-600 hover:text-medical-blue transition-colors"
            >
              {t.nav.problem}
            </a>
            <a
              href="#solucion"
              className="text-sm font-medium text-gray-600 hover:text-medical-blue transition-colors"
            >
              {t.nav.solution}
            </a>
            <a
              href="#seguridad"
              className="text-sm font-medium text-gray-600 hover:text-medical-blue transition-colors"
            >
              {t.nav.compliance}
            </a>
            <a
              href="#clientes"
              className="text-sm font-medium text-gray-600 hover:text-medical-blue transition-colors"
            >
              {t.nav.target}
            </a>

            {/* Segmented Language Switcher */}
            <div className="flex items-center bg-gray-100/90 p-1 rounded-xl border border-gray-200/80 shadow-inner">
              {languages.map((item) => {
                const isActive = lang === item.code;
                return (
                  <button
                    key={item.code}
                    onClick={() => setLang(item.code)}
                    className={`px-3 py-1.5 text-xs rounded-lg transition-all flex items-center gap-1.5 ${
                      isActive
                        ? "bg-medical-blue text-white font-bold shadow-sm"
                        : "text-gray-600 hover:text-gray-900 font-medium hover:bg-white/60"
                    }`}
                  >
                    <span>{item.flag}</span>
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>

            {/* CTA Button */}
            <a
              href="https://silent-goats-throw.loca.lt"
              target="_blank"
              className="inline-flex items-center justify-center bg-medical-blue hover:bg-medical-darkBlue text-white text-sm font-semibold px-5 py-2.5 rounded-full transition-all shadow-md shadow-blue-900/15 hover:shadow-lg hover:-translate-y-0.5"
            >
              {t.nav.contact}
            </a>
          </div>

          {/* Mobile Quick Controls */}
          <div className="lg:hidden flex items-center gap-2">
            {/* Mobile Lang Selector */}
            <div className="flex items-center bg-gray-100 p-0.5 rounded-lg border border-gray-200">
              {languages.map((item) => (
                <button
                  key={item.code}
                  onClick={() => setLang(item.code)}
                  className={`px-2 py-1 text-xs rounded font-medium ${
                    lang === item.code
                      ? "bg-medical-blue text-white font-bold shadow-sm"
                      : "text-gray-600"
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>

            {/* Hamburger Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-gray-600 hover:text-medical-blue hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-b border-gray-200 px-4 pt-3 pb-6 space-y-3 animate-fade-in shadow-xl">
          <a
            href="#problema"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-gray-700 hover:text-medical-blue"
          >
            {t.nav.problem}
          </a>
          <a
            href="#solucion"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-gray-700 hover:text-medical-blue"
          >
            {t.nav.solution}
          </a>
          <a
            href="#seguridad"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-gray-700 hover:text-medical-blue"
          >
            {t.nav.compliance}
          </a>
          <a
            href="#clientes"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-gray-700 hover:text-medical-blue"
          >
            {t.nav.target}
          </a>
          <div className="pt-2">
            <a
              href="https://silent-goats-throw.loca.lt"
              target="_blank"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-center w-full bg-medical-blue text-white py-3 rounded-xl font-semibold shadow-md"
            >
              {t.nav.contact}
            </a>
          </div>
        </div>
      )}
    </nav>
  );
};
