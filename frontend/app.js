// --- CONFIGURATION ---
// IMPORTANT: Change this to your Railway URL once deployed (e.g. 'https://myntra-insight-production.up.railway.app')
const BACKEND_API_URL = 'https://myntra-insight-production.up.railway.app'; 

// Supabase Credentials
const SUPABASE_URL = 'https://lmvwdvueptvglihzhebp.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtdndkdnVlcHR2Z2xpaHpoZWJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4Mzg2NTEzMiwiZXhwIjoyMDk5NDQxMTMyfQ.NVv1xnF4bdZmNL2wPO8mWQh2JxeYDzVz3ssdMwNLyxs';

const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// Color mappings for specific tags
const getTagColorClass = (tag) => {
    const t = tag.toLowerCase();
    if (t.includes('size') || t.includes('fit')) return 'text-error';
    if (t.includes('price') || t.includes('money')) return 'text-secondary';
    if (t.includes('trust') || t.includes('quality')) return 'text-primary';
    return 'text-on-surface-variant';
};

// Generate HTML card for a single review
const createReviewCard = (quote, tag, source) => {
    const color = getTagColorClass(tag);
    return `
    <div class="p-3 bg-surface-container/40 rounded-lg border border-white/5 transition-colors hover:bg-surface-container/60">
        <p class="font-code-md text-[13px] text-on-surface mb-2">"${quote}"</p>
        <div class="flex justify-between items-center">
            <span class="font-label-sm text-[10px] ${color} uppercase px-2 py-1 bg-white/5 rounded-full">${tag}</span>
        </div>
    </div>`;
};

// Generate Summary Cards
const createSummaryCard = (tag, count, sourceString, isTop) => {
    const icon = isTop ? 'trending_up' : 'insights';
    const color = isTop ? 'text-secondary' : 'text-primary';
    return `
    <div class="bg-surface-container p-4 rounded-lg border border-white/5">
        <div class="font-label-sm ${color} mb-2 flex items-center gap-2">
            <span class="material-symbols-outlined text-[16px]">${icon}</span> ${isTop ? 'Highest Friction Point' : 'Significant Friction'}
        </div>
        <p class="font-body-md text-on-surface font-bold text-lg">${tag}</p>
        <div class="font-label-sm text-on-surface-variant mt-2 text-right">${count} Occurrences • Found in ${sourceString}</div>
    </div>`;
};

// Fetch Data with Time Filter
const fetchData = async () => {
    try {
        const timeFilter = document.getElementById('time-filter').value;
        let timeConstraint = null;

        if (timeFilter !== 'all') {
            const date = new Date();
            date.setDate(date.getDate() - parseInt(timeFilter));
            timeConstraint = date.toISOString();
        }

        // Fetch Analysis Results joined with Source
        let analysisQuery = supabase.from('analysis_results')
            .select('*, processed_reviews(*, raw_reviews(source))')
            .order('analyzed_at', { ascending: false });

        if (timeConstraint) {
            analysisQuery = analysisQuery.gte('analyzed_at', timeConstraint);
        }
        
        const { data: analysisData, error } = await analysisQuery;
        if (error) throw error;
        
        // Split data by source
        const redditData = [];
        const playstoreData = [];
        const youtubeData = [];
        const tagCounts = {};

        analysisData.forEach(row => {
            // Count for summary
            tagCounts[row.hesitation_tag] = (tagCounts[row.hesitation_tag] || 0) + 1;
            
            // Route to correct column
            const source = row.processed_reviews?.raw_reviews?.source?.toLowerCase() || '';
            if (source.includes('reddit')) {
                redditData.push(row);
            } else if (source.includes('youtube')) {
                youtubeData.push(row);
            } else {
                playstoreData.push(row);
            }
        });

        // Update UI Columns
        const renderColumn = (id, data, emptyText) => {
            const el = document.getElementById(id);
            if (data.length === 0) {
                el.innerHTML = `<div class="text-center text-on-surface-variant py-8 font-code-md text-[13px]">${emptyText}</div>`;
            } else {
                el.innerHTML = data.map(r => createReviewCard(r.extracted_quote, r.hesitation_tag, r.processed_reviews?.raw_reviews?.source)).join('');
            }
        };

        renderColumn('col-reddit', redditData, 'No recent Reddit hesitations found.');
        renderColumn('col-playstore', playstoreData, 'No recent App Store hesitations found.');
        renderColumn('col-youtube', youtubeData, 'No recent YouTube hesitations found.');

        // Update Summary
        const sortedTags = Object.entries(tagCounts).sort((a, b) => b[1] - a[1]);
        const summaryContainer = document.getElementById('summary-container');
        
        if (sortedTags.length === 0) {
            summaryContainer.innerHTML = '<div class="text-on-surface-variant w-full col-span-2 text-center py-4">Run the scraper to collect AI analytics.</div>';
        } else {
            const topTag = sortedTags[0];
            const secondTag = sortedTags.length > 1 ? sortedTags[1] : null;
            
            let html = createSummaryCard(topTag[0], topTag[1], "Multiple Sources", true);
            if (secondTag) {
                html += createSummaryCard(secondTag[0], secondTag[1], "Multiple Sources", false);
            }
            summaryContainer.innerHTML = html;
        }

        // Update Badge
        const { count: totalRaw } = await supabase.from('raw_reviews').select('*', { count: 'exact', head: true });
        document.getElementById('total-scraped-badge').innerText = `${totalRaw || 0} Total Reviews Ingested`;

    } catch (err) {
        console.error("Error fetching data:", err);
    }
}

// Trigger Backend Scrape
const triggerScrape = async () => {
    const btn = document.getElementById('btn-scrape');
    const icon = document.getElementById('icon-scrape');
    const text = document.getElementById('text-scrape');
    const statusMsg = document.getElementById('scrape-status');

    // UI Loading State
    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed');
    icon.classList.add('animate-spin');
    text.innerText = "Initiating Pipeline...";

    try {
        const response = await fetch(`${BACKEND_API_URL}/api/scrape`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error("Failed to reach backend.");
        
        statusMsg.classList.remove('hidden');
        statusMsg.classList.replace('text-error', 'text-secondary');
        statusMsg.innerText = "Scraping pipeline triggered! Data will refresh automatically.";
        
        // Poll for fresh data
        let pollCount = 0;
        const pollInterval = setInterval(() => {
            fetchData();
            pollCount++;
            if (pollCount > 6) clearInterval(pollInterval);
        }, 10000);

    } catch (error) {
        console.error("Scrape API Error:", error);
        statusMsg.classList.remove('hidden');
        statusMsg.classList.replace('text-secondary', 'text-error');
        statusMsg.innerText = "Failed to connect to backend server. Check API URL.";
    } finally {
        setTimeout(() => {
            btn.disabled = false;
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
            icon.classList.remove('animate-spin');
            text.innerText = "Scrape Data";
        }, 3000);
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    fetchData();
    
    document.getElementById('time-filter').addEventListener('change', () => {
        const loader = '<div class="text-center text-on-surface-variant py-8"><span class="material-symbols-outlined animate-spin">refresh</span></div>';
        document.getElementById('col-reddit').innerHTML = loader;
        document.getElementById('col-playstore').innerHTML = loader;
        document.getElementById('col-youtube').innerHTML = loader;
        fetchData();
    });

    document.getElementById('btn-scrape').addEventListener('click', triggerScrape);
});
