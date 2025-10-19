import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { icp, limit = 500 } = await req.json();

    // Validate ICP (Ideal Customer Profile) input
    if (!icp || !icp.industry) {
      return Response.json(
        { error: 'ICP with industry is required' },
        { status: 400 }
      );
    }

    // TODO: Call Python backend scraping engine
    // For now, return mock data structure
    const leads = await generateLeads(icp, limit);

    return Response.json({
      success: true,
      count: leads.length,
      leads: leads,
      generatedAt: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error('Lead generation error:', error);
    return Response.json(
      { error: error.message || 'Failed to generate leads' },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  // Health check endpoint
  return Response.json({
    status: 'ok',
    service: 'WalterFetch Lead Generation API',
    version: '1.0.0',
  });
}

// Mock lead generation (will be replaced with actual Python backend call)
async function generateLeads(icp: any, limit: number) {
  // This will eventually call the Python scraping engine
  // For now, return structured mock data
  return Array.from({ length: Math.min(limit, 10) }, (_, i) => ({
    id: `lead_${Date.now()}_${i}`,
    company: {
      name: `${icp.industry} Company ${i + 1}`,
      industry: icp.industry,
      size: icp.companySize || '50-200',
      location: icp.location || 'United States',
      website: `https://example-${i + 1}.com`,
    },
    contact: {
      name: `Decision Maker ${i + 1}`,
      title: icp.title || 'VP of Sales',
      email: `contact${i + 1}@example-${i + 1}.com`,
      linkedin: `https://linkedin.com/in/contact-${i + 1}`,
    },
    enrichment: {
      verified: true,
      lastUpdated: new Date().toISOString(),
      confidence: 0.95,
    },
  }));
}
