"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api-client";

interface DashboardData {
  users: { total: number; pending: number };
  sounds: { total: number; cached: number };
  scraper: {
    last_run: string;
    success: boolean;
    sounds_fetched: number;
  } | null;
  cache: { total_size_gb: number; file_count: number } | null;
}

export default function AdminDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    apiGet<DashboardData>("/api/admin/dashboard").then((res) => {
      if (res.data) setData(res.data);
    });
  }, []);

  async function triggerRefresh() {
    await apiPost("/api/admin/scraper/refresh", {});
    alert("Trending refresh triggered");
  }

  if (!data)
    return (
      <div className="text-text-secondary text-center py-12">Loading...</div>
    );

  return (
    <main className="max-w-4xl mx-auto px-4 py-6 lg:ml-64">
      <h1 className="text-2xl font-bold text-text mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-surface p-4 rounded-lg">
          <p className="text-text-secondary text-sm">Total Users</p>
          <p className="text-text text-2xl font-bold">{data.users.total}</p>
        </div>
        <div className="bg-surface p-4 rounded-lg">
          <p className="text-text-secondary text-sm">Pending</p>
          <p className="text-warning text-2xl font-bold">
            {data.users.pending}
          </p>
        </div>
        <div className="bg-surface p-4 rounded-lg">
          <p className="text-text-secondary text-sm">Total Sounds</p>
          <p className="text-text text-2xl font-bold">{data.sounds.total}</p>
        </div>
        <div className="bg-surface p-4 rounded-lg">
          <p className="text-text-secondary text-sm">Cached</p>
          <p className="text-success text-2xl font-bold">
            {data.sounds.cached}
          </p>
        </div>
      </div>

      <div className="flex gap-4">
        <button
          onClick={triggerRefresh}
          className="px-4 py-2 bg-primary text-bg rounded-lg hover:opacity-90"
        >
          Refresh Trending
        </button>
      </div>
    </main>
  );
}
