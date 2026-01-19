"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { PageTransition } from "@/components/layout/page-transition"
import { motion, AnimatePresence } from "framer-motion"
import {
    Bot, Play, Loader2, CheckCircle2, XCircle, AlertCircle,
    BookOpen, ShieldCheck, MessageSquare, Activity, Check, X,
    Edit, ChevronRight, FileText, AlertTriangle, ArrowRight, XSquare, Clock,
    ThumbsUp, ThumbsDown, History
} from "lucide-react"
import { runAgentWorkflow, getAgentsStatus, listAgents, WorkflowResult, submitFeedback, getAuditTrail } from "@/lib/api"
import { cn } from "@/lib/utils"

// --- Types ---
interface Agent {
    name: string;
    type: string;
    role: string;
    description: string;
}

interface AgentStatus {
    status: string;
    llm: { model: string; available: boolean; };
    active_workflows: number;
}

const AGENT_STEPS = [
    { key: "monitor", label: "Monitor", icon: Activity, description: "Risk Detection" },
    { key: "retrieval", label: "Retrieval", icon: BookOpen, description: "Context Fetching" },
    { key: "planning", label: "Planning", icon: Bot, description: "Action Generation" },
    { key: "guardrail", label: "Guardrail", icon: ShieldCheck, description: "Safety Validation" },
]

