import React from 'react';
import { ArrowRight } from 'lucide-react';
import { PROJECT_TITLE, PROJECT_SUBTITLE } from '../constants';

const Hero: React.FC = () => {
  return (
    <section className="relative bg-slate-900 text-white pt-32 pb-24 md:pt-48 md:pb-32 overflow-hidden">
      {/* Abstract Background Shapes */}
      <div className="absolute top-0 right-0 -mr-20 -mt-20 w-[500px] h-[500px] bg-sky-600/20 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-3xl"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-3xl">
            <div className="inline-block px-3 py-1 mb-6 text-xs font-semibold tracking-wider text-sky-300 uppercase bg-sky-900/50 rounded-full border border-sky-700/50">
                Research Project
            </div>
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight mb-6">
                {PROJECT_TITLE}
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 leading-relaxed font-light mb-10">
                {PROJECT_SUBTITLE}
            </p>
            <div className="flex flex-wrap gap-4">
                <a 
                    href="#project-summary" 
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-sky-600 hover:bg-sky-700 transition-all shadow-lg hover:shadow-sky-500/25"
                >
                    Learn More
                    <ArrowRight className="ml-2 -mr-1 w-5 h-5" />
                </a>
                <a 
                    href="#publications" 
                    className="inline-flex items-center px-6 py-3 border border-slate-600 text-base font-medium rounded-lg text-slate-200 bg-transparent hover:bg-slate-800 transition-all"
                >
                    View Publications
                </a>
            </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;