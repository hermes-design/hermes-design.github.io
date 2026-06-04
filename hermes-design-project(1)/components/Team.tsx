import React from 'react';
import { Mail } from 'lucide-react';
import { TEAM_MEMBERS } from '../constants';

const Team: React.FC = () => {
  return (
    <section id="team" className="py-20 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-slate-900">Research Team</h2>
          <p className="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">
            Our interdisciplinary team combines expertise in formal methods, security, and systems engineering.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {TEAM_MEMBERS.map((member) => (
            <div 
              key={member.id} 
              className="bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden group"
            >
              <div className="aspect-w-1 aspect-h-1 w-full h-64 bg-slate-200 relative overflow-hidden">
                 {/* Image or Placeholder Fallback */}
                 <img 
                    src={member.imageUrl} 
                    alt={member.name}
                    className="w-full h-full object-cover transition-all duration-500"
                    onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                        (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                    }}
                 />
                 <div className="hidden absolute inset-0 bg-slate-100 flex items-center justify-center text-slate-400 font-bold text-4xl">
                    {member.initials}
                 </div>
              </div>
              
              <div className="p-6">
                <div className="mb-2">
                    <span className="inline-block px-2 py-0.5 text-xs font-semibold text-sky-700 bg-sky-100 rounded-full mb-2">
                        {member.role}
                    </span>
                    <h3 className="text-lg font-bold text-slate-900 leading-tight">
                        {member.name}
                    </h3>
                </div>
                {member.affiliation && (
                    <p className="text-sm text-slate-500 mb-4">{member.affiliation}</p>
                )}
                
                <a 
                    href={`mailto:${member.email}`}
                    className="inline-flex items-center text-sm text-slate-600 hover:text-sky-600 transition-colors mt-2"
                >
                    <Mail size={16} className="mr-2" />
                    <span className="truncate max-w-[180px]">{member.email}</span>
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Team;