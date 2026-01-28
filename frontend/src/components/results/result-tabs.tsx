import { motion, AnimatePresence } from "framer-motion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { MarkdownViewer } from "./markdown-viewer";
import { JsonViewer } from "./json-viewer";
import { ChunksTable } from "./chunks-table";
import { StatsPanel } from "./stats-panel";
import { TimingBreakdown } from "./timing-breakdown";
import { ResultSkeleton } from "./result-skeleton";
import type { ProcessingResult } from "@/lib/types";
import { formatSeconds } from "@/lib/utils";

interface ResultTabsProps {
  result: ProcessingResult | null;
  isProcessing: boolean;
}

const tabAnimation = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
  transition: { duration: 0.15 },
};

export function ResultTabs({ result, isProcessing }: ResultTabsProps) {
  if (isProcessing) return <ResultSkeleton />;

  if (!result) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted-foreground">
        <div className="text-center space-y-2">
          <p className="text-lg">No results yet</p>
          <p className="text-sm">
            Upload a document and click Process to get started
          </p>
        </div>
      </div>
    );
  }

  if (!result.success) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center space-y-2 text-destructive">
          <p className="text-lg font-medium">Processing Failed</p>
          <p className="text-sm">{result.error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-4 space-y-4">
      {result.timing && (
        <Badge variant="secondary" className="text-xs">
          Processed in {formatSeconds(result.timing.total_seconds)}
        </Badge>
      )}

      <Tabs defaultValue="markdown" className="w-full">
        <TabsList>
          <TabsTrigger value="markdown">Markdown</TabsTrigger>
          <TabsTrigger value="json">JSON</TabsTrigger>
          <TabsTrigger value="chunks">
            Chunks ({result.chunks.length})
          </TabsTrigger>
          <TabsTrigger value="stats">Stats</TabsTrigger>
          {result.timing && (
            <TabsTrigger value="timing">Timing</TabsTrigger>
          )}
        </TabsList>

        <AnimatePresence mode="wait">
          <TabsContent value="markdown">
            <motion.div {...tabAnimation}>
              <MarkdownViewer content={result.markdown} />
            </motion.div>
          </TabsContent>

          <TabsContent value="json">
            <motion.div {...tabAnimation}>
              <JsonViewer data={result.json_data} />
            </motion.div>
          </TabsContent>

          <TabsContent value="chunks">
            <motion.div {...tabAnimation}>
              <ChunksTable chunks={result.chunks} />
            </motion.div>
          </TabsContent>

          <TabsContent value="stats">
            <motion.div {...tabAnimation}>
              <StatsPanel stats={result.stats} />
            </motion.div>
          </TabsContent>

          {result.timing && (
            <TabsContent value="timing">
              <motion.div {...tabAnimation}>
                <TimingBreakdown timing={result.timing} />
              </motion.div>
            </TabsContent>
          )}
        </AnimatePresence>
      </Tabs>
    </div>
  );
}
