import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  BookOpen,
  BarChart3,
  Settings,
  Shield,
  AlertTriangle,
  Activity,
  TrendingUp,
  Clock,
  Search,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { userService } from '../services/userService';
import { statuteService } from '../services/statuteService';
import { caseService } from '../services/caseService';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/common/Toast';
import '../styles/admin.css';

const AdminPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalStatutes: 0,
    totalCases: 0,
    activeUsers: 0,
    newUsersToday: 0,
    totalSearches: 0
  });
  const [users, setUsers] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [toast, setToast] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [userFilter, setUserFilter] = useState('all');

  useEffect(() => {
    if (!user?.isAdmin) {
      return;
    }
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, usersRes, activityRes] = await Promise.all([
        userService.getAdminStats(),
        userService.getAllUsers(),
        userService.getRecentActivity()
      ]);

      if (statsRes.success) setStats(statsRes.data);
      if (usersRes.success) setUsers(usersRes.data);
      if (activityRes.success) setRecentActivity(activityRes.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = async (userId, action) => {
    try {
      let response;
      switch (action) {
        case 'activate':
          response = await userService.activateUser(userId);
          break;
        case 'deactivate':
          response = await userService.deactivateUser(userId);
          break;
        case 'makeAdmin':
          response = await userService.makeAdmin(userId);
          break;
        case 'removeAdmin':
          response = await userService.removeAdmin(userId);
          break;
        default:
          return;
      }

      if (response.success) {
        setToast({ message: 'User updated successfully', type: 'success' });
        fetchDashboardData();
      } else {
        throw new Error(response.error);
      }
    } catch (err) {
      setToast({ message: err.message, type: 'error' });
    }
  };

  const exportData = async (type) => {
    try {
      const response = await userService.exportData(type);
      const blob = new Blob([JSON.stringify(response.data, null, 2)], {
        type: 'application/json'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pakistan-law-app-${type}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setToast({ message: 'Data exported successfully', type: 'success' });
    } catch (err) {
      setToast({ message: 'Export failed', type: 'error' });
    }
  };

  const filteredUsers = users.filter(u => {
    const matchesSearch =
      u.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.email?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = userFilter === 'all' || u.role === userFilter;
    return matchesSearch && matchesFilter;
  });

  if (!user?.isAdmin) {
    return (
      <div className="admin-page">
        <div className="access-denied">
          <Shield size={48} />
          <h2>Access Denied</h2>
          <p>You need administrator privileges to access this page.</p>
        </div>
      </div>
    );
  }

  if (loading) return <LoadingSpinner />;

  if (error) {
    return (
      <div className="admin-page">
        <div className="error-container">
          <AlertTriangle size={48} />
          <h2>Error Loading Dashboard</h2>
          <p>{error}</p>
          <button onClick={fetchDashboardData} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'content', label: 'Content', icon: BookOpen },
    { id: 'activity', label: 'Activity', icon: Activity },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  return (
    <div className="admin-page">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <div className="header-actions">
          <button onClick={fetchDashboardData} className="refresh-btn">
            <RefreshCw size={18} />
            Refresh
          </button>
          <button onClick={() => exportData('all')} className="export-btn">
            <Download size={18} />
            Export All
          </button>
        </div>
      </div>

      <div className="admin-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon size={18} />
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <motion.div
          className="overview-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="stats-grid">
            <div className="stat-card">
              <Users size={24} />
              <div className="stat-info">
                <span className="stat-value">{stats.totalUsers}</span>
                <span className="stat-label">Total Users</span>
              </div>
            </div>
            <div className="stat-card">
              <BookOpen size={24} />
              <div className="stat-info">
                <span className="stat-value">{stats.totalStatutes}</span>
                <span className="stat-label">Total Statutes</span>
              </div>
            </div>
            <div className="stat-card">
              <BarChart3 size={24} />
              <div className="stat-info">
                <span className="stat-value">{stats.totalCases}</span>
                <span className="stat-label">Total Cases</span>
              </div>
            </div>
            <div className="stat-card">
              <Activity size={24} />
              <div className="stat-info">
                <span className="stat-value">{stats.activeUsers}</span>
                <span className="stat-label">Active Users</span>
              </div>
            </div>
            <div className="stat-card">
              <TrendingUp size={24} />
              <div className="stat-info">
                <span className="stat-value">{stats.newUsersToday}</span>
                <span className="stat-label">New Today</span>
              </div>
            </div>
            <div className="stat-card">
              <Search size={24} />
              <div className="stat-info">
                <span className="stat-value">{stats.totalSearches}</span>
                <span className="stat-label">Total Searches</span>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {activeTab === 'users' && (
        <motion.div
          className="users-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="users-filters">
            <div className="search-bar">
              <Search size={20} />
              <input
                type="text"
                placeholder="Search users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="filter-dropdown">
              <Filter size={20} />
              <select value={userFilter} onChange={(e) => setUserFilter(e.target.value)}>
                <option value="all">All Roles</option>
                <option value="user">Users</option>
                <option value="admin">Admins</option>
                <option value="advocate">Advocates</option>
              </select>
            </div>
          </div>

          <div className="users-table-container">
            <table className="users-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map(user => (
                  <tr key={user.id}>
                    <td>
                      <div className="user-info">
                        <div className="user-avatar">
                          {user.name?.charAt(0)?.toUpperCase() || 'U'}
                        </div>
                        <div className="user-details">
                          <span className="user-name">{user.name}</span>
                          <span className="user-email">{user.email}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className={`role-badge ${user.role}`}>
                        {user.role}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge ${user.status}`}>
                        {user.status}
                      </span>
                    </td>
                    <td>{new Date(user.createdAt).toLocaleDateString()}</td>
                    <td>
                      <div className="user-actions">
                        {user.status === 'active' ? (
                          <button
                            onClick={() => handleUserAction(user.id, 'deactivate')}
                            className="action-btn warning"
                          >
                            Deactivate
                          </button>
                        ) : (
                          <button
                            onClick={() => handleUserAction(user.id, 'activate')}
                            className="action-btn success"
                          >
                            Activate
                          </button>
                        )}
                        {user.role !== 'admin' ? (
                          <button
                            onClick={() => handleUserAction(user.id, 'makeAdmin')}
                            className="action-btn primary"
                          >
                            Make Admin
                          </button>
                        ) : (
                          <button
                            onClick={() => handleUserAction(user.id, 'removeAdmin')}
                            className="action-btn warning"
                          >
                            Remove Admin
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {activeTab === 'content' && (
        <motion.div
          className="content-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="content-cards">
            <div className="content-card">
              <h3>Statutes</h3>
              <p>{stats.totalStatutes} statutes in database</p>
              <button onClick={() => exportData('statutes')} className="action-btn">
                <Download size={16} />
                Export Statutes
              </button>
            </div>
            <div className="content-card">
              <h3>Cases</h3>
              <p>{stats.totalCases} cases in database</p>
              <button onClick={() => exportData('cases')} className="action-btn">
                <Download size={16} />
                Export Cases
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {activeTab === 'activity' && (
        <motion.div
          className="activity-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="activity-list">
            {recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <Clock size={16} />
                <div className="activity-details">
                  <span className="activity-action">{activity.action}</span>
                  <span className="activity-user">by {activity.userName}</span>
                  <span className="activity-time">
                    {new Date(activity.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {activeTab === 'settings' && (
        <motion.div
          className="settings-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="settings-card">
            <h3>System Settings</h3>
            <p>Configure application settings and preferences</p>
            <div className="settings-form">
              <div className="form-group">
                <label>Maintenance Mode</label>
                <select>
                  <option value="off">Off</option>
                  <option value="on">On</option>
                </select>
              </div>
              <div className="form-group">
                <label>User Registration</label>
                <select>
                  <option value="open">Open</option>
                  <option value="closed">Closed</option>
                  <option value="approval">Approval Required</option>
                </select>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
};

export default AdminPage;
