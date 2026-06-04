
import React from 'react';
import { Mic, Calendar, MapPin, ExternalLink } from 'lucide-react';
import { INVITED_TALKS } from '../constants';

const InvitedTalks: React.FC = () => {
  return (
    <section id="invited-talks" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-slate-900 mb-10 flex items-center border-b pb-4 border-slate-200">
          <Mic className="mr-3 text-sky-600" />
          Invited Talks
        </h2>

        <div className="grid grid-cols-1 gap-6">
          {INVITED_TALKS.map((talk) => (
            <div 
              key={talk.id} 
              className="flex flex-col md:flex-row p-6 rounded-xl border border-slate-200 bg-white hover:border-sky-300 hover:shadow-md transition-all duration-300"
            >
              <div className="md:w-1/4 flex-shrink-0 mb-4 md:mb-0 border-b md:border-b-0 md:border-r border-slate-100 md:pr-6 md:mr-6 flex items-start md:flex-col justify-between md:justify-start">
                 <div className="flex items-center text-sky-600 font-semibold mb-1">
                    <Calendar size={18} className="mr-2" />
                    {talk.date}
                 </div>
                 {talk.location && (
                     <div className="flex items-center text-slate-500 text-sm mt-1">
                        <MapPin size={14} className="mr-2" />
                        {talk.location}
                     </div>
                 )}
              </div>
              
              <div className="flex-grow flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-xl font-bold text-slate-800 mb-2">
                      {talk.title}
                  </h3>
                  <p className="text-slate-600 font-medium">
                      {talk.event}
                  </p>
                </div>
                
                {talk.link && (
                  <div className="flex-shrink-0">
                    <a 
                      href={talk.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-4 py-2 bg-sky-50 text-sky-700 text-sm font-medium rounded-lg hover:bg-sky-100 transition-colors"
                    >
                      Talk Details
                      <ExternalLink size={14} className="ml-2" />
                    </a>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default InvitedTalks;
