import { motion } from "framer-motion";
import { Download, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { ModelStatus } from "@/lib/types";

interface ModelTableProps {
  models: ModelStatus[];
  onDownload: (modelId: string) => void;
  isDownloading: boolean;
}

export function ModelTable({
  models,
  onDownload,
  isDownloading,
}: ModelTableProps) {
  return (
    <div className="rounded-lg border overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-muted/50">
          <tr>
            <th className="px-4 py-3 text-left font-medium">Model</th>
            <th className="px-4 py-3 text-left font-medium">Status</th>
            <th className="px-4 py-3 text-right font-medium">Size</th>
            <th className="px-4 py-3 text-center font-medium">Required</th>
            <th className="px-4 py-3 text-right font-medium">Action</th>
          </tr>
        </thead>
        <tbody>
          {models.map((model, i) => (
            <motion.tr
              key={model.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04 }}
              className="border-t hover:bg-muted/30"
            >
              <td className="px-4 py-3">
                <div>
                  <p className="font-medium">{model.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {model.description}
                  </p>
                </div>
              </td>
              <td className="px-4 py-3">
                <Badge variant={model.downloaded ? "success" : "warning"}>
                  {model.downloaded ? "Ready" : "Missing"}
                </Badge>
              </td>
              <td className="px-4 py-3 text-right text-muted-foreground">
                {model.size_mb} MB
              </td>
              <td className="px-4 py-3 text-center">
                {model.required ? (
                  <Badge variant="outline">Required</Badge>
                ) : (
                  <span className="text-muted-foreground text-xs">
                    Optional
                  </span>
                )}
              </td>
              <td className="px-4 py-3 text-right">
                {!model.downloaded && (
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={isDownloading}
                    onClick={() => onDownload(model.id)}
                  >
                    {isDownloading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Download className="h-4 w-4" />
                    )}
                  </Button>
                )}
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
