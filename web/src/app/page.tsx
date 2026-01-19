"use client"

import { useEffect, useState } from "react"
import { MetricCard } from "@/components/dashboard/metric-card"
import { ProphetChart } from "@/components/dashboard/prophet-chart"
import { AlertFeed } from "@/components/dashboard/alert-feed"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger } from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { RefreshCw, Download, Activity, Users, ClipboardList, BedDouble, Loader2, FileText, Sparkles, AlertTriangle, CheckCircle2, Zap } from "lucide-react"
import { motion, Variants } from "framer-motion"
import { getIcuForecast, getErForecast, getForecastSummary, simulateScenario } from "@/lib/api"
import { TimeSeriesPoint } from "@/lib/data-generators"

const container: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
}

const item: Variants = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 100 } }
}

type UserRole = "admin" | "nurse" | "physician"

// Role descriptions for the tooltip
const roleDescriptions: Record<UserRole, string> = {
  admin: "Full operational view with all metrics and alerts",
  nurse: "Patient-focused view with staffing and discharge data",
  physician: "Clinical view with ICU capacity and ER arrivals"
}

// Define which metrics each role sees
const roleMetrics: Record<UserRole, string[]> = {
  admin: ["ICU Occupancy", "ER Arrivals / Hr", "Staffing Ratio", "Ward Occupancy"],
  nurse: ["Staffing Ratio", "Ward Occupancy", "ER Arrivals / Hr"],
  physician: ["ICU Occupancy", "ER Arrivals / Hr", "Ward Occupancy"]
}

