import { JsonView, darkStyles, defaultStyles } from "react-json-view-lite";
import { useTheme } from "next-themes";
import "react-json-view-lite/dist/index.css";

interface JsonViewerProps {
  data: Record<string, unknown>;
}

export function JsonViewer({ data }: JsonViewerProps) {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === "dark";

  return (
    <div className="rounded-lg bg-muted/30 p-4 overflow-auto max-h-[600px] text-sm">
      <JsonView
        data={data}
        style={isDark ? darkStyles : defaultStyles}
      />
    </div>
  );
}
