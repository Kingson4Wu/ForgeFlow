import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Automate AI CLIs',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        ForgeFlow automates interactive AI CLI tools (Qwen, Gemini, Claude) inside tmux sessions,
        continuously driving programming tasks without manual intervention.
      </>
    ),
  },
  {
    title: 'Robust Session Management',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Handles tmux sessions robustly with timeout recovery strategies, automatic session
        creation/reuse, and smart input detection for reliable long-running automation.
      </>
    ),
  },
  {
    title: 'Configurable Rules Engine',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        Project-specific rules allow customization of behavior, supporting complex automation
        workflows with configurable responses based on AI CLI output.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" aria-label={title} />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
