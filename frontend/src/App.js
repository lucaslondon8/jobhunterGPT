import React, { useState, useEffect } from 'react';

function App() {
  const [status, setStatus] = useState('loading');
  const [stats, setStats] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [cvAnalysis, setCvAnalysis] = useState(null);
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [userEmail, setUserEmail] = useState(localStorage.getItem('user_email') || '');
  const [userName, setUserName] = useState(localStorage.getItem('user_name') || '');
  const [showUserForm, setShowUserForm] = useState(false);

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      const testResponse = await fetch('http://localhost:8000/api/test');
      if (!testResponse.ok) throw new Error('API not responding');
      
      setStatus('connected');
      await loadDashboardData();
      
    } catch (error) {
      console.error('API Error:', error);
      setStatus('error');
    }
  };

  const loadDashboardData = async () => {
    try {
      const statsResponse = await fetch('http://localhost:8000/api/dashboard-stats');
      const statsData = await statsResponse.json();
      setStats(statsData);
      
      try {
        const cvResponse = await fetch('http://localhost:8000/api/cv-analysis');
        const cvData = await cvResponse.json();
        setCvAnalysis(cvData.analysis);
      } catch (e) {
        // No CV uploaded yet
      }
      
      try {
        const jobsResponse = await fetch('http://localhost:8000/api/jobs/matches');
        const jobsData = await jobsResponse.json();
        setJobs(jobsData);
      } catch (e) {
        // No jobs yet
      }
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/upload-cv', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setCvAnalysis(result.analysis);
        alert('CV uploaded and analyzed successfully!');
        await loadDashboardData();
      } else {
        const error = await response.json();
        alert(`Failed to upload CV: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed: ' + error.message);
    }
  };

  const handleDiscoverJobs = async () => {
    if (!cvAnalysis) {
      alert('Please upload a CV first');
      return;
    }

    setIsDiscovering(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/discover-jobs', {
        method: 'POST',
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Discovered ${result.jobs_found} jobs!`);
        await loadDashboardData();
      } else {
        const error = await response.json();
        alert(`Failed to discover jobs: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Discovery error:', error);
      alert('Job discovery failed: ' + error.message);
    } finally {
      setIsDiscovering(false);
    }
  };

  const handleApplyToJob = async (jobId) => {
    // Check if user details are available
    if (!userEmail || !userName) {
      setShowUserForm(true);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/applications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_match_id: jobId.toString(),
          user_email: userEmail,
          user_name: userName,
          send_email: true
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Application result:', result);
        
        let message = `Application created for ${result.job_title} at ${result.company}!`;
        if (result.email_sent) {
          message += '\n✅ Email sent successfully!';
        } else if (result.email_result) {
          message += `\n⚠️ Email sending failed: ${result.email_result.error}`;
        }
        
        alert(message);
        await loadDashboardData();
      } else {
        const errorText = await response.text();
        let errorMessage = 'Unknown error';
        
        try {
          const errorObj = JSON.parse(errorText);
          errorMessage = errorObj.detail || errorObj.message || 'Unknown error';
        } catch (e) {
          errorMessage = errorText || 'Unknown error';
        }
        
        alert(`Failed to send application: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Application error:', error);
      alert('Application failed: ' + error.message);
    }
  };

  const saveUserDetails = () => {
    if (!userEmail || !userName) {
      alert('Please enter both email and name');
      return;
    }
    
    localStorage.setItem('user_email', userEmail);
    localStorage.setItem('user_name', userName);
    setShowUserForm(false);
    alert('User details saved! You can now apply to jobs.');
  };

  if (status === 'loading') {
    return (
      <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'Arial, sans-serif' }}>
        <h1>🎯 JobHuntGPT</h1>
        <p>Connecting to backend...</p>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'Arial, sans-serif' }}>
        <h1>🎯 JobHuntGPT</h1>
        <div style={{ color: 'red', marginBottom: '20px' }}>
          ❌ Cannot connect to backend API
        </div>
      </div>
    );
  }

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* User Details Modal */}
      {showUserForm && (
        <div style={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.5)', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{ 
            backgroundColor: 'white', 
            padding: '30px', 
            borderRadius: '8px', 
            maxWidth: '400px',
            width: '90%'
          }}>
            <h3 style={{ marginTop: 0 }}>📧 Enter Your Details for Email Applications</h3>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Your Name:</label>
              <input
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="Enter your full name"
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  border: '1px solid #ddd', 
                  borderRadius: '4px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Your Email:</label>
              <input
                type="email"
                value={userEmail}
                onChange={(e) => setUserEmail(e.target.value)}
                placeholder="Enter your email address"
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  border: '1px solid #ddd', 
                  borderRadius: '4px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => setShowUserForm(false)}
                style={{
                  flex: 1,
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  backgroundColor: 'white',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button
                onClick={saveUserDetails}
                style={{
                  flex: 1,
                  padding: '10px',
                  border: 'none',
                  borderRadius: '4px',
                  backgroundColor: '#007bff',
                  color: 'white',
                  cursor: 'pointer'
                }}
              >
                Save & Continue
              </button>
            </div>
          </div>
        </div>
      )}

      <header style={{ borderBottom: '2px solid #eee', paddingBottom: '20px', marginBottom: '30px' }}>
        <h1 style={{ color: '#333', display: 'flex', alignItems: 'center', gap: '10px' }}>
          🎯 JobHuntGPT
          <span style={{ fontSize: '14px', background: '#e8f5e8', color: '#2d5016', padding: '4px 8px', borderRadius: '4px' }}>
            ✅ Connected
          </span>
        </h1>
        <p style={{ color: '#666', margin: '10px 0 0 0' }}>AI-Powered Job Application Automation with Email & Cover Letters</p>
        
        {/* User Status */}
        {userEmail && userName ? (
          <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
            📧 Logged in as: <strong>{userName}</strong> ({userEmail})
            <button
              onClick={() => setShowUserForm(true)}
              style={{ 
                marginLeft: '10px', 
                padding: '2px 6px', 
                fontSize: '12px', 
                border: '1px solid #ddd', 
                borderRadius: '3px',
                background: 'white',
                cursor: 'pointer'
              }}
            >
              Edit
            </button>
          </div>
        ) : (
          <div style={{ marginTop: '10px', fontSize: '14px', color: '#856404', background: '#fff3cd', padding: '8px', borderRadius: '4px' }}>
            ⚠️ Please set your email details to send applications: 
            <button
              onClick={() => setShowUserForm(true)}
              style={{ 
                marginLeft: '10px', 
                padding: '4px 8px', 
                fontSize: '12px', 
                border: 'none', 
                borderRadius: '3px',
                background: '#007bff',
                color: 'white',
                cursor: 'pointer'
              }}
            >
              Set Details
            </button>
          </div>
        )}
      </header>

      {/* CV Status */}
      <div style={{ marginBottom: '30px' }}>
        {cvAnalysis ? (
          <div style={{ background: '#e8f5e8', border: '1px solid #c3e6c3', borderRadius: '8px', padding: '15px' }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#2d5016' }}>✅ CV Analyzed</h3>
            <p style={{ margin: '0', color: '#2d5016' }}>
              Experience: <strong>{cvAnalysis.experience_level}</strong> | 
              Industry: <strong>{cvAnalysis.primary_industry || 'tech'}</strong> | 
              Skills: <strong>{cvAnalysis.skills ? cvAnalysis.skills.length : 0}</strong>
            </p>
          </div>
        ) : (
          <div style={{ background: '#fff3cd', border: '1px solid #ffeaa7', borderRadius: '8px', padding: '15px' }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#856404' }}>📄 Upload Your CV</h3>
            <p style={{ margin: '0 0 15px 0', color: '#856404' }}>
              Upload your CV (TXT, PDF, DOCX) to enable intelligent job discovery
            </p>
            <input
              type="file"
              accept=".txt,.pdf,.doc,.docx"
              onChange={handleFileUpload}
              style={{ marginRight: '10px' }}
            />
          </div>
        )}
      </div>

      {/* Stats Dashboard */}
      {stats && (
        <div style={{ marginBottom: '30px' }}>
          <h2>📊 Dashboard Statistics</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            <div style={{ background: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '8px', padding: '15px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>{stats.applications_sent}</div>
              <div style={{ color: '#666', fontSize: '14px' }}>Applications Sent</div>
            </div>
            <div style={{ background: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '8px', padding: '15px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>{stats.response_rate}%</div>
              <div style={{ color: '#666', fontSize: '14px' }}>Response Rate</div>
            </div>
            <div style={{ background: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '8px', padding: '15px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#6f42c1' }}>{stats.jobs_discovered}</div>
              <div style={{ color: '#666', fontSize: '14px' }}>Jobs Discovered</div>
            </div>
            <div style={{ background: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '8px', padding: '15px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fd7e14' }}>{stats.email_discovery_rate}%</div>
              <div style={{ color: '#666', fontSize: '14px' }}>Email Success Rate</div>
            </div>
          </div>
        </div>
      )}

      {/* Job Discovery */}
      <div style={{ marginBottom: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>🔍 Job Discovery ({jobs.length} found)</h2>
          <button
            onClick={handleDiscoverJobs}
            disabled={!cvAnalysis || isDiscovering}
            style={{
              background: (!cvAnalysis || isDiscovering) ? '#6c757d' : '#28a745',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '6px',
              cursor: (!cvAnalysis || isDiscovering) ? 'not-allowed' : 'pointer',
              fontSize: '16px'
            }}
          >
            {isDiscovering ? '🔄 Discovering...' : '🚀 Discover Jobs'}
          </button>
        </div>

        {jobs.length > 0 ? (
          <div style={{ display: 'grid', gap: '15px' }}>
            {jobs.map((job) => (
              <div key={job.id} style={{ border: '1px solid #dee2e6', borderRadius: '8px', padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ margin: '0 0 5px 0', color: '#333' }}>{job.title}</h3>
                    <p style={{ margin: '0 0 5px 0', color: '#666' }}>{job.company} • {job.location}</p>
                    <p style={{ margin: '0 0 10px 0', color: '#666', fontSize: '14px' }}>{job.salary}</p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                      <span style={{
                        background: job.match_score >= 90 ? '#d4edda' : job.match_score >= 70 ? '#cce5ff' : '#fff3cd',
                        color: job.match_score >= 90 ? '#155724' : job.match_score >= 70 ? '#004085' : '#856404',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}>
                        {job.match_score}% Match
                      </span>
                      <span style={{ fontSize: '14px', color: job.has_email ? '#28a745' : '#dc3545' }}>
                        {job.has_email ? `📧 ${job.contact_email}` : '❌ No email'}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleApplyToJob(job.id)}
                    disabled={!job.has_email}
                    style={{
                      background: job.has_email ? '#007bff' : '#6c757d',
                      color: 'white',
                      border: 'none',
                      padding: '8px 16px',
                      borderRadius: '4px',
                      cursor: job.has_email ? 'pointer' : 'not-allowed',
                      fontSize: '14px'
                    }}
                  >
                    {job.has_email ? 'Apply & Send Email' : 'No Email'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            <div style={{ fontSize: '48px', marginBottom: '10px' }}>🔍</div>
            <p>No jobs discovered yet</p>
            <p style={{ fontSize: '14px' }}>
              {cvAnalysis ? 'Click "Discover Jobs" to find opportunities' : 'Upload your CV first to get started'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
