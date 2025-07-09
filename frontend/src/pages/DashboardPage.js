import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import * as api from '../services/api';

// You can keep your Icon and ICONS constants here or move them to a separate file
const Icon = ({ path, className = "w-6 h-6" }) => ( <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className}><path fillRule="evenodd" d={path} clipRule="evenodd" /></svg>);
const ICONS = {
    upload: "M12 16.5V9.75m0 0l-3.75 3.75M12 9.75l3.75 3.75M3 17.25V6.75a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 6.75v10.5a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 17.25z",
    briefcase: "M11.25 4.5A2.25 2.25 0 009 6.75v1.5a2.25 2.25 0 002.25 2.25h3.75a2.25 2.25 0 002.25-2.25v-1.5A2.25 2.25 0 0015 4.5h-3.75zM11.25 9V6.75h3.75V9h-3.75z",
    check: "M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    arrow: "M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3",
    search: "M15.75 15.75l-2.489-2.489m0 0a3.375 3.375 0 10-4.773-4.773 3.375 3.375 0 004.773 4.773zM21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    spinner: "M12 6v6m0 0v6m0-6h6m-6 0H6",
    logout: "M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m-3.75-3l3.75-3.75m0 0l-3.75-3.75m3.75 3.75H3"
};

function DashboardPage() {
    const [jobs, setJobs] = useState([]);
    const [cvAnalysis, setCvAnalysis] = useState(null);
    const [isDiscovering, setIsDiscovering] = useState(false);
    const [error, setError] = useState(null);
    const { user, logout } = useAuth();

    useEffect(() => {
        const loadInitialJobs = async () => {
            try {
                const matchedJobs = await api.getMatchedJobs();
                setJobs(matchedJobs);
            } catch (err) {
                setError(err.message);
            }
        };
        loadInitialJobs();
    }, []);

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        setError(null);
        try {
            const result = await api.uploadCv(file);
            setCvAnalysis(result.analysis);
            setJobs([]); // Clear old jobs
        } catch (err) {
            setError(err.message);
        }
    };

    const handleDiscoverJobs = async () => {
        if (!cvAnalysis) {
            setError('Please analyze a CV first by uploading it.');
            return;
        }
        setIsDiscovering(true);
        setError(null);
        try {
            await api.discoverJobs();
            const matchedJobs = await api.getMatchedJobs(); // Fetch fresh jobs
            setJobs(matchedJobs);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsDiscovering(false);
        }
    };
    
    // Your MatchScoreIndicator component can remain here
    const MatchScoreIndicator = ({ score }) => {
        // ... (same as your original component)
        const percentage = Math.round((score || 0) * 100);
        let bgColor = 'bg-red-100';
        let textColor = 'text-red-800';
        let ringColor = 'ring-red-200';

        if (percentage > 70) {
            bgColor = 'bg-green-100';
            textColor = 'text-green-800';
            ringColor = 'ring-green-200';
        } else if (percentage > 40) {
            bgColor = 'bg-yellow-100';
            textColor = 'text-yellow-800';
            ringColor = 'ring-yellow-200';
        }

        return (
            <div className={`flex items-center justify-center text-sm font-bold px-3 py-1 rounded-full ring-1 ring-inset ${bgColor} ${textColor} ${ringColor}`}>
                {percentage}% Match
            </div>
        );
    };

    return (
        <div className="bg-slate-50 min-h-screen font-sans text-slate-800">
            <div className="container mx-auto p-4 md:p-8">
                {/* Header */}
                <header className="mb-10 flex justify-between items-start">
                    <div>
                        <div className="flex items-center gap-3">
                            <Icon path={ICONS.briefcase} className="w-8 h-8 text-indigo-600" />
                            <h1 className="text-4xl font-bold text-slate-900">JobHuntGPT</h1>
                        </div>
                        <p className="mt-2 text-slate-500">Welcome, <span className="font-semibold text-indigo-700">{user?.email}</span>! Your AI co-pilot for the UK job market.</p>
                    </div>
                    <button onClick={logout} className="flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors">
                        <Icon path={ICONS.logout} className="w-5 h-5"/>
                        Logout
                    </button>
                </header>

                {error && <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-6">{error}</div>}

                {/* Main Content Grid */}
                <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column: Controls */}
                    <aside className="lg:col-span-1 space-y-8">
                       {/* CV Upload */}
                        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                            <div className="flex items-center gap-4">
                                <div className="bg-indigo-100 p-3 rounded-full"><Icon path={ICONS.upload} className="w-6 h-6 text-indigo-600" /></div>
                                <div>
                                    <h2 className="text-xl font-bold text-slate-900">1. Upload Your CV</h2>
                                    <p className="text-sm text-slate-500">Let's analyze your skills.</p>
                                </div>
                            </div>
                            <div className="mt-6">
                                <label htmlFor="cv-upload" className="w-full text-center cursor-pointer bg-slate-100 hover:bg-slate-200 transition-colors text-slate-700 font-semibold py-3 px-4 rounded-lg border border-slate-300 block">Choose File (.pdf, .docx)</label>
                                <input id="cv-upload" type="file" className="sr-only" onChange={handleFileUpload} />
                            </div>
                            {cvAnalysis && (
                                <div className="mt-6 bg-green-50 border-l-4 border-green-400 p-4 rounded-r-lg">
                                <div className="flex items-center gap-3">
                                    <Icon path={ICONS.check} className="w-5 h-5 text-green-600" />
                                    <p className="font-semibold text-green-800">CV Analyzed Successfully!</p>
                                </div>
                                <p className="text-sm text-green-700 mt-1">
                                    Industry: <span className="font-medium">{cvAnalysis.industry_category}</span> | Level: <span className="font-medium">{cvAnalysis.experience_level}</span>
                                </p>
                                </div>
                            )}
                        </div>

                        {/* Discover Jobs */}
                        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                            <h2 className="text-xl font-bold text-slate-900">2. Discover Opportunities</h2>
                            <p className="text-sm text-slate-500 mt-1">Find jobs tailored to your profile.</p>
                            <button onClick={handleDiscoverJobs} disabled={!cvAnalysis || isDiscovering} className="w-full mt-6 flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white font-bold py-3 px-4 rounded-lg transition-colors">
                                {isDiscovering ? (<> <Icon path={ICONS.spinner} className="w-5 h-5 animate-spin" /> <span>Searching...</span> </>) : (<> <Icon path={ICONS.search} className="w-5 h-5" /> <span>Discover Jobs</span> </>)}
                            </button>
                        </div>
                    </aside>
                    {/* Right Column: Job Listings */}
                    <section className="lg:col-span-2">
                        <h2 className="text-2xl font-bold text-slate-900 mb-4">Matched Jobs ({jobs.length})</h2>
                        <div className="space-y-4">
                            {jobs.length > 0 ? (
                                jobs.map(job => (
                                    <div key={job.id || job.job_url} className="bg-white p-6 rounded-2xl shadow-sm hover:shadow-md transition-shadow border border-slate-200 group">
                                        <div className="flex flex-col sm:flex-row justify-between gap-4">
                                            <div>
                                                <h3 className="text-lg font-bold text-slate-900">{job.title}</h3>
                                                <p className="text-slate-600">{job.company}</p>
                                                <p className="text-sm text-slate-500 mt-1">{job.location}</p>
                                            </div>
                                            <div className="flex-shrink-0"><MatchScoreIndicator score={job.score} /></div>
                                        </div>
                                        <div className="mt-4 pt-4 border-t border-slate-100 flex justify-between items-center">
                                            <p className="text-sm text-slate-500">Source: {job.source}</p>
                                            <a href={job.job_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm font-semibold text-indigo-600 hover:text-indigo-800 group-hover:underline">
                                                View Job <Icon path={ICONS.arrow} className="w-4 h-4" />
                                            </a>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-16 px-6 bg-white rounded-2xl border border-slate-200">
                                    <Icon path={ICONS.briefcase} className="w-12 h-12 mx-auto text-slate-300" />
                                    <h3 className="mt-4 text-xl font-semibold text-slate-900">No Jobs Found Yet</h3>
                                    <p className="mt-1 text-slate-500">{cvAnalysis ? 'Click "Discover Jobs" to start your search.' : 'Upload your CV to get started.'}</p>
                                </div>
                            )}
                        </div>
                    </section>
                </main>
            </div>
        </div>
    );
}

export default DashboardPage;
