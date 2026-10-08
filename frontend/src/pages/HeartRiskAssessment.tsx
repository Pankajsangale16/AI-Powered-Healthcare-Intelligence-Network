import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Heart,
  HelpCircle,
  ArrowRight,
  ArrowLeft,
  RotateCcw,
  Activity,
  CheckCircle,
  ExternalLink,
  ShieldAlert,
  Info,
  ChevronDown,
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts';
import { api, HeartFieldSchema, HeartAssessmentResult } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Stepper, StepItem } from '@/components/ui/Stepper';
import { ProgressRing } from '@/components/ui/ProgressRing';
import { Alert, Skeleton, ErrorState } from '@/components/ui/Feedback';
import { Modal } from '@/components/ui/Modal';
import { cn } from '@/lib/utils';

const STEPS: StepItem[] = [
  { id: 'demographics', title: 'Demographics' },
  { id: 'medical_history', title: 'Medical History' },
  { id: 'lifestyle', title: 'Lifestyle' },
  { id: 'review', title: 'Assessment' },
];

const PIE_COLORS = ['#0E7490', '#0284C7', '#0EA5E9', '#38BDF8', '#7DD3FC', '#F43F5E', '#FB7185', '#94A3B8'];

export const HeartRiskAssessment: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [activeTooltip, setActiveTooltip] = useState<{ title: string; content: string } | null>(null);
  const [pickerModal, setPickerModal] = useState<{ field: HeartFieldSchema } | null>(null);

  // Fetch options schema from backend
  const { data: schema, isLoading: isLoadingSchema } = useQuery({
    queryKey: ['heart-options-schema'],
    queryFn: () => api.getHeartOptions(),
    staleTime: 1000 * 60 * 60,
  });

  // Populate default form values as soon as schema arrives
  React.useEffect(() => {
    if (schema) {
      setFormData((prev) => {
        const next = { ...prev };
        [...schema.demographics, ...schema.medical_history, ...schema.lifestyle].forEach((f) => {
          if (!next[f.name]) {
            next[f.name] = f.default;
          }
        });
        return next;
      });
    }
  }, [schema]);

  // Risk assessment mutation
  const assessMutation = useMutation({
    mutationFn: (data: Record<string, string>) => api.assessHeartRisk(data),
  });

  const handleFieldChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep((prev) => prev + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      const fullPayload: Record<string, string> = {};
      if (schema) {
        [...schema.demographics, ...schema.medical_history, ...schema.lifestyle].forEach((f) => {
          fullPayload[f.name] = formData[f.name] || f.default;
        });
      }
      assessMutation.mutate({ ...fullPayload, ...formData });
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleRetake = () => {
    assessMutation.reset();
    setCurrentStep(0);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const currentStepFields = () => {
    if (!schema) return [];
    if (currentStep === 0) return schema.demographics;
    if (currentStep === 1) return schema.medical_history;
    if (currentStep === 2) return schema.lifestyle;
    return [];
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8 space-y-8 animate-fadeIn">
      {/* Title Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Badge variant="default" className="gap-1">
            <Heart className="h-3.5 w-3.5 text-rose-300" />
            EasyEnsemble + SHAP Explainability
          </Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
          Heart Disease Risk Assessment
        </h1>
        <p className="mt-1 text-sm sm:text-base text-muted-foreground">
          Evidence-based cardiovascular risk evaluation based on the CDC Behavioral Risk Factor Surveillance System (BRFSS).
        </p>
      </div>

      {/* Intro & How it Works (Shown before assessment results) */}
      {!assessMutation.data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="bg-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold">Introduction</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                The AI-Powered Heart Disease Risk Assessment App provides tailored risk scores and actionable recommendations to help mitigate heart disease risk. Using advanced machine learning, this module offers transparent assessments and preventive measures.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold">How It Works</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-xs sm:text-sm text-muted-foreground space-y-1.5 leading-relaxed">
                <li>• <strong>User Input:</strong> Enter demographics, medical history, and lifestyle factors.</li>
                <li>• <strong>AI Processing:</strong> EasyEnsemble classifier calculates cardiovascular risk.</li>
                <li>• <strong>SHAP Analysis:</strong> Pinpoints exact contributing factors.</li>
                <li>• <strong>Recommendations:</strong> Actionable steps to safeguard cardiovascular health.</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Multi-step Form Wizard */}
      {!assessMutation.data && (
        <Card>
          <CardHeader>
            <Stepper
              steps={STEPS}
              currentStep={currentStep}
              onStepClick={(idx) => idx <= currentStep && setCurrentStep(idx)}
            />
          </CardHeader>

          <CardContent className="space-y-6 pt-2">
            {isLoadingSchema && (
              <div className="space-y-4">
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
              </div>
            )}

            {/* Steps 0, 1, 2: Question fields */}
            {currentStep < 3 && !isLoadingSchema && (
              <div className="space-y-6">
                {currentStepFields().map((field) => {
                  const currentValue = formData[field.name] || field.default;
                  const isShortList = field.options.length <= 4;

                  return (
                    <div key={field.name} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <label className="text-sm font-semibold text-foreground flex items-center gap-1.5">
                          <span>{field.label}</span>
                          {field.help && (
                            <button
                              type="button"
                              onClick={() => setActiveTooltip({ title: field.label, content: field.help })}
                              className="touch-target text-muted-foreground hover:text-primary transition-colors"
                              aria-label={`Help for ${field.label}`}
                            >
                              <HelpCircle className="h-4 w-4" />
                            </button>
                          )}
                        </label>
                      </div>

                      {/* Render segmented buttons / radio cards for short lists (<=4 options) */}
                      {isShortList ? (
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                          {field.options.map((opt) => (
                            <button
                              key={opt.value}
                              type="button"
                              onClick={() => handleFieldChange(field.name, opt.value)}
                              className={cn(
                                'touch-target flex items-center justify-center rounded-lg p-3 text-sm font-medium border text-center transition-all select-none',
                                currentValue === opt.value
                                  ? 'border-primary bg-primary/10 text-primary font-semibold ring-2 ring-primary/20 shadow-sm'
                                  : 'border-border bg-background text-foreground hover:bg-muted active:scale-[0.98]'
                              )}
                            >
                              {opt.label}
                            </button>
                          ))}
                        </div>
                      ) : (
                        /* Native-feeling sheet trigger for long lists (>4 options) */
                        <div>
                          <button
                            type="button"
                            onClick={() => setPickerModal({ field })}
                            className="touch-target flex h-12 w-full items-center justify-between rounded-lg border border-input bg-background px-4 py-3 text-left text-base text-foreground shadow-sm transition-colors hover:border-primary/50 focus:outline-none focus:ring-2 focus:ring-ring"
                          >
                            <span>
                              {field.options.find((o) => o.value === currentValue)?.label || currentValue}
                            </span>
                            <ChevronDown className="h-4 w-4 text-muted-foreground ml-2" />
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Step 3: Review Step */}
            {currentStep === 3 && (
              <div className="space-y-4">
                <Alert variant="info" title="Ready for Risk Calculation">
                  Review your answers or tap any step above to make modifications. When ready, tap &quot;Calculate Heart Risk&quot; below.
                </Alert>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs sm:text-sm">
                  {schema &&
                    [...schema.demographics, ...schema.medical_history, ...schema.lifestyle].map((f) => (
                      <div key={f.name} className="flex justify-between p-2.5 rounded-lg bg-muted/40 border border-border">
                        <span className="text-muted-foreground truncate max-w-[150px]">{f.label}</span>
                        <span className="font-medium text-foreground text-right">
                          {f.options.find((o) => o.value === (formData[f.name] || f.default))?.label || formData[f.name]}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Mutation error */}
            {assessMutation.isError && (
              <ErrorState
                title="Assessment Error"
                message={(assessMutation.error as any)?.message || 'Failed to calculate risk score.'}
                onRetry={() => assessMutation.mutate(formData)}
              />
            )}
          </CardContent>

          {/* Sticky Navigation Bar */}
          <CardFooter className="sticky bottom-16 md:bottom-0 bg-card/95 backdrop-blur-md border-t border-border p-4 flex items-center justify-between gap-3 z-30">
            <Button
              variant="outline"
              onClick={handleBack}
              disabled={currentStep === 0 || assessMutation.isPending}
              className="gap-1.5"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>

            <Button
              onClick={handleNext}
              disabled={assessMutation.isPending}
              isLoading={assessMutation.isPending}
              className="gap-1.5"
            >
              <span>{currentStep === STEPS.length - 1 ? 'Calculate Heart Risk' : 'Next Step'}</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Results View */}
      {assessMutation.data && (
        <div className="space-y-8 animate-fadeIn">
          {/* Main Risk Score Card */}
          <Card className="border-primary/40 bg-gradient-to-b from-primary/5 to-card overflow-hidden">
            <CardHeader className="text-center pb-2">
              <Badge variant="outline" className="mx-auto mb-2">
                Cardiovascular Health Evaluation
              </Badge>
              <CardTitle className="text-2xl sm:text-3xl">AI Heart Disease Risk Assessment</CardTitle>
              <CardDescription>{assessMutation.data.risk_summary}</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center py-6">
              <ProgressRing
                value={assessMutation.data.risk_score}
                riskLevel={assessMutation.data.risk_level}
                size={180}
                strokeWidth={14}
              />
              <div className="mt-4 flex items-center gap-2">
                <span className="text-sm font-medium text-muted-foreground">Classification:</span>
                <Badge
                  variant={
                    assessMutation.data.risk_level === 'Low'
                      ? 'success'
                      : assessMutation.data.risk_level === 'Moderate'
                      ? 'warning'
                      : 'danger'
                  }
                  className="text-sm px-3 py-1 font-bold"
                >
                  {assessMutation.data.risk_level} Risk
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Contributing Factors & Pie Chart */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Pie Chart / Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Risk Factor Contribution</CardTitle>
                <CardDescription>
                  SHAP feature attribution breakdown indicating which factors elevated your cardiovascular risk.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={assessMutation.data.pie_chart_data}
                        dataKey="importance"
                        nameKey="feature"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        innerRadius={45}
                        paddingAngle={3}
                      >
                        {assessMutation.data.pie_chart_data.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip
                        formatter={(val: any) => [`${val}%`, 'Importance']}
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          borderColor: 'hsl(var(--border))',
                          borderRadius: '8px',
                          color: 'hsl(var(--foreground))',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                {/* Chart Legend */}
                <div className="mt-2 flex flex-wrap gap-2 text-xs">
                  {assessMutation.data.pie_chart_data.map((item, i) => (
                    <div key={i} className="flex items-center gap-1.5">
                      <span
                        className="h-2.5 w-2.5 rounded-full shrink-0"
                        style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }}
                      />
                      <span className="text-muted-foreground">
                        {item.feature}: <strong>{item.importance}%</strong>
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Personalized Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Tailored Clinical Recommendations</CardTitle>
                <CardDescription>
                  Preventative guidelines prioritized by your unique health and lifestyle inputs.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <ul className="space-y-3 text-sm">
                  {assessMutation.data.recommendations.map((rec, i) => (
                    <li key={i} className="flex items-start gap-2.5 p-3 rounded-lg bg-muted/40 border border-border">
                      <CheckCircle className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                      <span className="text-foreground leading-relaxed">{rec}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Action CTAs & Retake */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-6 rounded-xl border border-border bg-card">
            <div className="text-center sm:text-left">
              <h4 className="font-semibold text-foreground">Need to recalculate or adjust parameters?</h4>
              <p className="text-xs text-muted-foreground mt-0.5">Your input answers will be retained for review.</p>
            </div>
            <Button onClick={handleRetake} variant="outline" className="w-full sm:w-auto gap-2">
              <RotateCcw className="h-4 w-4" />
              Retake Assessment
            </Button>
          </div>

          {/* Learn More & Clinical Information */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Clinical Methodology & Evidence</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-xs text-muted-foreground leading-relaxed">
                {assessMutation.data.disclaimer}
              </p>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Evaluated against the CDC Behavioral Risk Factor Surveillance System (BRFSS) dataset with EasyEnsemble balanced classification and SHAP tree explainability.
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Help Tooltip Modal / Sheet */}
      {activeTooltip && (
        <Modal
          isOpen={Boolean(activeTooltip)}
          onClose={() => setActiveTooltip(null)}
          title={activeTooltip.title}
        >
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-primary shrink-0 mt-0.5" />
              <p className="text-sm text-foreground leading-relaxed">{activeTooltip.content}</p>
            </div>
            <div className="pt-4 flex justify-end">
              <Button size="sm" onClick={() => setActiveTooltip(null)}>
                Got it
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Picker Modal for Long Option Lists */}
      {pickerModal && (
        <Modal
          isOpen={Boolean(pickerModal)}
          onClose={() => setPickerModal(null)}
          title={`Select ${pickerModal.field.label}`}
        >
          <div className="space-y-2 max-h-[60vh] overflow-y-auto">
            {pickerModal.field.options.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => {
                  handleFieldChange(pickerModal.field.name, opt.value);
                  setPickerModal(null);
                }}
                className={cn(
                  'touch-target flex w-full items-center justify-between p-3.5 rounded-lg text-sm text-left border transition-colors',
                  (formData[pickerModal.field.name] || pickerModal.field.default) === opt.value
                    ? 'border-primary bg-primary/10 text-primary font-semibold'
                    : 'border-border hover:bg-muted text-foreground'
                )}
              >
                <span>{opt.label}</span>
                {(formData[pickerModal.field.name] || pickerModal.field.default) === opt.value && (
                  <CheckCircle className="h-4 w-4 text-primary shrink-0" />
                )}
              </button>
            ))}
          </div>
        </Modal>
      )}
    </div>
  );
};
