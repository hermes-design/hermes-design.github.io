import { SectionHeader } from './SectionHeader';
import { FileCode, Download, Code2, Sliders } from 'lucide-react';
import type { CodeResource } from '../types';

interface CodeSectionProps {
  title: string;
  items: CodeResource[];
}

export function CodeSection({ title, items }: CodeSectionProps) {
  return (
    <section className="py-12 border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-5xl mx-auto px-6 lg:px-8">
        <SectionHeader title={title} icon={<FileCode className="w-6 h-6" />} />
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {items.map((item, index) => (
            <div 
              key={index}
              className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-6">
                {item.name}
              </h3>
              
              <div className="flex flex-wrap gap-3">
                {item.links.map((link, linkIndex) => {
                  const isProperties = link.label.toLowerCase().includes('properties');
                  const isCode = link.label.toLowerCase().includes('code');
                  return (
                    <a
                      key={linkIndex}
                      href={link.url}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm font-medium transition-colors border border-slate-200 dark:border-slate-700"
                    >
                      {isProperties ? (
                        <Sliders className="w-4 h-4 text-blue-500" />
                      ) : isCode ? (
                        <Code2 className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <Download className="w-4 h-4 text-slate-400" />
                      )}
                      {link.label}
                    </a>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
