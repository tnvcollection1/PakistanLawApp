import React from 'react';
import { Card } from '@/components/ui/card';

const TermsOfServicePage = () => {
  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
      <div className="space-y-6">
        <section>
          <h2 className="text-xl font-semibold mb-3">1. Acceptance of Terms</h2>
          <p className="text-muted-foreground">
            By accessing and using Pakistan Law App, you accept and agree to be bound by the terms
            and provisions of this agreement. If you do not agree to abide by the above, please do
            not use this service.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">2. Use of Service</h2>
          <p className="text-muted-foreground">
            Pakistan Law App provides legal information and research tools for informational purposes
            only. The content on this platform should not be construed as legal advice. Always
            consult with a qualified legal professional for specific legal matters.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">3. User Accounts</h2>
          <p className="text-muted-foreground">
            You are responsible for maintaining the confidentiality of your account and password.
            You agree to accept responsibility for all activities that occur under your account.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">4. Content</h2>
          <p className="text-muted-foreground">
            The legal content provided on this platform is sourced from publicly available court
            decisions and statutes. While we strive for accuracy, we make no representations or
            warranties of any kind about the completeness, accuracy, reliability, or availability
            of the content.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">5. Limitation of Liability</h2>
          <p className="text-muted-foreground">
            Pakistan Law App shall not be liable for any indirect, incidental, special, or
            consequential damages arising out of or in connection with the use of this service.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">6. Changes to Terms</h2>
          <p className="text-muted-foreground">
            We reserve the right to modify these terms at any time. Continued use of the platform
            after any changes constitutes acceptance of the new terms.
          </p>
        </section>
      </div>
    </div>
  );
};

export default TermsOfServicePage;
