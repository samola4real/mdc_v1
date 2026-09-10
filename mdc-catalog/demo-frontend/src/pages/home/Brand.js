import React, { useRef, useState } from 'react';
import { Toast } from 'primereact/toast';

/* ------------------------------------------------------------------
   Source of truth for the MaaSAI brand identity.
   Edit this file when the design system changes.
   ------------------------------------------------------------------ */

const BRAND_COLORS = [
    {
        hex: '#223F61',
        name: 'Brand Navy',
        role: 'Primary brand colour',
        usage: 'Headers, primary surfaces, sidebars, key UI accents.'
    },
    {
        hex: '#E78C3A',
        name: 'Brand Orange',
        role: 'Primary accent',
        usage: 'CTAs, highlights, key actions, focus rings.'
    },
    {
        hex: '#D8D1BE',
        name: 'Warm Sand',
        role: 'Secondary surface',
        usage: 'Section dividers, neutral cards, supportive backgrounds.'
    },
    {
        hex: '#F3F2EE',
        name: 'Off-White',
        role: 'Background',
        usage: 'Page background, large neutral areas.'
    },
    {
        hex: '#262626',
        name: 'Ink',
        role: 'Typography & icons',
        usage: 'Body copy, headings, line icons on light surfaces.'
    }
];

/**
 * Picks black or white text for a given hex background using the relative
 * luminance formula (Rec. 709). Threshold tuned so mid-tone brand colours
 * like #E78C3A get dark text (better WCAG contrast) and dark navies get
 * white. Robust to any new colour added to BRAND_COLORS.
 */
const getContrastText = (hex) => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const luma = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
    return luma > 0.55
        ? { text: '#262626', subtle: 'rgba(38, 38, 38, 0.66)' }
        : { text: '#FFFFFF', subtle: 'rgba(255, 255, 255, 0.78)' };
};

const TYPE_WEIGHTS = [
    { weight: 300, label: 'Light · 300' },
    { weight: 400, label: 'Regular · 400' },
    { weight: 500, label: 'Medium · 500' },
    { weight: 600, label: 'Semibold · 600' },
    { weight: 700, label: 'Bold · 700' },
    { weight: 800, label: 'Extrabold · 800' }
];

/* ------------------------------------------------------------------ */

const cssSnippet = `:root {
  --brand-navy:   #223F61;
  --brand-orange: #E78C3A;
  --brand-sand:   #D8D1BE;
  --brand-bg:     #F3F2EE;
  --brand-ink:    #262626;
}`;

const scssSnippet = `$brand-navy:   #223F61;
$brand-orange: #E78C3A;
$brand-sand:   #D8D1BE;
$brand-bg:     #F3F2EE;
$brand-ink:    #262626;`;

const tailwindSnippet = `// tailwind.config.js
theme: {
  extend: {
    colors: {
      'brand-navy':   '#223F61',
      'brand-orange': '#E78C3A',
      'brand-sand':   '#D8D1BE',
      'brand-bg':     '#F3F2EE',
      'brand-ink':    '#262626'
    }
  }
}`;

/* ------------------------------------------------------------------ */

const ColorSwatch = ({ color, onCopy }) => {
    const { text: textColor, subtle: subtleText } = getContrastText(color.hex);

    return (
        <button
            type="button"
            className="brand-swatch"
            onClick={() => onCopy(color.hex)}
            style={{ background: color.hex, color: textColor }}
            aria-label={`Copy ${color.hex} ${color.name}`}
        >
            <div className="brand-swatch__head">
                <span className="brand-swatch__hex">{color.hex}</span>
                <span className="brand-swatch__copy" aria-hidden="true" style={{ color: subtleText }}>
                    <svg viewBox="0 0 24 24" width="18" height="18">
                        <rect x="9" y="9" width="10" height="10" rx="2" fill="none" stroke="currentColor" strokeWidth="1.6" />
                        <path d="M15 9V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"
                              fill="none" stroke="currentColor" strokeWidth="1.6" />
                    </svg>
                </span>
            </div>
            <div className="brand-swatch__body">
                <strong>{color.name}</strong>
                <span className="brand-swatch__role" style={{ color: subtleText }}>{color.role}</span>
                <span className="brand-swatch__usage" style={{ color: subtleText }}>{color.usage}</span>
            </div>
        </button>
    );
};

