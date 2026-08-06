import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const DashboardSidebar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', label: 'Overview', icon: '📊' },
    { path: '/dashboard/cases', label: 'My Cases', icon: '📁' },
    { path: '/dashboard/notes', label: 'Notes', icon: '📝' },
    { path: '/dashboard/alerts', label: 'Alerts', icon: '🔔' },
    { path: '/dashboard/settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold">PLS Dashboard</h1>
      </div>
      <nav className="space-y-2">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center px-4 py-2 rounded-md transition ${
              location.pathname === item.path
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-800'
            }`}
          >
            <span className="mr-3">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default DashboardSidebar;
