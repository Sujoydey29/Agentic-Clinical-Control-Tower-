import { Badge } from "@/components/ui/badge"

interface RiskBadgeProps {
    score: number
    label?: string
    reverse?: boolean // If true, High Score = Good (e.g. Discharge Readiness)
}

export function RiskBadge({ score, label, reverse = false }: RiskBadgeProps) {
    let colorClass = "bg-muted text-muted-foreground border-muted-foreground/20"
    let glowClass = ""

    // Standard Risk: High Score = Bad
    if (!reverse)
    {
        if (score >= 70)
        {
            colorClass = "bg-chart-5/10 text-chart-5 border-chart-5/50"
            glowClass = "shadow-[0_0_10px_-2px_oklch(var(--chart-5)/0.5)]"
        } else if (score >= 40)
        {
            colorClass = "bg-chart-3/10 text-chart-3 border-chart-3/50"
            glowClass = "shadow-[0_0_10px_-2px_oklch(var(--chart-3)/0.5)]"
        } else
        {
            colorClass = "bg-chart-2/10 text-chart-2 border-chart-2/50"
            glowClass = "shadow-[0_0_10px_-2px_oklch(var(--chart-2)/0.5)]"
        }
    } else
    {
        // Reveresed: High Score = Good (e.g. Readiness)
        if (score >= 80)
        {
            colorClass = "bg-chart-2/10 text-chart-2 border-chart-2/50"
            glowClass = "shadow-[0_0_10px_-2px_oklch(var(--chart-2)/0.5)]"
        } else if (score >= 50)
        {
            colorClass = "bg-chart-3/10 text-chart-3 border-chart-3/50"
            glowClass = "shadow-[0_0_10px_-2px_oklch(var(--chart-3)/0.5)]"
        } else
        {
            colorClass = "bg-chart-5/10 text-chart-5 border-chart-5/50"
            glowClass = "shadow-[0_0_10px_-2px_oklch(var(--chart-5)/0.5)]"
        }
    }

    return (
        <div className="flex flex-col items-center">
            <Badge variant="outline" className={`${colorClass} ${glowClass} border font-mono text-sm px-3 py-1 transition-all duration-300`}>
                {score}%
            </Badge>
            {label && <span className="text-[10px] text-muted-foreground mt-1 uppercase tracking-wider">{label}</span>}
        </div>
    )
}