const CodeBlock = ({ label, code, onCopy }) => (
    <div className="brand-code">
        <div className="brand-code__head">
            <span>{label}</span>
            <button type="button" className="brand-code__copy" onClick={() => onCopy(code, label)}>
                <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
                    <rect x="9" y="9" width="10" height="10" rx="2" fill="none" stroke="currentColor" strokeWidth="1.6" />
                    <path d="M15 9V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"
                          fill="none" stroke="currentColor" strokeWidth="1.6" />
                </svg>
                <span>Copy</span>
            </button>
        </div>
        <pre><code>{code}</code></pre>
    </div>
);

/* ------------------------------------------------------------------ */

const Brand = () => {
    const toast = useRef(null);
    const [copiedHex, setCopiedHex] = useState('');

    const copyValue = async (value, label) => {
        try {
            await navigator.clipboard.writeText(value);
            setCopiedHex(value);
            toast.current?.show({
                severity: 'success',
                summary: 'Copied',
                detail: label ? `${label} copied to clipboard` : `${value} copied to clipboard`,
                life: 1800
            });
            setTimeout(() => setCopiedHex(''), 1800);
        } catch (error) {
            console.error('Brand: clipboard error', error);
            toast.current?.show({
                severity: 'error',
                summary: 'Clipboard error',
                detail: 'Your browser blocked clipboard access.',
                life: 2400
            });
        }
    };

    return (
        <div className="brand-page">
            <Toast ref={toast} position="top-right" />

            <header className="brand-hero">
                <div className="brand-hero__copy">
                    <span className="brand-hero__eyebrow">MaaSAI · Brand &amp; Identity</span>
                    <h1>Design system reference</h1>
                    <p>
                        Official colour palette and typography for every MaaSAI subsystem. Click any
                        swatch or code block to copy. Keep these values consistent across dashboards,
                        HMIs, reports and slide decks.
                    </p>
                </div>
                <div className="brand-hero__chip" aria-hidden="true">
                    <span style={{ background: '#223F61' }} />
                    <span style={{ background: '#E78C3A' }} />
                    <span style={{ background: '#D8D1BE' }} />
                    <span style={{ background: '#F3F2EE', border: '1px solid #E5E5E5' }} />
                    <span style={{ background: '#262626' }} />
                </div>
            </header>

            <section className="brand-section">
                <div className="brand-section__head">
                    <h2>Brand Colours</h2>
                    <span className="brand-section__hint">Click a swatch to copy its hex value</span>
                </div>
                <div className="brand-grid">
                    {BRAND_COLORS.map((color) => (
                        <ColorSwatch
                            key={color.hex}
                            color={{ ...color, copied: copiedHex === color.hex }}
                            onCopy={(hex) => copyValue(hex, color.name)}
                        />
                    ))}
                </div>
            </section>

            <section className="brand-section">
                <div className="brand-section__head">
                    <h2>Typography</h2>
                    <span className="brand-section__hint">Outfit · Google Fonts</span>
                </div>
                <div className="brand-type">
                    <div className="brand-type__sample">
                        <span className="brand-type__meta">Display · 64 / 80</span>
                        <div className="brand-type__display">The quick brown fox</div>
                        <span className="brand-type__meta">Body · 18 / 28</span>
                        <p className="brand-type__body">
                            The quick brown fox jumps over the lazy dog. La rápida zorra parda salta
                            sobre el perro perezoso.
                        </p>
                    </div>
                    <div className="brand-type__weights">
                        {TYPE_WEIGHTS.map((row) => (
                            <div key={row.weight} className="brand-type__row" style={{ fontWeight: row.weight }}>
                                <span className="brand-type__row-label">{row.label}</span>
                                <span className="brand-type__row-sample">Aa Bb Cc 0123 — MaaSAI</span>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <section className="brand-section">
                <div className="brand-section__head">
                    <h2>Usage snippets</h2>
                    <span className="brand-section__hint">Drop these into your project</span>
                </div>
                <div className="brand-snippets">
                    <CodeBlock label="CSS variables" code={cssSnippet} onCopy={copyValue} />
                    <CodeBlock label="SCSS" code={scssSnippet} onCopy={copyValue} />
                    <CodeBlock label="Tailwind" code={tailwindSnippet} onCopy={copyValue} />
                </div>
            </section>

        </div>
    );
};

export default Brand;
