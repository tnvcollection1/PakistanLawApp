import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Filter } from "lucide-react";
import { Separator } from "@/components/ui/separator";

export default function SearchSidebar({ onSearch, filters, onFilterChange }) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <div className="w-80 border-r bg-background p-4 h-[calc(100vh-3.5rem)]">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search..."
            className="pl-8"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <Button type="submit" className="w-full">
          <Search className="mr-2 h-4 w-4" />
          Search
        </Button>
      </form>
      <Separator className="my-4" />
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4" />
          <h3 className="font-semibold">Filters</h3>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Court</label>
          <select
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={filters.court || ""}
            onChange={(e) => onFilterChange({ ...filters, court: e.target.value })}
          >
            <option value="">All Courts</option>
            <option value="Supreme Court">Supreme Court</option>
            <option value="High Court">High Court</option>
            <option value="District Court">District Court</option>
          </select>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Year</label>
          <Input
            type="number"
            placeholder="e.g. 2023"
            value={filters.year || ""}
            onChange={(e) => onFilterChange({ ...filters, year: e.target.value })}
          />
        </div>
      </div>
    </div>
  );
}
