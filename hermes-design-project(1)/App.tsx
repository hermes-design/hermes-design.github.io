
import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Summary from './components/Summary';
import Team from './components/Team';
import Deliverables from './components/Deliverables';
import Publications from './components/Publications';
import InvitedTalks from './components/InvitedTalks';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <Hero />
        <Summary />
        <Team />
        <Deliverables />
        <Publications />
        <InvitedTalks />
      </main>
      <Footer />
    </div>
  );
}

export default App;
