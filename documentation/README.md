# ForgeFlow Documentation

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## About ForgeFlow

ForgeFlow is an automation tool that automatically drives AI CLI tools to continuously complete programming tasks within a `tmux` session. It provides robust session management, configurable rule systems, multi-CLI support, reliable input detection, and timeout recovery strategies.

## Installation

```bash
$ npm i
```

## Local Development

```bash
$ npm run start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
$ npm run build
```

This command generates static content into the `build` directory and can be served using any static content hosting service.

## Deployment

Using SSH:

```bash
$ USE_SSH=true npm run deploy
```

Not using SSH:

```bash
$ GIT_USER=<Your GitHub username> npm run deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.

## Documentation Structure

- `/blog` - Contains blog posts about automation experiences
- `/docs` - Contains the documentation content in Markdown format
  - `/tutorial-basics` - Basic tutorials on customizing ForgeFlow
  - `/tutorial-extras` - Advanced customization guides
- `/src` - Contains custom React components and styling
- `/static` - Contains static assets like images
- `docusaurus.config.js` - Main configuration file for the website
- `sidebars.js` - Defines the sidebar navigation structure
- `package.json` - npm package file with build scripts and dependencies
