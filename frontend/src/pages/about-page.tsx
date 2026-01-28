import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Shield, Cpu } from "lucide-react";

export function AboutPage() {
  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: api.health,
  });

  return (
    <div className="flex-1 p-6 max-w-3xl mx-auto w-full space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Docling Playground</h1>
        <p className="text-muted-foreground">
          Interactive document processing powered by{" "}
          <a
            href="https://github.com/docling-project/docling"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            Docling
          </a>
        </p>
      </div>

      {health && (
        <div className="flex gap-2">
          <Badge variant="success">v{health.version}</Badge>
          {health.offline_mode && (
            <Badge variant="secondary">Offline Mode</Badge>
          )}
          <Badge variant="outline">{health.status}</Badge>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <FileText className="h-4 w-4 text-blue-500" />
              Document Processing
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Process PDF, DOCX, PPTX, HTML, and image files with advanced OCR
            and layout analysis.
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Cpu className="h-4 w-4 text-purple-500" />
              Multiple Pipelines
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Standard and VLM pipelines with configurable accelerator support
            (CPU, CUDA, MPS).
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-500" />
              Offline First
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            All processing runs locally. Download models once and work
            completely offline.
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Supported Formats</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {[
              ".pdf",
              ".docx",
              ".pptx",
              ".html",
              ".htm",
              ".png",
              ".jpg",
              ".jpeg",
              ".tiff",
              ".tif",
              ".bmp",
            ].map((ext) => (
              <Badge key={ext} variant="secondary">
                {ext}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
