import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { useConfig } from "@/hooks/use-config";
import type { ProcessingOptions as ProcessingOpts } from "@/lib/types";

interface ProcessingOptionsProps {
  options: ProcessingOpts;
  onUpdate: <K extends keyof ProcessingOpts>(
    key: K,
    value: ProcessingOpts[K]
  ) => void;
}

export function ProcessingOptions({
  options,
  onUpdate,
}: ProcessingOptionsProps) {
  const { data: config } = useConfig();

  const ocrLanguages = config?.ocr_languages[options.ocr_library] ?? [];

  return (
    <Accordion
      type="multiple"
      defaultValue={["pipeline", "ocr", "advanced", "output"]}
      className="w-full"
    >
      {/* Pipeline & Accelerator */}
      <AccordionItem value="pipeline">
        <AccordionTrigger>Pipeline & Accelerator</AccordionTrigger>
        <AccordionContent>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label>Pipeline</Label>
              <Select
                value={options.pipeline}
                onValueChange={(v) => onUpdate("pipeline", v)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {config?.pipelines.map((p) => (
                    <SelectItem key={p.value} value={p.value}>
                      {p.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Accelerator</Label>
              <Select
                value={options.accelerator}
                onValueChange={(v) => onUpdate("accelerator", v)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {config?.accelerators.map((a) => (
                    <SelectItem key={a.value} value={a.value}>
                      {a.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </AccordionContent>
      </AccordionItem>

      {/* OCR Settings */}
      <AccordionItem value="ocr">
        <AccordionTrigger>OCR Settings</AccordionTrigger>
        <AccordionContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label>Enable OCR</Label>
            <Switch
              checked={options.ocr_enabled}
              onCheckedChange={(v) => onUpdate("ocr_enabled", v)}
            />
          </div>

          {options.ocr_enabled && (
            <>
              <div className="space-y-2">
                <Label>OCR Library</Label>
                <Select
                  value={options.ocr_library}
                  onValueChange={(v) => {
                    onUpdate("ocr_library", v);
                    const newLangs =
                      config?.ocr_languages[v];
                    if (newLangs && newLangs.length > 0) {
                      onUpdate("ocr_languages", [newLangs[0]]);
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {config?.ocr_libraries.map((l) => (
                      <SelectItem key={l.value} value={l.value}>
                        {l.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Languages</Label>
                <div className="flex flex-wrap gap-1.5">
                  {ocrLanguages.map((lang) => {
                    const isSelected =
                      options.ocr_languages.includes(lang);
                    return (
                      <button
                        key={lang}
                        onClick={() => {
                          if (isSelected) {
                            if (options.ocr_languages.length > 1) {
                              onUpdate(
                                "ocr_languages",
                                options.ocr_languages.filter(
                                  (l) => l !== lang
                                )
                              );
                            }
                          } else {
                            onUpdate("ocr_languages", [
                              ...options.ocr_languages,
                              lang,
                            ]);
                          }
                        }}
                        className={`px-2 py-0.5 text-xs rounded-full border transition-colors cursor-pointer ${
                          isSelected
                            ? "bg-primary text-primary-foreground border-primary"
                            : "bg-muted text-muted-foreground border-border hover:border-primary/50"
                        }`}
                      >
                        {lang}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <Label>Force Full Page OCR</Label>
                <Switch
                  checked={options.force_full_page_ocr}
                  onCheckedChange={(v) =>
                    onUpdate("force_full_page_ocr", v)
                  }
                />
              </div>
            </>
          )}
        </AccordionContent>
      </AccordionItem>

      {/* Advanced Features */}
      <AccordionItem value="advanced">
        <AccordionTrigger>Advanced Features</AccordionTrigger>
        <AccordionContent className="space-y-3">
          <div className="grid grid-cols-2 gap-x-4 gap-y-3">
            <div className="flex items-center justify-between">
              <Label>Table Structure</Label>
              <Switch
                checked={options.do_table_structure}
                onCheckedChange={(v) => onUpdate("do_table_structure", v)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label>Code Enrichment</Label>
              <Switch
                checked={options.do_code_enrichment}
                onCheckedChange={(v) => onUpdate("do_code_enrichment", v)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label>Formula Enrichment</Label>
              <Switch
                checked={options.do_formula_enrichment}
                onCheckedChange={(v) =>
                  onUpdate("do_formula_enrichment", v)
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <Label>Picture Description</Label>
              <Switch
                checked={options.do_picture_description}
                onCheckedChange={(v) =>
                  onUpdate("do_picture_description", v)
                }
              />
            </div>
          </div>
        </AccordionContent>
      </AccordionItem>

      {/* Output Settings */}
      <AccordionItem value="output">
        <AccordionTrigger>Output Settings</AccordionTrigger>
        <AccordionContent className="space-y-4">
          <div className="space-y-2">
            <Label>Output Format</Label>
            <Select
              value={options.output_format}
              onValueChange={(v) => onUpdate("output_format", v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {config?.output_formats.map((f) => (
                  <SelectItem key={f.value} value={f.value}>
                    {f.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Chunk Max Tokens</Label>
              <span className="text-xs text-muted-foreground">
                {options.chunk_max_tokens}
              </span>
            </div>
            <Slider
              min={64}
              max={2048}
              step={64}
              value={options.chunk_max_tokens}
              onValueChange={(v) => onUpdate("chunk_max_tokens", v)}
            />
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
