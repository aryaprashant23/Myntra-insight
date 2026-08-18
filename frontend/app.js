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
    
    // Hide loader
    document.getElementById('chart-loader').style.display = 'none';

    const labels = Object.keys(tagCounts);
    const data = Object.values(tagCounts);
    
    const bgColors = labels.map(tag => getTagColor(tag).bg.replace('0.2', '0.6'));
    const borderColors = labels.map(tag => getTagColor(tag).border);

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
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#cbd5e1',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8
                }
            }
        }
    });
}

// Fetch Data
const fetchData = async () => {
    try {
        // 1. Fetch Total Raw Reviews
        const { count: totalRaw } = await supabase.from('raw_reviews').select('*', { count: 'exact', head: true });
        animateValue('stat-total-reviews', 0, totalRaw || 0, 1500);

        // 2. Fetch Valid Processed Reviews
        const { count: validProcessed } = await supabase.from('processed_reviews').select('*', { count: 'exact', head: true }).eq('is_valid', true);
        animateValue('stat-valid-reviews', 0, validProcessed || 0, 1500);

        // 3. Fetch Analysis Results
        const { data: analysisData, error } = await supabase.from('analysis_results').select('*').order('analyzed_at', { ascending: false });
        
        if (error) throw error;
        
        animateValue('stat-hesitations', 0, analysisData.length, 1500);

        // Process Data for Chart
        const tagCounts = {};
        analysisData.forEach(row => {
            tagCounts[row.hesitation_tag] = (tagCounts[row.hesitation_tag] || 0) + 1;
        });
        
        renderChart(tagCounts);

        // Process Data for Table
        const tbody = document.getElementById('quotes-table-body');
        tbody.innerHTML = ''; // clear loader
        
        if (analysisData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="2" class="px-6 py-12 text-center text-slate-500">No hesitations analyzed yet.</td></tr>';
            return;
        }

        analysisData.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.className = `hover:bg-slate-800/50 transition-colors animate-fade-in-up`;
            tr.style.animationDelay = `${0.1 + (index * 0.05)}s`;
            
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

    } catch (err) {
        console.error("Error fetching data:", err);
        document.getElementById('table-loader').innerHTML = `<td colspan="2" class="px-6 py-12 text-center text-red-400">Error connecting to database. See console.</td>`;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});
