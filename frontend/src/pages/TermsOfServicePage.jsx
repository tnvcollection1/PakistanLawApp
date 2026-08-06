import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TermsOfServicePage() {
  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
      <Card>
        <CardHeader>
          <CardTitle>Agreement</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm leading-relaxed">
          <p>Welcome to Pakistan Law App. By accessing or using our service, you agree to be bound by these terms.</p>
          <h2 className="text-lg font-semibold mt-4">1. Use of Service</h2>
          <p>This service provides legal information and tools for research purposes. It does not constitute legal advice.</p>
          <h2 className="text-lg font-semibold mt-4">2. User Accounts</h2>
          <p>You are responsible for maintaining the confidentiality of your account credentials.</p>
          <h2 className="text-lg font-semibold mt-4">3. Content</h2>
          <p>All content provided is for informational purposes only. We do not guarantee accuracy or completeness.</p>
          <h2 className="text-lg font-semibold mt-4">4. Limitation of Liability</h2>
          <p>We shall not be liable for any damages arising from the use of this service.</p>
          <h2 className="text-lg font-semibold mt-4">5. Changes</h2>
          <p>We reserve the right to modify these terms at any time. Continued use constitutes acceptance.</p>
        </CardContent>
      </Card>
    </div>
  );
}
