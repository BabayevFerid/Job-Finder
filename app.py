// API Configuration
const API_KEYS = {
    upwork: 'YOUR_UPWORK_API_KEY',
    freelancer: 'YOUR_FREELANCER_API_KEY'
};

// DOM Elements
const searchInput = document.getElementById('searchInput');
const platformSelect = document.getElementById('platformSelect');
const searchBtn = document.getElementById('searchBtn');
const jobList = document.getElementById('jobList');
const detailTitle = document.getElementById('detailTitle');
const detailPlatform = document.getElementById('detailPlatform');
const detailPrice = document.getElementById('detailPrice');
const detailDate = document.getElementById('detailDate');
const detailSkills = document.getElementById('detailSkills');
const detailDescription = document.getElementById('detailDescription');
const detailLink = document.getElementById('detailLink');
const upworkStatus = document.getElementById('upworkStatus');
const freelancerStatus = document.getElementById('freelancerStatus');
const offlineStatus = document.getElementById('offlineStatus');
const installBtn = document.getElementById('installBtn');

// Global variables
let jobs = [];
let deferredPrompt;

// Check API status
updateApiStatus();

// Event Listeners
searchBtn.addEventListener('click', searchJobs);
installBtn.addEventListener('click', installApp);

// Check network status
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

// Before install prompt
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installBtn.classList.remove('hidden');
});

// Initialize service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

// Functions
function updateApiStatus() {
    upworkStatus.textContent = 'Upwork';
    upworkStatus.classList.toggle('active', !!API_KEYS.upwork);
    
    freelancerStatus.textContent = 'Freelancer';
    freelancerStatus.classList.toggle('active', !!API_KEYS.freelancer);
}

function updateOnlineStatus() {
    if (navigator.onLine) {
        offlineStatus.classList.remove('show');
    } else {
        offlineStatus.classList.add('show');
    }
}

async function searchJobs() {
    const keyword = searchInput.value.trim();
    const platform = platformSelect.value;
    
    if (!keyword) {
        alert('Please enter search keywords');
        return;
    }
    
    if (!API_KEYS.upwork && !API_KEYS.freelancer) {
        alert('API keys not configured');
        return;
    }
    
    jobList.innerHTML = '<div class="loading">Searching for jobs...</div>';
    detailTitle.textContent = 'Select a job to view details';
    detailPlatform.textContent = '';
    detailPrice.textContent = '';
    detailDate.textContent = '';
    detailSkills.innerHTML = '';
    detailDescription.textContent = '';
    detailLink.href = '#';
    
    try {
        jobs = [];
        
        if (platform === 'all' || platform === 'upwork') {
            if (API_KEYS.upwork) {
                const upworkJobs = await fetchUpworkJobs(keyword);
                jobs = jobs.concat(upworkJobs);
            }
        }
        
        if (platform === 'all' || platform === 'freelancer') {
            if (API_KEYS.freelancer) {
                const freelancerJobs = await fetchFreelancerJobs(keyword);
                jobs = jobs.concat(freelancerJobs);
            }
        }
        
        displayJobList();
    } catch (error) {
        console.error('Search error:', error);
        jobList.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
}

async function fetchUpworkJobs(keyword) {
    try {
        const response = await fetch(`https://api.upwork.com/api/jobs/v2/jobs/search?q=${encodeURIComponent(keyword)}&limit=10`, {
            headers: {
                'Authorization': `Bearer ${API_KEYS.upwork}`,
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Upwork API request failed');
        }
        
        const data = await response.json();
        
        return data.jobs.map(job => ({
            id: job.id,
            title: job.title,
            description: job.snippet,
            price: job.budget?.amount ? `$${job.budget.amount}` : 'N/A',
            platform: 'Upwork',
            url: job.url,
            date: new Date(job.posted_on).toLocaleDateString(),
            skills: job.skills || []
        }));
    } catch (error) {
        console.error('Upwork API error:', error);
        return [];
    }
}

async function fetchFreelancerJobs(keyword) {
    try {
        const response = await fetch('https://www.freelancer.com/api/projects/0.1/projects/search/', {
            method: 'POST',
            headers: {
                'freelancer-oauth-v1': API_KEYS.freelancer,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: keyword,
                limit: 10,
                sort_field: "submitdate",
                job_details: true
            })
        });
        
        if (!response.ok) {
            throw new Error('Freelancer API request failed');
        }
        
        const data = await response.json();
        
        return data.projects.map(project => ({
            id: project.id,
            title: project.title,
            description: project.description,
            price: project.budget?.minimum ? `$${project.budget.minimum}` : 'N/A',
            platform: 'Freelancer',
            url: `https://www.freelancer.com/projects/${project.id}`,
            date: new Date(project.submitdate * 1000).toLocaleDateString(),
            skills: project.jobs?.map(job => job.name) || []
        }));
    } catch (error) {
        console.error('Freelancer API error:', error);
        return [];
    }
}

function displayJobList() {
    jobList.innerHTML = '';
    
    if (jobs.length === 0) {
        jobList.innerHTML = '<div class="loading">No jobs found</div>';
        return;
    }
    
    jobs.forEach(job => {
        const jobElement = document.createElement('div');
        jobElement.className = 'job-card';
        jobElement.dataset.id = job.id;
        
        jobElement.innerHTML = `
            <h3>${job.title}</h3>
            <div>
                <span class="platform">${job.platform}</span>
                <span class="price">${job.price}</span>
            </div>
            <p>${job.date}</p>
        `;
        
        jobElement.addEventListener('click', () => showJobDetails(job.id));
        jobList.appendChild(jobElement);
    });
}

function showJobDetails(jobId) {
    const job = jobs.find(j => j.id === jobId);
    if (!job) return;
    
    detailTitle.textContent = job.title;
    detailPlatform.textContent = job.platform;
    detailPrice.textContent = job.price;
    detailDate.textContent = job.date;
    
    detailSkills.innerHTML = '';
    job.skills.forEach(skill => {
        const skillElement = document.createElement('span');
        skillElement.textContent = skill;
        detailSkills.appendChild(skillElement);
    });
    
    detailDescription.textContent = job.description;
    detailLink.href = job.url;
    detailLink.textContent = `View on ${job.platform}`;
}

function installApp() {
    if (!deferredPrompt) return;
    
    deferredPrompt.prompt();
    
    deferredPrompt.userChoice.then(choiceResult => {
        if (choiceResult.outcome === 'accepted') {
            console.log('User accepted install prompt');
        } else {
            console.log('User dismissed install prompt');
        }
        deferredPrompt = null;
        installBtn.classList.add('hidden');
    });
}
