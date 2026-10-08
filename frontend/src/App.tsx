import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/context/ThemeContext';
import { Layout } from '@/components/layout/Layout';
import { Skeleton } from '@/components/ui/Feedback';

// Lazy-loaded routes for mobile performance and code splitting
const Home = lazy(() => import('@/pages/Home').then((m) => ({ default: m.Home })));
const DiseasePrediction = lazy(() =>
  import('@/pages/DiseasePrediction').then((m) => ({ default: m.DiseasePrediction }))
);
const DrugRecommendation = lazy(() =>
  import('@/pages/DrugRecommendation').then((m) => ({ default: m.DrugRecommendation }))
);
const HeartRiskAssessment = lazy(() =>
  import('@/pages/HeartRiskAssessment').then((m) => ({ default: m.HeartRiskAssessment }))
);
const Medibot = lazy(() => import('@/pages/Medibot').then((m) => ({ default: m.Medibot })));
const NotFound = lazy(() => import('@/pages/NotFound').then((m) => ({ default: m.NotFound })));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const PageLoader: React.FC = () => (
  <div className="mx-auto max-w-4xl px-4 py-12 space-y-4">
    <Skeleton className="h-10 w-48" />
    <Skeleton className="h-4 w-96 max-w-full" />
    <div className="pt-6 space-y-3">
      <Skeleton className="h-36 w-full" />
      <Skeleton className="h-28 w-full" />
    </div>
  </div>
);

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route index element={<Home />} />
                <Route path="disease" element={<DiseasePrediction />} />
                <Route path="drugs" element={<DrugRecommendation />} />
                <Route path="heart" element={<HeartRiskAssessment />} />
                <Route path="medibot" element={<Medibot />} />

                {/* Streamlit Legacy Route Redirects */}
                <Route
                  path="1_Disease-Prediction-and-medical-recommendation"
                  element={<Navigate to="/disease" replace />}
                />
                <Route
                  path="2_drug_recommendation"
                  element={<Navigate to="/drugs" replace />}
                />
                <Route
                  path="3_heart_Disease_Risk_Assesment"
                  element={<Navigate to="/heart" replace />}
                />
                <Route path="4_Medibot" element={<Navigate to="/medibot" replace />} />

                {/* 404 */}
                <Route path="*" element={<NotFound />} />
              </Route>
            </Routes>
          </Suspense>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
