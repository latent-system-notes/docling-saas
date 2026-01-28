import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster } from "sonner";
import { Header } from "@/components/layout/header";
import { ThemeProvider } from "@/providers/theme-provider";
import { QueryProvider } from "@/providers/query-provider";
import { ProcessingPage } from "@/pages/processing-page";
import { ModelsPage } from "@/pages/models-page";
import { AboutPage } from "@/pages/about-page";

export default function App() {
  return (
    <QueryProvider>
      <ThemeProvider>
        <BrowserRouter>
          <div className="min-h-screen flex flex-col">
            <Header />
            <main className="flex-1 flex">
              <Routes>
                <Route path="/" element={<ProcessingPage />} />
                <Route path="/models" element={<ModelsPage />} />
                <Route path="/about" element={<AboutPage />} />
              </Routes>
            </main>
          </div>
          <Toaster richColors position="bottom-right" />
        </BrowserRouter>
      </ThemeProvider>
    </QueryProvider>
  );
}
