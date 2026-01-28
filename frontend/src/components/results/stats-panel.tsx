import { motion } from "framer-motion";
import {
  FileText,
  Table2,
  Image,
  Layers,
  Hash,
  ScanSearch,
  Workflow,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import type { ProcessingStats } from "@/lib/types";

interface StatsPanelProps {
  stats: ProcessingStats;
}

const statConfig = [
  { key: "num_pages" as const, label: "Pages", icon: FileText, color: "text-blue-500" },
  { key: "num_tables" as const, label: "Tables", icon: Table2, color: "text-green-500" },
  { key: "num_figures" as const, label: "Figures", icon: Image, color: "text-purple-500" },
  { key: "num_chunks" as const, label: "Chunks", icon: Layers, color: "text-amber-500" },
  { key: "total_tokens" as const, label: "Tokens", icon: Hash, color: "text-cyan-500" },
];

function AnimatedNumber({ value }: { value: number }) {
  return (
    <motion.span
      key={value}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-2xl font-bold"
    >
      {value.toLocaleString()}
    </motion.span>
  );
}

export function StatsPanel({ stats }: StatsPanelProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {statConfig.map(({ key, label, icon: Icon, color }, i) => (
          <motion.div
            key={key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Icon className={`h-5 w-5 ${color}`} />
                  <div>
                    <p className="text-xs text-muted-foreground">{label}</p>
                    <AnimatedNumber value={stats[key]} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="flex gap-4 text-sm text-muted-foreground">
        {stats.pipeline_used && (
          <div className="flex items-center gap-1.5">
            <Workflow className="h-4 w-4" />
            Pipeline: {stats.pipeline_used}
          </div>
        )}
        {stats.ocr_library_used && (
          <div className="flex items-center gap-1.5">
            <ScanSearch className="h-4 w-4" />
            OCR: {stats.ocr_library_used}
          </div>
        )}
      </div>
    </div>
  );
}
