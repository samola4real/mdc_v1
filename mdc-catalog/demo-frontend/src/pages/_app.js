import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { LayoutProvider } from '@/layout/context/layoutcontext';
import { ThemeProvider } from '@/layout/context/ThemeContext';
import Layout from '../layout/layout';
import 'primereact/resources/primereact.css';
import 'primeflex/primeflex.css';
import 'primeicons/primeicons.css';
import 'reactflow/dist/style.css';
import '@/styles/layout/layout.scss';
import '@/styles/demo/Demos.scss';
import { AuthProvider, useAuth } from "@/layout/context/AuthContext";
import { canAccessRoute, isPublicRoute } from '@/config/routes';

const ProtectedContent = ({ Component, pageProps }) => {
    const router = useRouter();
    const { authenticated, isInitialized, roles } = useAuth();
    const routeIsPublic = isPublicRoute(router.pathname);
    const canAccess = canAccessRoute(router.pathname, { authenticated, roles });

    useEffect(() => {
        if (!isInitialized || canAccess) {
            return;
        }

        // Not allowed → send to home if unauthenticated, to AccessDenied if authenticated
        const fallback = authenticated ? '/home/AccessDenied' : '/';
        router.replace(fallback);
    }, [authenticated, isInitialized, canAccess, router]);

    if (!routeIsPublic && !isInitialized) {
        return <div>Loading...</div>;
    }

    if (!canAccess) {
        return null;
    }

    const page = <Component {...pageProps} />;
    if (Component.getLayout) {
        return Component.getLayout(page);
    }

    return <Layout>{page}</Layout>;
};

export default function MyApp({ Component, pageProps }) {
    return (
        <ThemeProvider>
            <AuthProvider>
                <LayoutProvider>
                    <ProtectedContent Component={Component} pageProps={pageProps} />
                </LayoutProvider>
            </AuthProvider>
        </ThemeProvider>
    );
}
