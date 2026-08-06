import React from "react";
import { Separator } from "@/components/ui/separator";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

export default function HelpPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Help Center</h1>
      <p className="text-muted-foreground mb-6">
        Find answers to common questions about using PakistanLaw.
      </p>
      <Separator className="my-6" />
      <Accordion type="single" collapsible className="max-w-2xl">
        <AccordionItem value="item-1">
          <AccordionTrigger>How do I search for cases?</AccordionTrigger>
          <AccordionContent>
            Use the search bar at the top of the page. Enter keywords, case citations, or party names. You can also use filters to narrow results by court, year, or case type.
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-2">
          <AccordionTrigger>What courts are covered?</AccordionTrigger>
          <AccordionContent>
            We cover the Supreme Court of Pakistan, all High Courts (Lahore, Sindh, Islamabad, Peshawar, Balochistan), and selected District Court decisions.
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-3">
          <AccordionTrigger>How do I cite a case?</AccordionTrigger>
          <AccordionContent>
            Each case has a standard citation format displayed at the top of the case page. You can copy this citation directly for your legal documents.
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-4">
          <AccordionTrigger>Is the data up to date?</AccordionTrigger>
          <AccordionContent>
            We update our database regularly. New cases are typically added within 48-72 hours of publication on official court websites.
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
