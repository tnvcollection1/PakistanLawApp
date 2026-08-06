import React, { useState } from 'react';
import SidebarLayout from '../components/SidebarLayout';
import { HelpCircle, Search, BookOpen, Gavel, Scale, FileText, Users, Briefcase, Building2, BarChart3, MessageSquare, ChevronDown, ChevronUp } from 'lucide-react';

const helpSections = [
  {
    title: 'Getting Started',
    icon: HelpCircle,
    items: [
      { q: 'How do I search for a case?', a: 'Use the Global Search in the sidebar to search across all cases by keyword, citation, or party name. For more specific searches, use Judge Search, Party Search, or Courtwise Search from the sidebar.' },
      { q: 'How do I find a specific citation?', a: 'Use Citation Search from the sidebar. Enter the journal (e.g., PLD, SCMR), year, and page number to find the exact case.' },
      { q: 'How do I bookmark a case?', a: 'Open any case and click the Bookmark icon in the toolbar at the top of the case view. You can find all your bookmarks in the Bookmarks section from the sidebar.' },
    ]
  },
  {
    title: 'Search Features',
    icon: Search,
    items: [
      { q: 'What is Judge Search?', a: 'Judge Search lets you find all cases decided by a specific judge. Start typing the judge\'s name and select from autocomplete suggestions to see their case history.' },
      { q: 'What is Party Search?', a: 'Party Search finds cases by the name of any party involved — petitioner, respondent, or appellant. This is useful for tracking a person or organization\'s litigation history.' },
      { q: 'What is Lawyer Search?', a: 'Lawyer Search finds cases where a specific lawyer/advocate appeared. It searches the full judgment text for the lawyer\'s name.' },
      { q: 'How does Advanced Search work?', a: 'Advanced Search combines multiple filters: judge name, party name, lawyer name, court, year range, act, section, and rule number. Use it when you need precise results.' },
    ]
  },
  {
    title: 'Case Tools',
    icon: Gavel,
    items: [
      { q: 'What is the Citator?', a: 'The Citator shows you which later cases have cited or referenced a particular judgment. Look for the "Cited By" panel on any case detail page.' },
      { q: 'How do I compare two cases?', a: 'Use the Compare Cases feature from the sidebar. Select two cases and view them side-by-side to analyze similarities and differences.' },
      { q: 'Can I export a case as PDF?', a: 'Yes! On the case detail page, click the Export/Print button to generate a formatted PDF of the judgment.' },
      { q: 'What is the AI Assistant?', a: 'The AI Assistant can help you understand legal concepts, summarize judgments, and answer questions about Pakistani law. Access it from the sidebar.' },
    ]
  },
  {
    title: 'Reference Data',
    icon: BookOpen,
    items: [
      { q: 'What are Statutes?', a: 'The Statutes Browser contains 22,590+ Pakistani statutes organized by category, province, and alphabetical order. You can browse sections and find related cases.' },
      { q: 'What are Head Notes?', a: 'Head Notes are concise summaries of the key legal principles established in a case. They appear at the top of each judgment and can be browsed separately.' },
      { q: 'What is the Most Cited Cases feature?', a: 'This leaderboard ranks cases by how many times they have been cited in other judgments, helping you identify the most influential precedents.' },
    ]
  },
  {
    title: 'Court Integrations',
    icon: Building2,
    items: [
      { q: 'What are Court Integrations?', a: 'Court Integrations fetch the latest cause lists from Pakistani superior courts (SHC, SC, LHC, IHC, PHC, BHC) so you can check upcoming cases and schedules.' },
      { q: 'How often are cause lists updated?', a: 'Click "Fetch Cause Lists" to get the latest data. Cause lists are scraped directly from court websites.' },
    ]
  },
];

export default function HelpPage() {
  const [openSections, setOpenSections] = useState({});

  const toggleItem = (sectionIdx, itemIdx) => {
    const key = `${sectionIdx}-${itemIdx}`;
    setOpenSections(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background dark:bg-background">
        <div className="bg-white dark:bg-background border-b border-muted dark:border-border">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6">
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-slate-900 dark:text-foreground flex items-center gap-3" data-testid="help-title">
              <HelpCircle className="text-blue-600" size={28} />
              Help & Guide
            </h1>
            <p className="text-sm text-muted-foreground dark:text-muted-foreground mt-1">Learn how to use PakistanLawApp effectively</p>
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-6">
          {helpSections.map((section, sIdx) => (
            <div key={sIdx} className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border overflow-hidden" data-testid={`help-section-${sIdx}`}>
              <div className="px-5 py-3 bg-background border-b border-muted dark:border-border flex items-center gap-2">
                <section.icon size={18} className="text-blue-600" />
                <h2 className="font-semibold text-slate-800 dark:text-foreground">{section.title}</h2>
              </div>
              <div className="divide-y divide-slate-100">
                {section.items.map((item, iIdx) => {
                  const isOpen = openSections[`${sIdx}-${iIdx}`];
                  return (
                    <button key={iIdx} onClick={() => toggleItem(sIdx, iIdx)}
                      className="w-full text-left px-5 py-3 hover:bg-background transition-colors" data-testid={`help-item-${sIdx}-${iIdx}`}>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-slate-800 dark:text-foreground">{item.q}</span>
                        {isOpen ? <ChevronUp size={16} className="text-muted-foreground" /> : <ChevronDown size={16} className="text-muted-foreground" />}
                      </div>
                      {isOpen && <p className="text-sm text-foreground dark:text-muted-foreground mt-2 leading-relaxed">{item.a}</p>}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </SidebarLayout>
  );
}
