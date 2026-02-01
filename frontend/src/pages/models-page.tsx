import { toast } from "sonner";
import { Download, Trash2, Loader2, Wifi, WifiOff, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ModelTable } from "@/components/models/model-table";
import { DiskUsage } from "@/components/models/disk-usage";
import { Skeleton } from "@/components/ui/skeleton";
import { useModels } from "@/hooks/use-models";

export function ModelsPage() {
  const {
    models,
    diskUsage,
    offlineStatus,
    isLoading,
    downloadModel,
    downloadRequired,
    downloadAll,
    downloadEasyOCR,
    verifyRapidOCR,
    clearCache,
  } = useModels();

  const isAnyDownloading =
    downloadModel.isPending ||
    downloadRequired.isPending ||
    downloadAll.isPending ||
    downloadEasyOCR.isPending ||
    verifyRapidOCR.isPending;

  return (
    <div className="flex-1 p-6 space-y-6 max-w-5xl mx-auto w-full">
      {/* Offline Status Banner */}
      {offlineStatus && (
        <div
          className={`p-3 rounded-lg flex items-center gap-2 text-sm ${
            offlineStatus.offline_mode
              ? "bg-green-500/10 text-green-600 border border-green-500/20"
              : "bg-yellow-500/10 text-yellow-600 border border-yellow-500/20"
          }`}
        >
          {offlineStatus.offline_mode ? (
            <>
              <WifiOff className="h-4 w-4" />
              <span>
                <strong>Offline Mode:</strong> Using local models only. No
                downloads will occur.
              </span>
            </>
          ) : (
            <>
              <Wifi className="h-4 w-4" />
              <span>
                <strong>Online Mode:</strong> Downloads are allowed. Models will
                be fetched from the internet if not cached.
              </span>
            </>
          )}
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Model Management</h1>
          <p className="text-sm text-muted-foreground">
            Download and manage AI models for document processing
          </p>
        </div>
        <div className="flex gap-2 flex-wrap justify-end">
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
            Required
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
            All Models
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={isAnyDownloading}
            onClick={() =>
              downloadEasyOCR.mutate(["en", "ar"], {
                onSuccess: (res) =>
                  toast.success(`EasyOCR models downloaded: ${res.languages.join(", ")}`),
                onError: (e) => toast.error(e.message),
              })
            }
          >
            {downloadEasyOCR.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <Download className="h-4 w-4 mr-1" />
            )}
            EasyOCR
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={isAnyDownloading}
            onClick={() =>
              verifyRapidOCR.mutate(undefined, {
                onSuccess: (res) =>
                  toast.success(res.success ? "RapidOCR is ready" : "RapidOCR not available"),
                onError: (e) => toast.error(e.message),
              })
            }
          >
            {verifyRapidOCR.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <Eye className="h-4 w-4 mr-1" />
            )}
            RapidOCR
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
            Clear
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

      <div className="text-xs text-muted-foreground space-y-1">
        <p>
          Ready: {models.filter((m) => m.downloaded).length}/{models.length}{" "}
          models
        </p>
        <p>
          Required:{" "}
          {models.filter((m) => m.required && m.downloaded).length}/
          {models.filter((m) => m.required).length} ready
        </p>
        {offlineStatus && (
          <div className="mt-2 p-2 bg-muted rounded text-xs font-mono">
            <p>Models Dir: {offlineStatus.models_dir}</p>
            <p>HF Home: {offlineStatus.hf_home}</p>
            <p>EasyOCR Path: {offlineStatus.easyocr_module_path}</p>
          </div>
        )}
      </div>
    </div>
  );
}
