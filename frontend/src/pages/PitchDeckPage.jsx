import React from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Helmet } from 'react-helmet';
import { 
  BookOpen, 
  Search, 
  Users, 
  TrendingUp, 
  Shield, 
  Globe,
  ArrowRight,
  CheckCircle
} from 'lucide-react';

const PitchDeckPage = () => {
  const stats = [
    { label: 'Cases', value: '50K+', icon: BookOpen },
    { label: 'Users', value: '5K+', icon: Users },
    { label: 'Searches', value: '100K+', icon: Search },
    { label: 'Growth', value: '200%', icon: TrendingUp }
  ];

  const features = [
    {
      title: 'Comprehensive Database',
      description: 'Access to 50,000+ cases from all Pakistani courts',
      icon: BookOpen
    },
    {
      title: 'AI-Powered Search',
      description: 'Find relevant cases using natural language queries',
      icon: Search
    },
    {
      title: 'Enterprise Ready',
      description: 'Secure, scalable solution for legal firms',
      icon: Shield
    },
    {
      title: 'Nationwide Coverage',
      description: 'Coverage of all provincial and federal courts',
      icon: Globe
    }
  ];

  const milestones = [
    { year: '2023', event: 'Platform Launch' },
    { year: '2024 Q1', event: '10,000 Users' },
    { year: '2024 Q2', event: 'AI Features Release' },
    { year: '2024 Q3', event: 'Enterprise Clients' },
    { year: '2025', event: 'Regional Expansion' }
  ];

  return (
    <>
      <Helmet>
        <title>Pitch Deck | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white py-20">
          <div className="max-w-6xl mx-auto px-4">
            <div className="text-center">
              <h1 className="text-5xl font-bold mb-6">Pakistan Law App</h1>
              <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
                The most comprehensive legal research platform for Pakistani law,
                empowering lawyers, judges, and law students with AI-driven insights.
              </p>
              <div className="flex justify-center gap-4">
                <Button size="lg" className="bg-white text-blue-900 hover:bg-blue-50">
                  Get Started
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                  View Demo
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="py-16">
          <div className="max-w-6xl mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {stats.map((stat, index) => (
                <Card key={index} className="p-6 text-center">
                  <stat.icon className="w-8 h-8 mx-auto mb-3 text-blue-600" />
                  <div className="text-3xl font-bold text-slate-900">{stat.value}</div>
                  <div className="text-sm text-slate-600">{stat.label}</div>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* Problem Statement */}
        <div className="py-16 bg-white">
          <div className="max-w-6xl mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-slate-900">The Problem</h2>
              <p className="text-slate-600 mt-4 max-w-2xl mx-auto">
                Legal research in Pakistan is fragmented, time-consuming, and expensive.
                Lawyers spend hours searching through scattered sources.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                'Scattered legal sources',
                'No unified search',
                'High research costs'
              ].map((problem, index) => (
                <Card key={index} className="p-6 text-center border-red-200">
                  <div className="text-red-500 font-semibold text-lg">{problem}</div>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* Solution */}
        <div className="py-16">
          <div className="max-w-6xl mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-slate-900">Our Solution</h2>
              <p className="text-slate-600 mt-4 max-w-2xl mx-auto">
                A unified platform with AI-powered search and comprehensive coverage
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {features.map((feature, index) => (
                <Card key={index} className="p-6">
                  <div className="flex items-start gap-4">
                    <feature.icon className="w-8 h-8 text-blue-600 flex-shrink-0" />
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">{feature.title}</h3>
                      <p className="text-slate-600 mt-1">{feature.description}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* Milestones */}
        <div className="py-16 bg-white">
          <div className="max-w-6xl mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-slate-900">Roadmap</h2>
            </div>
            
            <div className="space-y-6">
              {milestones.map((milestone, index) => (
                <div key={index} className="flex items-center gap-6">
                  <div className="w-24 flex-shrink-0 text-right">
                    <Badge variant="secondary">{milestone.year}</Badge>
                  </div>
                  <div className="w-4 h-4 rounded-full bg-blue-600 flex-shrink-0" />
                  <div className="flex-1">
                    <Card className="p-4">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                        <span className="font-medium">{milestone.event}</span>
                      </div>
                    </Card>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="py-16 bg-gradient-to-br from-blue-900 to-indigo-900 text-white">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Transform Legal Research?</h2>
            <p className="text-blue-100 mb-8">
              Join thousands of legal professionals using Pakistan Law App
            </p>
            <div className="flex justify-center gap-4">
              <Button size="lg" className="bg-white text-blue-900 hover:bg-blue-50">
                Start Free Trial
              </Button>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                Contact Sales
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default PitchDeckPage;
