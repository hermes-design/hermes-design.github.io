import { Mail, Shield, Globe } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 pt-16 pb-12 border-t border-slate-800">
      <div className="max-w-5xl mx-auto px-6 lg:px-8">
        
        {/* Middle Footer Navigation & Collaboration Information */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-8 mb-6">
          
          {/* Column 1: About the Project */}
          <div className="flex flex-col">
            <div className="flex items-center gap-2 mb-4">
              <Shield className="w-5 h-5 text-blue-400" />
              <h3 className="font-bold text-slate-100 text-lg tracking-tight">HERMES-Design</h3>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed max-w-sm">
              Human-Centric Collaborative Architectural Decision-Making for Secure System Design. A framework addressing system modeling, synthesis, and formal verification of secure Cyber-Physical Systems (CPS).
            </p>
          </div>

          {/* Column 2: Contact & Core Team */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Globe className="w-5 h-5 text-blue-400" />
              <h3 className="font-bold text-slate-100 text-base">Core Scientific Team</h3>
            </div>
            <div className="space-y-3">
              <div className="flex flex-col text-sm">
                <span className="font-medium text-slate-200">Brahim Hamid</span>
                <a href="mailto:brahim.hamid@irit.fr" className="text-slate-400 hover:text-blue-400 inline-flex items-center gap-1.5 transition-colors text-xs mt-0.5">
                  <Mail className="w-3.5 h-3.5" /> brahim.hamid@irit.fr
                </a>
              </div>
              <div className="flex flex-col text-sm">
                <span className="font-medium text-slate-200">Saddek Bensalem</span>
                <a href="mailto:saddek.bensalem@univ-grenoble-alpes.fr" className="text-slate-400 hover:text-blue-400 inline-flex items-center gap-1.5 transition-colors text-xs mt-0.5">
                  <Mail className="w-3.5 h-3.5" /> saddek.bensalem@univ-grenoble-alpes.fr
                </a>
              </div>
              <div className="flex flex-col text-sm">
                <span className="font-medium text-slate-200">Otmane Ait Mohamed</span>
                <a href="mailto:otmane.aitmohamed@concordia.ca" className="text-slate-400 hover:text-blue-400 inline-flex items-center gap-1.5 transition-colors text-xs mt-0.5">
                  <Mail className="w-3.5 h-3.5" /> otmane.aitmohamed@concordia.ca
                </a>
              </div>
            </div>
          </div>

          {/* Column 3: Institutional Partners on the Right */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-100 mb-4">
              Institutional Partners
            </h4>
            <div className="flex flex-col gap-3.5">
              {/* IRIT Logo Partner */}
              <a 
                href="https://www.irit.fr/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-3 p-2.5 bg-slate-950/40 rounded-lg border border-slate-800/60 hover:border-blue-500/30 hover:bg-slate-950/60 transition-all max-w-sm group"
              >
                <div className="bg-white rounded-md p-1.5 w-28 h-14 flex items-center justify-center shrink-0 animate-pulse-subtle">
                  <img 
                    src="https://hermes-design.github.io/images/logo1.png" 
                    alt="IRIT" 
                    className="max-h-11 max-w-full object-contain" 
                    referrerPolicy="no-referrer" 
                  />
                </div>
                <div className="flex flex-col leading-tight">
                  <span className="text-xs font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">IRIT</span>
                  <span className="text-[10px] text-slate-500">Institut de Recherche en Informatique de Toulouse</span>
                </div>
              </a>

              {/* ICO Logo Partner */}
              <a 
                href="https://www.ico-occitanie.fr/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-3 p-2.5 bg-slate-950/40 rounded-lg border border-slate-800/60 hover:border-blue-500/30 hover:bg-slate-950/60 transition-all max-w-sm group"
              >
                <div className="bg-white rounded-md p-1.5 w-28 h-14 flex items-center justify-center shrink-0">
                  <img 
                    src="https://hermes-design.github.io/images/logo2.png" 
                    alt="ICO" 
                    className="max-h-11 max-w-full object-contain" 
                    referrerPolicy="no-referrer" 
                  />
                </div>
                <div className="flex flex-col leading-tight">
                  <span className="text-xs font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">ICO Occitanie</span>
                  <span className="text-[10px] text-slate-500">Institut de Calcul Global et d'Optimisation</span>
                </div>
              </a>
            </div>
          </div>

        </div>

      </div>
    </footer>
  );
}
