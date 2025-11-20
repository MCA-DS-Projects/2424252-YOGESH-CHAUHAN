import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { StatsCard } from './StatsCard';
import {
  Users,
  Crown,
  Server,
  Activity,
  Settings,
  UserCheck
} from 'lucide-react';

export const SuperAdminDashboard: React.FC = () => {
  const { user } = useAuth();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const statsData = [
    { title: 'Total Users', value: '1,247', icon: Users, color: 'blue' as const, change: '+12% this month' },
    { title: 'System Status', value: 'Online', icon: Server, color: 'green' as const, change: '99.9% uptime' },
    { title: 'Active Users', value: '892', icon: UserCheck, color: 'purple' as const, change: 'Currently online' }
  ];

  return (
    <div className="p-6 space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-purple-900 via-indigo-800 to-blue-900 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
              <Crown className="h-8 w-8 text-yellow-400" />
              {getGreeting()}, {user?.name}! 👑
            </h1>
            <p className="text-purple-100 text-lg">
              System administration dashboard
            </p>
          </div>
          <div className="hidden md:block">
            <Crown className="h-24 w-24 text-yellow-400 opacity-30" />
          </div>
        </div>
      </div>

      {/* Essential Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {statsData.map((stat, index) => (
          <StatsCard
            key={index}
            title={stat.title}
            value={stat.value}
            change={stat.change}
            changeType="positive"
            icon={stat.icon}
            color={stat.color}
          />
        ))}
      </div>

      {/* Quick Actions Section */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
          <Activity className="h-5 w-5 text-blue-600" />
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button 
            onClick={() => {
              window.history.pushState({}, '', '/admin/users');
              window.dispatchEvent(new PopStateEvent('popstate'));
            }}
            className="p-6 bg-blue-50 hover:bg-blue-100 rounded-lg text-left transition-colors group"
          >
            <div className="flex items-center gap-3 mb-2">
              <Users className="h-5 w-5 text-blue-600" />
              <div className="font-medium text-blue-900">User Management</div>
            </div>
            <div className="text-sm text-blue-700">Manage all system users and roles</div>
          </button>
          
          <button 
            onClick={() => {
              window.history.pushState({}, '', '/settings');
              window.dispatchEvent(new PopStateEvent('popstate'));
            }}
            className="p-6 bg-green-50 hover:bg-green-100 rounded-lg text-left transition-colors group"
          >
            <div className="flex items-center gap-3 mb-2">
              <Settings className="h-5 w-5 text-green-600" />
              <div className="font-medium text-green-900">Settings</div>
            </div>
            <div className="text-sm text-green-700">Configure system parameters</div>
          </button>
          
          <button className="p-6 bg-purple-50 hover:bg-purple-100 rounded-lg text-left transition-colors group">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="h-5 w-5 text-purple-600" />
              <div className="font-medium text-purple-900">System Status</div>
            </div>
            <div className="text-sm text-purple-700">View system health and activity</div>
          </button>
        </div>
      </div>
    </div>
  );
};