export default function DashboardPage() {
  const [icuData, setIcuData] = useState<TimeSeriesPoint[]>([])
  const [erData, setErData] = useState<TimeSeriesPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRole, setSelectedRole] = useState<UserRole>("admin")
  const [metrics, setMetrics] = useState({
    icuOccupancy: 0,
    erArrivals: 0,
    staffingRatio: "1:4",
    wardOccupancy: 0
  })

  // Scenario Simulation State
  const [scenarioDialogOpen, setScenarioDialogOpen] = useState(false)
  const [scenarioInput, setScenarioInput] = useState("")
  const [scenarioLoading, setScenarioLoading] = useState(false)
  const [scenarioResult, setScenarioResult] = useState<any>(null)

  useEffect(() => {
    async function loadForecasts() {
      try
      {
        setLoading(true)

        // Fetch ICU forecast
        const icuForecast = await getIcuForecast(12)
        const icuChartData: TimeSeriesPoint[] = icuForecast.data_points.map((p, i) => ({
          time: `+${i}h`,
          actual: i === 0 ? p.predicted_value : null,
          forecast: p.predicted_value,
          lowerCI: p.lower_bound,
          upperCI: p.upper_bound
        }))
        setIcuData(icuChartData)

        // Fetch ER forecast
        const erForecast = await getErForecast(6)
        const erChartData: TimeSeriesPoint[] = erForecast.data_points.map((p, i) => ({
          time: `+${i}h`,
          actual: i === 0 ? p.predicted_value : null,
          forecast: p.predicted_value,
          lowerCI: p.lower_bound,
          upperCI: p.upper_bound
        }))
        setErData(erChartData)

        // Get summary for metrics
        const summary = await getForecastSummary()
        setMetrics({
          icuOccupancy: Math.round(summary.metrics.icu_occupancy.current),
          erArrivals: Math.round(summary.metrics.er_arrivals.current),
          staffingRatio: "1:4",
          wardOccupancy: Math.round(summary.metrics.ward_occupancy.current)
        })

      } catch (err)
      {
        console.error("Failed to load forecasts:", err)
      } finally
      {
        setLoading(false)
      }
    }
    loadForecasts()
  }, [])

  const refreshData = () => {
    setLoading(true)
    window.location.reload()
  }

  // Scenario Simulation Handler
  const handleRunSimulation = async () => {
    if (!scenarioInput.trim()) return
    setScenarioLoading(true)
    setScenarioResult(null)
    try
    {
      const result = await simulateScenario(scenarioInput)
      setScenarioResult(result)
    } catch (err)
    {
      console.error("Simulation failed:", err)
      setScenarioResult({ error: "Failed to run simulation. Check backend connection." })
    } finally
    {
      setScenarioLoading(false)
    }
  }

  // Export Report functionality - generates CSV download
  const exportReport = () => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const reportData = [
      ["ACCT Control Tower Report"],
      [`Generated: ${new Date().toLocaleString()}`],
      [`Role View: ${selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)}`],
      [""],
      ["CURRENT METRICS"],
      ["Metric", "Value", "Status"],
      ["ICU Occupancy", `${metrics.icuOccupancy}%`, metrics.icuOccupancy > 85 ? "Critical" : metrics.icuOccupancy > 75 ? "Warning" : "Normal"],
      ["ER Arrivals/Hr", `${metrics.erArrivals}`, metrics.erArrivals > 20 ? "Critical" : metrics.erArrivals > 15 ? "Warning" : "Normal"],
      ["Staffing Ratio", metrics.staffingRatio, "Normal"],
      ["Ward Occupancy", `${metrics.wardOccupancy}%`, metrics.wardOccupancy > 85 ? "Warning" : "Normal"],
      [""],
      ["ICU FORECAST (Next 12 Hours)"],
      ["Hour", "Predicted", "Lower Bound", "Upper Bound"],
      ...icuData.map((d) => [d.time, d.forecast?.toFixed(1) || "", d.lowerCI?.toFixed(1) || "", d.upperCI?.toFixed(1) || ""]),
      [""],
      ["ER ARRIVALS FORECAST (Next 6 Hours)"],
      ["Hour", "Predicted", "Lower Bound", "Upper Bound"],
      ...erData.map((d) => [d.time, d.forecast?.toFixed(1) || "", d.lowerCI?.toFixed(1) || "", d.upperCI?.toFixed(1) || ""])
    ]

    const csvContent = reportData.map(row => row.join(",")).join("\n")
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = `ACCT_Report_${timestamp}.csv`
    link.click()
  }

  const allMetricCards = [
    { label: "ICU Occupancy", value: `${metrics.icuOccupancy}%`, trend: metrics.icuOccupancy > 80 ? "up" as const : "neutral" as const, trendValue: "2.5%", status: metrics.icuOccupancy > 85 ? "critical" as const : metrics.icuOccupancy > 75 ? "warning" as const : "normal" as const, icon: BedDouble },
    { label: "ER Arrivals / Hr", value: `${metrics.erArrivals}`, trend: "up" as const, trendValue: "4", status: metrics.erArrivals > 20 ? "critical" as const : metrics.erArrivals > 15 ? "warning" as const : "normal" as const, icon: Activity },
    { label: "Staffing Ratio", value: metrics.staffingRatio, trend: "neutral" as const, trendValue: "0", status: "normal" as const, icon: Users },
    { label: "Ward Occupancy", value: `${metrics.wardOccupancy}%`, trend: "neutral" as const, trendValue: "1", status: metrics.wardOccupancy > 85 ? "warning" as const : "normal" as const, icon: ClipboardList },
  ]

  // Filter metrics based on selected role
  const visibleMetrics = allMetricCards.filter(m => roleMetrics[selectedRole].includes(m.label))

  // Risk level color mapping
  const getRiskColor = (level: string) => {
    switch (level?.toLowerCase())
    {
      case 'critical': return 'text-red-400 bg-red-500/10 border-red-500/30'
      case 'high': return 'text-orange-400 bg-orange-500/10 border-orange-500/30'
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
      case 'low': return 'text-green-400 bg-green-500/10 border-green-500/30'
      default: return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
    }
  }

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="flex flex-col gap-8 h-full p-2"
    >
      <motion.div variants={item} className="flex items-center justify-between">
        <div>
          <h2 className="text-4xl font-extrabold tracking-tight text-glow bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-400 to-purple-500">
            Control Tower
          </h2>
          <p className="text-lg text-muted-foreground">
            {loading ? "Loading real-time forecasts..." : `${roleDescriptions[selectedRole]}`}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Role Toggle */}
          <div className="glass px-3 py-1.5 rounded-xl flex items-center gap-2 border border-white/10">
            <span className="text-[10px] uppercase font-bold text-muted-foreground">View As:</span>
            <select
              className="bg-transparent text-sm font-bold text-primary focus:outline-none cursor-pointer"
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value as UserRole)}
            >
              <option value="admin">Admin</option>
              <option value="nurse">Nurse</option>
              <option value="physician">Physician</option>
            </select>
          </div>

          {/* Scenario Sandbox Dialog Trigger */}
          <Dialog open={scenarioDialogOpen} onOpenChange={setScenarioDialogOpen}>
            <DialogTrigger asChild>
              <button className="h-10 px-4 rounded-xl bg-primary/10 border border-primary/20 text-primary font-bold text-sm tracking-wide hover:bg-primary/20 hover:shadow-[0_0_15px_oklch(var(--primary)/0.4)] transition-all flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                Simulate Scenario
              </button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px] bg-card/95 backdrop-blur-xl border-white/10">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2 text-xl">
                  <Zap className="h-5 w-5 text-primary" />
                  AI Scenario Simulation
                </DialogTitle>
                <DialogDescription>
                  Describe a "What-If" scenario to predict operational impact using AI.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 py-4">
                <Textarea
                  placeholder="Example: ER surge of 50% more patients in the next 2 hours due to a local event..."
                  value={scenarioInput}
                  onChange={(e) => setScenarioInput(e.target.value)}
                  className="min-h-[100px] bg-black/20 border-white/10 focus:border-primary"
                />

                {/* Result Display */}
                {scenarioResult && !scenarioResult.error && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4 p-4 rounded-xl bg-black/30 border border-white/10"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-white">Simulation Result</h4>
                      <Badge className={getRiskColor(scenarioResult.simulation_result?.risk_level_change || scenarioResult.risk_level_change)}>
                        {scenarioResult.simulation_result?.risk_level_change || scenarioResult.risk_level_change || 'Unknown'}
                      </Badge>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <p className="text-xs text-muted-foreground uppercase font-bold mb-1">Predicted Impact</p>
                        <p className="text-sm text-white/90">
                          {scenarioResult.simulation_result?.predicted_impact || scenarioResult.predicted_impact || 'N/A'}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-muted-foreground uppercase font-bold mb-1">Recommended Preparations</p>
                        <ul className="space-y-1">
                          {(scenarioResult.simulation_result?.recommended_preparations || scenarioResult.recommended_preparations || []).map((prep: string, i: number) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-white/80">
                              <CheckCircle2 className="h-4 w-4 text-green-400 mt-0.5 shrink-0" />
                              {prep}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </motion.div>
                )}

                {scenarioResult?.error && (
                  <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                    <AlertTriangle className="inline h-4 w-4 mr-2" />
                    {scenarioResult.error}
                  </div>
                )}
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => { setScenarioDialogOpen(false); setScenarioResult(null); setScenarioInput(""); }}>
                  Close
                </Button>
                <Button
                  onClick={handleRunSimulation}
                  disabled={scenarioLoading || !scenarioInput.trim()}
                  className="bg-primary text-primary-foreground"
                >
                  {scenarioLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
                  Run Simulation
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Button
            variant="outline"
            className="glass hover:bg-white/5 border-white/10 h-10 px-4"
            onClick={exportReport}
          >
            <Download className="mr-2 h-4 w-4" /> Export Report
          </Button>
          <Button
            onClick={refreshData}
            className="bg-primary hover:bg-primary/80 shadow-[0_0_20px_-5px_oklch(var(--primary))] h-10 px-4 text-primary-foreground font-bold transition-all hover:scale-105"
          >
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
            Refresh Data
          </Button>
        </div>
      </motion.div>

      {/* Top Metrics Row - filtered by role */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {visibleMetrics.map((m, i) => (
          <motion.div key={m.label} variants={item}>
            <MetricCard
              label={m.label}
              value={m.value}
              trend={m.trend}
              trendValue={m.trendValue}
              status={m.status}
              icon={m.icon}
            />
          </motion.div>
        ))}
      </div>

      {/* Charts & Monitor Row */}
      <div className="grid gap-6 md:grid-cols-7 lg:grid-cols-7 h-[650px] min-h-0">
        <motion.div variants={item} className="md:col-span-4 lg:col-span-5 flex flex-col gap-6 h-full min-h-0">
          {/* Show ICU chart for Admin and Physician */}
          {(selectedRole === "admin" || selectedRole === "physician") && (
            <div className="flex-1 min-h-[300px]">
              {loading ? (
                <div className="flex items-center justify-center h-full glass rounded-3xl">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : (
                <ProphetChart
                  title="ICU Occupancy Forecast (Next 12 Hours)"
                  data={icuData}
                  fluentColor="oklch(0.65 0.25 264)"
                />
              )}
            </div>
          )}
          {/* Show ER chart for all roles */}
          <div className="flex-1 min-h-[300px]">
            {loading ? (
              <div className="flex items-center justify-center h-full glass rounded-3xl">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : (
              <ProphetChart
                title="ER Arrival Volume (Next 6 Hours)"
                data={erData}
                fluentColor="oklch(0.75 0.22 150)"
              />
            )}
          </div>
        </motion.div>
        <motion.div variants={item} className="md:col-span-3 lg:col-span-2 h-full min-h-0">
          <AlertFeed />
        </motion.div>
      </div>
    </motion.div>
  )
}

