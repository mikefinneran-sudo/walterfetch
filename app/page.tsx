'use client';

import { useState } from 'react';

export default function Home() {
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const plans = [
    {
      name: 'Starter',
      price: 99,
      features: [
        '500 verified leads/month',
        'Basic ICP targeting',
        'CSV export',
        'Email support'
      ],
      priceId: 'price_starter' // Replace with real Stripe price ID
    },
    {
      name: 'Pro',
      price: 249,
      features: [
        '2,000 verified leads/month',
        'Advanced ICP targeting',
        'CSV + CRM integration',
        'Priority support',
        'Weekly delivery'
      ],
      priceId: 'price_pro',
      popular: true
    },
    {
      name: 'Enterprise',
      price: 499,
      features: [
        'Unlimited leads',
        'Custom ICP builder',
        'API access',
        'Dedicated account manager',
        'Daily delivery',
        'Custom integrations'
      ],
      priceId: 'price_enterprise'
    }
  ];

  const handleCheckout = async (priceId: string) => {
    // TODO: Integrate Stripe checkout
    alert('Stripe integration coming next!');
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-blue-950 to-slate-950">
      {/* Hero */}
      <div className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            WalterFetch
          </h1>
          <p className="text-2xl md:text-3xl text-gray-300 mb-4">
            Signal Through the Noise
          </p>
          <p className="text-xl text-gray-400 mb-12">
            AI-powered lead generation that actually works.<br />
            Get 500+ verified prospects every month for 80% less than ZoomInfo.
          </p>
          <div className="flex gap-4 justify-center">
            <a href="#pricing" className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition">
              Get Started
            </a>
            <a href="#how-it-works" className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-lg transition">
              How It Works
            </a>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="text-center p-6 bg-white/5 rounded-lg border border-white/10">
            <div className="text-4xl font-bold text-blue-400 mb-2">95%</div>
            <div className="text-gray-400">Verification Rate</div>
          </div>
          <div className="text-center p-6 bg-white/5 rounded-lg border border-white/10">
            <div className="text-4xl font-bold text-blue-400 mb-2">$0.20</div>
            <div className="text-gray-400">Cost Per Lead</div>
          </div>
          <div className="text-center p-6 bg-white/5 rounded-lg border border-white/10">
            <div className="text-4xl font-bold text-blue-400 mb-2">80%</div>
            <div className="text-gray-400">Cheaper Than Competitors</div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div id="how-it-works" className="container mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-16 text-white">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="p-8 bg-white/5 rounded-xl border border-white/10">
            <div className="text-3xl font-bold text-blue-400 mb-4">1</div>
            <h3 className="text-xl font-semibold mb-3 text-white">Define Your ICP</h3>
            <p className="text-gray-400">
              Tell us your ideal customer profile - industry, size, location, and more.
            </p>
          </div>
          <div className="p-8 bg-white/5 rounded-xl border border-white/10">
            <div className="text-3xl font-bold text-blue-400 mb-4">2</div>
            <h3 className="text-xl font-semibold mb-3 text-white">AI Finds & Verifies</h3>
            <p className="text-gray-400">
              Our engine scrapes, enriches, and verifies prospects automatically.
            </p>
          </div>
          <div className="p-8 bg-white/5 rounded-xl border border-white/10">
            <div className="text-3xl font-bold text-blue-400 mb-4">3</div>
            <h3 className="text-xl font-semibold mb-3 text-white">Receive Your Leads</h3>
            <p className="text-gray-400">
              Get verified leads delivered weekly via CSV or direct CRM integration.
            </p>
          </div>
        </div>
      </div>

      {/* Pricing */}
      <div id="pricing" className="container mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-4 text-white">Simple, Transparent Pricing</h2>
        <p className="text-center text-gray-400 mb-16">No contracts. Cancel anytime.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`p-8 rounded-2xl border ${
                plan.popular
                  ? 'bg-gradient-to-b from-blue-900/20 to-purple-900/20 border-blue-500'
                  : 'bg-white/5 border-white/10'
              } relative`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-blue-600 text-white text-sm font-semibold rounded-full">
                  Most Popular
                </div>
              )}

              <h3 className="text-2xl font-bold mb-2 text-white">{plan.name}</h3>
              <div className="mb-6">
                <span className="text-5xl font-bold text-white">${plan.price}</span>
                <span className="text-gray-400">/month</span>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start text-gray-300">
                    <svg className="w-5 h-5 text-blue-400 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleCheckout(plan.priceId)}
                className={`w-full py-4 rounded-lg font-semibold transition ${
                  plan.popular
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-white/10 hover:bg-white/20 text-white'
                }`}
              >
                Get Started
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Social Proof */}
      <div className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-8 text-white">Trusted By</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-8 text-gray-400">
            <div>Private Equity Firms</div>
            <div>B2B Sales Teams</div>
            <div>Growth Agencies</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center text-gray-400">
            <div className="mb-4 md:mb-0">
              <span className="font-bold text-white">WalterFetch</span> - Part of WalterSignal
            </div>
            <div className="flex gap-8">
              <a href="https://github.com/mikefinneran-sudo/walterfetch" className="hover:text-white transition">
                GitHub
              </a>
              <a href="mailto:hello@waltersignal.ai" className="hover:text-white transition">
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
