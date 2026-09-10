/** @type {import('next').NextConfig} */
const securityHeaders = [
    { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
    { key: 'X-Content-Type-Options', value: 'nosniff' },
    { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
    { key: 'X-DNS-Prefetch-Control', value: 'on' },
    {
        key: 'Strict-Transport-Security',
        value: 'max-age=63072000; includeSubDomains; preload'
    },
    {
        key: 'Permissions-Policy',
        value: 'camera=(), microphone=(), geolocation=(), payment=()'
    }
];

const nextConfig = {
    // Emit a minimal self-contained server bundle into `.next/standalone`.
    // The Dockerfile copies just that + .next/static + public, shrinking the
    // runtime image by ~80% versus shipping node_modules.
    output: 'standalone',

    // Hide the `X-Powered-By: Next.js` header.
    poweredByHeader: false,

    // SWC minification (default in 13+, kept explicit for clarity).
    swcMinify: true,

    // React Strict Mode catches the double-init bug we hit with Keycloak; keep it on.
    reactStrictMode: true,

    // Tree-shake the heavy PrimeReact bundle and its icon font.
    experimental: {
        optimizePackageImports: ['primereact', 'primeicons', 'primeflex']
    },

    // Optimise images for the factory floor — most assets are local but allow
    // remote logos (organisations in Contact page, etc.). Add domains here as
    // they appear.
    images: {
        formats: ['image/avif', 'image/webp'],
        remotePatterns: [
            // Example — uncomment and customise:
            // { protocol: 'https', hostname: 'cdn.maasai-srv.cigip.upv.es' }
        ]
    },

    async headers() {
        return [
            { source: '/:path*', headers: securityHeaders }
        ];
    }
};

module.exports = nextConfig;
