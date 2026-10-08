import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Pill,
  Search,
  ExternalLink,
  ShoppingCart,
  Sparkles,
  ChevronRight,
  Info,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { api, DrugRecommendationResult } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Alert, Skeleton, EmptyState, ErrorState } from '@/components/ui/Feedback';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';

export const DrugRecommendation: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [selectedMedicine, setSelectedMedicine] = useState<string>('');
  const [isPickerOpen, setIsPickerOpen] = useState(false);

  // Debounce search query (250ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(searchQuery.trim());
    }, 250);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  // Query paginated drugs for autocomplete / picker
  const {
    data: drugsData,
    isLoading: isLoadingDrugs,
    error: drugsError,
  } = useQuery({
    queryKey: ['drugs-search', debouncedQuery],
    queryFn: () => api.searchDrugs(debouncedQuery, 1, 30),
    staleTime: 1000 * 60 * 5,
  });

  // Mutation for recommending similar drugs
  const recommendMutation = useMutation({
    mutationFn: (medicineName: string) => api.recommendDrug(medicineName),
  });

  const handleSelectMedicine = (med: string) => {
    setSelectedMedicine(med);
    setIsPickerOpen(false);
    recommendMutation.mutate(med);
  };

  const handleRecommendClick = () => {
    if (!selectedMedicine) return;
    recommendMutation.mutate(selectedMedicine);
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8 space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Badge variant="default" className="gap-1">
            <Pill className="h-3.5 w-3.5" />
            NLP & Cosine Similarity
          </Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
          AI Drug Recommendation System
        </h1>
        <p className="mt-1 text-sm sm:text-base text-muted-foreground">
          Discover verified pharmacological alternatives, descriptions, and similarity ratings across 9,720 medications.
        </p>
      </div>

      {/* Main Search and Selection Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5 text-primary" />
            Find Similar Medications
          </CardTitle>
          <CardDescription>
            Select a medicine to view clinical alternatives with identical therapeutic tags and molecular profiles.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-foreground">Select Medication</label>
            <div className="flex flex-col sm:flex-row gap-3">
              {/* Trigger Button that opens responsive full-screen search sheet / modal */}
              <button
                type="button"
                onClick={() => setIsPickerOpen(true)}
                className="flex-1 touch-target flex items-center justify-between h-12 w-full rounded-lg border border-input bg-background px-4 py-3 text-left text-base text-foreground shadow-sm transition-colors hover:border-primary/50 focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <span className={selectedMedicine ? 'font-medium text-foreground' : 'text-muted-foreground'}>
                  {selectedMedicine || 'Tap to search 9,700+ medicines...'}
                </span>
                <Search className="h-4 w-4 text-muted-foreground shrink-0 ml-2" />
              </button>

              <Button
                type="button"
                onClick={handleRecommendClick}
                disabled={!selectedMedicine || recommendMutation.isPending}
                isLoading={recommendMutation.isPending}
                className="w-full sm:w-auto"
                size="md"
              >
                <Sparkles className="mr-2 h-4 w-4" />
                Recommend Drug
              </Button>
            </div>
          </div>

          {/* Popular medicines quick select */}
          <div className="pt-1">
            <span className="text-xs text-muted-foreground block mb-2 font-medium">Popular medications:</span>
            <div className="flex flex-wrap gap-1.5">
              {['Paracetamol', 'Amoxicillin', 'Metformin', 'Ibuprofen', 'Cetirizine', 'Azithromycin'].map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => handleSelectMedicine(m)}
                  className="touch-target inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border border-border bg-muted/60 text-foreground hover:bg-primary/10 hover:border-primary/30 transition-colors"
                >
                  {m}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Modal / BottomSheet for searching and picking medicine */}
      <Modal
        isOpen={isPickerOpen}
        onClose={() => setIsPickerOpen(false)}
        title="Search Medicine"
        description="Search through 9,720 verified medications"
      >
        <div className="space-y-4">
          <Input
            autoFocus
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Type medicine name (e.g. Paracip, Dolo, Calpol)..."
            aria-label="Search medicine name"
          />

          {isLoadingDrugs && (
            <div className="space-y-2 py-4">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          )}

          {drugsData && drugsData.results && drugsData.results.length > 0 && (
            <ul className="divide-y divide-border rounded-lg border border-border max-h-[60vh] overflow-y-auto">
              {drugsData.results.map((drugName) => (
                <li
                  key={drugName}
                  onClick={() => handleSelectMedicine(drugName)}
                  className="flex items-center justify-between p-3.5 hover:bg-muted active:bg-muted/80 cursor-pointer transition-colors touch-target"
                >
                  <span className="text-sm font-medium text-foreground">{drugName}</span>
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                </li>
              ))}
            </ul>
          )}

          {drugsData?.results.length === 0 && !isLoadingDrugs && (
            <EmptyState
              title="No medications found"
              description={`No medication matched "${debouncedQuery}". Try another spelling.`}
            />
          )}
        </div>
      </Modal>

      {/* Error state */}
      {recommendMutation.isError && (
        <ErrorState
          title="Recommendation Error"
          message={(recommendMutation.error as any)?.message || 'Failed to generate drug recommendations.'}
          onRetry={handleRecommendClick}
        />
      )}

      {/* Loading Skeleton */}
      {recommendMutation.isPending && (
        <div className="space-y-4">
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
      )}

      {/* Results Display */}
      {recommendMutation.isSuccess && recommendMutation.data && (
        <div className="space-y-6 animate-fadeIn">
          {/* Selected Medicine Details */}
          <Card className="border-primary/30 bg-primary/5">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-primary">Selected Medication</span>
                <Badge variant="outline">Target Drug</Badge>
              </div>
              <CardTitle className="text-xl sm:text-2xl mt-1">{recommendMutation.data.medicine}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-foreground/90 leading-relaxed">
                {recommendMutation.data.description || 'No detailed pharmacological description available for this record.'}
              </p>
            </CardContent>
          </Card>

          {/* Recommended Drugs List */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Top Similar Alternative Medications
              </h3>
              <span className="text-xs text-muted-foreground">Ranked by Cosine Similarity</span>
            </div>

            <div className="space-y-3">
              {recommendMutation.data.recommendations.map((rec, idx) => (
                <Card key={idx} className="hover:border-primary/40 transition-all">
                  <CardContent className="p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h4 className="text-base font-bold text-foreground">{rec.name}</h4>
                        <Badge variant="success" className="text-[11px]">
                          {rec.similarity_percent}% match
                        </Badge>
                      </div>
                      {rec.description && (
                        <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                          {rec.description}
                        </p>
                      )}
                    </div>

                    <a
                      href={rec.buy_link}
                      target="_blank"
                      rel="noreferrer"
                      className="w-full sm:w-auto"
                    >
                      <Button variant="outline" size="sm" className="w-full sm:w-auto gap-1.5 touch-target">
                        <ShoppingCart className="h-4 w-4 text-emerald-600" />
                        <span>Pharmacy Options</span>
                        <ExternalLink className="h-3 w-3 opacity-60" />
                      </Button>
                    </a>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
