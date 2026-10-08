import React from 'react';
import { Link } from 'react-router-dom';
import {
  Stethoscope,
  Pill,
  Heart,
  MessageSquare,
  ArrowRight,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export const Home: React.FC = () => {
  return (
    <div className="flex flex-col space-y-12 sm:space-y-16 pb-12 animate-fadeIn">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-primary/10 via-background to-background pt-8 pb-12 md:pt-16 md:pb-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <Badge variant="default" className="mb-4 px-3 py-1 text-xs">
            ✨ Next-Gen Clinical Intelligence
          </Badge>

          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-foreground leading-[1.15] max-w-4xl mx-auto">
            AI-Powered Healthcare <span className="text-primary">Intelligence Network</span>
          </h1>

          <p className="mt-4 sm:mt-6 text-base sm:text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Transforming Healthcare with AI-driven Predictions & Insights. Accurate disease diagnosis, drug recommendations, and cardiovascular risk evaluation.
          </p>

          {/* Action CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 max-w-md mx-auto">
            <Link to="/disease" className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto gap-2 text-base">
                <Stethoscope className="h-5 w-5" />
                Check Symptoms
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link to="/heart" className="w-full sm:w-auto">
              <Button variant="outline" size="lg" className="w-full sm:w-auto gap-2 text-base">
                <Heart className="h-5 w-5 text-rose-500" />
                Assess Heart Risk
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* 4 Core Features / Modules */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-8 sm:mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">Core Clinical Modules</h2>
          <p className="mt-2 text-sm sm:text-base text-muted-foreground">
            Explore four specialized intelligent tools designed for patient support and healthcare insight.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          {/* Module 1: Disease Prediction */}
          <Card className="hover:border-primary/40 hover:shadow-md transition-all group">
            <CardHeader>
              <div className="flex items-center justify-between mb-2">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary group-hover:scale-105 transition-transform">
                  <Stethoscope className="h-6 w-6" />
                </div>
                <Badge variant="outline">Machine Learning</Badge>
              </div>
              <CardTitle>Disease Prediction & Guidance</CardTitle>
              <CardDescription>
                Analyze patient symptoms and receive instant disease predictions with personalized precautions, medications, diets, and exercise regimes.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link to="/disease">
                <Button variant="secondary" className="w-full justify-between">
                  <span>Start Symptom Check</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Module 2: Drug Recommendation */}
          <Card className="hover:border-primary/40 hover:shadow-md transition-all group">
            <CardHeader>
              <div className="flex items-center justify-between mb-2">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary group-hover:scale-105 transition-transform">
                  <Pill className="h-6 w-6" />
                </div>
                <Badge variant="outline">NLP & Cosine Similarity</Badge>
              </div>
              <CardTitle>Drug Recommendation System</CardTitle>
              <CardDescription>
                Search across 9,700+ medications to discover safe alternatives, verified compositions, detailed pharmacological descriptions, and pharmacy links.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link to="/drugs">
                <Button variant="secondary" className="w-full justify-between">
                  <span>Find Alternative Drugs</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Module 3: Heart Risk Assessment */}
          <Card className="hover:border-primary/40 hover:shadow-md transition-all group">
            <CardHeader>
              <div className="flex items-center justify-between mb-2">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-rose-500/10 text-rose-500 group-hover:scale-105 transition-transform">
                  <Heart className="h-6 w-6" />
                </div>
                <Badge variant="outline">EasyEnsemble + SHAP</Badge>
              </div>
              <CardTitle>Heart Disease Risk Assessment</CardTitle>
              <CardDescription>
                Evaluate cardiovascular risk using 22 BRFSS clinical indicators. Includes SHAP factor importance analysis and tailored lifestyle advice.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link to="/heart">
                <Button variant="secondary" className="w-full justify-between">
                  <span>Calculate Heart Risk</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Module 4: Medibot AI */}
          <Card className="hover:border-primary/40 hover:shadow-md transition-all group">
            <CardHeader>
              <div className="flex items-center justify-between mb-2">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-sky-500/10 text-sky-500 group-hover:scale-105 transition-transform">
                  <MessageSquare className="h-6 w-6" />
                </div>
                <Badge variant="outline">RAG + Groq LLM</Badge>
              </div>
              <CardTitle>Medibot Health Assistant</CardTitle>
              <CardDescription>
                Conversational clinical AI grounded in medical literature with FAISS vector retrieval. Inquires symptoms, home care remedies, and specialist guidance.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link to="/medibot">
                <Button variant="secondary" className="w-full justify-between">
                  <span>Chat with Medibot</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>



      {/* Support / Feedback Section */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
        <div className="max-w-xl mx-auto space-y-3">
          <h3 className="text-xl font-bold text-foreground">Continuous Clinical Research</h3>
          <p className="text-sm text-muted-foreground">
            Built as an open clinical intelligence demonstration network to explore machine-learning-assisted diagnosis, pharmacology, and cardiovascular prevention.
          </p>
        </div>
      </section>
    </div>
  );
};
