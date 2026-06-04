
import React, { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import { PROJECT_TITLE } from '../constants';

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Summary', href: '#project-summary' },
    { name: 'Team', href: '#team' },
    { name: 'Deliverables', href: '#deliverables' },
    { name: 'Publications', href: '#publications' },
    { name: 'Invited Talks', href: '#invited-talks' },
  ];

  const handleNavClick = (href: string) => {
    setIsOpen(false);
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <nav 
      className={`fixed w-full z-50 transition-all duration-300 ${
        scrolled ? 'bg-white/90 backdrop-blur-md shadow-lg py-2' : 'bg-transparent py-4'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-24">
          <div className="flex items-center space-x-6">
            <img 
              src="images/1704997992104.png" 
              alt="HERMES-Design Logo" 
              className="h-20 w-auto rounded-md bg-white object-contain p-1 shadow-sm"
            />
            <span className={`font-bold text-2xl tracking-tight ${scrolled ? 'text-slate-900' : 'text-white'}`}>
              {PROJECT_TITLE}
            </span>
          </div>
          
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-6">
              {navLinks.map((link) => (
                <button
                  key={link.name}
                  onClick={() => handleNavClick(link.href)}
                  className={`text-base font-medium transition-colors hover:text-sky-500 ${
                    scrolled ? 'text-slate-600' : 'text-slate-200'
                  }`}
                >
                  {link.name}
                </button>
              ))}
            </div>
          </div>

          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className={`p-2 rounded-md ${scrolled ? 'text-slate-800' : 'text-white'}`}
            >
              {isOpen ? <X size={32} /> : <Menu size={32} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isOpen && (
        <div className="md:hidden absolute top-full left-0 w-full bg-white shadow-xl border-t border-slate-100">
          <div className="px-4 pt-2 pb-6 space-y-1 sm:px-3 flex flex-col">
            {navLinks.map((link) => (
              <button
                key={link.name}
                onClick={() => handleNavClick(link.href)}
                className="block w-full text-left px-3 py-3 rounded-md text-lg font-medium text-slate-700 hover:text-sky-600 hover:bg-slate-50"
              >
                {link.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;