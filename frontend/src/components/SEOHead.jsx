import React from 'react';
import { Helmet } from 'react-helmet-async';

export default function SEOHead({ title, description }) {
  return (
    <Helmet>
      <title>{title ? `${title} | PakistanLaw` : 'PakistanLaw'}</title>
      <meta name="description" content={description || 'PakistanLaw - Legal research platform'} />
    </Helmet>
  );
}
