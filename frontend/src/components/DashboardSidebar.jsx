import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Home, Search, BookOpen, Settings, User } from "lucide-react";

export default function DashboardSidebar() {
  return (
    <div className="w-64 border-r bg-background h-screen p-4 flex flex-col">
      <div className="mb-6">
        <h2 className="text-lg font-bold">Dashboard</h2>
      </div>
      <nav className="space-y-2 flex-1">
        <Link to="/dashboard">
          <Button variant="ghost" className="w-full justify-start">
            <Home className="mr-2 h-4 w-4" />
            Home
          </Button>
        </Link>
        <Link to="/search">
          <Button variant="ghost" className="w-full justify-start">
            <Search className="mr-2 h-4 w-4" />
            Search
          </Button>
        </Link>
        <Link to="/statutes">
          <Button variant="ghost" className="w-full justify-start">
            <BookOpen className="mr-2 h-4 w-4" />
            Statutes
          </Button>
        </Link>
        <Separator className="my-2" />
        <Link to="/profile">
          <Button variant="ghost" className="w-full justify-start">
            <User className="mr-2 h-4 w-4" />
            Profile
          </Button>
        </Link>
        <Link to="/settings">
          <Button variant="ghost" className="w-full justify-start">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
        </Link>
      </nav>
    </div>
  );
}
