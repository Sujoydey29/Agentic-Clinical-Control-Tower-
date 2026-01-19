"use client"

import { Area, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TimeSeriesPoint } from "@/lib/data-generators"

interface ProphetChartProps {
    title: string
    data: TimeSeriesPoint[]
    fluentColor?: string
}

export function ProphetChart({ title, data, fluentColor = "#3b82f6" }: ProphetChartProps) {
    // Extract RGB values for gradient opacity (simplified tick: assume CSS var or hex)
    // For now, we rely on the passed fluidColor which is an OKLCH string in our new theme, 
    // but Recharts needs explicit IDs for gradients. We'll use the title as ID key.

    return (
        <Card className="col-span-1 md:col-span-2 lg:col-span-1 h-full glass border-none overflow-hidden relative group">
            <div className="absolute inset-0 bg-gradient-to-b from-card/50 to-transparent pointer-events-none z-0" />

            <CardHeader className="relative z-10 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: fluentColor, boxShadow: `0 0 10px ${fluentColor}` }} />
                    {title}
                </CardTitle>
            </CardHeader>

            <CardContent className="relative z-10 p-0 pb-4">
                <div className="w-full h-[250px]" style={{ minWidth: 0 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <defs>
                                <linearGradient id={`${title}-fill`} x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={fluentColor} stopOpacity={0.3} />
                                    <stop offset="95%" stopColor={fluentColor} stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id={`${title}-stroke`} x1="0" y1="0" x2="1" y2="0">
                                    <stop offset="0%" stopColor={fluentColor} stopOpacity={1} />
                                    <stop offset="100%" stopColor={fluentColor} stopOpacity={0.8} />
                                </linearGradient>
                            </defs>

                            <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="oklch(var(--border) / 0.5)" />

                            <XAxis
                                dataKey="time"
                                stroke="oklch(var(--muted-foreground))"
                                fontSize={10}
                                tickLine={false}
                                axisLine={false}
                                minTickGap={30}
                                dy={10}
                            />
                            <YAxis
                                stroke="oklch(var(--muted-foreground))"
                                fontSize={10}
                                tickLine={false}
                                axisLine={false}
                                domain={[0, 100]}
                                dx={-5}
                            />

                            <Tooltip
                                cursor={{ stroke: fluentColor, strokeWidth: 1, strokeDasharray: '4 4' }}
                                content={({ active, payload }) => {
                                    if (active && payload && payload.length)
                                    {
                                        return (
                                            <div className="rounded-lg border border-white/10 bg-black/80 backdrop-blur-xl p-3 shadow-2xl">
                                                <div className="flex flex-col gap-2">
                                                    <span className="text-[10px] uppercase tracking-widest text-muted-foreground">{payload[0]?.payload.time}</span>
                                                    <div className="grid grid-cols-2 gap-x-6 gap-y-1">
                                                        <div className="flex flex-col">
                                                            <span className="text-[10px] uppercase text-muted-foreground">Actual</span>
                                                            <span className="font-bold text-lg text-foreground">{payload[0]?.value ?? '-'}%</span>
                                                        </div>
                                                        <div className="flex flex-col text-right">
                                                            <span className="text-[10px] uppercase text-muted-foreground">Forecast</span>
                                                            <span className="font-bold text-lg" style={{ color: fluentColor }}>
                                                                {payload[1]?.value ? `${payload[1].value}%` : '-'}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )
                                    }
                                    return null
                                }}
                            />

                            {/* Confidence Interval (Shaded Background) */}
                            <Area
                                type="monotone"
                                dataKey="upperCI"
                                stroke="none"
                                fill={fluentColor}
                                fillOpacity={0.05}
                            />
                            <Area
                                type="monotone"
                                dataKey="lowerCI"
                                stroke="none"
                                fill="var(--background)" // Cheat to "erase" bottom part to create band - assumes solid background, careful with glass
                                fillOpacity={1}
                            />

                            {/* Actual Data Line */}
                            <Line
                                type="monotone"
                                dataKey="actual"
                                stroke={fluentColor}
                                strokeWidth={3}
                                dot={{ r: 4, fill: fluentColor, strokeWidth: 0, stroke: 'none' }}
                                activeDot={{ r: 6, stroke: 'white', strokeWidth: 2 }}
                                strokeOpacity={1}
                                filter={`drop-shadow(0 0 8px ${fluentColor})`}
                            />

                            {/* Forecast Line (Dashed) */}
                            <Line
                                type="monotone"
                                dataKey="forecast"
                                stroke={fluentColor}
                                strokeWidth={2}
                                strokeDasharray="4 4"
                                dot={false}
                                strokeOpacity={0.6}
                            />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    )
}
