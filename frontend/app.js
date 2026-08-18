// --- CONFIGURATION ---
// IMPORTANT: Change this to your Railway URL once deployed (e.g. 'https://myntra-insight-production.up.railway.app')
const BACKEND_API_URL = 'http://localhost:8000'; 

// Supabase Credentials
const SUPABASE_URL = 'https://lmvwdvueptvglihzhebp.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtdndkdnVlcHR2Z2xpaHpoZWJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4Mzg2NTEzMiwiZXhwIjoyMDk5NDQxMTMyfQ.NVv1xnF4bdZmNL2wPO8mWQh2JxeYDzVz3ssdMwNLyxs';

const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// Color palette mapping for tags
const tagColors = {
    'Size/Fit': { bg: 'rgba(236, 72, 153, 0.2)', border: '#ec4899', text: 'text-pink-400' },
    'Price': { bg: 'rgba(34, 197, 94, 0.2)', border: '#22c55e', text: 'text-green-400' },
    'Styling': { bg: 'rgba(168, 85, 247, 0.2)', border: '#a855f7', text: 'text-purple-400' },
    'Occasion': { bg: 'rgba(234, 179, 8, 0.2)', border: '#eab308', text: 'text-yellow-400' },
    'Comparing': { bg: 'rgba(59, 130, 246, 0.2)', border: '#3b82f6', text: 'text-blue-400' },
    'Window Shopping': { bg: 'rgba(249, 115, 22, 0.2)', border: '#f97316', text: 'text-orange-400' },
    'Trust/Quality': { bg: 'rgba(239, 68, 68, 0.2)', border: '#ef4444', text: 'text-red-400' },
    'Other': { bg: 'rgba(100, 116, 139, 0.2)', border: '#64748b', text: 'text-slate-400' },
};

const getTagColor = (tag) => tagColors[tag] || tagColors['Other'];

// Animate counting numbers
const animateValue = (id, start, end, duration) => {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        document.getElementById(id).innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Render Chart
let hesitationChartInstance = null;
const renderChart = (tagCounts) => {
    const ctx = document.getElementById('hesitationChart').getContext('2d');
    
    document.getElementById('chart-loader').style.display = 'none';

    const labels = Object.keys(tagCounts);
    const data = Object.values(tagCounts);
    
    const bgColors = labels.map(tag => getTagColor(tag).bg.replace('0.2', '0.6'));
    const borderColors = labels.map(tag => getTagColor(tag).border);

    if (hesitationChartInstance) {
        hesitationChartInstance.destroy();
    }

    hesitationChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: bgColors,
                borderColor: borderColors,
                borderWidth: 1,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#cbd5e1', padding: 20, font: { family: 'Inter', size: 12 } }
                }
            }
        }
    });
}

