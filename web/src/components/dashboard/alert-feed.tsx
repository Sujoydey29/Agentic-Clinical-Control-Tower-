"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, Siren, Activity, CheckCircle, Zap, Loader2 } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { getTimeSeriesAlerts, TimeSeriesAlert } from "@/lib/api"

interface DisplayAlert {
    id: string
    title: string
    message: string
    severity: "critical" | "warning" | "info" | "success"
    timestamp: string
}

function formatTimeAgo(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)

    if (diffMins < 1) return "Just now"
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${Math.floor(diffHours / 24)}d ago`
}

function mapApiAlertToDisplay(alert: TimeSeriesAlert): DisplayAlert {
    const severity: DisplayAlert["severity"] =
        alert.severity === "critical" ? "critical" :
            alert.severity === "high" ? "warning" :
                alert.severity === "medium" ? "info" : "info"

    const title = alert.event_type.split('_').map(w =>
        w.charAt(0).toUpperCase() + w.slice(1)
    ).join(' ')

    const message = `${alert.metric_name.replace('_', ' ')} at ${alert.current_value.toFixed(1)}${alert.unit} (threshold: ${alert.threshold_value}${alert.unit}). Affected: ${alert.affected_units.join(', ')}`

    return {
        id: alert.event_id,
        title: title,
        message: message,
        severity: severity,
        timestamp: formatTimeAgo(alert.detected_at)
    }
}

export function AlertFeed() {
    const [alerts, setAlerts] = useState<DisplayAlert[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function loadAlerts() {
            try
            {
                setLoading(true)
                const apiAlerts = await getTimeSeriesAlerts()
                const displayAlerts = apiAlerts.map(mapApiAlertToDisplay)
                setAlerts(displayAlerts)
            } catch (err)
            {
                console.error("Failed to load alerts:", err)
                // Show a default info alert on error
                setAlerts([{
                    id: "0",
                    title: "System Status",
                    message: "Unable to fetch alerts. Backend may be offline.",
                    severity: "info",
                    timestamp: "Just now"
                }])
            } finally
            {
                setLoading(false)
            }
        }
        loadAlerts()

        // Refresh alerts every 30 seconds
        const interval = setInterval(loadAlerts, 30000)
        return () => clearInterval(interval)
    }, [])

    const getIcon = (severity: string) => {
        switch (severity)
        {
            case "critical": return <Siren className="h-4 w-4 text-red-500 animate-pulse" />
            case "warning": return <AlertTriangle className="h-4 w-4 text-orange-500" />
            case "success": return <CheckCircle className="h-4 w-4 text-green-500" />
            default: return <Activity className="h-4 w-4 text-blue-500" />
        }
    }

    const getSeverityStyle = (severity: string) => {
        switch (severity)
        {
            case "critical": return "border-l-2 border-l-red-500 bg-red-500/5 group-hover:bg-red-500/10"
            case "warning": return "border-l-2 border-l-orange-500 bg-orange-500/5 group-hover:bg-orange-500/10"
            case "success": return "border-l-2 border-l-green-500 bg-green-500/5 group-hover:bg-green-500/10"
            default: return "border-l-2 border-l-blue-500 bg-blue-500/5 group-hover:bg-blue-500/10"
        }
    }

    return (
        <Card className="col-span-1 h-full max-h-[600px] flex flex-col glass border-none">
            <CardHeader>
                <CardTitle className="text-base font-medium flex items-center gap-2 text-glow">
                    <Zap className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                    Live Monitor Feed
                    {loading && <Loader2 className="h-3 w-3 animate-spin ml-2" />}
                </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 p-0 overflow-hidden">
                <ScrollArea className="h-[500px] px-4">
                    <div className="space-y-3 pb-4">
                        {alerts.length === 0 && !loading ? (
                            <div className="text-center text-muted-foreground py-8">
                                <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                                <p>All systems normal. No active alerts.</p>
                            </div>
                        ) : (
                            alerts.map((alert) => (
                                <div key={alert.id} className={`group flex gap-4 items-start p-3 rounded-md transition-colors ${getSeverityStyle(alert.severity)}`}>
                                    <div className={`mt-1 rounded-full p-1.5 bg-background/50 border border-white/5 shadow-inner shrink-0`}>
                                        {getIcon(alert.severity)}
                                    </div>
                                    <div className="flex-1 space-y-1 min-w-0">
                                        <div className="flex items-center justify-between">
                                            <p className="text-sm font-semibold leading-none text-foreground/90">{alert.title}</p>
                                            <span className="text-[10px] text-muted-foreground whitespace-nowrap ml-2">{alert.timestamp}</span>
                                        </div>
                                        <p className="text-xs text-muted-foreground leading-snug">{alert.message}</p>
                                        {alert.severity === "critical" && <Badge variant="destructive" className="mt-2 text-[10px] h-4 px-1.5 shadow-md shadow-red-900/20">Action Required</Badge>}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </ScrollArea>
            </CardContent>
        </Card>
    )
}
