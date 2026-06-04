import { SectionHeader } from './SectionHeader';
import { ExternalLink, ChevronRight } from 'lucide-react';
import type { Project } from '../types';

interface ProjectsSectionProps {
  title: string;
  items: Project[];
}

export function ProjectsSection({ title, items }: ProjectsSectionProps) {
  return (
    <section className="py-12 border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-5xl mx-auto px-6 lg:px-8">
        <SectionHeader title={title} icon={<ExternalLink className="w-6 h-6" />} />
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((project, index) => (
            <a
              key={index}
              href={project.url}
              className="group flex items-center justify-between p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl hover:border-blue-500 dark:hover:border-blue-500 transition-all shadow-sm hover:shadow-md"
            >
              <span className="font-medium text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                {project.name}
              </span>
              <div className="w-8 h-8 rounded-full bg-slate-50 dark:bg-slate-800 flex items-center justify-center group-hover:bg-blue-50 dark:group-hover:bg-blue-900/30 transition-colors">
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400" />
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
