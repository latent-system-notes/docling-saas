import { Link, useLocation } from "react-router-dom";
import { useTheme } from "next-themes";
import { FileText, Moon, Sun, Cpu, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", label: "Process", icon: FileText },
  { to: "/models", label: "Models", icon: Cpu },
  { to: "/about", label: "About", icon: Info },
];

export function Header() {
  const location = useLocation();
  const { theme, setTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center px-6">
        <Link to="/" className="flex items-center gap-2 mr-8">
          <FileText className="h-6 w-6 text-primary" />
          <span className="font-semibold text-lg">Docling Playground</span>
        </Link>

        <nav className="flex items-center gap-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <Link key={to} to={to}>
              <Button
                variant={location.pathname === to ? "secondary" : "ghost"}
                size="sm"
                className={cn(
                  "gap-2",
                  location.pathname === to && "font-semibold"
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Button>
            </Link>
          ))}
        </nav>

        <div className="ml-auto">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
