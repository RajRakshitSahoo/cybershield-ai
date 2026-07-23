import { ReactNode } from "react";

export default function Panel({
  title,
  icon,
  children,
  className = "",
  action,
}: {
  title?: string;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}) {
  return (
    <div className={`panel rounded-xl p-5 ${className}`}>
      {title && (
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {icon}
            <h3 className="font-display text-sm font-semibold text-ink">{title}</h3>
          </div>
          {action}
        </div>
      )}
      {children}
    </div>
  );
}
