import { SectionHeader } from './SectionHeader';
import { Handshake } from 'lucide-react';

export function OrganizersSection() {
  return (
    <section className="py-16 bg-slate-50/50 dark:bg-slate-900/30 border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-4xl mx-auto px-6 lg:px-8">
        <SectionHeader 
          title="Organizers and Supporters" 
          icon={<Handshake className="w-6 h-6 text-blue-500" />} 
        />
        
        {/* Special Thanks Block */}
        <div className="mt-8 p-6 md:p-8 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl shadow-sm">
          <p className="text-sm md:text-base text-slate-700 dark:text-slate-300 leading-relaxed text-center italic mx-auto max-w-3xl">
            "We express our heartfelt appreciation to our esteemed organisers, the Montenegrin Association for New Technologies (MANT), the Mediterranean Excellence in Computing and Ontology (MECOnet), and the MECO Conference, alongside our visionary founders Prof. dr Lech Jozwiak and Prof. dr Radovan Stojanović, for their outstanding guidance, dedication, and invaluable support in making our collaborative scientific achievements successful."
          </p>
        </div>
      </div>
    </section>
  );
}
