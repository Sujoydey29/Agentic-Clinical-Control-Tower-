"use client"

import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Search, FileText, Book, Shield, Sparkles, Brain, Loader2, Activity, Pill, Stethoscope, AlertTriangle, Database } from "lucide-react"
import { PageTransition } from "@/components/layout/page-transition"
import { motion, Variants } from "framer-motion"
import { processNLP, extractEntities, deidentifyText, searchKnowledge, getRAGDocuments, getRAGStats, RAGDocument, RAGStats, RAGSearchResult } from "@/lib/api"

const container: Variants = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
}

const item: Variants = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 }
}

// Sample clinical note for demo
const sampleNote = `Patient: John Smith, MRN: 123456
Date: 01/15/2026
Age: 67 years old

Chief Complaint: Chest pain and shortness of breath

History: The patient presents with acute onset chest pain radiating to the left arm. 
Blood pressure is 140/90 mmHg, heart rate 95 bpm, SpO2 94%.
Patient has history of hypertension and diabetes mellitus type 2.

Current medications include Metformin 500mg, Lisinopril 10mg, and Aspirin 81mg.

Assessment: Possible acute coronary syndrome. 
Plan: Obtain ECG, cardiac enzymes, and admit to CCU for monitoring.
Dr. Sarah Johnson, MD`

