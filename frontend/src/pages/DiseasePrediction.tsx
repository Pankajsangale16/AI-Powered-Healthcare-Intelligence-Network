import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Stethoscope,
  Search,
  Sparkles,
  ShieldCheck,
  Pill,
  Utensils,
  Dumbbell,
  FileText,
  AlertCircle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { api, DiseasePredictionResult } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { TagInput } from '@/components/ui/TagInput';
import { Badge } from '@/components/ui/Badge';
import { Alert, Skeleton, ErrorState } from '@/components/ui/Feedback';
import { Input } from '@/components/ui/Input';

export const DiseasePrediction: React.FC = () => {
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [diseaseSearchQuery, setDiseaseSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [expandedSections, setExpandedSections] = useState({
    precautions: true,
    medications: true,
    diet: true,
    workout: true,
  });

  // Fetch valid symptoms list for TagInput autocomplete
  const { data: symptomsData, isLoading: isLoadingSymptoms } = useQuery({
    queryKey: ['symptoms-list'],
    queryFn: () => api.getSymptoms(),
    staleTime: 1000 * 60 * 60, // 1 hour cache
  });

  // Debounce disease search input (300ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(diseaseSearchQuery.trim());
    }, 300);
    return () => clearTimeout(handler);
  }, [diseaseSearchQuery]);

  // Query for disease direct search
  const {
    data: searchResults,
    isLoading: isSearchingDisease,
    error: searchError,
  } = useQuery({
    queryKey: ['disease-search', debouncedQuery],
    queryFn: () => api.searchDisease(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
  });

  // Mutation for predicting disease from symptoms
  const predictMutation = useMutation({
    mutationFn: (symptomList: string[]) => api.predictDisease(symptomList),
  });

  const handlePredict = (e: React.FormEvent) => {
    e.preventDefault();
    if (symptoms.length === 0) return;
    predictMutation.mutate(symptoms);
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8 space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Badge variant="default" className="gap-1">
            <Stethoscope className="h-3.5 w-3.5" />
            RandomForest Classifier
          </Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
          Disease Prediction & Medical Recommendation
        </h1>
        <p className="mt-1 text-sm sm:text-base text-muted-foreground">
          Provide your symptoms to receive AI-powered differential diagnoses and personalized lifestyle guidance.
        </p>
      </div>

      {/* Prediction Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Check Symptoms
          </CardTitle>
          <CardDescription>
            Type symptoms or paste a comma-separated list (e.g. headache, nausea, chills). For highest accuracy, specify all active symptoms.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePredict} className="space-y-4">
            <TagInput
              value={symptoms}
              onChange={setSymptoms}
              availableOptions={symptomsData?.results || []}
              placeholder={isLoadingSymptoms ? 'Loading symptoms list...' : 'e.g., headache, fever, cough...'}
              label="Selected Symptoms"
              helperText="Press Enter or comma to add. Tap any tag to remove."
            />

            {/* Quick symptom pills for rapid entry */}
            <div className="pt-1">
              <span className="text-xs text-muted-foreground block mb-2 font-medium">Common suggestions:</span>
              <div className="flex flex-wrap gap-1.5">
                {['headache', 'fever', 'cough', 'fatigue', 'nausea', 'joint pain', 'acidity'].map((suggest) => (
                  <button
                    key={suggest}
                    type="button"
                    onClick={() => {
                      if (!symptoms.includes(suggest)) {
                        setSymptoms([...symptoms, suggest]);
                      }
                    }}
                    className="touch-target inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border border-border bg-muted/60 text-foreground hover:bg-primary/10 hover:border-primary/30 transition-colors"
                  >
                    + {suggest}
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-2">
              <Button
                type="submit"
                disabled={symptoms.length === 0 || predictMutation.isPending}
                isLoading={predictMutation.isPending}
                className="w-full sm:w-auto"
                size="lg"
              >
                <Stethoscope className="mr-2 h-5 w-5" />
                Predict Disease
              </Button>
            </div>
          </form>

          {/* Mutation Error */}
          {predictMutation.isError && (
            <div className="mt-6">
              <ErrorState
                title="Prediction Error"
                message={(predictMutation.error as any)?.message || 'Failed to predict disease.'}
                onRetry={() => predictMutation.mutate(symptoms)}
              />
            </div>
          )}

          {/* Prediction Result Display */}
          {predictMutation.isSuccess && predictMutation.data && (
            <div className="mt-8 pt-6 border-t border-border space-y-6 animate-fadeIn">
              {/* Top Result Card */}
              <div className="rounded-xl border border-primary/30 bg-primary/5 p-5">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <span className="text-xs font-semibold uppercase tracking-wider text-primary">
                    Primary Diagnosis
                  </span>
                  <Badge variant="success" className="text-xs">
                    Analysis Complete
                  </Badge>
                </div>
                <h3 className="text-2xl font-bold text-foreground">
                  {predictMutation.data.predicted_disease}
                </h3>
                <p className="mt-2 text-sm text-foreground/90 leading-relaxed">
                  {predictMutation.data.description}
                </p>

                {/* Confidence Bars */}
                {predictMutation.data.confidence_scores && predictMutation.data.confidence_scores.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-primary/20 space-y-2">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">
                      Differential Confidence Probabilities
                    </span>
                    <div className="space-y-2">
                      {predictMutation.data.confidence_scores.slice(0, 3).map((item, idx) => (
                        <div key={idx} className="space-y-1">
                          <div className="flex justify-between text-xs font-medium">
                            <span className="text-foreground">{item.disease}</span>
                            <span className="text-primary font-semibold">{item.confidence}%</span>
                          </div>
                          <div className="w-full h-2 rounded-full bg-muted/60 overflow-hidden">
                            <div
                              className="h-full bg-primary transition-all duration-500 rounded-full"
                              style={{ width: `${Math.min(item.confidence, 100)}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Actionable Guidance Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Precautions */}
                <Card>
                  <CardHeader className="py-3 px-4 cursor-pointer" onClick={() => toggleSection('precautions')}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <ShieldCheck className="h-4 w-4 text-primary" />
                        <CardTitle className="text-base">Precautions</CardTitle>
                      </div>
                      {expandedSections.precautions ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
                    </div>
                  </CardHeader>
                  {expandedSections.precautions && (
                    <CardContent className="px-4 pb-4 pt-0">
                      <ul className="space-y-1.5 text-sm">
                        {predictMutation.data.precautions.map((p, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-primary font-bold">•</span>
                            <span>{p}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  )}
                </Card>

                {/* Medications */}
                <Card>
                  <CardHeader className="py-3 px-4 cursor-pointer" onClick={() => toggleSection('medications')}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Pill className="h-4 w-4 text-primary" />
                        <CardTitle className="text-base">Typical Medications</CardTitle>
                      </div>
                      {expandedSections.medications ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
                    </div>
                  </CardHeader>
                  {expandedSections.medications && (
                    <CardContent className="px-4 pb-4 pt-0">
                      <div className="flex flex-wrap gap-1.5">
                        {predictMutation.data.medications.map((m, i) => (
                          <Badge key={i} variant="secondary">
                            {m}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  )}
                </Card>

                {/* Diet */}
                <Card>
                  <CardHeader className="py-3 px-4 cursor-pointer" onClick={() => toggleSection('diet')}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Utensils className="h-4 w-4 text-primary" />
                        <CardTitle className="text-base">Recommended Diet</CardTitle>
                      </div>
                      {expandedSections.diet ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
                    </div>
                  </CardHeader>
                  {expandedSections.diet && (
                    <CardContent className="px-4 pb-4 pt-0">
                      <ul className="space-y-1.5 text-sm">
                        {predictMutation.data.diet.map((d, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-primary font-bold">•</span>
                            <span>{d}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  )}
                </Card>

                {/* Workout */}
                <Card>
                  <CardHeader className="py-3 px-4 cursor-pointer" onClick={() => toggleSection('workout')}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Dumbbell className="h-4 w-4 text-primary" />
                        <CardTitle className="text-base">Recommended Exercises</CardTitle>
                      </div>
                      {expandedSections.workout ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
                    </div>
                  </CardHeader>
                  {expandedSections.workout && (
                    <CardContent className="px-4 pb-4 pt-0">
                      <ul className="space-y-1.5 text-sm">
                        {predictMutation.data.workout.map((w, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-primary font-bold">•</span>
                            <span>{w}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  )}
                </Card>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Separate Disease Search Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5 text-primary" />
            Search Disease Information
          </CardTitle>
          <CardDescription>
            Look up detailed medical guidelines, diet plans, and precautions by disease name directly.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            value={diseaseSearchQuery}
            onChange={(e) => setDiseaseSearchQuery(e.target.value)}
            placeholder="Type disease name (e.g., Malaria, Fungal infection, Diabetes)..."
            aria-label="Search disease name"
          />

          {isSearchingDisease && (
            <div className="space-y-3 pt-2">
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-24 w-full" />
            </div>
          )}

          {searchResults && searchResults.results && searchResults.results.length > 0 && (
            <div className="space-y-4 pt-2">
              {searchResults.results.map((item, idx) => (
                <div key={idx} className="rounded-xl border border-border bg-card p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-lg font-bold text-foreground">{item.disease}</h4>
                    <Badge variant="outline">Verified Database</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">{item.description}</p>

                  <div className="pt-2 flex flex-wrap gap-2 text-xs">
                    {item.precautions && item.precautions.length > 0 && (
                      <span className="bg-muted px-2.5 py-1 rounded-md text-foreground">
                        <strong>Precautions:</strong> {item.precautions.slice(0, 2).join(', ')}
                      </span>
                    )}
                    {item.medications && item.medications.length > 0 && (
                      <span className="bg-muted px-2.5 py-1 rounded-md text-foreground">
                        <strong>Medications:</strong> {item.medications.slice(0, 3).join(', ')}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {debouncedQuery.length >= 2 && searchResults?.results.length === 0 && !isSearchingDisease && (
            <Alert variant="warning" title="No matching disease found">
              No disease matching &quot;{debouncedQuery}&quot; was found. Try a different term or verify spelling.
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
