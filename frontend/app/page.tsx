"use client";

import { BarChart3, TrendingUp, Video, Sparkles, Bot, Globe, Shield, Zap, ChevronRight } from "lucide-react";
import { useState } from "react";

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navItems = [
    { icon: BarChart3, label: "Dashboard", href: "#", active: true },
    { icon: TrendingUp, label: "Trends", href: "#" },
    { icon: Video, label: "Videos", href: "#" },
    { icon: Bot, label: "AI Agents", href: "#" },
    { icon: Globe, label: "Channels", href: "#" },
    { icon: Shield, label: "Settings", href: "#" },
  ];

  const stats = [
    { label: "Active Videos", value: "24", change: "+12%", icon: Video, color: "from-blue-500 to-cyan-500" },
    { label: "Trends Tracked", value: "156", change: "+8%", icon: TrendingUp, color: "from-purple-500 to-pink-500" },
    { label: "AI Generations", value: "892", change: "+23%", icon: Bot, color: "from-emerald-500 to-teal-500" },
    { label: "Total Views", value: "45.2K", change: "+18%", icon: BarChart3, color: "from-orange-500 to-red-500" },
  ];

  const recentTrends = [
    { title: "AI Video Agents", score: 95, source: "Google Trends", growth: "+18.4%" },
    { title: "Open Source MCP", score: 87, source: "GitHub", growth: "+14.2%" },
    { title: "Interest Rate Cuts", score: 82, source: "Yahoo Finance", growth: "+9.8%" },
    { title: "Quantum Computing", score: 78, source: "Reddit", growth: "+12.1%" },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-[#0a0a1a]">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300 bg-[#0d0d2b] border-r border-white/5 flex flex-col`}>
        <div className="p-4 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            {sidebarOpen && <span className="font-semibold text-white text-sm">TrendTube AI</span>}
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                item.active
                  ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              }`}
            >
              <item.icon className="w-4 h-4 flex-shrink-0" />
              {sidebarOpen && <span>{item.label}</span>}
            </a>
          ))}
        </nav>
        <div className="p-3 border-t border-white/5">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-xs font-bold text-black">
              JD
            </div>
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate">John Doe</p>
                <p className="text-xs text-gray-400">Pro Plan</p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <header className="sticky top-0 bg-[#0a0a1a]/80 backdrop-blur-xl border-b border-white/5 z-10">
          <div className="flex items-center justify-between px-6 py-4">
            <div>
              <h1 className="text-xl font-semibold text-white">Dashboard</h1>
              <p className="text-sm text-gray-400">Welcome back, John! Here's your AI content factory status.</p>
            </div>
            <button className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors">
              + New Video
            </button>
          </div>
        </header>

        <div className="p-6 space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((stat) => (
              <div key={stat.label} className="glass rounded-xl p-4 card-hover">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-gray-400">{stat.label}</p>
                    <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
                  </div>
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${stat.color} p-2`}>
                    <stat.icon className="w-full h-full text-white" />
                  </div>
                </div>
                <div className="flex items-center gap-1 mt-3">
                  <span className="text-xs text-emerald-400">{stat.change}</span>
                  <span className="text-xs text-gray-400">vs last month</span>
                </div>
              </div>
            ))}
          </div>

          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Trends */}
            <div className="lg:col-span-2 glass rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-white font-semibold">Trending Topics</h2>
                <button className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1">
                  View All <ChevronRight className="w-3 h-3" />
                </button>
              </div>
              <div className="space-y-3">
                {recentTrends.map((trend) => (
                  <div key={trend.title} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                    <div className="flex-1">
                      <p className="text-sm text-white font-medium">{trend.title}</p>
                      <p className="text-xs text-gray-400">{trend.source}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1">
                        <Zap className="w-3 h-3 text-yellow-400" />
                        <span className="text-xs text-yellow-400">{trend.score}</span>
                      </div>
                      <span className="text-xs text-emerald-400">{trend.growth}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Status */}
            <div className="space-y-4">
              <div className="glass rounded-xl p-5">
                <h2 className="text-white font-semibold mb-4">AI Agents Status</h2>
                <div className="space-y-3">
                  {[
                    { name: "Trend Agent", status: "active", time: "2m ago" },
                    { name: "Research Agent", status: "active", time: "5m ago" },
                    { name: "Script Writer", status: "idle", time: "15m ago" },
                    { name: "Video Editor", status: "processing", time: "Now" },
                    { name: "Publisher", status: "idle", time: "1h ago" },
                  ].map((agent) => (
                    <div key={agent.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${
                          agent.status === "active" ? "bg-emerald-400" :
                          agent.status === "processing" ? "bg-blue-400 animate-pulse" :
                          "bg-gray-500"
                        }`} />
                        <span className="text-sm text-gray-300">{agent.name}</span>
                      </div>
                      <span className="text-xs text-gray-500">{agent.time}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="glass rounded-xl p-5">
                <h2 className="text-white font-semibold mb-3">Quick Actions</h2>
                <div className="space-y-2">
                  <button className="w-full px-4 py-2.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm transition-colors">
                    Generate New Video
                  </button>
                  <button className="w-full px-4 py-2.5 bg-white/5 hover:bg-white/10 text-gray-300 rounded-lg text-sm transition-colors">
                    Discover Trends
                  </button>
                  <button className="w-full px-4 py-2.5 bg-white/5 hover:bg-white/10 text-gray-300 rounded-lg text-sm transition-colors">
                    View Analytics
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Activity Feed */}
          <div className="glass rounded-xl p-5">
            <h2 className="text-white font-semibold mb-4">Recent Activity</h2>
            <div className="space-y-3">
              {[
                { action: "Video published", detail: "AI Revolution in 2024", time: "5 minutes ago", icon: Video },
                { action: "Trend discovered", detail: "Quantum Computing Breakthrough", time: "12 minutes ago", icon: TrendingUp },
                { action: "Script generated", detail: "Future of AI Agents", time: "25 minutes ago", icon: Bot },
                { action: "Analytics updated", detail: "Channel performance improved 23%", time: "1 hour ago", icon: BarChart3 },
              ].map((activity, i) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <activity.icon className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-white">{activity.action}</p>
                    <p className="text-xs text-gray-400">{activity.detail}</p>
                  </div>
                  <span className="text-xs text-gray-500">{activity.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

