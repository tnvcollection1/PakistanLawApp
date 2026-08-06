import React from "react";
import { Separator } from "@/components/ui/separator";

export default function PrivacyPolicyPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Privacy Policy</h1>
      <p className="text-muted-foreground mb-6">
        Last updated: January 2024
      </p>
      <Separator className="my-6" />
      <div className="space-y-6 max-w-3xl">
        <section>
          <h2 className="text-xl font-semibold mb-2">1. Information We Collect</h2>
          <p className="text-muted-foreground">
            We collect information you provide directly to us, including your email address, name, and any search queries you make on our platform.
          </p>
        </section>
        <section>
          <h2 className="text-xl font-semibold mb-2">2. How We Use Information</h2>
          <p className="text-muted-foreground">
            We use the information to provide and improve our services, personalize your experience, and communicate with you about updates and features.
          </p>
        </section>
        <section>
          <h2 className="text-xl font-semibold mb-2">3. Data Security</h2>
          <p className="text-muted-foreground">
            We implement appropriate security measures to protect your personal information from unauthorized access or disclosure.
          </p>
        </section>
        <section>
          <h2 className="text-xl font-semibold mb-2">4. Contact Us</h2>
          <p className="text-muted-foreground">
            If you have any questions about this Privacy Policy, please contact us at privacy@pakistanlaw.pk.
          </p>
        </section>
      </div>
    </div>
  );
}
