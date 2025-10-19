'use client';

import { useState } from 'react';

export default function Dashboard() {
  const [icp, setIcp] = useState({
    industry: '',
    companySize: '50-200',
    location: 'United States',
    title: 'VP of Sales',
  });
  const [leads, setLeads] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleGenerateLeads = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ icp, limit: 10 }),
      });

      const data = await response.json();
      if (data.success) {
        setLeads(data.leads);
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      console.error('Error generating leads:', error);
      alert('Failed to generate leads');
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (leads.length === 0) return;

    const headers = ['Company', 'Industry', 'Size', 'Website', 'Contact Name', 'Title', 'Email', 'LinkedIn'];
    const rows = leads.map(lead => [
      lead.company.name,
      lead.company.industry,
      lead.company.size,
      lead.company.website,
      lead.contact.name,
      lead.contact.title,
      lead.contact.email,
      lead.contact.linkedin,
    ]);

    const csv = [headers, ...rows].map(row => row.join(',').replace(/,/g, ',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `walterfetch-leads-${Date.now()}.csv`;
    a.click();
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-blue-950 to-slate-950">
      <nav className="border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white">WalterFetch Dashboard</h1>
            <a href="/" className="text-gray-400 hover:text-white transition">
              Back to Home
            </a>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          {/* ICP Configuration */}
          <div className="bg-white/5 border border-white/10 rounded-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-white mb-6">Define Your Ideal Customer Profile</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Industry
                </label>
                <input
                  type="text"
                  value={icp.industry}
                  onChange={(e) => setIcp({ ...icp, industry: e.target.value })}
                  placeholder="e.g., SaaS, E-commerce, Healthcare"
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Company Size
                </label>
                <select
                  value={icp.companySize}
                  onChange={(e) => setIcp({ ...icp, companySize: e.target.value })}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="1-10">1-10 employees</option>
                  <option value="11-50">11-50 employees</option>
                  <option value="51-200">51-200 employees</option>
                  <option value="201-500">201-500 employees</option>
                  <option value="501-1000">501-1000 employees</option>
                  <option value="1001+">1001+ employees</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={icp.location}
                  onChange={(e) => setIcp({ ...icp, location: e.target.value })}
                  placeholder="e.g., United States, California, New York"
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Target Title
                </label>
                <input
                  type="text"
                  value={icp.title}
                  onChange={(e) => setIcp({ ...icp, title: e.target.value })}
                  placeholder="e.g., CEO, VP of Sales, CTO"
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <button
              onClick={handleGenerateLeads}
              disabled={loading || !icp.industry}
              className="w-full md:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Generating Leads...' : 'Generate Leads (Demo)'}
            </button>
          </div>

          {/* Leads Display */}
          {leads.length > 0 && (
            <div className="bg-white/5 border border-white/10 rounded-lg p-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">
                  Generated Leads ({leads.length})
                </h2>
                <button
                  onClick={downloadCSV}
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition"
                >
                  Download CSV
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-3 px-4 text-gray-300 font-semibold">Company</th>
                      <th className="text-left py-3 px-4 text-gray-300 font-semibold">Industry</th>
                      <th className="text-left py-3 px-4 text-gray-300 font-semibold">Contact</th>
                      <th className="text-left py-3 px-4 text-gray-300 font-semibold">Title</th>
                      <th className="text-left py-3 px-4 text-gray-300 font-semibold">Email</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leads.map((lead) => (
                      <tr key={lead.id} className="border-b border-white/5 hover:bg-white/5">
                        <td className="py-3 px-4 text-white">
                          <div>
                            <div className="font-medium">{lead.company.name}</div>
                            <a href={lead.company.website} className="text-sm text-blue-400 hover:underline" target="_blank" rel="noopener noreferrer">
                              {lead.company.website}
                            </a>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-gray-300">{lead.company.industry}</td>
                        <td className="py-3 px-4 text-white">
                          <div>
                            <div className="font-medium">{lead.contact.name}</div>
                            <a href={lead.contact.linkedin} className="text-sm text-blue-400 hover:underline" target="_blank" rel="noopener noreferrer">
                              LinkedIn
                            </a>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-gray-300">{lead.contact.title}</td>
                        <td className="py-3 px-4">
                          <a href={`mailto:${lead.contact.email}`} className="text-blue-400 hover:underline">
                            {lead.contact.email}
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Empty State */}
          {leads.length === 0 && !loading && (
            <div className="bg-white/5 border border-white/10 rounded-lg p-12 text-center">
              <svg className="w-16 h-16 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-xl font-semibold text-gray-400 mb-2">No leads generated yet</h3>
              <p className="text-gray-500">Configure your ICP above and click "Generate Leads" to get started</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
