// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'ForgeFlow',
  tagline: 'Engineering-Grade Automation for AI CLIs Inside Tmux',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://kingson4wu.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/ForgeFlow/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'kingson4wu', // Usually your GitHub org/user name.
  projectName: 'ForgeFlow', // Usually your repo name.

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/kingson4wu/ForgeFlow/edit/main/documentation/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/kingson4wu/ForgeFlow/edit/main/documentation/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'ignore',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      metadata: [
        {name: 'keywords', content: 'ai automation, cli tools, tmux, programming automation, ai cli, terminal automation, development tools, workflow automation, ai integration'},
        {name: 'author', content: 'Kingson Wu'},
        {name: 'robots', content: 'index, follow'},
        {name: 'og:type', content: 'website'},
        {name: 'og:locale', content: 'en_US'},
        {name: 'og:site_name', content: 'ForgeFlow'},
        {name: 'og:title', content: 'ForgeFlow - Engineering-Grade Automation for AI CLIs Inside Tmux'},
        {name: 'og:description', content: 'ForgeFlow automates interactive AI CLI tools (Qwen, Gemini, Claude) inside tmux sessions for continuous programming task execution with configurable rules.'},
        {name: 'og:image', content: 'https://kingson4wu.github.io/ForgeFlow/img/docusaurus-social-card.jpg'},
        {name: 'og:url', content: 'https://kingson4wu.github.io/ForgeFlow/'},
        {name: 'twitter:card', content: 'summary_large_image'},
        {name: 'twitter:site', content: '@kingson4wu'},
        {name: 'twitter:creator', content: '@kingson4wu'},
        {name: 'twitter:title', content: 'ForgeFlow - Engineering-Grade Automation for AI CLIs Inside Tmux'},
        {name: 'twitter:description', content: 'Automate interactive AI CLI tools inside tmux sessions for continuous programming task execution.'},
        {name: 'twitter:image', content: 'https://kingson4wu.github.io/ForgeFlow/img/docusaurus-social-card.jpg'},
      ],
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'ForgeFlow',
        logo: {
          alt: 'ForgeFlow Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {to: '/blog', label: 'Blog', position: 'left'},
          {
            href: 'https://github.com/kingson4wu/ForgeFlow',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Introduction',
                to: '/docs/intro',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub Discussions',
                href: 'https://github.com/kingson4wu/ForgeFlow/discussions',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/kingson4wu/ForgeFlow',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} ForgeFlow. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
