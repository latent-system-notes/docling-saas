import { toast } from "sonner";
import { Download, Trash2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ModelTable } from "@/components/models/model-table";
import { DiskUsage } from "@/components/models/disk-usage";
import { Skeleton } from "@/components/ui/skeleton";
import { useModels } from "@/hooks/use-models";

export function ModelsPage() {
  const {
    models,
    diskUsage,
    isLoading,
    downloadModel,
    downloadRequired,
    downloadAll,
    clearCache,
  } = useModels();

  const isAnyDownloading =
    downloadModel.isPending ||
    downloadRequired.isPending ||
    downloadAll.isPending;

  return (
    <div className="flex-1 p-6 space-y-6 max-w-5xl mx-auto w-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Model Management</h1>
          <p className="text-sm text-muted-foreground">
            Download and manage AI models for document processing
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={isAnyDownloading}
            onClick={() =>
              downloadRequired.mutate(undefined, {
                onSuccess: () => toast.success("Required models downloaded"),
                onError: (e) => toast.error(e.message),
              })
            }
          >
            {downloadRequired.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <Download className="h-4 w-4 mr-1" />
            )}
            Download Required
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={isAnyDownloading}
            onClick={() =>
              downloadAll.mutate(undefined, {
                onSuccess: () => toast.success("All models downloaded"),
                onError: (e) => toast.error(e.message),
              })
            }
          >
            {downloadAll.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <Download className="h-4 w-4 mr-1" />
            )}
            Download All
          </Button>
          <Button
            variant="destructive"
            size="sm"
            disabled={clearCache.isPending}
            onClick={() =>
              clearCache.mutate(undefined, {
                onSuccess: () => toast.success("Cache cleared"),
                onError: (e) => toast.error(e.message),
              })
            }
          >
            {clearCache.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <Trash2 className="h-4 w-4 mr-1" />
            )}
            Clear Cache
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      ) : (
        <ModelTable
          models={models}
          onDownload={(id) =>
            downloadModel.mutate(id, {
              onSuccess: (res) => {
                if (res.success) toast.success(`Model downloaded`);
                else toast.error(res.message ?? "Download failed");
              },
              onError: (e) => toast.error(e.message),
            })
          }
          isDownloading={isAnyDownloading}
        />
      )}

      {diskUsage && <DiskUsage usage={diskUsage} />}

      <div className="text-xs text-muted-foreground">
        <p>
          Ready: {models.filter((m) => m.downloaded).length}/{models.length}{" "}
          models
        </p>
        <p>
          Required:{" "}
          {models.filter((m) => m.required && m.downloaded).length}/
          {models.filter((m) => m.required).length} ready
        </p>
      </div>
    </div>
  );
}
