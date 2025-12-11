import React from 'react';
import {useLocation} from '@docusaurus/router';
import {useBaseUrlUtils} from '@docusaurus/useBaseUrl';
import {useSiteMetadata} from '@docusaurus/useSiteMetadata';

// Enhanced Head component with additional SEO tags
export default function Head(props) {
  const {pathname} = useLocation();
  const {withBaseUrl} = useBaseUrlUtils();
  const siteMetadata = useSiteMetadata();
  
  const {
    title: siteTitle,
    description: siteDescription,
    image: defaultImage,
    url: siteUrl,
    baseUrl,
  } = siteMetadata;

  // Get page-specific metadata
  const metaTitle = props.title || siteTitle;
  const metaDescription = props.description || siteDescription;
  const metaImage = props.image || defaultImage;
  
  // Create image URL if it's relative
  const imageUrl = metaImage && !metaImage.startsWith('http')
    ? withBaseUrl(metaImage)
    : metaImage;

  // Create canonical URL
  const canonicalUrl = pathname ? `${siteUrl}${pathname}` : siteUrl;

  // Generate keywords from title and description
  const generateKeywords = (title, description) => {
    const combined = `${title || ''} ${description || ''}`.toLowerCase();
    const words = combined.split(/[ ,.!?;:()\-]+/).filter(Boolean);
    const uniqueWords = [...new Set(words)];
    const filteredWords = uniqueWords
      .filter(word => word.length > 2)
      .slice(0, 20)
      .join(', ');
    return filteredWords || 'ai automation, cli tools, tmux, programming automation';
  };

  const keywords = generateKeywords(metaTitle, metaDescription);

  return (
    <React.Fragment>
      {/* Standard SEO Meta Tags */}
      <title>{metaTitle}</title>
      <meta name="description" content={metaDescription} />
      <meta name="keywords" content={keywords} />
      <meta name="author" content="Kingson Wu" />
      <meta name="robots" content="index, follow" />
      <link rel="canonical" href={canonicalUrl} />

      {/* Open Graph Meta Tags */}
      <meta property="og:title" content={metaTitle} />
      <meta property="og:description" content={metaDescription} />
      <meta property="og:type" content="website" />
      <meta property="og:url" content={canonicalUrl} />
      {imageUrl && <meta property="og:image" content={imageUrl} />}
      <meta property="og:site_name" content={siteTitle} />
      <meta property="og:locale" content="en_US" />

      {/* Twitter Card Meta Tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={metaTitle} />
      <meta name="twitter:description" content={metaDescription} />
      {imageUrl && <meta name="twitter:image" content={imageUrl} />}
      <meta name="twitter:site" content="@kingson4wu" />
      <meta name="twitter:creator" content="@kingson4wu" />

      {/* Additional SEO Tags */}
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <meta name="theme-color" content="#2e8555" />
    </React.Fragment>
  );
}