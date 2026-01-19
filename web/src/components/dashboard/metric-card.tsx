"use client"

import { Card, CardContent } from "@/components/ui/card"
import { ArrowDown, ArrowUp, Minus, Activity } from "lucide-react"
import { motion } from "framer-motion"

interface MetricCardProps {
    label: string
    value: string | number
    subValue?: string
    trend?: "up" | "down" | "neutral"
    trendValue?: string
    status?: "normal" | "warning" | "critical"
    icon?: React.ElementType
}

export function MetricCard({ label, value, subValue, trend, trendValue, status = "normal", icon: Icon }: MetricCardProps) {
    const statusGlows = {
        normal: "shadow-[0_0_20px_-10px_oklch(var(--primary)/0.4)] border-primary/20",
        warning: "shadow-[0_0_30px_-10px_oklch(var(--chart-3)/0.5)] border-chart-3/30",
        critical: "shadow-[0_0_40px_-10px_oklch(var(--chart-5)/0.6)] border-chart-5/40 animate-pulse-subtle"
    }

    const bgGradients = {
        normal: "bg-gradient-to-br from-card to-card/60",
        warning: "bg-gradient-to-br from-card to-chart-3/10",
        critical: "bg-gradient-to-br from-card to-chart-5/15"
    }

    const textColors = {
        normal: "text-foreground",
        warning: "text-chart-3",
        critical: "text-chart-5"
    }

    return (
        <motion.div whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
            <Card className={`relative overflow-hidden backdrop-blur-2xl border transition-all duration-500 hover:shadow-2xl group ${statusGlows[status]} ${bgGradients[status]} h-full`}>
                {/* Tech Decor Corners */}
                <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-primary/30 rounded-tl-sm" />
                <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-primary/30 rounded-tr-sm" />
                <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-primary/30 rounded-bl-sm" />
                <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-primary/30 rounded-br-sm" />

                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-25 transition-opacity duration-500 scale-150 rotate-12 origin-top-right">
                    {Icon ? <Icon className="h-24 w-24" /> : <Activity className="h-24 w-24" />}
                </div>

                <CardContent className="p-6 relative z-10 flex flex-col justify-between h-full">
                    <div className="flex items-center justify-between space-y-0 pb-4">
                        <p className="text-sm font-bold text-muted-foreground tracking-widest uppercase">{label}</p>
                        {status !== "normal" && (
                            <span className="relative flex h-3 w-3">
                                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${status === 'critical' ? 'bg-chart-5' : 'bg-chart-3'}`}></span>
                                <span className={`relative inline-flex rounded-full h-3 w-3 ${status === 'critical' ? 'bg-chart-5' : 'bg-chart-3'}`}></span>
                            </span>
                        )}
                    </div>

                    <div className="flex flex-col gap-1">
                        <div className={`text-5xl font-extrabold tracking-tight ${textColors[status]} text-glow tabular-nums`}>{value}</div>

                        <div className="flex items-end justify-between mt-2">
                            {subValue && <p className="text-sm text-muted-foreground font-mono opacity-80">{subValue}</p>}

                            {(trend && trendValue) && (
                                <div className="flex items-center text-sm font-bold bg-background/40 backdrop-blur-sm px-3 py-1.5 rounded-full border border-white/5 shadow-inner">
                                    {trend === "up" && <ArrowUp className="mr-1.5 h-4 w-4 text-chart-5" />}
                                    {trend === "down" && <ArrowDown className="mr-1.5 h-4 w-4 text-chart-2" />}
                                    {trend === "neutral" && <Minus className="mr-1.5 h-4 w-4 text-muted-foreground" />}
                                    <span className={trend === "up" ? "text-chart-5" : trend === "down" ? "text-chart-2" : "text-muted-foreground"}>
                                        {trendValue}
                                    </span>
                                    <span className="text-muted-foreground/60 ml-1.5 text-xs font-normal">vs 1h</span>
                                </div>
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    )
}
