export interface EnumOption {
  value: string;
  label: string;
}

export interface AppConfig {
  pipelines: EnumOption[];
  accelerators: EnumOption[];
  ocr_libraries: EnumOption[];
  ocr_languages: Record<string, string[]>;
  output_formats: EnumOption[];
  supported_extensions: string[];
  defaults: {
    pipeline: string;
    accelerator: string;
    ocr_enabled: boolean;
    ocr_library: string;
    ocr_languages: string[];
    force_full_page_ocr: boolean;
    do_table_structure: boolean;
    do_code_enrichment: boolean;
    do_formula_enrichment: boolean;
    do_picture_description: boolean;
    output_format: string;
    chunk_max_tokens: number;
  };
}

export interface ProcessingOptions {
  pipeline: string;
  accelerator: string;
  ocr_enabled: boolean;
  ocr_library: string;
  ocr_languages: string[];
  force_full_page_ocr: boolean;
  do_table_structure: boolean;
  do_code_enrichment: boolean;
  do_formula_enrichment: boolean;
  do_picture_description: boolean;
  output_format: string;
  chunk_max_tokens: number;
}

export interface ProcessingTiming {
  total_seconds: number;
  loading_seconds: number | null;
  ocr_seconds: number | null;
  layout_seconds: number | null;
  table_seconds: number | null;
  chunking_seconds: number | null;
}

export interface ChunkInfo {
  index: number;
  text: string;
  preview: string;
  page_num: number | null;
  token_count: number;
}

export interface ProcessingStats {
  num_pages: number;
  num_tables: number;
  num_figures: number;
  num_chunks: number;
  total_tokens: number;
  ocr_library_used: string | null;
  pipeline_used: string;
}

export interface ProcessingResult {
  success: boolean;
  error: string | null;
  markdown: string;
  json_data: Record<string, unknown>;
  chunks: ChunkInfo[];
  stats: ProcessingStats;
  timing: ProcessingTiming | null;
}

export interface ModelStatus {
  id: string;
  name: string;
  description: string;
  size_mb: number;
  required: boolean;
  downloaded: boolean;
  path: string | null;
}

export interface DiskUsage {
  total: number;
  huggingface: number;
  easyocr: number;
}

export interface HealthStatus {
  status: string;
  version: string;
  offline_mode: boolean;
}
