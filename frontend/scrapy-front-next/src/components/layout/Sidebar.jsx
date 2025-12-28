"use client"; 

import { LayoutDashboard, BarChart3, BrainCircuit, Bot, Settings } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const menuItems = [
  { icon: LayoutDashboard, label: "Overview", path: "/" },
  { icon: BarChart3, label: "Market", path: "/market" },
  { icon: BrainCircuit, label: "Sentiment", path: "/sentiment" },
  { icon: Bot, label: "Bot", path: "/bot" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen bg-[#11151c] border-r border-slate-800 flex flex-col fixed left-0 top-0">
      <div className="p-8 font-bold text-2xl text-blue-500 tracking-tighter italic">
        SCRAPY
      </div>

      <nav className="flex-1 px-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = pathname === item.path;
          return (
            <Link
              key={item.path}
              href={item.path}
              className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all ${
                isActive
                  ? "bg-blue-600/10 text-blue-500 border border-blue-600/20"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              <item.icon size={20} />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-6 border-t border-slate-800 text-slate-500 flex gap-2 items-center text-sm cursor-pointer hover:text-slate-300 transition-colors">
        <Settings size={16} />
      </div>
    </aside>
  );
}