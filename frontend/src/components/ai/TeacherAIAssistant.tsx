import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Users, 
  BookOpen, 
  TrendingUp, 
  MessageSquare, 
  FileText, 
  Award,
  AlertTriangle,
  Lightbulb,
  Target,
  Clock,
  RefreshCw
} from 'lucide-react';
import { aiAPI, learnerAnalyticsAPI } from '../../config/api';
import { useAuth } from '../../contexts/AuthContext';

interface TeachingSuggestion {
  type: 'content' | 'engagement' | 'assessment' | 'support';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  actionItems: string[];
}

export const TeacherAIAssistant: React.FC = () => {
  const { user } = useAuth();
  const [suggestions, setSuggestions] = useState<TeachingSuggestion[]>([]);
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'suggestions' | 'insights' | 'chat'>('suggestions');

  useEffect(() => {
    loadTeachingInsights();
  }, []);

  const loadTeachingInsights = async () => {
    setLoading(true);
    try {
      const [analyticsData] = await Promise.all([
        learnerAnalyticsAPI.getPerformanceAnalysis()
      ]);
      
      setInsights(analyticsData.summary);
      generateTeachingSuggestions(analyticsData.summary);
    } catch (error) {
      console.error('Failed to load teaching insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateTeachingSuggestions = (data: any) => {
    const suggestions: TeachingSuggestion[] = [];

    // Content suggestions based on performance
    if (data.slow_learners_count > data.total_students * 0.3) {
      suggestions.push({
        type: 'content',
        title: 'Simplify Course Content',
        description: `${data.slow_learners_count} students are struggling. Consider breaking down complex topics.`,
        priority: 'high',
        actionItems: [
          'Create additional practice materials',
          'Add more visual explanations',
          'Provide step-by-step guides',
          'Offer supplementary resources'
        ]
      });
    }

    // Engagement suggestions
    if (data.inactive_students > 0) {
      suggestions.push({
        type: 'engagement',
        title: 'Boost Student Engagement',
        description: `${data.inactive_students} students haven't been active recently.`,
        priority: 'medium',
        actionItems: [
          'Send personalized check-in messages',
          'Create interactive assignments',
          'Schedule virtual office hours',
          'Form study groups'
        ]
      });
    }

    // Assessment suggestions
    if (data.average_performance < 70) {
      suggestions.push({
        type: 'assessment',
        title: 'Adjust Assessment Strategy',
        description: `Average performance is ${data.average_performance}%. Consider modifying assessments.`,
        priority: 'high',
        actionItems: [
          'Provide more practice opportunities',
          'Offer formative assessments',
          'Give detailed feedback',
          'Create rubrics for clarity'
        ]
      });
    }

    // Support suggestions
    if (data.students_at_risk > 0) {
      suggestions.push({
        type: 'support',
        title: 'Support At-Risk Students',
        description: `${data.students_at_risk} students need additional support.`,
        priority: 'high',
        actionItems: [
          'Schedule one-on-one meetings',
          'Provide additional resources',
          'Connect with academic advisors',
          'Offer flexible deadlines'
        ]
      });
    }

    setSuggestions(suggestions);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-200 bg-red-50 text-red-800';
      case 'medium': return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      case 'low': return 'border-blue-200 bg-blue-50 text-blue-800';
      default: return 'border-gray-200 bg-gray-50 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'content': return <BookOpen className="h-5 w-5" />;
      case 'engagement': return <Users className="h-5 w-5" />;
      case 'assessment': return <Award className="h-5 w-5" />;
      case 'support': return <Target className="h-5 w-5" />;
      default: return <Lightbulb className="h-5 w-5" />;
    }
  };

  const renderSuggestions = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">AI Teaching Suggestions</h2>
        <button
          onClick={loadTeachingInsights}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
          <span className="ml-3 text-gray-600">Analyzing student data...</span>
        </div>
      ) : suggestions.length > 0 ? (
        <div className="grid gap-6">
          {suggestions.map((suggestion, index) => (
            <div key={index} className={`border rounded-lg p-6 ${getPriorityColor(suggestion.priority)}`}>
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  {getTypeIcon(suggestion.type)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold">{suggestion.title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      suggestion.priority === 'high' ? 'bg-red-100 text-red-700' :
                      suggestion.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {suggestion.priority} priority
                    </span>
                  </div>
                  <p className="text-sm mb-4">{suggestion.description}</p>
                  <div>
                    <h4 className="font-medium text-sm mb-2">Recommended Actions:</h4>
                    <ul className="text-sm space-y-1">
                      {suggestion.actionItems.map((item, itemIndex) => (
                        <li key={itemIndex} className="flex items-center gap-2">
                          <div className="w-1.5 h-1.5 bg-current rounded-full"></div>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No specific suggestions at this time. Your students are doing well!</p>
        </div>
      )}
    </div>
  );

  const renderInsights = () => (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-gray-900">Student Performance Insights</h2>
      
      {insights ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Users className="h-8 w-8 text-blue-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Total Students</h3>
                <p className="text-2xl font-bold text-blue-600">{insights.total_students}</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="h-8 w-8 text-green-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Average Performance</h3>
                <p className="text-2xl font-bold text-green-600">{insights.average_performance}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="h-8 w-8 text-red-600" />
              <div>
                <h3 className="font-semibold text-gray-900">At Risk</h3>
                <p className="text-2xl font-bold text-red-600">{insights.students_at_risk}</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Slow Learners</h3>
                <p className="text-2xl font-bold text-yellow-600">{insights.slow_learners_count}</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Award className="h-8 w-8 text-purple-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Fast Learners</h3>
                <p className="text-2xl font-bold text-purple-600">{insights.fast_learners_count}</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Users className="h-8 w-8 text-gray-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Inactive Students</h3>
                <p className="text-2xl font-bold text-gray-600">{insights.inactive_students}</p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <RefreshCw className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Loading insights...</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Teaching Assistant</h1>
        <p className="text-gray-600">Get AI-powered insights and suggestions to improve your teaching</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('suggestions')}
            className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'suggestions'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Lightbulb className="h-4 w-4" />
            Teaching Suggestions
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'insights'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <TrendingUp className="h-4 w-4" />
            Student Insights
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'suggestions' && renderSuggestions()}
        {activeTab === 'insights' && renderInsights()}
      </div>
    </div>
  );
};