export default function AgentsPage() {
    // --- State ---
    const [agents, setAgents] = useState<Agent[]>([])
    const [status, setStatus] = useState<AgentStatus | null>(null)
    const [loadingData, setLoadingData] = useState(true)

    // Workflow State
    const [isRunning, setIsRunning] = useState(false)
    const [currentStepIndex, setCurrentStepIndex] = useState(-1) // -1: idle, 0-3: steps
    const [workflowResult, setWorkflowResult] = useState<WorkflowResult | null>(null)
    const [approvalStatus, setApprovalStatus] = useState<"pending" | "approved" | "rejected">("pending")
    const [selectedRole, setSelectedRole] = useState<"nurse" | "physician" | "admin">("nurse")

    // Evaluation State (Part 8)
    const [feedbackSubmitted, setFeedbackSubmitted] = useState<string | null>(null)
    const [auditTrail, setAuditTrail] = useState<any>(null)
    const [loadingAudit, setLoadingAudit] = useState(false)

    // --- Effects ---
    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try
        {
            setLoadingData(true)
            const [agentsRes, statusRes] = await Promise.all([listAgents(), getAgentsStatus()])
            setAgents(agentsRes.agents || [])
            setStatus(statusRes)
        } catch (e)
        {
            console.error(e)
        } finally
        {
            setLoadingData(false)
        }
    }

    // --- Handlers ---
    const handleRunWorkflow = async () => {
        setIsRunning(true)
        setWorkflowResult(null)
        setApprovalStatus("pending")
        setCurrentStepIndex(0)

        // Simulate step progression for visual effect
        // Real app would use websockets or polling for granular updates
        let step = 0
        const interval = setInterval(() => {
            step++
            if (step <= 3)
            {
                setCurrentStepIndex(step)
            } else
            {
                clearInterval(interval)
            }
        }, 1500) // 1.5s per step

        try
        {
            const result = await runAgentWorkflow("auto", selectedRole)

            // Wait for animation to catch up if API is too fast
            setTimeout(() => {
                clearInterval(interval)
                setCurrentStepIndex(3) // Ensure we are at guardrail
                setWorkflowResult(result)
                setIsRunning(false)
            }, 6000) // Ensure at least 6s total animation

        } catch (err)
        {
            console.error(err)
            setIsRunning(false)
            clearInterval(interval)
        }
    }

    const handleApprove = () => {
        setApprovalStatus("approved")
        // logic to call approve API would go here
    }

    const handleReject = () => {
        setApprovalStatus("rejected")
        // logic to call reject API would go here
    }

    const handleReset = () => {
        setWorkflowResult(null)
        setCurrentStepIndex(-1)
        setApprovalStatus("pending")
        setFeedbackSubmitted(null)
        setAuditTrail(null)
    }

    // Feedback Handler (Part 8)
    const handleFeedback = async (type: "thumbs_up" | "thumbs_down") => {
        if (!workflowResult?.workflow_id) return
        try
        {
            await submitFeedback(workflowResult.workflow_id, type, undefined, selectedRole)
            setFeedbackSubmitted(type)
        } catch (err)
        {
            console.error("Failed to submit feedback:", err)
        }
    }

    // Audit Trail Handler (Part 8)
    const handleViewAudit = async () => {
        if (!workflowResult?.workflow_id) return
        setLoadingAudit(true)
        try
        {
            const trail = await getAuditTrail(workflowResult.workflow_id)
            setAuditTrail(trail)
        } catch (err)
        {
            console.error("Failed to get audit trail:", err)
            setAuditTrail({ error: "Could not load audit trail" })
        } finally
        {
            setLoadingAudit(false)
        }
    }

    // --- Render Helpers ---
    const getStepState = (index: number) => {
        if (currentStepIndex > index) return "completed"
        if (currentStepIndex === index) return "active"
        return "waiting"
    }

    return (
        <PageTransition>
            <div className="w-full p-4 md:p-6 space-y-8">

                {/* Header Section */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-1"
                    >
                        <h1 className="text-4xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400 filter drop-shadow-lg">
                            Agentic Workflow Hub
                        </h1>
                        <p className="text-muted-foreground text-lg">
                            Orchestrate autonomous AI agents for clinical operations
                        </p>
                    </motion.div>

                    {/* Status Indicators */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-3 bg-card/30 backdrop-blur-md p-2 rounded-xl border border-white/5"
                    >
                        <Badge variant="outline" className="h-8 bg-emerald-500/10 text-emerald-400 border-emerald-500/20 gap-2">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            {status?.status === "operational" ? "System Online" : "Connecting..."}
                        </Badge>
                        <Badge variant="outline" className="h-8 bg-blue-500/10 text-blue-400 border-blue-500/20 gap-2">
                            <Bot className="w-4 h-4" />
                            {loadingData ? "..." : agents.length} Agents Active
                        </Badge>
                    </motion.div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                    {/* LEFT COLUMN: Main Workflow Area (8 cols) */}
                    <div className="lg:col-span-8 space-y-6">

                        {/* 1. Workflow Trigger Card */}
                        <AnimatePresence mode="wait">
                            {!workflowResult && !isRunning ? (
                                <motion.div
                                    key="trigger"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                >
                                    <TriggerCard
                                        selectedRole={selectedRole}
                                        setSelectedRole={setSelectedRole}
                                        onRun={handleRunWorkflow}
                                    />
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="workflow"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ type: "spring", bounce: 0.3 }}
                                >
                                    <WorkflowExecutionCard
                                        currentStepIndex={currentStepIndex}
                                        result={workflowResult}
                                        approvalStatus={approvalStatus}
                                        onApprove={handleApprove}
                                        onReject={handleReject}
                                        onReset={handleReset}
                                        feedbackSubmitted={feedbackSubmitted}
                                        handleFeedback={handleFeedback}
                                        auditTrail={auditTrail}
                                        loadingAudit={loadingAudit}
                                        handleViewAudit={handleViewAudit}
                                    />
                                </motion.div>
                            )}
                        </AnimatePresence>

                    </div>


                    {/* RIGHT COLUMN: Sidebar (4 cols) */}
                    <div className="lg:col-span-4 space-y-6">

                        {/* Agent Stats / Mini List */}
                        <Card className="bg-card/20 backdrop-blur-sm border-white/10">
                            <CardHeader>
                                <CardTitle className="text-lg flex items-center gap-2">
                                    <Activity className="w-5 h-5 text-primary" />
                                    Active Swarm
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="grid gap-3">
                                {loadingData ? (
                                    <div className="flex justify-center p-4"><Loader2 className="animate-spin text-muted-foreground" /></div>
                                ) : (
                                    agents.map((agent, i) => (
                                        <motion.div
                                            key={agent.type}
                                            initial={{ opacity: 0, x: 20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: i * 0.1 }}
                                            className="group flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 transition-all"
                                        >
                                            <div className={cn("p-2 rounded-md", getAgentColorBg(agent.type))}>
                                                {getAgentIcon(agent.type)}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="font-medium text-sm truncate">{agent.name}</div>
                                                <div className="text-xs text-muted-foreground truncate">{agent.role}</div>
                                            </div>
                                            <div className="w-2 h-2 rounded-full bg-green-500/50 group-hover:bg-green-400 transition-colors" />
                                        </motion.div>
                                    ))
                                )}
                            </CardContent>
                        </Card>

                        {/* Recent Activity / Logs Placeholder */}
                        <Card className="bg-card/20 backdrop-blur-sm border-white/10 h-[300px] flex flex-col">
                            <CardHeader>
                                <CardTitle className="text-lg flex items-center gap-2">
                                    <FileText className="w-5 h-5 text-muted-foreground" />
                                    System Logs
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="flex-1 overflow-hidden relative">
                                <div className="absolute inset-0 p-6 flex flex-col items-center justify-center text-center text-muted-foreground opacity-50">
                                    <Clock className="w-8 h-8 mb-2" />
                                    <p className="text-sm">Waiting for workflow events...</p>
                                </div>
                            </CardContent>
                        </Card>

                    </div>
                </div>

            </div>
        </PageTransition>
    )
}

