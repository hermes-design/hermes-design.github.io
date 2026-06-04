
import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-300 py-12 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          
          <div className="text-center md:text-left">
            <h3 className="text-lg font-bold text-white mb-2">HERMES-Design Project</h3>
            <p className="text-sm text-slate-400 mb-4">
              Human-Centric Collaborative Architectural Decision-Making<br/> for Secure System Design
            </p>
            <p className="text-xs text-slate-500">
              &copy; {new Date().getFullYear()} All rights reserved.
            </p>
             <p className="text-xs text-slate-500 mt-1">
              <em>This page was developed for the ICO <a href="https://hermes-design.github.io/" target="_blank" rel="noopener noreferrer" className="text-sky-400 hover:text-sky-300 hover:underline">HERMES-Design project</a>.</em>
            </p>
             <p className="text-xs text-slate-500 mt-1">
              Contact: <a href="mailto:abaouya@acm.org" className="text-sky-400 hover:text-sky-300 hover:underline">abaouya@acm.org</a>
            </p>
          </div>

          <div className="flex items-center space-x-10">
             {/* Institutional logos */}
             <a href="https://www.ico-occitanie.fr/" target="_blank" rel="noopener noreferrer" className="hover:opacity-80 transition-opacity">
                <img 
                    src="images/logo2.png" 
                    alt="ICO Occitanie Logo" 
                    width="240" 
                    height="120" 
                    className="rounded-md h-32 w-auto object-contain bg-white p-2"
                />
             </a>
             <a href="https://www.irit.fr/" target="_blank" rel="noopener noreferrer" className="hover:opacity-80 transition-opacity">
                <img 
                    src="images/logo1.png" 
                    alt="IRIT Logo" 
                    width="240" 
                    height="120" 
                    className="rounded-md h-32 w-auto object-contain bg-white p-2"
                />
             </a>
          </div>
          
        </div>
      </div>
    </footer>
  );
};

export default Footer;