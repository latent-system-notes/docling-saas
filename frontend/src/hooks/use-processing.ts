import { useMutation } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { ProcessingOptions, ProcessingResult } from "@/lib/types";
import { useConfig } from "./use-config";

export function useProcessing() {
  const { data: config } = useConfig();

  const [file, setFile] = useState<File | null>(null);
  const [options, setOptions] = useState<ProcessingOptions>({
    pipeline: "standard",
    accelerator: "auto",
    ocr_enabled: true,
    ocr_library: "easyocr",
    ocr_languages: ["en"],
    force_full_page_ocr: false,
    do_table_structure: true,
    do_code_enrichment: false,
    do_formula_enrichment: false,
    do_picture_description: false,
    output_format: "markdown",
    chunk_max_tokens: 512,
  });

  // Apply defaults from config once loaded
  const appliedDefaults = useRef(false);
  useEffect(() => {
    if (config?.defaults && !appliedDefaults.current) {
      appliedDefaults.current = true;
      setOptions((prev) => ({ ...prev, ...config.defaults }));
    }
  }, [config]);

  const mutation = useMutation<ProcessingResult, Error>({
    mutationFn: () => {
      if (!file) throw new Error("No file selected");
      return api.process(file, options);
    },
  });

  const updateOption = <K extends keyof ProcessingOptions>(
    key: K,
    value: ProcessingOptions[K]
  ) => {
    setOptions((prev) => ({ ...prev, [key]: value }));
  };

  return {
    file,
    setFile,
    options,
    updateOption,
    process: mutation.mutate,
    result: mutation.data ?? null,
    error: mutation.error,
    isProcessing: mutation.isPending,
    isSuccess: mutation.isSuccess,
    reset: mutation.reset,
  };
}
