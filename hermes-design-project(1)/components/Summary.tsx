
import React from 'react';
import { Activity, Shield, Users } from 'lucide-react';
import { PROJECT_SUMMARY, PROJECT_FUNDING } from '../constants';

const Summary: React.FC = () => {
  return (
    <section id="project-summary" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="lg:grid lg:grid-cols-12 lg:gap-16 items-start">
          
          <div className="lg:col-span-7">
            <h2 className="text-3xl font-bold text-slate-900 mb-6 flex items-center">
              <span className="bg-sky-100 text-sky-600 p-2 rounded-lg mr-4">
                <Activity size={24} />
              </span>
              Project Overview
            </h2>
            
            <div className="prose prose-lg text-slate-600 space-y-4 mb-6">
                {PROJECT_SUMMARY.split('\n\n').map((paragraph, idx) => (
                    <p key={idx} className="leading-relaxed">
                        {paragraph}
                    </p>
                ))}
            </div>

            <div className="mt-8 p-4 bg-slate-50 border-l-4 border-sky-500 rounded-r-lg">
                <p className="text-sm font-medium text-slate-700 italic">
                    {PROJECT_FUNDING}
                </p>
            </div>
          </div>

          <div className="hidden lg:block lg:col-span-5 space-y-6">
            <div className="bg-slate-50 p-8 rounded-2xl shadow-sm border border-slate-100">
                <h3 className="font-semibold text-slate-900 mb-4 flex items-center">
                    <Shield className="w-5 h-5 mr-2 text-sky-600" /> Key Objectives
                </h3>
                <ul className="space-y-4">
                    <li className="flex items-start">
                        <div className="flex-shrink-0 w-2 h-2 mt-2 bg-sky-500 rounded-full mr-3"></div>
                        <span className="text-slate-600 text-sm">Formal modeling framework for human factors in architecture.</span>
                    </li>
                    <li className="flex items-start">
                        <div className="flex-shrink-0 w-2 h-2 mt-2 bg-sky-500 rounded-full mr-3"></div>
                        <span className="text-slate-600 text-sm">Traceability of decisions impacting system security, performance, and dependability.</span>
                    </li>
                    <li className="flex items-start">
                        <div className="flex-shrink-0 w-2 h-2 mt-2 bg-sky-500 rounded-full mr-3"></div>
                        <span className="text-slate-600 text-sm">Enhancing confidence in diverse collaborative teams.</span>
                    </li>
                </ul>
            </div>
            
             <div className="bg-sky-900 p-8 rounded-2xl shadow-lg text-white relative overflow-hidden">
                <div className="relative z-10">
                    <h3 className="font-semibold mb-2 flex items-center">
                        <Users className="w-5 h-5 mr-2 text-sky-300" /> Collaborative Design
                    </h3>
                    <p className="text-sky-100 text-sm leading-relaxed opacity-90">
                        Bridging the gap between technical constraints and human expertise to build safer, more reliable systems.
                    </p>
                </div>
                <div className="absolute top-0 right-0 -mt-10 -mr-10 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};

export default Summary;
