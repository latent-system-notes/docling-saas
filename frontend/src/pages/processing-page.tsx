import { toast } from "sonner";
import { Sidebar } from "@/components/layout/sidebar";
import { FileUploadZone } from "@/components/processing/file-upload-zone";
import { ProcessingOptions } from "@/components/processing/processing-options";
import { ProcessButton } from "@/components/processing/process-button";
import { ResultTabs } from "@/components/results/result-tabs";
import { useProcessing } from "@/hooks/use-processing";
import { useConfig } from "@/hooks/use-config";

export function ProcessingPage() {
  const { data: config } = useConfig();
  const {
    file,
    setFile,
    options,
    updateOption,
    process,
    result,
    error,
    isProcessing,
    isSuccess,
  } = useProcessing();

  const handleProcess = () => {
    if (!file) {
      toast.error("Please select a file first");
      return;
    }
    process(undefined, {
      onError: (err) => toast.error(`Processing failed: ${err.message}`),
      onSuccess: (res) => {
        if (res.success) {
          toast.success("Document processed successfully");
        } else {
          toast.error(res.error ?? "Processing failed");
        }
      },
    });
  };

  return (
    <div className="flex-1 flex min-h-0">
      <Sidebar>
        <ProcessingOptions options={options} onUpdate={updateOption} />
        <FileUploadZone
          file={file}
          onFileSelect={setFile}
          acceptedExtensions={config?.supported_extensions}
        />
        <ProcessButton
          onClick={handleProcess}
          isProcessing={isProcessing}
          isSuccess={isSuccess}
          disabled={!file}
        />
        {error && (
          <p className="text-xs text-destructive">{error.message}</p>
        )}
      </Sidebar>

      <div className="flex-1 flex flex-col min-h-0 overflow-auto">
        <ResultTabs result={result} isProcessing={isProcessing} />
      </div>
    </div>
  );
}
