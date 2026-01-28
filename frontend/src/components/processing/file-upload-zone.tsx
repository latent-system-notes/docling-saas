import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { formatBytes } from "@/lib/utils";

interface FileUploadZoneProps {
  file: File | null;
  onFileSelect: (file: File | null) => void;
  acceptedExtensions?: string[];
}

export function FileUploadZone({
  file,
  onFileSelect,
  acceptedExtensions,
}: FileUploadZoneProps) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted.length > 0) onFileSelect(accepted[0]);
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: acceptedExtensions
      ? Object.fromEntries(
          acceptedExtensions.map((ext) => [`application/${ext.replace(".", "")}`, [ext]])
        )
      : undefined,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all duration-200",
        isDragActive
          ? "border-primary bg-primary/5 scale-[1.02]"
          : file
            ? "border-success/50 bg-success/5"
            : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50"
      )}
    >
      <input {...getInputProps()} />
      <AnimatePresence mode="wait">
        {file ? (
          <motion.div
            key="selected"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-3 justify-center"
          >
            <FileText className="h-8 w-8 text-success" />
            <div className="text-left">
              <p className="text-sm font-medium truncate max-w-[200px]">
                {file.name}
              </p>
              <p className="text-xs text-muted-foreground">
                {formatBytes(file.size)}
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={(e) => {
                e.stopPropagation();
                onFileSelect(null);
              }}
            >
              <X className="h-4 w-4" />
            </Button>
          </motion.div>
        ) : (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Upload
              className={cn(
                "h-8 w-8 mx-auto mb-2 text-muted-foreground",
                isDragActive && "text-primary"
              )}
            />
            <p className="text-sm text-muted-foreground">
              {isDragActive
                ? "Drop file here"
                : "Drag & drop or click to select"}
            </p>
            <p className="text-xs text-muted-foreground/60 mt-1">
              PDF, DOCX, PPTX, HTML, images
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
