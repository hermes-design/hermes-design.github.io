/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import data from './data.json';
import type { SiteData } from './types';
import { Hero } from './components/Hero';
import { CodeSection } from './components/CodeSection';
import { ToolsSection } from './components/ToolsSection';
import { ProjectsSection } from './components/ProjectsSection';
import { OrganizersSection } from './components/OrganizersSection';
import { Footer } from './components/Footer';

const siteData = data as SiteData;

export default function App() {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 font-sans selection:bg-blue-100 dark:selection:bg-blue-900/40">
      <Hero event={siteData.event} eventLink={siteData.eventLink} presentation={siteData.presentation} />
      
      <main>
        <CodeSection 
          title={siteData.sections.codeResources.title} 
          items={siteData.sections.codeResources.items} 
        />
        
        <CodeSection 
          title={siteData.sections.caseStudies.title} 
          items={siteData.sections.caseStudies.items} 
        />
        
        <ToolsSection 
          title={siteData.sections.tools.title} 
          items={siteData.sections.tools.items} 
        />
        
        <ProjectsSection 
          title={siteData.sections.relatedProjects.title} 
          items={siteData.sections.relatedProjects.items} 
        />

        <OrganizersSection />
      </main>
      
      <Footer />
    </div>
  );
}