export default function KnowledgePage() {
    const [clinicalText, setClinicalText] = useState("")
    const [nlpResult, setNlpResult] = useState<any>(null)
    const [processing, setProcessing] = useState(false)
    const [activeTab, setActiveTab] = useState<"entities" | "deidentify" | "full">("full")

    // RAG state
    const [searchQuery, setSearchQuery] = useState("")
    const [searchResults, setSearchResults] = useState<RAGSearchResult | null>(null)
    const [searching, setSearching] = useState(false)
    const [documents, setDocuments] = useState<RAGDocument[]>([])
    const [stats, setStats] = useState<RAGStats | null>(null)
    const [loadingDocs, setLoadingDocs] = useState(true)

    // Load documents and stats on mount
    useEffect(() => {
        async function loadKnowledgeBase() {
            try
            {
                setLoadingDocs(true)
                const [docsResult, statsResult] = await Promise.all([
                    getRAGDocuments(),
                    getRAGStats()
                ])
                setDocuments(docsResult.documents)
                setStats(statsResult)
            } catch (err)
            {
                console.error("Failed to load knowledge base:", err)
            } finally
            {
                setLoadingDocs(false)
            }
        }
        loadKnowledgeBase()
    }, [])

    const performSearch = async () => {
        if (!searchQuery.trim()) return

        setSearching(true)
        try
        {
            const results = await searchKnowledge(searchQuery, 5)
            setSearchResults(results)
        } catch (err)
        {
            console.error("Search failed:", err)
        } finally
        {
            setSearching(false)
        }
    }

    const processText = async () => {
        if (!clinicalText.trim()) return

        setProcessing(true)
        try
        {
            let result
            if (activeTab === "entities")
            {
                result = await extractEntities(clinicalText)
            } else if (activeTab === "deidentify")
            {
                result = await deidentifyText(clinicalText)
            } else
            {
                result = await processNLP(clinicalText)
            }
            setNlpResult(result)
        } catch (err)
        {
            console.error("NLP processing failed:", err)
            setNlpResult({ error: "Failed to process text. Is the backend running?" })
        } finally
        {
            setProcessing(false)
        }
    }

    const loadSample = () => {
        setClinicalText(sampleNote)
        setNlpResult(null)
    }

    const getEntityIcon = (label: string) => {
        switch (label)
        {
            case "DISEASE": return <AlertTriangle className="h-3 w-3" />
            case "DRUG": return <Pill className="h-3 w-3" />
            case "PROCEDURE": return <Stethoscope className="h-3 w-3" />
            case "VITAL_SIGN": return <Activity className="h-3 w-3" />
            default: return <Brain className="h-3 w-3" />
        }
    }

    const getEntityColor = (label: string) => {
        switch (label)
        {
            case "DISEASE": return "bg-red-500/20 text-red-400 border-red-500/30"
            case "DRUG": return "bg-green-500/20 text-green-400 border-green-500/30"
            case "PROCEDURE": return "bg-blue-500/20 text-blue-400 border-blue-500/30"
            case "VITAL_SIGN": return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
            case "LAB_VALUE": return "bg-purple-500/20 text-purple-400 border-purple-500/30"
            default: return "bg-primary/20 text-primary border-primary/30"
        }
    }

    const getDocTypeColor = (docType: string) => {
        switch (docType)
        {
            case "sop": return "bg-primary/20 text-primary border-primary/30"
            case "guideline": return "bg-green-500/20 text-green-400 border-green-500/30"
            case "policy": return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
            default: return "bg-blue-500/20 text-blue-400 border-blue-500/30"
        }
    }

    return (
        <PageTransition>
            <div className="flex flex-col gap-8 w-full max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex flex-col gap-2">
                    <h2 className="text-4xl font-extrabold tracking-tight text-glow bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-400 to-purple-500">
                        Knowledge Base
                    </h2>
                    <p className="text-lg text-muted-foreground font-medium">Search protocols and process clinical text with NLP.</p>
                </div>

                {/* Search Bar with RAG */}
                <div className="relative group max-w-4xl">
                    <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 via-blue-500/20 to-purple-500/20 rounded-xl blur opacity-25 group-hover:opacity-100 transition duration-1000 group-hover:duration-200" />
                    <div className="relative flex gap-2">
                        <div className="flex-1 relative">
                            <Search className="absolute left-4 top-3.5 h-5 w-5 text-primary" />
                            <Input
                                type="search"
                                placeholder="Search protocols (e.g. 'ICU transfer', 'sepsis treatment')..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && performSearch()}
                                className="pl-12 h-12 bg-black/40 border-white/10 text-lg w-full rounded-xl focus:ring-primary/50 focus:border-primary transition-all shadow-xl backdrop-blur-md"
                            />
                        </div>
                        <Button
                            onClick={performSearch}
                            disabled={searching || !searchQuery.trim()}
                            className="h-12 px-6"
                        >
                            {searching ? <Loader2 className="h-5 w-5 animate-spin" /> : "Search"}
                        </Button>
                    </div>
                </div>

                {/* Search Results */}
                {searchResults && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-4"
                    >
                        <h3 className="font-bold text-lg flex items-center gap-2">
                            <Database className="h-5 w-5 text-primary" />
                            Search Results ({searchResults.total_results})
                        </h3>
                        <div className="grid gap-3">
                            {searchResults.results.map((result, i) => (
                                <Card key={i} className="glass border-primary/20 hover:border-primary/40 transition-colors">
                                    <CardContent className="p-4">
                                        <div className="flex items-start justify-between gap-4">
                                            <div className="flex-1">
                                                <h4 className="font-bold text-base text-primary">{result.doc_title}</h4>
                                                <p className="text-sm text-muted-foreground mt-1 line-clamp-3">{result.content}</p>
                                            </div>
                                            <Badge variant="outline" className="shrink-0">
                                                {(result.score * 100).toFixed(0)}% match
                                            </Badge>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </motion.div>
                )}

                {/* Stats Cards */}
                <motion.div
                    variants={container}
                    initial="hidden"
                    animate="show"
                    className="grid gap-6 md:grid-cols-3"
                >
                    <motion.div variants={item} whileHover={{ scale: 1.03 }} transition={{ type: "spring", stiffness: 300 }}>
                        <Card className="bg-primary/5 border-primary/20 cursor-pointer hover:bg-primary/10 transition-all duration-300 shadow-[0_0_20px_-5px_oklch(var(--primary)/0.3)] relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:rotate-12 transition-transform duration-500 scale-150">
                                <FileText className="h-20 w-20 text-primary" />
                            </div>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
                                <CardTitle className="text-sm font-bold uppercase tracking-wider text-primary">Documents</CardTitle>
                                <FileText className="h-5 w-5 text-primary" />
                            </CardHeader>
                            <CardContent className="relative z-10">
                                <div className="text-4xl font-extrabold text-foreground text-glow">
                                    {loadingDocs ? <Loader2 className="h-8 w-8 animate-spin" /> : stats?.total_documents || 0}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1 font-mono">In Knowledge Base</p>
                            </CardContent>
                        </Card>
                    </motion.div>

                    <motion.div variants={item} whileHover={{ scale: 1.03 }} transition={{ type: "spring", stiffness: 300 }}>
                        <Card className="bg-chart-2/5 border-chart-2/20 cursor-pointer hover:bg-chart-2/10 transition-all duration-300 shadow-[0_0_20px_-5px_oklch(var(--chart-2)/0.3)] relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:rotate-12 transition-transform duration-500 scale-150">
                                <Book className="h-20 w-20 text-chart-2" />
                            </div>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
                                <CardTitle className="text-sm font-bold uppercase tracking-wider text-chart-2">Chunks</CardTitle>
                                <Book className="h-5 w-5 text-chart-2" />
                            </CardHeader>
                            <CardContent className="relative z-10">
                                <div className="text-4xl font-extrabold text-foreground text-glow">
                                    {loadingDocs ? <Loader2 className="h-8 w-8 animate-spin" /> : stats?.total_chunks || 0}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1 font-mono">Embedded Vectors</p>
                            </CardContent>
                        </Card>
                    </motion.div>

                    <motion.div variants={item} whileHover={{ scale: 1.03 }} transition={{ type: "spring", stiffness: 300 }}>
                        <Card className="bg-chart-4/5 border-chart-4/20 cursor-pointer hover:bg-chart-4/10 transition-all duration-300 shadow-[0_0_20px_-5px_oklch(var(--chart-4)/0.3)] relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:rotate-12 transition-transform duration-500 scale-150">
                                <Shield className="h-20 w-20 text-chart-4" />
                            </div>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
                                <CardTitle className="text-sm font-bold uppercase tracking-wider text-chart-4">Model</CardTitle>
                                <Shield className="h-5 w-5 text-chart-4" />
                            </CardHeader>
                            <CardContent className="relative z-10">
                                <div className="text-lg font-bold text-foreground truncate">
                                    {loadingDocs ? <Loader2 className="h-6 w-6 animate-spin" /> : stats?.embedding_model || "N/A"}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1 font-mono">{stats?.embedding_dimension || 0}D Embeddings</p>
                            </CardContent>
                        </Card>
                    </motion.div>
                </motion.div>

                {/* Document List from Backend */}
                <div className="grid gap-4 md:grid-cols-2">
                    <div className="md:col-span-2">
                        <h3 className="font-bold text-lg flex items-center gap-2 mb-2">
                            <Sparkles className="h-4 w-4 text-secondary" />
                            Knowledge Base Documents ({documents.length})
                            {loadingDocs && <Loader2 className="h-4 w-4 animate-spin ml-2" />}
                        </h3>
                    </div>
                    {loadingDocs ? (
                        <div className="md:col-span-2 text-center py-8 text-muted-foreground">
                            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2" />
                            Loading documents...
                        </div>
                    ) : documents.length === 0 ? (
                        <div className="md:col-span-2 text-center py-8 text-muted-foreground">
                            No documents found in knowledge base.
                        </div>
                    ) : (
                        documents.map((doc) => (
                            <div key={doc.doc_id} className="animate-in fade-in duration-300">
                                <Card className="bg-card/50 border-white/10 hover:bg-white/5 cursor-pointer transition-all duration-300 hover:scale-[1.01] hover:shadow-lg group h-full">
                                    <div className="flex items-center p-4 gap-4">
                                        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary/20 to-primary/10 border border-primary/30 flex items-center justify-center shrink-0 group-hover:border-primary/50 transition-colors shadow-inner">
                                            <FileText className="h-6 w-6 text-primary" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <h4 className="font-bold text-base truncate text-white group-hover:text-primary transition-colors">{doc.title || "Untitled"}</h4>
                                            <div className="flex gap-3 text-xs text-muted-foreground mt-1 items-center">
                                                <Badge variant="outline" className={`text-[10px] h-5 ${getDocTypeColor(doc.doc_type || "sop")}`}>
                                                    {(doc.doc_type || "SOP").toUpperCase()}
                                                </Badge>
                                                <span className="h-1 w-1 rounded-full bg-white/20" />
                                                <span className="truncate text-gray-400">{doc.source || "Unknown source"}</span>
                                            </div>
                                        </div>
                                    </div>
                                </Card>
                            </div>
                        ))
                    )}
                </div>

                {/* NLP Text Processor Section */}
                <motion.div variants={container} initial="hidden" animate="show">
                    <Card className="glass border-primary/20 shadow-[0_0_30px_-10px_oklch(var(--primary)/0.3)]">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-primary">
                                <Brain className="h-5 w-5" />
                                Clinical Text Processor (NLP Pipeline)
                            </CardTitle>
                            <CardDescription>
                                Paste clinical notes to extract entities, de-identify PHI, or run the full NLP pipeline.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Tabs */}
                            <div className="flex gap-2">
                                <Button
                                    variant={activeTab === "full" ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => { setActiveTab("full"); setNlpResult(null); }}
                                >
                                    Full Pipeline
                                </Button>
                                <Button
                                    variant={activeTab === "entities" ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => { setActiveTab("entities"); setNlpResult(null); }}
                                >
                                    Extract Entities
                                </Button>
                                <Button
                                    variant={activeTab === "deidentify" ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => { setActiveTab("deidentify"); setNlpResult(null); }}
                                >
                                    De-identify PHI
                                </Button>
                                <div className="flex-1" />
                                <Button variant="ghost" size="sm" onClick={loadSample}>
                                    Load Sample Note
                                </Button>
                            </div>

                            {/* Input */}
                            <Textarea
                                placeholder="Paste clinical note here..."
                                value={clinicalText}
                                onChange={(e) => setClinicalText(e.target.value)}
                                rows={6}
                                className="bg-black/40 border-white/10 font-mono text-sm"
                            />

                            {/* Process Button */}
                            <Button
                                onClick={processText}
                                disabled={processing || !clinicalText.trim()}
                                className="w-full"
                            >
                                {processing ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        <Brain className="mr-2 h-4 w-4" />
                                        Process with NLP
                                    </>
                                )}
                            </Button>

                            {/* Results */}
                            {nlpResult && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="space-y-4"
                                >
                                    {nlpResult.error ? (
                                        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">
                                            {nlpResult.error}
                                        </div>
                                    ) : (
                                        <>
                                            {/* Entities */}
                                            {nlpResult.entities && (
                                                <div className="space-y-2">
                                                    <h4 className="font-bold text-sm uppercase tracking-wider text-muted-foreground">
                                                        Extracted Entities ({nlpResult.entity_count || nlpResult.entities.length})
                                                    </h4>
                                                    <div className="flex flex-wrap gap-2">
                                                        {nlpResult.entities.map((entity: any, i: number) => (
                                                            <Badge
                                                                key={i}
                                                                variant="outline"
                                                                className={`${getEntityColor(entity.label)} flex items-center gap-1`}
                                                            >
                                                                {getEntityIcon(entity.label)}
                                                                {entity.text}
                                                                <span className="text-[10px] opacity-70">({entity.label})</span>
                                                            </Badge>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {/* De-identified Text */}
                                            {nlpResult.deidentified_text && (
                                                <div className="space-y-2">
                                                    <h4 className="font-bold text-sm uppercase tracking-wider text-muted-foreground">
                                                        De-identified Text (PHI Removed: {nlpResult.phi_count})
                                                    </h4>
                                                    <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg font-mono text-sm whitespace-pre-wrap max-h-40 overflow-auto">
                                                        {nlpResult.deidentified_text}
                                                    </div>
                                                </div>
                                            )}

                                            {/* Embedding Ready Text */}
                                            {nlpResult.embedding_ready_text && (
                                                <div className="space-y-2">
                                                    <h4 className="font-bold text-sm uppercase tracking-wider text-muted-foreground">
                                                        Embedding-Ready Text
                                                    </h4>
                                                    <div className="p-3 bg-primary/10 border border-primary/30 rounded-lg font-mono text-sm whitespace-pre-wrap max-h-32 overflow-auto">
                                                        {nlpResult.embedding_ready_text}
                                                    </div>
                                                </div>
                                            )}
                                        </>
                                    )}
                                </motion.div>
                            )}
                        </CardContent>
                    </Card>
                </motion.div>
            </div>
        </PageTransition>
    )
}
