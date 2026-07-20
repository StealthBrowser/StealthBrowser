import React from 'react';

interface Tab {
  id: string;
  title: string;
  url: string;
  active: boolean;
}

interface TabBarProps {
  tabs: Tab[];
  onAddTab: () => void;
  onCloseTab: (id: string) => void;
  onSwitchTab: (id: string) => void;
}

export function TabBar({ tabs, onAddTab, onCloseTab, onSwitchTab }: TabBarProps) {
  return (
    <div className="tab-bar">
      {tabs.map(tab => (
        <div
          key={tab.id}
          className={`tab ${tab.active ? 'active' : ''}`}
          onClick={() => onSwitchTab(tab.id)}
        >
          <span className="tab-title">{tab.title || 'New Tab'}</span>
          <button
            className="tab-close"
            onClick={(e) => {
              e.stopPropagation();
              onCloseTab(tab.id);
            }}
          >
            &times;
          </button>
        </div>
      ))}
      <button className="new-tab-btn" onClick={onAddTab}>+</button>
    </div>
  );
}
