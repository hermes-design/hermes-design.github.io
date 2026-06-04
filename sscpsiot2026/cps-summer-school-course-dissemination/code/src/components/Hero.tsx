import { BookOpen, MonitorPlay, Users, Mic, Mail } from 'lucide-react';
import type { Presentation } from '../types';

interface HeroProps {
  event: string;
  eventLink?: string;
  presentation: Presentation;
}

export function Hero({ event, eventLink, presentation }: HeroProps) {
  // Find presenter and co-authors dynamically from JSON fields
  const presenter = presentation.authors.find(a => a.isPresenter) || presentation.authors[0];
  const coAuthors = presentation.authors.filter(a => a.name !== presenter.name);

  return (
    <header className="bg-slate-900 text-white py-16 md:py-24 border-b border-slate-800">
      <div className="max-w-5xl mx-auto px-6 lg:px-8">
        {eventLink ? (
          <a
            href={eventLink}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-6 text-sm md:text-base font-medium uppercase tracking-wider transition-colors group cursor-pointer"
          >
            <BookOpen className="w-5 h-5 group-hover:scale-110 transition-transform" />
            <span className="underline decoration-dotted underline-offset-4 decoration-blue-400 hover:decoration-blue-300">
              {event}
            </span>
          </a>
        ) : (
          <div className="flex items-center gap-2 text-blue-400 mb-6 text-sm md:text-base font-medium uppercase tracking-wider">
            <BookOpen className="w-5 h-5" />
            <span>{event}</span>
          </div>
        )}
        
        <h1 className="text-3xl md:text-5xl font-bold tracking-tight mb-8 leading-tight max-w-4xl">
          {presentation.title}
        </h1>

        {/* Presenter Highlight Card */}
        <div className="mb-8 p-5 bg-slate-950/50 border border-slate-800/80 rounded-2xl max-w-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-5">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 shrink-0 shadow-inner">
              <Mic className="w-5 h-5 animate-pulse-subtle" />
            </div>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-widest text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-md inline-block mb-1.5">
                {presenter.role || "Speaker / Presenter"}
              </span>
              <h4 className="text-lg font-bold text-slate-100 flex items-center gap-2 leading-snug">
                {presenter.name}
              </h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                {presenter.department && <>{presenter.department}<br /></>}
                {presenter.university}
              </p>
              <a 
                href={presenter.link}
                className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-blue-400 transition-colors mt-2"
              >
                <Mail className="w-3.5 h-3.5" />
                {presenter.link.replace('mailto:', '')}
              </a>
            </div>
          </div>
          
          <a
            href={presentation.slidesLink}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 text-white bg-blue-600 hover:bg-blue-700 px-5 py-3 rounded-xl font-bold transition-all w-full sm:w-auto shrink-0 shadow-lg shadow-blue-500/10"
          >
            <MonitorPlay className="w-5 h-5" />
            View Slides PDF
          </a>
        </div>

        {/* Co-Authors Info Highlighted Horizontally */}
        <div className="mt-8 pt-6 border-t border-slate-800/60 max-w-3xl">
          <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-4 flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-400/85" />
            Co-Authors & Academic Collaborators
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {coAuthors.map((author, index) => {
              const role = author.role || "Collaborator";
              const affiliation = author.university;

              return (
                <a
                  key={index}
                  href={author.link}
                  className="flex flex-col p-4 rounded-xl bg-slate-950/45 border border-slate-800/75 hover:border-blue-500/40 hover:bg-slate-950/80 transition-all duration-155 group"
                >
                  <div className="flex items-center gap-2 mb-1 text-slate-200 group-hover:text-blue-400 transition-colors">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500/80 group-hover:bg-blue-400 shrink-0 transition-colors" />
                    <span className="font-bold text-sm tracking-tight leading-none">{author.name}</span>
                  </div>
                  <span className="text-[11px] font-semibold text-slate-400 tracking-wide mt-1">
                    {role}
                  </span>
                  {author.department && (
                    <span className="text-[10px] text-slate-500 leading-normal mt-0.5">
                      {author.department}
                    </span>
                  )}
                  {affiliation && (
                    <span className="text-[10px] text-slate-500 leading-normal">
                      {affiliation}
                    </span>
                  )}
                </a>
              );
            })}
          </div>
        </div>

      </div>
    </header>
  );
}
