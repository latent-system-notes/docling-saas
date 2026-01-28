import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  children: ReactNode;
  className?: string;
}

export function Sidebar({ children, className }: SidebarProps) {
  return (
    <aside
      className={cn(
        "w-[380px] shrink-0 border-r bg-card overflow-y-auto",
        className
      )}
    >
      <div className="p-4 space-y-4">{children}</div>
    </aside>
  );
}
