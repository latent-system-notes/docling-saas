import { motion } from "framer-motion";
import type { ProcessingTiming } from "@/lib/types";
import { formatSeconds } from "@/lib/utils";

interface TimingBreakdownProps {
  timing: ProcessingTiming;
}

const stages: { key: keyof ProcessingTiming; label: string; color: string }[] =
  [
    { key: "loading_seconds", label: "Loading", color: "bg-blue-500" },
    { key: "ocr_seconds", label: "OCR", color: "bg-green-500" },
    { key: "layout_seconds", label: "Layout", color: "bg-purple-500" },
    { key: "table_seconds", label: "Tables", color: "bg-amber-500" },
    { key: "chunking_seconds", label: "Chunking", color: "bg-cyan-500" },
  ];

export function TimingBreakdown({ timing }: TimingBreakdownProps) {
  const total = timing.total_seconds || 1;

  const activeStages = stages.filter(
    (s) => timing[s.key] != null && (timing[s.key] as number) > 0
  );

  return (
    <div className="space-y-4">
      <div className="text-sm font-medium">
        Total: {formatSeconds(timing.total_seconds)}
      </div>

      {/* Bar chart */}
      <div className="h-6 rounded-full overflow-hidden bg-muted flex">
        {activeStages.map((stage) => {
          const value = timing[stage.key] as number;
          const pct = (value / total) * 100;
          return (
            <motion.div
              key={stage.key}
              initial={{ width: 0 }}
              animate={{ width: `${pct}%` }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className={`${stage.color} relative group`}
              title={`${stage.label}: ${formatSeconds(value)}`}
            >
              <div className="absolute inset-0 flex items-center justify-center text-[10px] text-white font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                {pct > 10 ? stage.label : ""}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-1">
        {activeStages.map((stage) => {
          const value = timing[stage.key] as number;
          return (
            <div key={stage.key} className="flex items-center gap-1.5 text-xs">
              <div className={`w-3 h-3 rounded-sm ${stage.color}`} />
              <span className="text-muted-foreground">{stage.label}</span>
              <span className="font-medium">{formatSeconds(value)}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
