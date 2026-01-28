import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import type { ChunkInfo } from "@/lib/types";

interface ChunksTableProps {
  chunks: ChunkInfo[];
}

export function ChunksTable({ chunks }: ChunksTableProps) {
  const [search, setSearch] = useState("");
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);
  const [sortBy, setSortBy] = useState<"index" | "tokens">("index");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const filtered = chunks.filter(
    (c) =>
      c.text.toLowerCase().includes(search.toLowerCase()) ||
      String(c.index).includes(search)
  );

  const sorted = [...filtered].sort((a, b) => {
    const mul = sortDir === "asc" ? 1 : -1;
    if (sortBy === "index") return (a.index - b.index) * mul;
    return (a.token_count - b.token_count) * mul;
  });

  const toggleSort = (col: "index" | "tokens") => {
    if (sortBy === col) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(col);
      setSortDir("asc");
    }
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search chunks..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      <div className="rounded-lg border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th
                className="px-3 py-2 text-left font-medium cursor-pointer hover:text-primary"
                onClick={() => toggleSort("index")}
              >
                # {sortBy === "index" && (sortDir === "asc" ? "\u2191" : "\u2193")}
              </th>
              <th className="px-3 py-2 text-left font-medium">Preview</th>
              <th className="px-3 py-2 text-left font-medium">Page</th>
              <th
                className="px-3 py-2 text-right font-medium cursor-pointer hover:text-primary"
                onClick={() => toggleSort("tokens")}
              >
                Tokens{" "}
                {sortBy === "tokens" && (sortDir === "asc" ? "\u2191" : "\u2193")}
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((chunk, i) => (
              <motion.tr
                key={chunk.index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.02 }}
                className="border-t hover:bg-muted/30 cursor-pointer"
                onClick={() =>
                  setExpandedIdx(
                    expandedIdx === chunk.index ? null : chunk.index
                  )
                }
              >
                <td className="px-3 py-2 text-muted-foreground">
                  {chunk.index}
                </td>
                <td className="px-3 py-2">
                  <div className="flex items-center gap-2">
                    <ChevronDown
                      className={`h-3 w-3 transition-transform ${
                        expandedIdx === chunk.index ? "rotate-180" : ""
                      }`}
                    />
                    <span className="truncate max-w-[300px]">
                      {chunk.preview}
                    </span>
                  </div>
                  <AnimatePresence>
                    {expandedIdx === chunk.index && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="mt-2 p-3 bg-muted/50 rounded text-xs whitespace-pre-wrap overflow-auto max-h-48"
                      >
                        {chunk.text}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </td>
                <td className="px-3 py-2 text-muted-foreground">
                  {chunk.page_num ?? "-"}
                </td>
                <td className="px-3 py-2 text-right text-muted-foreground">
                  {chunk.token_count}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>

        {sorted.length === 0 && (
          <div className="p-8 text-center text-muted-foreground text-sm">
            No chunks found
          </div>
        )}
      </div>
    </div>
  );
}
