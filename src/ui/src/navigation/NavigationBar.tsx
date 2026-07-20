import React, { useState } from 'react';

interface SecurityStats {
  blockedCount: number;
  strippedTrackers: number;
  fingerprintProtected: boolean;
  httpsOnly: boolean;
}

interface NavigationBarProps {
  url: string;
  onNavigate: (url: string) => void;
  onOpenSettings: () => void;
  stats: SecurityStats;
}

export function NavigationBar({ url, onNavigate, onOpenSettings, stats }: NavigationBarProps) {
  const [inputUrl, setInputUrl] = useState(url);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      let target = inputUrl;
      if (!/^https?:\/\//i.test(target)) {
        if (/^[\w-]+(\.[\w-]+)+/.test(target)) {
          target = 'https://' + target;
        } else {
          target = 'https://duckduckgo.com/?q=' + encodeURIComponent(target);
        }
      }
      onNavigate(target);
    }
  };

  return (
    <div className="nav-bar">
      <button className="nav-btn" disabled>&#9664;</button>
      <button className="nav-btn" disabled>&#9654;</button>
      <button className="nav-btn">&#8635;</button>
      <div className="url-bar-container">
        <span className="security-icon">
          {url.startsWith('https://') ? '\uD83D\uDD12' : '\u26A0\uFE0F'}
        </span>
        <input
          type="text"
          className="url-bar"
          value={inputUrl}
          onChange={(e) => setInputUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter URL or search..."
          spellCheck={false}
          autoComplete="off"
        />
        {stats.blockedCount > 0 && (
          <span className="adblock-indicator">
            &#128737; {stats.blockedCount.toLocaleString()}
          </span>
        )}
      </div>
      <button className="nav-btn" onClick={onOpenSettings}>&#9881;</button>
    </div>
  );
}
