import { SectionHeader } from './SectionHeader';
import { Wrench, ExternalLink } from 'lucide-react';
import { PrismGuide } from './PrismGuide';
import type { Tool } from '../types';

interface ToolsSectionProps {
  title: string;
  items: Tool[];
}

export function ToolsSection({ title, items }: ToolsSectionProps) {
  return (
    <section className="py-12 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50">
      <div className="max-w-5xl mx-auto px-6 lg:px-8">
        <SectionHeader title={title} icon={<Wrench className="w-6 h-6" />} />
        
        <div className="grid grid-cols-1 gap-6">
          {items.map((tool, index) => (
            <div 
              key={index}
              className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 md:p-8 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6"
            >
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-3">
                  {tool.name}
                </h3>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed max-w-3xl">
                  {tool.description}
                </p>
              </div>
              
              <a
                href={tool.url}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 rounded-lg font-medium transition-colors whitespace-nowrap"
              >
                Access Tool
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          ))}
        </div>

        {/* PRISM & PRISM Games Configuration Guide */}
        <PrismGuide />
      </div>
    </section>
  );
}
