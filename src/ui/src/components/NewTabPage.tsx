import React, { useState } from 'react';

interface NewTabPageProps {
  stats: {
    blockedCount: number;
    fingerprintProtected: boolean;
  };
  onNavigate: (url: string) => void;
}

export function NewTabPage({ stats, onNavigate }: NewTabPageProps) {
  const [search, setSearch] = useState('');

  const handleSearch = () => {
    if (search.trim()) {
      onNavigate('https://duckduckgo.com/?q=' + encodeURIComponent(search));
    }
  };

  return (
    <div className="ntp">
      <div className="ntp-center">
        <img src="/assets/logo.svg" alt="Stealth Browser" className="ntp-logo" />
        <h1 className="ntp-title">Stealth Browser</h1>
        <p className="ntp-subtitle">Private. Secure. Zero tracking.</p>
        <div className="ntp-search">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search the web..."
            spellCheck={false}
          />
        </div>
        <div className="ntp-stats">
          <div className="stat-card">
            <span className="stat-number">{stats.blockedCount.toLocaleString()}</span>
            <span className="stat-label">Ads Blocked</span>
          </div>
          <div className="stat-card">
            <span className="stat-number">&#10003;</span>
            <span className="stat-label">Zero Data Stored</span>
          </div>
          <div className="stat-card">
            <span className="stat-number">{stats.fingerprintProtected ? '&#128274;' : '&#9888;'}</span>
            <span className="stat-label">Fingerprint Protected</span>
          </div>
        </div>
      </div>
    </div>
  );
}
