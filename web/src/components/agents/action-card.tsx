import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Check, X, Edit, FileText, ChevronRight, Sparkles } from "lucide-react"
import { AgentStateStepper } from "./agent-state-stepper"
import { motion } from "framer-motion"

interface ActionCardProps {
    id: string
    title: string
    reasoning: string
    plan: string[]
    sources: string[]
    status: "pending" | "approved" | "rejected" | "processing"
    currentStep: number
}

export function ActionCard({ id, title, reasoning, plan, sources, status, currentStep }: ActionCardProps) {
    const statusBorder = {
        pending: "border-primary/50 hover:border-primary",
        approved: "border-chart-2/50 hover:border-chart-2",
        rejected: "border-chart-5/50 hover:border-chart-5",
        processing: "border-chart-3/50 hover:border-chart-3"
    }

    return (
        <motion.div whileHover={{ scale: 1.01 }} transition={{ type: "spring", stiffness: 400 }}>
            <Card className={`w-full glass border ${statusBorder[status]} transition-colors duration-300 overflow-hidden`}>
                <CardHeader className="bg-white/5 pb-2">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <Badge variant="outline" className="font-mono bg-black/20 text-muted-foreground border-white/10">#{id}</Badge>
                            <CardTitle className="text-xl font-bold tracking-tight text-foreground">{title}</CardTitle>
                        </div>
                        {status === "processing" && <Badge variant="secondary" className="animate-pulse bg-chart-3/20 text-chart-3 border-chart-3/30">Processing</Badge>}
                        {status === "approved" && <Badge className="bg-chart-2/20 text-chart-2 border-chart-2/30 shadow-[0_0_10px_oklch(var(--chart-2)/0.4)]">Approved</Badge>}
                        {status === "pending" && <Badge variant="outline" className="bg-primary/20 text-primary border-primary/30 animate-pulse-slow">Action Required</Badge>}
                    </div>
                    <AgentStateStepper currentStep={currentStep} />
                </CardHeader>

                <CardContent className="space-y-6 pt-6">
                    <div className="rounded-xl bg-gradient-to-br from-primary/5 to-purple-500/5 p-5 border border-white/5 relative group">
                        <div className="absolute top-0 right-0 p-2 opacity-50">
                            <Sparkles className="h-10 w-10 text-primary/20 group-hover:rotate-12 transition-transform duration-700" />
                        </div>
                        <h4 className="flex items-center gap-2 font-bold text-sm mb-3 text-primary uppercase tracking-wider">
                            <BrainIcon className="h-4 w-4" />
                            Agent Reasoning
                        </h4>
                        <p className="text-base text-muted-foreground leading-relaxed">{reasoning}</p>
                    </div>

                    <div>
                        <h4 className="font-bold text-sm mb-3 uppercase tracking-wider text-muted-foreground">Proposed Plan</h4>
                        <div className="space-y-3">
                            {plan.map((step, i) => (
                                <div key={i} className="flex gap-4 items-start p-3 rounded-lg bg-card/50 border border-white/5 hover:bg-card/80 transition-colors">
                                    <div className="mt-0.5 h-5 w-5 rounded-full bg-primary/20 flex items-center justify-center shrink-0 border border-primary/30">
                                        <ChevronRight className="h-3 w-3 text-primary" />
                                    </div>
                                    <span className="text-sm font-medium text-foreground/90">{step}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <Separator className="bg-white/10" />

                    <div>
                        <h4 className="font-bold text-sm mb-3 flex items-center gap-2 text-muted-foreground uppercase tracking-wider">
                            <FileText className="h-3 w-3" />
                            Cited Sources
                        </h4>
                        <div className="flex flex-wrap gap-2">
                            {sources.map((source, i) => (
                                <Badge key={i} variant="secondary" className="cursor-pointer bg-secondary/50 hover:bg-primary/20 hover:text-primary transition-all border-white/5 hover:border-primary/30 py-1.5 px-3">
                                    {source}
                                </Badge>
                            ))}
                        </div>
                    </div>
                </CardContent>

                <CardFooter className="flex justify-between bg-black/20 p-4 border-t border-white/5 backdrop-blur-sm">
                    <Button variant="ghost" size="sm" className="hover:bg-white/5 hover:text-primary">
                        <Edit className="mr-2 h-4 w-4" /> Edit Plan
                    </Button>
                    {status === "pending" && (
                        <div className="flex gap-3">
                            <Button variant="destructive" size="sm" className="shadow-lg shadow-red-900/20 hover:bg-red-600">
                                <X className="mr-2 h-4 w-4" /> Reject
                            </Button>
                            <Button size="sm" className="bg-chart-2 hover:bg-chart-2/90 text-white shadow-[0_0_15px_-3px_oklch(var(--chart-2)/0.6)] font-bold">
                                <Check className="mr-2 h-4 w-4" /> Approve Plan
                            </Button>
                        </div>
                    )}
                </CardFooter>
            </Card>
        </motion.div>
    )
}

function BrainIcon(props: React.SVGProps<SVGSVGElement>) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z" />
            <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z" />
        </svg>
    )
}
