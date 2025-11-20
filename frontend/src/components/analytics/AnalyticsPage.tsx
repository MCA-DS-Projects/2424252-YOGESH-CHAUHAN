import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLMS } from '../../contexts/LMSContext';
import { analyticsAPI } from '../../config/api';
import {
  TrendingUp,
  Clock,
  Target,
  Award,
  BarChart3,
  PieChart,
  Calendar,
  BookOpen,
  Loader,
  AlertCircle
} from 'lucide-react';

interface AnalyticsData {
  total_study_time?: number;
  completion_rate?: number;
  average_grade?: string;
  learning_streak?: number;
  weekly_progress?: Array<{ day: string; hours: number; completed: number }>;
  subject_performance?: Array<{ subject: string; progress: number; grade: string }>;
  most_active_day?: string;
  preferred_subject?: string;
  improvement_rate?: number;
}

export const AnalyticsPage: React.FC = () => {
  const { user } = useAuth();
  const { courses } = useLMS();
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!user?._id) return;
      
      try {
        setLoading(true);
        setError(null);
        
        // Fetch analytics data from API
        const response: any = await analyticsAPI.getStudentAnalytics(user._id);
        setAnalyticsData(response.data || response);
      } catch (err: any) {
        console.error('Failed to fetch analytics:', err);
        setError('Failed to load analytics data');
        
        // Fallback to calculated data from courses
        const calculatedData = calculateAnalyticsFromCourses();
        setAnalyticsData(calculatedData);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [user?._id]);

  // Calculate analytics from available course data as fallback
  const calculateAnalyticsFromCourses = (): AnalyticsData => {
    const totalProgress = courses.length > 0
      ? courses.reduce((sum, course) => sum + (course.progress || 0), 0) / courses.length
      : 0;

    const subjectPerformance = courses.map(course => ({
      subject: course.title,
      progress: course.progress || 0,
      grade: getGradeFromProgress(course.progress || 0)
    }));

    return {
      total_study_time: 0,
      completion_rate: Math.round(totalProgress),
      average_grade: getGradeFromProgress(totalProgress),
      learning_streak: (user as any)?.study_streak || 0,
      weekly_progress: [],
      subject_performance: subjectPerformance,
      most_active_day: 'N/A',
      preferred_subject: courses.length > 0 ? courses[0].title : 'N/A',
      improvement_rate: 0
    };
  };

  const getGradeFromProgress = (progress: number): string => {
    if (progress >= 90) return 'A';
    if (progress >= 80) return 'A-';
    if (progress >= 75) return 'B+';
    if (progress >= 70) return 'B';
    if (progress >= 65) return 'B-';
    if (progress >= 60) return 'C+';
    if (progress >= 55) return 'C';
    return 'C-';
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Learning Analytics</h1>
        <p className="text-gray-600">Track your progress and performance insights</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-yellow-800 text-sm">{error}</p>
            <p className="text-yellow-700 text-xs mt-1">Showing calculated data from your courses</p>
          </div>
        </div>
      )}

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Total Study Time</p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData?.total_study_time ? `${analyticsData.total_study_time}h` : 'N/A'}
              </p>
            </div>
          </div>
          <p className="text-sm text-gray-500">Track your learning hours</p>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-green-100 p-3 rounded-lg">
              <Target className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Completion Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData?.completion_rate || 0}%
              </p>
            </div>
          </div>
          <p className="text-sm text-gray-500">Average course progress</p>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-purple-100 p-3 rounded-lg">
              <Award className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Average Grade</p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData?.average_grade || 'N/A'}
              </p>
            </div>
          </div>
          <p className="text-sm text-gray-500">Overall performance</p>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-yellow-100 p-3 rounded-lg">
              <TrendingUp className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Learning Streak</p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData?.learning_streak || 0} days
              </p>
            </div>
          </div>
          <p className="text-sm text-gray-500">
            {(analyticsData?.learning_streak || 0) > 0 ? 'Keep it up!' : 'Start today!'}
          </p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Weekly Progress Chart */}
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-6">
            <BarChart3 className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Weekly Study Hours</h3>
          </div>
          {analyticsData?.weekly_progress && analyticsData.weekly_progress.length > 0 ? (
            <div className="space-y-4">
              {analyticsData.weekly_progress.map((day, index) => (
                <div key={index} className="flex items-center gap-4">
                  <span className="text-sm font-medium text-gray-600 w-8">{day.day}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min((day.hours / 5) * 100, 100)}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-12">{day.hours}h</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <BarChart3 className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm">No weekly data available yet</p>
              <p className="text-xs mt-1">Start learning to see your progress</p>
            </div>
          )}
        </div>

        {/* Subject Performance */}
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-6">
            <PieChart className="h-6 w-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">Course Performance</h3>
          </div>
          {analyticsData?.subject_performance && analyticsData.subject_performance.length > 0 ? (
            <div className="space-y-4">
              {analyticsData.subject_performance.slice(0, 5).map((subject, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 truncate pr-2">{subject.subject}</span>
                    <span className="text-sm font-bold text-gray-900">{subject.grade}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${subject.progress}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-600">{subject.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <PieChart className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm">No course data available yet</p>
              <p className="text-xs mt-1">Enroll in courses to see performance</p>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Analytics */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Learning Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center gap-3 mb-3">
              <Calendar className="h-5 w-5 text-blue-600" />
              <h4 className="font-medium text-gray-900">Most Active Day</h4>
            </div>
            <p className="text-lg font-bold text-blue-600">
              {analyticsData?.most_active_day || 'N/A'}
            </p>
            <p className="text-sm text-gray-600">Track your study patterns</p>
          </div>

          <div className="p-4 bg-green-50 rounded-lg">
            <div className="flex items-center gap-3 mb-3">
              <BookOpen className="h-5 w-5 text-green-600" />
              <h4 className="font-medium text-gray-900">Top Course</h4>
            </div>
            <p className="text-lg font-bold text-green-600 truncate">
              {analyticsData?.preferred_subject || 'N/A'}
            </p>
            <p className="text-sm text-gray-600">Your best performance</p>
          </div>

          <div className="p-4 bg-purple-50 rounded-lg">
            <div className="flex items-center gap-3 mb-3">
              <TrendingUp className="h-5 w-5 text-purple-600" />
              <h4 className="font-medium text-gray-900">Improvement Rate</h4>
            </div>
            <p className="text-lg font-bold text-purple-600">
              {analyticsData?.improvement_rate ? `+${analyticsData.improvement_rate}%` : 'N/A'}
            </p>
            <p className="text-sm text-gray-600">Keep learning!</p>
          </div>
        </div>
      </div>

      {/* Course Summary */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-2 rounded-lg">
            <BookOpen className="h-5 w-5 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Your Learning Journey</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Enrolled Courses</h4>
            <p className="text-2xl font-bold text-blue-600 mb-1">{courses.length}</p>
            <p className="text-sm text-gray-600">Active learning paths</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Average Progress</h4>
            <p className="text-2xl font-bold text-green-600 mb-1">
              {analyticsData?.completion_rate || 0}%
            </p>
            <p className="text-sm text-gray-600">Overall completion</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Study Streak</h4>
            <p className="text-2xl font-bold text-purple-600 mb-1">
              {analyticsData?.learning_streak || 0}
            </p>
            <p className="text-sm text-gray-600">Consecutive days</p>
          </div>
        </div>
      </div>
    </div>
  );
}