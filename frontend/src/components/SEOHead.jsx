import React from 'react';
import { Helmet } from 'react-helmet-async';

const SEOHead = ({
  title = 'Pakistan Law App',
  description = 'Search Pakistan case law and statutes',
  keywords = 'pakistan law, case law, statutes, legal search',
  canonical,
  ogImage = '/og-image.png',
}) => {
  const siteTitle = title === 'Pakistan Law App' ? title : `${title} | Pakistan Law App`;
  
  return (
    <Helmet>
      <title>{siteTitle}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      
      {canonical && <link rel="canonical" href={canonical} />}
      
      {/* Open Graph */}
      <meta property="og:title" content={siteTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:type" content="website" />
      {canonical && <meta property="og:url" content={canonical} />}
      {ogImage && <meta property="og:image" content={ogImage} />}
      
      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={siteTitle} />
      <meta name="twitter:description" content={description} />
      {ogImage && <meta name="twitter:image" content={ogImage} />}
      
      {/* Robots */}
      <meta name="robots" content="index, follow" />
    </Helmet>
  );
};

export default SEOHead;
