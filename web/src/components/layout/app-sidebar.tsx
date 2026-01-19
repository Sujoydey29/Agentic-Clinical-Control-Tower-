import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarRail,
    SidebarFooter,
} from "@/components/ui/sidebar"
import { LayoutDashboard, Users, Brain, Book, Settings, Sparkles, Activity } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

// Menu items.
const items = [
    {
        title: "Control Tower",
        url: "/",
        icon: LayoutDashboard,
    },
    {
        title: "Patient List",
        url: "/patients",
        icon: Users,
    },
    {
        title: "Agent Hub",
        url: "/agents",
        icon: Brain,
    },
    {
        title: "Knowledge Base",
        url: "/knowledge",
        icon: Book,
    },
]

export function AppSidebar() {
    return (
        <Sidebar className="border-r-0 bg-transparent transition-all duration-300" collapsible="icon">
            <div className="absolute inset-0 bg-sidebar/80 backdrop-blur-3xl border-r border-white/5 z-0" />
            <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent pointer-events-none z-0" />

            <SidebarHeader className="z-10 relative pt-8 pb-4 group-data-[collapsible=icon]:py-4 group-data-[collapsible=icon]:items-center">
                <div className="flex items-center gap-4 px-2 transition-all group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:gap-0 overflow-hidden w-full">
                    <div className="relative flex h-11 w-11 group-data-[collapsible=icon]:h-9 group-data-[collapsible=icon]:w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-blue-600 text-primary-foreground font-bold shadow-[0_0_25px_oklch(var(--primary)/0.6)] ring-1 ring-white/20 z-20 group-hover:scale-105 transition-all duration-300">
                        <Activity className="h-7 w-7 group-data-[collapsible=icon]:h-6 group-data-[collapsible=icon]:w-6 animate-pulse-slow" />
                        <div className="absolute inset-0 rounded-xl ring-2 ring-white/10 animate-pulse-glow" />
                    </div>
                    <div className="flex flex-col group-data-[collapsible=icon]:hidden transition-all duration-300 opacity-100 group-data-[collapsible=icon]:opacity-0 group-data-[collapsible=icon]:w-0 group-data-[collapsible=icon]:overflow-hidden whitespace-nowrap">
                        <span className="font-extrabold text-2xl tracking-tighter text-foreground text-glow leading-none filter drop-shadow-lg">
                            ACCT
                        </span>
                        <span className="text-[10px] font-mono text-primary font-bold tracking-[0.2em] uppercase mt-0.5 ml-0.5">
                            Cosmic OS
                        </span>
                    </div>
                </div>
            </SidebarHeader>

            <SidebarContent className="z-10 relative px-3 py-4">
                <SidebarGroup>
                    <SidebarGroupLabel className="text-muted-foreground/60 tracking-widest text-[10px] uppercase font-bold mb-4 px-2 group-data-[collapsible=icon]:hidden animate-in fade-in slide-in-from-left-4 duration-500 delay-150">Operations Center</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu className="space-y-2">
                            {items.map((item) => (
                                <SidebarMenuItem key={item.title}>
                                    <SidebarMenuButton
                                        asChild
                                        tooltip={item.title}
                                        className="h-14 transition-all duration-300 hover:bg-white/10 hover:pl-5 data-[state=open]:bg-sidebar-accent group relative overflow-hidden rounded-xl border border-transparent hover:border-primary/30 hover:shadow-[0_0_15px_-5px_oklch(var(--primary)/0.3)]"
                                    >
                                        <a href={item.url} className="flex items-center gap-4">
                                            <div className="relative z-10 p-1 shrink-0">
                                                <item.icon className="h-5 w-5 group-hover:text-primary group-hover:scale-110 transition-all duration-300" />
                                            </div>
                                            <span className="font-semibold text-base group-hover:text-white transition-all duration-300 relative z-10 group-data-[collapsible=icon]:hidden whitespace-nowrap overflow-hidden text-ellipsis">{item.title}</span>

                                            {/* Hover Glow & Neon Bar */}
                                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary opacity-0 group-hover:opacity-100 transition-all duration-300 -translate-x-full group-hover:translate-x-0" />
                                            <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 z-0" />
                                        </a>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>

            <SidebarFooter className="z-10 relative pb-6 px-3 group-data-[collapsible=icon]:px-1">
                <div className="glass-card rounded-2xl p-4 group-data-[collapsible=icon]:p-2 border border-white/5 hover:border-primary/30 transition-all duration-500 hover:shadow-[0_0_30px_-5px_oklch(var(--primary)/0.4)] group cursor-pointer relative overflow-hidden bg-black/20">
                    {/* Animated background sheen - Holographic Effect */}
                    <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-primary/10 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-[1.5s] ease-in-out" />

                    <div className="flex items-center gap-3 relative z-10 justify-between group-data-[collapsible=icon]:justify-center">
                        <div className="relative shrink-0 flex justify-center group-data-[collapsible=icon]:w-full">
                            <Avatar className="h-10 w-10 border-2 border-white/10 shadow-lg group-hover:border-primary transition-colors duration-300 group-hover:scale-105">
                                <AvatarFallback className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white font-bold">DS</AvatarFallback>
                            </Avatar>
                            <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-green-500 border-2 border-black shadow-[0_0_10px_oklch(0.6_0.2_150)] animate-pulse group-data-[collapsible=icon]:right-1" />
                        </div>

                        <div className="flex flex-col text-left group-data-[collapsible=icon]:hidden transition-all overflow-hidden whitespace-nowrap min-w-0 flex-1">
                            <span className="font-bold text-sm text-foreground group-hover:text-glow transition-all truncate">Dr. Sujoy</span>
                            <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium group-hover:text-primary transition-colors truncate">Chief Medical Officer</span>
                        </div>

                        <Settings className="shrink-0 h-4 w-4 text-muted-foreground/50 group-data-[collapsible=icon]:hidden group-hover:text-primary group-hover:rotate-180 transition-all duration-700" />
                    </div>
                </div>
            </SidebarFooter>
            <SidebarRail />
        </Sidebar>
    )
}