// --- Sub-Components ---

function TriggerCard({ selectedRole, setSelectedRole, onRun }: any) {
    return (
        <Card className="border-primary/20 bg-gradient-to-br from-card to-primary/5 overflow-hidden relative group">
            <div className="absolute inset-0 bg-grid-white/5 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] -z-10" />

            <CardHeader>
                <CardTitle className="text-2xl flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-primary/20 text-primary">
                        <Play className="w-6 h-6 fill-current" />
                    </div>
                    Start New Workflow
                </CardTitle>
                <CardDescription className="text-lg">
                    Initialize the autonomous agent swarm to analyze current hospital state and generate optimization plans.
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
                <div className="space-y-2">
                    <label className="text-sm font-medium text-muted-foreground">Target Role for Action Plan</label>
                    <div className="flex gap-2">
                        {['nurse', 'physician', 'admin'].map((role) => (
                            <button
                                key={role}
                                onClick={() => setSelectedRole(role)}
                                className={cn(
                                    "px-4 py-2 rounded-lg border text-sm font-medium capitalize transition-all",
                                    selectedRole === role
                                        ? "bg-primary text-primary-foreground border-primary shadow-lg shadow-primary/25"
                                        : "bg-card border-white/10 hover:border-white/20 hover:bg-white/5"
                                )}
                            >
                                {role}
                            </button>
                        ))}
                    </div>
                </div>
            </CardContent>

            <CardFooter className="pt-2">
                <Button size="lg" onClick={onRun} className="w-full md:w-auto gap-2 bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90 shadow-xl shadow-primary/20">
                    <Activity className="w-4 h-4 animate-pulse" />
                    Run Risk Analysis Workflow
                    <ArrowRight className="w-4 h-4 ml-1 opacity-70" />
                </Button>
            </CardFooter>
        </Card>
    )
}

