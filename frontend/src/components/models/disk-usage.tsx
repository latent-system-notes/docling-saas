import { motion } from "framer-motion";
import { HardDrive } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatBytes } from "@/lib/utils";
import type { DiskUsage as DiskUsageType } from "@/lib/types";

interface DiskUsageProps {
  usage: DiskUsageType;
}

export function DiskUsage({ usage }: DiskUsageProps) {
  const total = usage.total || 1;
  const hfPct = (usage.huggingface / total) * 100;
  const ocrPct = (usage.easyocr / total) * 100;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <HardDrive className="h-4 w-4" />
          Disk Usage
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="text-2xl font-bold">{formatBytes(usage.total)}</div>

        <div className="h-3 rounded-full overflow-hidden bg-muted flex">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${hfPct}%` }}
            transition={{ duration: 0.6 }}
            className="bg-blue-500"
            title={`HuggingFace: ${formatBytes(usage.huggingface)}`}
          />
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${ocrPct}%` }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="bg-green-500"
            title={`EasyOCR: ${formatBytes(usage.easyocr)}`}
          />
        </div>

        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-sm bg-blue-500" />
            <span className="text-muted-foreground">HuggingFace</span>
            <span className="font-medium">
              {formatBytes(usage.huggingface)}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-sm bg-green-500" />
            <span className="text-muted-foreground">EasyOCR</span>
            <span className="font-medium">{formatBytes(usage.easyocr)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
