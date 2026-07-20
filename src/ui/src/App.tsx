import React, { useState, useCallback } from 'react';
import { TabBar } from './tabs/TabBar';
import { NavigationBar } from './navigation/NavigationBar';
import { SettingsPanel } from './components/SettingsPanel';
import { NewTabPage } from './components/NewTabPage';

export interface Tab {
  id: string;
  title: string;
  url: string;
  active: boolean;
}

export interface SecurityStats {
  blockedCount: number;
  strippedTrackers: number;
  fingerprintProtected: boolean;
  httpsOnly: boolean;
}

export default function App() {
  const [tabs, setTabs] = useState<Tab[]>([
    { id: '1', title: 'New Tab', url: '', active: true },
  ]);
  const [activeTabId, setActiveTabId] = useState('1');
  const [showSettings, setShowSettings] = useState(false);
  const [stats, setStats] = useState<SecurityStats>({
    blockedCount: 0,
    strippedTrackers: 0,
    fingerprintProtected: true,
    httpsOnly: true,
  });

  const addTab = useCallback(() => {
    const newTab: Tab = {
      id: Date.now().toString(),
      title: 'New Tab',
      url: '',
      active: true,
    };
    setTabs(prev =>
      prev.map(t => ({ ...t, active: false })).concat(newTab)
    );
    setActiveTabId(newTab.id);
  }, []);

  const closeTab = useCallback((id: string) => {
    setTabs(prev => {
      const filtered = prev.filter(t => t.id !== id);
      if (filtered.length === 0) {
        const newTab: Tab = {
          id: Date.now().toString(),
          title: 'New Tab',
          url: '',
          active: true,
        };
        setActiveTabId(newTab.id);
        return [newTab];
      }
      return filtered;
    });
  }, []);

  const switchTab = useCallback((id: string) => {
    setActiveTabId(id);
    setTabs(prev => prev.map(t => ({ ...t, active: t.id === id })));
  }, []);

  const navigate = useCallback((url: string) => {
    setTabs(prev =>
      prev.map(t =>
        t.id === activeTabId ? { ...t, url, title: url } : t
      )
    );
  }, [activeTabId]);

  return (
    <div className="app">
      <TabBar
        tabs={tabs}
        onAddTab={addTab}
        onCloseTab={closeTab}
        onSwitchTab={switchTab}
      />
      <NavigationBar
        url={tabs.find(t => t.id === activeTabId)?.url || ''}
        onNavigate={navigate}
        onOpenSettings={() => setShowSettings(true)}
        stats={stats}
      />
      <div className="content-area">
        {tabs.find(t => t.id === activeTabId)?.url ? (
          <webview
            src={tabs.find(t => t.id === activeTabId)?.url}
            className="browser-view"
          />
        ) : (
          <NewTabPage stats={stats} onNavigate={navigate} />
        )}
      </div>
      {showSettings && (
        <SettingsPanel onClose={() => setShowSettings(false)} />
      )}
    </div>
  );
}
