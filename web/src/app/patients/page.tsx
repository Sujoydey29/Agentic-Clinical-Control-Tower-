"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { RiskBadge } from "@/components/patients/risk-badge"
import { Activity, Heart, ChevronRight, Loader2 } from "lucide-react"
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet"
import { ResponsiveContainer, LineChart, Line } from "recharts"
import { getPatients, Patient } from "@/lib/api"

const container = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
}

const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
}

function VitalsSparkline({ data, dataKey, color, label, value, unit }: { data: any[], dataKey: string, color: string, label: string, value: string | number, unit: string }) {
    return (
        <div className="glass-card p-3 rounded-xl border border-white/5 flex flex-col gap-2">
            <div className="flex justify-between items-end">
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold">{label}</span>
                <span className={`text-lg font-bold ${color === "#ef4444" ? "text-red-400 text-glow" : "text-foreground"}`}>
                    {value} <span className="text-[10px] text-muted-foreground font-normal">{unit}</span>
                </span>
            </div>
            <div className="h-12 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                        <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} strokeOpacity={0.8} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

export default function PatientsPage() {
    const [patients, setPatients] = useState<Patient[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        async function loadPatients() {
            try
            {
                setLoading(true)
                const data = await getPatients(50)
                setPatients(data)
            } catch (err)
            {
                setError("Failed to load patients. Is the backend running?")
                console.error(err)
            } finally
            {
                setLoading(false)
            }
        }
        loadPatients()
    }, [])

    if (loading)
    {
        return (
            <div className="flex items-center justify-center h-full">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <span className="ml-2 text-muted-foreground">Loading patients from backend...</span>
            </div>
        )
    }

    if (error)
    {
        return (
            <div className="flex flex-col items-center justify-center h-full gap-4">
                <div className="text-red-400 text-xl">⚠️ {error}</div>
                <p className="text-muted-foreground">Make sure the backend is running on http://localhost:8000</p>
            </div>
        )
    }

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="flex flex-col gap-8 h-full p-2 w-full max-w-[1800px] mx-auto"
        >
            <motion.div variants={item} className="flex flex-col gap-2">
                <h2 className="text-4xl font-extrabold tracking-tight text-glow bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-400 to-purple-500 w-fit">
                    Patient Monitor
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl">
                    Real-time tracking of {patients.length} patients from MIMIC-IV dataset with AI-driven risk stratification.
                </p>
            </motion.div>

            <motion.div variants={item} className="flex-1 overflow-hidden rounded-3xl glass border border-white/10 shadow-2xl relative">
                <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent pointer-events-none" />
                <ScrollArea className="h-full">
                    <div className="p-1">
                        <Table>
                            <TableHeader className="bg-white/5 sticky top-0 backdrop-blur-md z-10">
                                <TableRow className="border-white/10 hover:bg-transparent">
                                    <TableHead className="font-bold text-primary uppercase tracking-wider text-xs w-[120px]">ID</TableHead>
                                    <TableHead className="font-bold text-primary uppercase tracking-wider text-xs">Patient</TableHead>
                                    <TableHead className="font-bold text-primary uppercase tracking-wider text-xs">Diagnosis</TableHead>
                                    <TableHead className="font-bold text-primary uppercase tracking-wider text-xs">Unit</TableHead>
                                    <TableHead className="font-bold text-primary uppercase tracking-wider text-xs">Risk Score</TableHead>
                                    <TableHead className="font-bold text-primary uppercase tracking-wider text-xs text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {patients.map((patient) => (
                                    <Sheet key={patient.demographics.patient_id}>
                                        <SheetTrigger asChild>
                                            <motion.tr
                                                variants={item}
                                                className="group border-b border-white/5 transition-all duration-300 hover:bg-white/5 cursor-pointer"
                                            >
                                                <TableCell className="font-mono text-muted-foreground group-hover:text-primary transition-colors">{patient.demographics.patient_id}</TableCell>
                                                <TableCell>
                                                    <div className="flex flex-col">
                                                        <span className="text-lg font-bold group-hover:text-glow transition-all">{patient.demographics.name}</span>
                                                        <span className="text-xs text-muted-foreground">{patient.demographics.age} yrs • {patient.demographics.gender}</span>
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <Badge variant="outline" className="border-white/10 bg-white/5 hover:bg-white/10 hover:border-primary/50 transition-all">
                                                        {patient.clinical.diagnosis_text || "N/A"}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className="font-medium text-foreground/80">{patient.demographics.unit}</TableCell>
                                                <TableCell>
                                                    <RiskBadge score={Math.round(patient.risk_scores.escalation_risk)} />
                                                </TableCell>
                                                <TableCell className="text-right">
                                                    <button className="p-2 rounded-full hover:bg-primary/20 hover:text-primary transition-all">
                                                        <ChevronRight className="h-5 w-5" />
                                                    </button>
                                                </TableCell>
                                            </motion.tr>
                                        </SheetTrigger>

                                        {/* Patient Detail Sheet */}
                                        <SheetContent className="w-[400px] sm:w-[540px] border-l border-white/10 bg-black/80 backdrop-blur-xl p-0 shadow-[0_0_50px_oklch(var(--primary)/0.2)]">
                                            <div className="h-full flex flex-col">
                                                {/* Header */}
                                                <div className="p-6 border-b border-white/10 relative overflow-hidden">
                                                    <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent pointer-events-none" />
                                                    <SheetHeader className="relative z-10 text-left">
                                                        <div className="flex justify-between items-start">
                                                            <div>
                                                                <SheetTitle className="text-3xl font-extrabold text-glow text-white tracking-tight">{patient.demographics.name}</SheetTitle>
                                                                <SheetDescription className="text-primary font-mono text-xs uppercase tracking-widest mt-1">
                                                                    ID: {patient.demographics.patient_id} • {patient.demographics.unit}
                                                                </SheetDescription>
                                                            </div>
                                                            <RiskBadge score={Math.round(patient.risk_scores.escalation_risk)} />
                                                        </div>
                                                    </SheetHeader>
                                                </div>

                                                <ScrollArea className="flex-1 p-6">
                                                    <div className="flex flex-col gap-6">
                                                        {/* Diagnosis Card */}
                                                        <div className="glass-card p-4 rounded-xl border-l-4 border-l-primary flex items-start gap-4">
                                                            <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                                                                <Activity className="h-5 w-5 text-primary" />
                                                            </div>
                                                            <div>
                                                                <h4 className="font-bold text-white">Primary Diagnosis</h4>
                                                                <p className="text-muted-foreground text-sm mt-1">{patient.clinical.diagnosis_text || "No diagnosis available"}</p>
                                                                <p className="text-xs text-muted-foreground mt-2">
                                                                    Admitted: {new Date(patient.demographics.admission_date).toLocaleDateString()} • Expected LOS: {patient.risk_scores.expected_los_days.toFixed(1)} days
                                                                </p>
                                                            </div>
                                                        </div>

                                                        {/* Risk Scores */}
                                                        <div className="space-y-3">
                                                            <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                                                                <Activity className="h-4 w-4" /> Risk Scores (ML)
                                                            </h3>
                                                            <div className="grid grid-cols-2 gap-3">
                                                                <div className="glass-card p-3 rounded-xl">
                                                                    <span className="text-xs text-muted-foreground">Escalation Risk</span>
                                                                    <div className="text-2xl font-bold text-red-400">{patient.risk_scores.escalation_risk.toFixed(0)}%</div>
                                                                </div>
                                                                <div className="glass-card p-3 rounded-xl">
                                                                    <span className="text-xs text-muted-foreground">Readmission (30d)</span>
                                                                    <div className="text-2xl font-bold text-yellow-400">{patient.risk_scores.readmission_risk_30d.toFixed(0)}%</div>
                                                                </div>
                                                                <div className="glass-card p-3 rounded-xl">
                                                                    <span className="text-xs text-muted-foreground">Discharge Ready</span>
                                                                    <div className="text-2xl font-bold text-green-400">{patient.risk_scores.discharge_readiness.toFixed(0)}%</div>
                                                                </div>
                                                                <div className="glass-card p-3 rounded-xl">
                                                                    <span className="text-xs text-muted-foreground">Expected LOS</span>
                                                                    <div className="text-2xl font-bold">{patient.risk_scores.expected_los_days.toFixed(1)} days</div>
                                                                </div>
                                                            </div>
                                                        </div>

                                                        {/* Status Badge */}
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-sm font-bold uppercase tracking-widest text-muted-foreground">Status:</span>
                                                            <Badge variant={patient.status === "Critical" ? "destructive" : patient.status === "Watch" ? "secondary" : "outline"}>
                                                                {patient.status}
                                                            </Badge>
                                                        </div>

                                                        {/* Live Vitals from API */}
                                                        <div className="space-y-3">
                                                            <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                                                                <Heart className="h-4 w-4" /> Live Vitals (Real-time)
                                                            </h3>
                                                            <div className="grid grid-cols-2 gap-3">
                                                                <VitalsSparkline
                                                                    label="Heart Rate"
                                                                    value={patient.clinical.current_vitals.heart_rate.toFixed(0)}
                                                                    unit="bpm"
                                                                    color="#ef4444"
                                                                    data={patient.clinical.vitals_history.slice(-20).map((v, i) => ({ time: i, hr: v.heart_rate }))}
                                                                    dataKey="hr"
                                                                />
                                                                <VitalsSparkline
                                                                    label="SpO2"
                                                                    value={patient.clinical.current_vitals.spo2.toFixed(0)}
                                                                    unit="%"
                                                                    color="#22c55e"
                                                                    data={patient.clinical.vitals_history.slice(-20).map((v, i) => ({ time: i, spo2: v.spo2 }))}
                                                                    dataKey="spo2"
                                                                />
                                                                <VitalsSparkline
                                                                    label="BP (Sys)"
                                                                    value={patient.clinical.current_vitals.blood_pressure_systolic.toFixed(0)}
                                                                    unit="mmHg"
                                                                    color="#f59e0b"
                                                                    data={patient.clinical.vitals_history.slice(-20).map((v, i) => ({ time: i, bp: v.blood_pressure_systolic }))}
                                                                    dataKey="bp"
                                                                />
                                                                <VitalsSparkline
                                                                    label="Resp Rate"
                                                                    value={patient.clinical.current_vitals.respiratory_rate.toFixed(0)}
                                                                    unit="/min"
                                                                    color="#3b82f6"
                                                                    data={patient.clinical.vitals_history.slice(-20).map((v, i) => ({ time: i, rr: v.respiratory_rate }))}
                                                                    dataKey="rr"
                                                                />
                                                            </div>
                                                        </div>
                                                    </div>
                                                </ScrollArea>
                                            </div>
                                        </SheetContent>
                                    </Sheet>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </ScrollArea>
            </motion.div>
        </motion.div>
    )
}
