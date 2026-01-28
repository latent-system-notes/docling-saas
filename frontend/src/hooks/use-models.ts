import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useModels() {
  const queryClient = useQueryClient();

  const modelsQuery = useQuery({
    queryKey: ["models"],
    queryFn: api.models.list,
  });

  const diskUsageQuery = useQuery({
    queryKey: ["disk-usage"],
    queryFn: api.models.diskUsage,
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["models"] });
    queryClient.invalidateQueries({ queryKey: ["disk-usage"] });
  };

  const downloadModel = useMutation({
    mutationFn: (modelId: string) => api.models.download(modelId),
    onSuccess: invalidate,
  });

  const downloadRequired = useMutation({
    mutationFn: api.models.downloadRequired,
    onSuccess: invalidate,
  });

  const downloadAll = useMutation({
    mutationFn: api.models.downloadAll,
    onSuccess: invalidate,
  });

  const clearCache = useMutation({
    mutationFn: api.models.clearCache,
    onSuccess: invalidate,
  });

  return {
    models: modelsQuery.data ?? [],
    diskUsage: diskUsageQuery.data ?? null,
    isLoading: modelsQuery.isLoading,
    downloadModel,
    downloadRequired,
    downloadAll,
    clearCache,
  };
}
