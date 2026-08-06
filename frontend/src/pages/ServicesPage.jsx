import React from "react";
import { Separator } from "@/components/ui/separator";

export default function ServicesPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Our Services</h1>
      <p className="text-muted-foreground mb-6">
        PakistanLaw offers a range of services for legal professionals and researchers.
      </p>
      <Separator className="my-6" />
      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-lg border p-4">
          <h2 className="text-xl font-semibold mb-2">Case Search</h2>
          <p className="text-muted-foreground">
            Search through thousands of cases from Pakistani courts with advanced filters and AI-powered relevance ranking.
          </p>
        </div>
        <div className="rounded-lg border p-4">
          <h2 className="text-xl font-semibold mb-2">Statute Explorer</h2>
          <p className="text-muted-foreground">
            Browse and search statutes from the Pakistan Code with section-level detail and cross-references.
          </p>
        </div>
        <div className="rounded-lg border p-4">
          <h2 className="text-xl font-semibold mb-2">AI Summaries</h2>
          <p className="text-muted-foreground">
            Get AI-generated summaries of cases to quickly understand key points and legal principles.
          </p>
        </div>
      </div>
    </div>
  );
}
