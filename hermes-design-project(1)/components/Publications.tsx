
import React from 'react';
import { BookOpen, ExternalLink, Calendar, Layers } from 'lucide-react';
import { PUBLICATIONS } from '../constants';

const Publications: React.FC = () => {
  return (
    <section id="publications" className="py-20 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-slate-900 mb-10 flex items-center border-b pb-4 border-slate-200">
          <BookOpen className="mr-3 text-sky-600" />
          Publications
        </h2>

        <div className="space-y-6">
          {PUBLICATIONS.map((pub) => (
            <div 
              key={pub.id} 
              className="group relative bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-all border-l-4 border-transparent hover:border-sky-500 overflow-hidden"
            >
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                         <span className="px-2 py-1 bg-slate-100 text-slate-600 text-xs font-bold rounded uppercase tracking-wide">
                            {pub.id}
                        </span>
                        <div className="flex items-center text-sm text-sky-600 font-medium">
                            <Calendar size={14} className="mr-1.5" />
                            {pub.date}
                        </div>
                    </div>
                  
                  <h3 className="text-xl font-bold text-slate-800 mb-2 group-hover:text-sky-700 transition-colors">
                    {pub.title}
                  </h3>
                  
                  <p className="text-slate-600 text-sm mb-3">
                    {pub.authors}
                  </p>
                  
                  <div className="text-sm text-slate-500 italic border-l-2 border-slate-200 pl-3">
                    In {pub.venue}
                  </div>
                </div>

                <div className="mt-4 md:mt-0 flex-shrink-0 flex flex-col sm:flex-row gap-3">
                  <a 
                    href={pub.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center w-full md:w-auto px-4 py-2 bg-sky-50 text-sky-700 text-sm font-medium rounded-lg hover:bg-sky-100 transition-colors"
                  >
                    View Paper
                    <ExternalLink size={14} className="ml-2" />
                  </a>
                  
                  {pub.artefactLink && (
                    <a 
                      href={pub.artefactLink}
                      className="inline-flex items-center justify-center w-full md:w-auto px-4 py-2 bg-slate-100 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-200 transition-colors"
                    >
                      Artefacts
                      <Layers size={14} className="ml-2" />
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Publications;