// Generate Summary Text based on data
const generateSummary = (total, topTag) => {
    if (total === 0) return "No hesitations found in this timeframe. Run a scrape to fetch new data.";
    return `In this timeframe, the AI identified <strong>${total}</strong> specific purchase hesitations. The most common bottleneck preventing checkout is <strong>${topTag}</strong>.`;
}

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

        document.getElementById('table-time-label').innerText = timeFilter === 'all' ? 'All Time' : `Last ${timeFilter} Days`;

        // 1. Fetch Analysis Results
        let analysisQuery = supabase.from('analysis_results').select('*').order('analyzed_at', { ascending: false });
        if (timeConstraint) {
            analysisQuery = analysisQuery.gte('analyzed_at', timeConstraint);
        }
        
        const { data: analysisData, error } = await analysisQuery;
        if (error) throw error;
        
        animateValue('stat-hesitations', 0, analysisData.length, 1000);

        // Process Data for Chart & Categorization
        const tagCounts = {};
        const groupedData = {}; // For categorization in table
        
        analysisData.forEach(row => {
            tagCounts[row.hesitation_tag] = (tagCounts[row.hesitation_tag] || 0) + 1;
            if (!groupedData[row.hesitation_tag]) groupedData[row.hesitation_tag] = [];
            groupedData[row.hesitation_tag].push(row);
        });
        
        renderChart(tagCounts);

        // Calculate Top Tag for Summary
        let topTag = 'None';
        let maxCount = 0;
        for (const [tag, count] of Object.entries(tagCounts)) {
            if (count > maxCount) { maxCount = count; topTag = tag; }
        }
        document.getElementById('summary-text').innerHTML = generateSummary(analysisData.length, topTag);

        // Process Data for Categorized Table
        const tbody = document.getElementById('quotes-table-body');
        tbody.innerHTML = ''; 
        
        if (analysisData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="2" class="px-6 py-12 text-center text-slate-500">No data available for this timeframe.</td></tr>';
        } else {
            // Render Grouped by Tag
            Object.keys(groupedData).sort().forEach((tag) => {
                groupedData[tag].forEach((row, index) => {
                    const tr = document.createElement('tr');
                    tr.className = `hover:bg-slate-800/50 transition-colors`;
                    
                    const colorMeta = getTagColor(row.hesitation_tag);
                    
                    tr.innerHTML = `
                        <td class="px-6 py-4 border-b border-slate-700/50 whitespace-nowrap">
                            <span class="tag-badge bg-slate-900 border-slate-700 ${colorMeta.text}" style="background-color: ${colorMeta.bg}; border-color: ${colorMeta.border}">
                                ${row.hesitation_tag}
                            </span>
                        </td>
                        <td class="px-6 py-4 border-b border-slate-700/50 text-slate-300 italic">
                            "${row.extracted_quote}"
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            });
        }

        // Update Total Stats (without time filters for global perspective)
        const { count: totalRaw } = await supabase.from('raw_reviews').select('*', { count: 'exact', head: true });
        animateValue('stat-total-reviews', 0, totalRaw || 0, 1000);

        const { count: validProcessed } = await supabase.from('processed_reviews').select('*', { count: 'exact', head: true }).eq('is_valid', true);
        animateValue('stat-valid-reviews', 0, validProcessed || 0, 1000);

    } catch (err) {
        console.error("Error fetching data:", err);
        document.getElementById('table-loader').innerHTML = `<td colspan="2" class="px-6 py-12 text-center text-red-400">Error connecting to database.</td>`;
    }
}

// Trigger Backend Scrape
const triggerScrape = async () => {
    const btn = document.getElementById('btn-scrape');
    const icon = document.getElementById('icon-scrape');
    const text = document.getElementById('text-scrape');
    const toast = document.getElementById('status-toast');
    const toastMsg = document.getElementById('toast-message');

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

        const result = await response.json();
        
        toast.classList.remove('hidden');
        toastMsg.innerText = result.message;
        
        // Polling to refresh data every 10 seconds while background job runs
        let pollCount = 0;
        const pollInterval = setInterval(() => {
            fetchData();
            pollCount++;
            if (pollCount > 6) clearInterval(pollInterval); // Stop polling after a minute
        }, 10000);

    } catch (error) {
        console.error("Scrape API Error:", error);
        toast.classList.remove('hidden', 'bg-emerald-500/10', 'text-emerald-400', 'border-emerald-500/50');
        toast.classList.add('bg-red-500/10', 'text-red-400', 'border-red-500/50');
        toastMsg.innerText = "Error: Cannot reach the backend API. Check if the server is running.";
        document.getElementById('api-warning').classList.remove('hidden');
    } finally {
        // Reset UI Button
        setTimeout(() => {
            btn.disabled = false;
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
            icon.classList.remove('animate-spin');
            text.innerText = "Scrape New Data";
        }, 3000);
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    fetchData();
    
    document.getElementById('time-filter').addEventListener('change', () => {
        document.getElementById('quotes-table-body').innerHTML = '<tr id="table-loader"><td colspan="2" class="px-6 py-12 text-center text-slate-500"><i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2"></i>Filtering data...</td></tr>';
        lucide.createIcons();
        fetchData();
    });

    document.getElementById('btn-scrape').addEventListener('click', triggerScrape);
});
