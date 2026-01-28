import { motion } from "framer-motion";
import { Play, Loader2, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ProcessButtonProps {
  onClick: () => void;
  isProcessing: boolean;
  isSuccess: boolean;
  disabled: boolean;
}

export function ProcessButton({
  onClick,
  isProcessing,
  isSuccess,
  disabled,
}: ProcessButtonProps) {
  return (
    <motion.div whileTap={{ scale: 0.98 }}>
      <Button
        onClick={onClick}
        disabled={disabled || isProcessing}
        className={cn(
          "w-full h-11 text-base font-semibold gap-2 transition-all",
          isProcessing && "animate-pulse",
          isSuccess &&
            "bg-success text-white hover:bg-success/90"
        )}
        size="lg"
      >
        {isProcessing ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            Processing...
          </>
        ) : isSuccess ? (
          <>
            <CheckCircle className="h-5 w-5" />
            Done
          </>
        ) : (
          <>
            <Play className="h-5 w-5" />
            Process Document
          </>
        )}
      </Button>
    </motion.div>
  );
}
