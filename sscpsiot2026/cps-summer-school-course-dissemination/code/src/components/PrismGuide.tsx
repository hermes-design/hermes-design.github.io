import { useState } from 'react';
import { Download, Terminal, Settings, Check, Copy, Cpu, BookOpen, ExternalLink, Code2 } from 'lucide-react';

export function PrismGuide() {
  const [activeTab, setActiveTab] = useState<'prism' | 'prism-games'>('prism-games');
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedText(id);
      setTimeout(() => setCopiedText(null), 2000);
    }).catch(() => {
      // Fallback
    });
  };

  const prismCommands = `tar -zxf prism-4.8-linux64.tar.gz
cd prism-4.8
./install.sh`;

  const prismGamesCommands = `tar -zxf prism-games-3.2-linux64.tar.gz
cd prism-games-3.2
./install.sh`;

  return (
    <div className="mt-16 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800/80 rounded-2xl shadow-sm overflow-hidden" id="prism-guide">
      {/* Header Banner */}
      <div className="p-6 md:p-8 bg-slate-950 text-white border-b border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <Cpu className="w-3.5 h-3.5" />
            Verification Engine Setup
          </div>
          <h3 className="text-2xl font-bold tracking-tight text-slate-100">
            PRISM Configuration Guide
          </h3>
          <p className="text-slate-400 text-sm mt-1 max-w-xl">
            Steps to download, build, and configure the PRISM suite for modeling and analyzing Stochastic Games.
          </p>
        </div>
        
        {/* Quick Official Manual Button */}
        <a 
          href="https://www.prismmodelchecker.org/manual/" 
          target="_blank" 
          rel="noopener noreferrer" 
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition-colors duration-150 px-3 py-1.5 bg-slate-900 rounded-lg border border-slate-800"
        >
          <BookOpen className="w-3.5 h-3.5" />
          PRISM Manual <ExternalLink className="w-3 h-3" />
        </a>
      </div>

      {/* Tabs Toggles */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40 p-1.5 gap-2">
        <button
          onClick={() => setActiveTab('prism-games')}
          className={`flex-1 py-3 px-4 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center justify-center gap-2 ${
            activeTab === 'prism-games'
              ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm border border-slate-200/65 dark:border-slate-800/80'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-300'
          }`}
        >
          <Code2 className="w-4 h-4" />
          PRISM Games (CSG) Setup
        </button>
        <button
          onClick={() => setActiveTab('prism')}
          className={`flex-1 py-3 px-4 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center justify-center gap-2 ${
            activeTab === 'prism'
              ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm border border-slate-200/65 dark:border-slate-800/80'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-300'
          }`}
        >
          <Cpu className="w-4 h-4" />
          Standard PRISM Setup
        </button>
      </div>

      <div className="p-6 md:p-8">
        {/* Description Section based on tab */}
        {activeTab === 'prism-games' ? (
          <div className="mb-8">
            <h4 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2 mb-2">
              PRISM Games extension for Stochastic Games
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed max-w-3xl">
              PRISM-games is a specialized version of the PRISM model checker featuring support for modeling and verifying **Concurrent Stochastic Games (CSGs)**, turn-based stochastic games (TSGs), and multi-agent systems. It allows evaluating cooperative and competitive strategies essential for securing collaborative system interactions.
            </p>
          </div>
        ) : (
          <div className="mb-8">
            <h4 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2 mb-2">
              PRISM Probabilistic Model Checker
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed max-w-3xl">
              PRISM is a mature probabilistic model checker for formal analysis of systems exhibiting random or stochastic behavior. It supports modeling systems as Discrete-Time Markov Chains (DTMC), Continuous-Time Markov Chains (CTMC), and Markov Decision Processes (MDP).
            </p>
          </div>
        )}

        {/* Setup Flow (Grid-based steps) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          
          {/* Step 1: Pre-requisites */}
          <div className="flex flex-col">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-7 h-7 bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center font-bold text-xs">
                01
              </span>
              <h5 className="font-bold text-slate-800 dark:text-slate-200 text-sm">Prerequisites</h5>
            </div>
            <div className="flex-1 bg-slate-50 dark:bg-slate-950/30 border border-slate-200/60 dark:border-slate-800/50 rounded-xl p-4 text-xs space-y-3.5 text-slate-600 dark:text-slate-400">
              <div className="flex items-start gap-2.5">
                <Check className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-slate-800 dark:text-slate-200 font-semibold">Java JRE/JDK (9+):</strong> Required to launch both GUI and command-line execution. Check via <code className="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded font-mono">java -version</code>.
                </span>
              </div>
              <div className="flex items-start gap-2.5">
                <Check className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-slate-800 dark:text-slate-200 font-semibold">C/C++ Compiler & Make:</strong> GNU gcc/g++ and make tools are required to compile C++ solvers on Unix-like environments.
                </span>
              </div>
            </div>
          </div>

          {/* Step 2: Download */}
          <div className="flex flex-col">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-7 h-7 bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center font-bold text-xs">
                02
              </span>
              <h5 className="font-bold text-slate-800 dark:text-slate-200 text-sm">Download Sources</h5>
            </div>
            <div className="flex-1 bg-slate-50 dark:bg-slate-950/30 border border-slate-200/60 dark:border-slate-800/50 rounded-xl p-4 flex flex-col justify-between gap-4">
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Download the official pre-compiled package or the source archive compatible with your operating system (Linux, macOS, or Windows).
              </p>
              
              {activeTab === 'prism-games' ? (
                <a
                  href="https://www.prismmodelchecker.org/games/download.php"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition-colors shadow-sm"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download PRISM Games <ExternalLink className="w-3 h-3" />
                </a>
              ) : (
                <a
                  href="https://www.prismmodelchecker.org/download.php"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition-colors shadow-sm"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download PRISM Model Checker <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>

          {/* Step 3: Run & Execute */}
          <div className="flex flex-col">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-7 h-7 bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center font-bold text-xs">
                03
              </span>
              <h5 className="font-bold text-slate-800 dark:text-slate-200 text-sm">Execution Commands</h5>
            </div>
            <div className="flex-1 bg-slate-50 dark:bg-slate-950/30 border border-slate-200/60 dark:border-slate-800/50 rounded-xl p-4 text-xs space-y-3.5 text-slate-600 dark:text-slate-400">
              <div className="flex items-start gap-2">
                <Settings className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-slate-800 dark:text-slate-200 font-semibold">Launch GUI:</strong> Run the shell script <code className="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded font-mono">bin/xprism</code> to use the interactive application interface.
                </span>
              </div>
              <div className="flex items-start gap-2">
                <Terminal className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-slate-800 dark:text-slate-200 font-semibold">Command Line:</strong> Verify models headless via terminal by calling <code className="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded font-mono">bin/prism [model-file] [properties-file]</code>.
                </span>
              </div>
            </div>
          </div>

        </div>

        {/* Linux / macOS Compilation Guide Terminal Codeblock */}
        <div className="bg-slate-950 rounded-xl border border-slate-900 p-5 font-mono text-xs text-slate-300">
          <div className="flex items-center justify-between pb-3.5 mb-3.5 border-b border-slate-905 border-slate-900/40">
            <span className="text-slate-400 font-bold flex items-center gap-2">
              <Terminal className="w-4 h-4 text-blue-400" />
              Unix-like (Linux/macOS) Installation Terminal
            </span>
            <button
              onClick={() => handleCopy(activeTab === 'prism-games' ? prismGamesCommands : prismCommands, 'terminal')}
              className="text-slate-400 hover:text-white flex items-center gap-1 px-2.5 py-1 bg-slate-900 border border-slate-800 rounded transition-colors"
            >
              {copiedText === 'terminal' ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  Copy Block
                </>
              )}
            </button>
          </div>
          <pre className="overflow-x-auto select-all text-slate-105 leading-relaxed p-1">
            {activeTab === 'prism-games' ? prismGamesCommands : prismCommands}
          </pre>
        </div>

        {/* Windows Note Box */}
        <div className="mt-5 p-4 bg-blue-50/50 dark:bg-blue-950/15 border border-blue-100 dark:border-blue-900/35 rounded-xl flex items-start gap-3 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
          <Settings className="w-5 h-5 text-blue-505 text-blue-500 shrink-0 mt-0.5" />
          <div>
            <span className="text-slate-800 dark:text-slate-200 font-semibold block mb-0.5">Note on Windows Environment</span>
            Precompiled Windows binaries of PRISM do not require running a compiler script. Simply unzip the file, confirm Java is configured on your system environment variables, and run <code className="bg-blue-100/50 dark:bg-blue-900/30 px-1 py-0.5 rounded font-mono">xprism.bat</code> or run properties through CLI using <code className="bg-blue-100/50 dark:bg-blue-900/30 px-1 py-0.5 rounded font-mono">prism.bat</code>.
          </div>
        </div>

      </div>
    </div>
  );
}
