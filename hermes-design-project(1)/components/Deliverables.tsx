
import React from 'react';
import { FileText, Download, CheckCircle } from 'lucide-react';
import { DELIVERABLES } from '../constants';

const Deliverables: React.FC = () => {
  return (
    <section id="deliverables" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-slate-900 mb-10 flex items-center border-b pb-4 border-slate-200">
          <FileText className="mr-3 text-sky-600" />
          Project Deliverables
        </h2>

        <div className="space-y-6">
          {DELIVERABLES.map((item) => (
            <div 
              key={item.id} 
              className="group relative bg-slate-50 hover:bg-white rounded-xl p-6 border border-slate-200 hover:border-sky-300 hover:shadow-md transition-all duration-300"
            >
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center flex-wrap gap-3 mb-2">
                    <span className="inline-flex items-center justify-center h-8 w-10 rounded bg-sky-100 text-sky-700 text-sm font-bold">
                      {item.id}
                    </span>
                    <span className="text-sm font-medium text-slate-500 bg-white px-2 py-1 rounded border border-slate-200">
                      {item.date}
                    </span>
                    {item.id === 'D2' && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                            <CheckCircle size={12} className="mr-1" />
                            Final Deliverable
                        </span>
                    )}
                  </div>
                  
                  <h3 className="text-lg font-bold text-slate-900">
                    {item.title}
                  </h3>
                </div>
                
                <div className="mt-2 md:mt-0 flex-shrink-0">
                  <a 
                    href={item.downloadLink}
                    download
                    className="inline-flex items-center justify-center w-full md:w-auto px-5 py-2.5 bg-white border border-slate-300 text-slate-700 text-sm font-medium rounded-lg hover:bg-sky-50 hover:text-sky-700 hover:border-sky-300 transition-colors shadow-sm group-hover:shadow"
                  >
                    <Download size={16} className="mr-2" />
                    Download PDF
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Deliverables;
