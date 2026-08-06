import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { User, ChevronLeft, Mail, Calendar, BookOpen, Edit2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function ProfilePage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/profile");
      setProfile(res.data);
    } catch (err) {
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Profile" onMenuClick={() => setSidebarOpen(true)} />

        <div className="p-6 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <div className="flex items-center gap-4 mb-6">
              <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                <ChevronLeft className="w-5 h-5 text-slate-300" />
              </Button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-sky-500/20 flex items-center justify-center">
                  <User className="w-5 h-5 text-sky-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Profile</h1>
                  <p className="text-slate-400 text-sm">Your account information</p>
                </div>
              </div>
            </div>

            {isLoading ? (
              <div className="rounded-xl bg-slate-800/40 h-64 animate-pulse" />
            ) : profile ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-6 text-center">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                    {profile.name?.charAt(0)?.toUpperCase() || "U"}
                  </div>
                  <h2 className="text-white font-semibold text-lg">{profile.name}</h2>
                  <p className="text-slate-400 text-sm">{profile.role || "User"}</p>
                  <Button variant="outline" size="sm" className="mt-4">
                    <Edit2 className="w-3 h-3 mr-1" /> Edit Profile
                  </Button>
                </div>

                <div className="lg:col-span-2 space-y-4">
                  <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
                    <h3 className="text-white font-semibold mb-4">Account Details</h3>
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <Mail className="w-4 h-4 text-slate-400" />
                        <span className="text-slate-400 text-sm">Email:</span>
                        <span className="text-white text-sm">{profile.email}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        <span className="text-slate-400 text-sm">Joined:</span>
                        <span className="text-white text-sm">{profile.created_at}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <BookOpen className="w-4 h-4 text-slate-400" />
                        <span className="text-slate-400 text-sm">Cases Viewed:</span>
                        <span className="text-white text-sm">{profile.cases_viewed || 0}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-20 text-slate-400">
                <User className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>Profile not found.</p>
              </div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
