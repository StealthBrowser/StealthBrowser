import React, { useState } from 'react';

interface SettingsPanelProps {
  onClose: () => void;
}

export function SettingsPanel({ onClose }: SettingsPanelProps) {
  const [adBlockEnabled, setAdBlockEnabled] = useState(true);
  const [clearOnClose, setClearOnClose] = useState(true);
  const [httpsOnly, setHttpsOnly] = useState(true);
  const [canvasProtection, setCanvasProtection] = useState(true);
  const [webglProtection, setWebglProtection] = useState(true);

  return (
    <div className="settings-panel">
      <div className="settings-overlay" onClick={onClose} />
      <div className="settings-drawer">
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        <div className="settings-body">
          <section className="settings-section">
            <h3>Ad Blocker</h3>
            <label className="toggle-row">
              <span>Enable Ad Blocker</span>
              <input type="checkbox" checked={adBlockEnabled} onChange={(e) => setAdBlockEnabled(e.target.checked)} />
            </label>
          </section>

          <section className="settings-section">
            <h3>Privacy</h3>
            <label className="toggle-row">
              <span>Clear data on close</span>
              <input type="checkbox" checked={clearOnClose} onChange={(e) => setClearOnClose(e.target.checked)} />
            </label>
          </section>

          <section className="settings-section">
            <h3>Fingerprint Protection</h3>
            <label className="toggle-row">
              <span>Spoof Canvas</span>
              <input type="checkbox" checked={canvasProtection} onChange={(e) => setCanvasProtection(e.target.checked)} />
            </label>
            <label className="toggle-row">
              <span>Spoof WebGL</span>
              <input type="checkbox" checked={webglProtection} onChange={(e) => setWebglProtection(e.target.checked)} />
            </label>
          </section>

          <section className="settings-section">
            <h3>Security</h3>
            <label className="toggle-row">
              <span>HTTPS Only</span>
              <input type="checkbox" checked={httpsOnly} onChange={(e) => setHttpsOnly(e.target.checked)} />
            </label>
          </section>
        </div>
      </div>
    </div>
  );
}
