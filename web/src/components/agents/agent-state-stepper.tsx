import { Check, Loader2, Eye, Brain, FileSearch, ShieldCheck } from "lucide-react"

interface AgentStateProps {
    currentStep: number // 0: Monitor, 1: Retrieval, 2: Planning, 3: Guardrail, 4: Complete
}

export function AgentStateStepper({ currentStep }: AgentStateProps) {
    const steps = [
        { label: "Monitor", icon: Eye },
        { label: "Retrieval", icon: FileSearch },
        { label: "Planning", icon: Brain },
        { label: "Guardrail", icon: ShieldCheck },
    ]

    return (
        <div className="w-full py-6">
            <div className="relative flex items-center justify-between px-4">
                {/* Connector Line */}
                <div className="absolute top-1/2 left-0 w-full -translate-y-1/2 px-8">
                    <div className="h-[2px] w-full bg-secondary/50 overflow-hidden rounded-full">
                        <div
                            className="h-full bg-primary/50 transition-all duration-700 ease-in-out shadow-[0_0_10px_oklch(var(--primary))]"
                            style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
                        />
                    </div>
                </div>

                {steps.map((step, index) => {
                    const isActive = index === currentStep
                    const isCompleted = index < currentStep
                    const Icon = step.icon

                    let circleClass = "bg-card border-muted-foreground/30 text-muted-foreground"
                    if (isActive) circleClass = "bg-primary/20 border-primary text-primary shadow-[0_0_15px_oklch(var(--primary)/0.6)] scale-110"
                    if (isCompleted) circleClass = "bg-chart-2/20 border-chart-2 text-chart-2 shadow-[0_0_10px_oklch(var(--chart-2)/0.4)]"

                    return (
                        <div key={step.label} className="relative z-10 flex flex-col items-center gap-3">
                            <div className={`flex h-12 w-12 items-center justify-center rounded-full border-2 transition-all duration-500 ${circleClass}`}>
                                {isActive ? (
                                    <Loader2 className="h-6 w-6 animate-spin" />
                                ) : isCompleted ? (
                                    <Check className="h-6 w-6" />
                                ) : (
                                    <Icon className="h-5 w-5" />
                                )}
                            </div>
                            <span className={`text-xs font-bold uppercase tracking-wider transition-colors duration-300 ${isActive ? "text-primary text-glow" : isCompleted ? "text-chart-2" : "text-muted-foreground"}`}>
                                {step.label}
                            </span>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
