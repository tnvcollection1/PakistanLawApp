import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">About PakistanLaw</h1>
      <p className="text-muted-foreground mb-6">
        PakistanLaw is a comprehensive legal research platform providing access to case law, statutes, and legal analysis for Pakistan's legal system.
      </p>
      <Separator className="my-6" />
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <h2 className="text-xl font-semibold mb-2">Our Mission</h2>
          <p className="text-muted-foreground">
            To make legal research accessible, efficient, and comprehensive for legal professionals, students, and researchers in Pakistan.
          </p>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">Coverage</h2>
          <p className="text-muted-foreground">
            We cover Supreme Court decisions, High Court judgments, statutes from the Pakistan Code, and legal articles.
          </p>
        </div>
      </div>
      <Separator className="my-6" />
      <div className="flex gap-4">
        <Link to="/contact">
          <Button>Contact Us</Button>
        </Link>
        <Link to="/feedback">
          <Button variant="outline">Feedback</Button>
        </Link>
      </div>
    </div>
  );
}
