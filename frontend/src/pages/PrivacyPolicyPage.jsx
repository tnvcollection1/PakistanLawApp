import React from 'react';

const PrivacyPolicyPage = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>
      
      <div className="space-y-6 text-gray-700">
        <section>
          <h2 className="text-xl font-semibold mb-2">Information We Collect</h2>
          <p>We collect information you provide directly to us, such as when you create an account, use our services, or contact us.</p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">How We Use Your Information</h2>
          <p>We use the information we collect to provide, maintain, and improve our services, and to communicate with you.</p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">Information Sharing</h2>
          <p>We do not sell your personal information. We may share information with service providers who assist us in operating our platform.</p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">Data Security</h2>
          <p>We implement reasonable security measures to protect your information from unauthorized access and disclosure.</p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">Contact Us</h2>
          <p>If you have any questions about this Privacy Policy, please contact us at privacy@pakistanlawsite.com</p>
        </section>
      </div>
    </div>
  );
};

export default PrivacyPolicyPage;
