import { ReactNode } from 'react';

interface SectionHeaderProps {
  title: string;
  icon: ReactNode;
}

export function SectionHeader({ title, icon }: SectionHeaderProps) {
  return (
    <div className="flex items-center gap-3 mb-8">
      <div className="p-2.5 bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 rounded-lg">
        {icon}
      </div>
      <h2 className="text-2xl font-semibold text-slate-900 dark:text-white">
        {title}
      </h2>
    </div>
  );
}