function WorkflowExecutionCard({ currentStepIndex, result, approvalStatus, onApprove, onReject, onReset, feedbackSubmitted, handleFeedback, auditTrail, loadingAudit, handleViewAudit }: any) {
    // If we have a result, we assume the basics are there.
    const steps = AGENT_STEPS
    const isFinished = currentStepIndex >= steps.length - 1 && result

    return (
        <Card className="border-white/10 bg-black/40 backdrop-blur-xl overflow-hidden shadow-2xl">
            {/* Header / Stepper Area */}
            <div className="bg-white/5 border-b border-white/5 p-6 md:p-8">
                <div className="flex justify-between items-center mb-8">
                    <div className="flex items-center gap-3">
                        <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="font-mono text-sm text-green-400 tracking-wider">WORKFLOW ACTIVE</span>
                    </div>
                    {/* Workflow ID */}
                    {result && (
                        <Badge variant="outline" className="font-mono text-xs text-muted-foreground border-white/10">
                            ID: {result.workflow_id?.substring(0, 8)}...
                        </Badge>
                    )}
                </div>

                {/* Stepper with Arrows */}
                <div className="relative flex justify-between items-center">

                    {/* Continuous Line Background */}
                    <div className="absolute top-1/2 left-0 w-full h-[2px] bg-white/5 -translate-y-1/2 z-0" />

                    {steps.map((step, idx) => {
                        // Custom logic for Guardrail (last step)
                        let state = 'waiting'
                        let dotColor = 'border-white/10 bg-black'
                        let iconColor = 'text-muted-foreground'

                        if (idx < currentStepIndex)
                        {
                            state = 'completed'
                            dotColor = 'border-primary bg-primary text-primary-foreground'
                            iconColor = 'text-white'
                        } else if (idx === currentStepIndex)
                        {
                            state = 'active'
                            dotColor = 'border-primary bg-black shadow-[0_0_20px_rgba(59,130,246,0.5)]'
                            iconColor = 'text-primary'
                        }

                        // Special Guardrail Logic
                        if (step.key === 'guardrail')
                        {
                            if (approvalStatus === 'approved')
                            {
                                state = 'completed'
                                dotColor = 'border-emerald-500 bg-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.5)]'
                                iconColor = 'text-white'
                            } else if (approvalStatus === 'rejected')
                            {
                                state = 'rejected'
                                dotColor = 'border-red-500 bg-red-500 shadow-[0_0_20px_rgba(239,68,68,0.5)]'
                                iconColor = 'text-white'
                            } else if (isFinished)
                            {
                                // Wait state
                                state = 'active'
                                dotColor = 'border-primary bg-black shadow-[0_0_20px_rgba(59,130,246,0.5)]'
                                iconColor = 'text-primary'
                            }
                        }

                        const Icon = step.icon

                        return (
                            <div key={step.key} className="relative z-10 flex flex-col items-center flex-1">
                                {idx < steps.length - 1 && (
                                    <div className="absolute top-1/2 left-[50%] w-full h-[2px] -translate-y-1/2 z-[-1]">
                                        <div className={cn(
                                            "h-full w-full transition-all duration-700 ease-out origin-left",
                                            idx < currentStepIndex ? "bg-primary scale-x-100" : "bg-white/5 scale-x-0"
                                        )} />
                                        {/* Arrow Head */}
                                        {idx === currentStepIndex - 1 && (
                                            <motion.div
                                                initial={{ opacity: 0, x: -10 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 text-primary"
                                            >
                                                <ChevronRight className="w-4 h-4" />
                                            </motion.div>
                                        )}
                                    </div>
                                )}

                                <motion.div
                                    initial={false}
                                    animate={{
                                        scale: state === 'active' ? 1.15 : 1,
                                    }}
                                    className={cn(
                                        "w-12 h-12 rounded-full border-2 flex items-center justify-center transition-all duration-300",
                                        dotColor
                                    )}
                                >
                                    {state === 'completed' ? (
                                        <Check className="w-6 h-6 text-white" />
                                    ) : state === 'rejected' ? (
                                        <X className="w-6 h-6 text-white" />
                                    ) : state === 'active' ? (
                                        step.key === 'guardrail' && isFinished ? (
                                            <Loader2 className="w-6 h-6 animate-spin text-primary" />
                                        ) : (
                                            <Loader2 className="w-6 h-6 animate-spin text-primary" />
                                        )
                                    ) : (
                                        <Icon className={cn("w-5 h-5", iconColor)} />
                                    )}
                                </motion.div>

                                <div className="mt-4 text-center">
                                    <div className={cn("text-sm font-bold transition-colors", state !== 'waiting' ? "text-white" : "text-muted-foreground")}>
                                        {step.label}
                                    </div>
                                    <div className="text-[10px] text-muted-foreground hidden md:block">{step.description}</div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            </div>

            {/* Content Area */}
            <div className="p-6 md:p-8 min-h-[600px] flex flex-col">
                {!result ? (
                    <div className="flex flex-col items-center justify-center h-full text-muted-foreground space-y-4 py-20">
                        <Loader2 className="w-12 h-12 animate-spin text-primary/50" />
                        <p className="text-lg">Agents are processing clinical data...</p>
                        <div className="flex gap-2 text-xs">
                            <Badge variant="secondary" className="animate-pulse">Retrieving RAG Context</Badge>
                            <Badge variant="secondary" className="animate-pulse delay-150">Validating Policies</Badge>
                        </div>
                    </div>
                ) : !result.action_card ? (
                    /* No risks detected - show success state */
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex flex-col items-center justify-center h-full py-16 text-center"
                    >
                        <div className="w-20 h-20 rounded-full bg-emerald-500/10 border-2 border-emerald-500/30 flex items-center justify-center mb-6">
                            <CheckCircle2 className="w-10 h-10 text-emerald-400" />
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-2">All Clear ✓</h3>
                        <p className="text-muted-foreground max-w-md">
                            {result.final_output?.message || "No risk events detected in the current monitoring window. All systems operating normally."}
                        </p>
                        <div className="mt-6 flex gap-2">
                            <Badge variant="outline" className="bg-emerald-500/10 border-emerald-500/20 text-emerald-400">
                                Monitor Agent: No Alerts
                            </Badge>
                        </div>
                        <Button variant="outline" className="mt-8 border-white/10 hover:bg-white/5" onClick={onReset}>
                            Start New Analysis
                        </Button>
                    </motion.div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        {/* Risk detected banner */}
                        {result.risk_event && (
                            <div className="rounded-xl bg-orange-500/10 border border-orange-500/20 p-4 flex items-start gap-4">
                                <div className="p-2 bg-orange-500/20 rounded-lg text-orange-500 mt-1">
                                    <AlertTriangle className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="text-orange-400 font-bold flex items-center gap-2">
                                        Risk Detected: {result.risk_event.event_type}
                                        <Badge className="bg-orange-500 text-white border-none text-[10px]">HIGH SEVERITY</Badge>
                                    </h3>
                                    <p className="text-muted-foreground text-sm mt-1">
                                        {result.risk_event.description}
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* Title & Sources */}
                        <div>
                            <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                                {result.action_card?.title}
                            </h2>
                            <div className="flex flex-wrap gap-2 mt-3">
                                {result.action_card?.cited_sources?.map((src: any, i: number) => (
                                    <Badge key={i} variant="outline" className="bg-blue-500/5 border-blue-500/20 text-blue-300 text-xs gap-1">
                                        <BookOpen className="w-3 h-3" />
                                        {typeof src === 'object' ? src.source_title : src}
                                    </Badge>
                                ))}
                            </div>
                        </div>

                        {/* 2-Col Layout for Plan & Context */}
                        <div className="grid md:grid-cols-2 gap-6">

                            {/* Left: Reasoning & Context */}
                            <div className="space-y-4">
                                <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2">
                                    <h4 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Agent Reasoning</h4>
                                    <p className="text-sm leading-relaxed text-gray-300">
                                        {result.action_card?.reasoning}
                                    </p>
                                </div>
                            </div>

                            {/* Right: The Plan */}
                            <div className="space-y-4">
                                <h4 className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                                    <FileText className="w-4 h-4" /> Proposed Action Plan
                                </h4>
                                <div className="space-y-3">
                                    {result.action_card?.steps?.map((step: string, i: number) => (
                                        <div key={i} className="flex gap-3 items-start group">
                                            <div className="mt-1 w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center shrink-0 border border-primary/20 group-hover:border-primary/50 transition-colors">
                                                <span className="text-[10px] text-primary font-bold">{i + 1}</span>
                                            </div>
                                            <p className="text-sm text-gray-200 group-hover:text-white transition-colors pt-0.5">
                                                {step}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Approval Actions */}
                        <Separator className="bg-white/10" />

                        {approvalStatus === "pending" ? (
                            <div className="flex items-center justify-between p-2">
                                <p className="text-sm text-muted-foreground italic">
                                    Review the AI-generated plan before execution.
                                </p>
                                <div className="flex gap-4">
                                    <Button variant="ghost" className="text-muted-foreground hover:text-white hover:bg-white/5" onClick={onReject}>
                                        Dismiss
                                    </Button>
                                    <Button variant="destructive" className="gap-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20" onClick={onReject}>
                                        <XCircle className="w-4 h-4" />
                                        Reject Plan
                                    </Button>
                                    <Button className="gap-2 bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg shadow-emerald-500/20" onClick={onApprove}>
                                        <CheckCircle2 className="w-4 h-4" />
                                        Approve & Execute
                                    </Button>
                                </div>
                            </div>
                        ) : (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: "auto" }}
                                className={cn(
                                    "rounded-xl p-6 text-center border",
                                    approvalStatus === "approved"
                                        ? "bg-emerald-500/10 border-emerald-500/30"
                                        : "bg-red-500/10 border-red-500/30"
                                )}
                            >
                                {approvalStatus === "approved" ? (
                                    <div className="space-y-3">
                                        <div className="w-12 h-12 rounded-full bg-emerald-500 mx-auto flex items-center justify-center shadow-lg shadow-emerald-500/50">
                                            <Check className="w-6 h-6 text-white" />
                                        </div>
                                        <h3 className="text-xl font-bold text-white">Action Plan Approved</h3>
                                        <p className="text-emerald-200/70 text-sm max-w-lg mx-auto">
                                            Optimized workflow has been dispatched to the {result?.final_output?.role || 'target'} role.
                                            Notifier agent successfully delivered the message.
                                        </p>

                                        {/* Feedback Buttons (Part 8) */}
                                        <div className="mt-4 pt-4 border-t border-emerald-500/20">
                                            <p className="text-xs text-muted-foreground mb-2">Was this recommendation helpful?</p>
                                            <div className="flex justify-center gap-3">
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    className={cn("gap-2 border-white/10", feedbackSubmitted === "thumbs_up" && "bg-emerald-500/20 border-emerald-500/50 text-emerald-400")}
                                                    onClick={() => handleFeedback("thumbs_up")}
                                                    disabled={!!feedbackSubmitted}
                                                >
                                                    <ThumbsUp className="w-4 h-4" />
                                                    {feedbackSubmitted === "thumbs_up" ? "Thanks!" : "Helpful"}
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    className={cn("gap-2 border-white/10", feedbackSubmitted === "thumbs_down" && "bg-red-500/20 border-red-500/50 text-red-400")}
                                                    onClick={() => handleFeedback("thumbs_down")}
                                                    disabled={!!feedbackSubmitted}
                                                >
                                                    <ThumbsDown className="w-4 h-4" />
                                                    {feedbackSubmitted === "thumbs_down" ? "Noted" : "Not Helpful"}
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    className="gap-2 border-white/10"
                                                    onClick={handleViewAudit}
                                                    disabled={loadingAudit}
                                                >
                                                    {loadingAudit ? <Loader2 className="w-4 h-4 animate-spin" /> : <History className="w-4 h-4" />}
                                                    View Audit Trail
                                                </Button>
                                            </div>
                                            {/* Audit Trail Display */}
                                            {auditTrail && !auditTrail.error && (
                                                <div className="mt-4 text-left bg-black/30 rounded-lg p-4 max-h-48 overflow-y-auto">
                                                    <h5 className="text-xs font-bold text-muted-foreground mb-2">Decision History</h5>
                                                    <div className="space-y-2 text-xs">
                                                        <div className="flex gap-2">
                                                            <span className="text-muted-foreground">Workflow:</span>
                                                            <span className="text-white font-mono">{auditTrail.workflow_id?.substring(0, 12)}...</span>
                                                        </div>
                                                        <div className="flex gap-2">
                                                            <span className="text-muted-foreground">Status:</span>
                                                            <span className="text-emerald-400">{auditTrail.status}</span>
                                                        </div>
                                                        <Separator className="bg-white/10 my-2" />
                                                        <span className="text-muted-foreground font-bold">Agent Timeline:</span>
                                                        <ul className="space-y-1 mt-1">
                                                            {auditTrail.timeline?.map((entry: any, i: number) => (
                                                                <li key={i} className="flex gap-2 items-start">
                                                                    <span className="text-primary">→</span>
                                                                    <span className="text-white capitalize">{typeof entry === 'object' ? entry.agent : entry}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        <div className="w-12 h-12 rounded-full bg-red-500 mx-auto flex items-center justify-center shadow-lg shadow-red-500/50">
                                            <X className="w-6 h-6 text-white" />
                                        </div>
                                        <h3 className="text-xl font-bold text-white">Action Plan Rejected</h3>
                                        <p className="text-red-200/70 text-sm">
                                            The workflow has been terminated. No actions were taken.
                                        </p>
                                    </div>
                                )}

                                <Button variant="outline" className="mt-6 border-white/10 hover:bg-white/5" onClick={onReset}>
                                    Start New Workflow
                                </Button>
                            </motion.div>
                        )}

                    </motion.div>
                )}
            </div>
        </Card>
    )
}

// --- Utils ---

function getAgentIcon(type: string) {
    if (type === "monitor") return <Activity className="w-4 h-4 text-yellow-400" />
    if (type === "retrieval") return <BookOpen className="w-4 h-4 text-blue-400" />
    if (type === "planning") return <Bot className="w-4 h-4 text-purple-400" />
    if (type === "guardrail") return <ShieldCheck className="w-4 h-4 text-emerald-400" />
    return <Bot className="w-4 h-4 text-primary" />
}

function getAgentColorBg(type: string) {
    if (type === "monitor") return "bg-yellow-500/10"
    if (type === "retrieval") return "bg-blue-500/10"
    if (type === "planning") return "bg-purple-500/10"
    if (type === "guardrail") return "bg-emerald-500/10"
    return "bg-primary/10"
}
