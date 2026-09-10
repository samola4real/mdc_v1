import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/layout/context/AuthContext';

const privateQuickActions = [
    {
        title: 'Create a Project',
        description: 'Create a project from scratch',
        href: '/home/Help',
        tone: 'green',
        delay: '0.08s',
        icon: (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="4" y="5" width="16" height="14" rx="2" />
                <path d="M8 9h8M8 13h5" />
            </svg>
        )
    },
    {
        title: 'View your Projects',
        description: 'View the projects that you have created',
        href: '/workspace/crud',
        tone: 'blue',
        delay: '0.14s',
        icon: (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m12 4 2.3 4.66 5.14.75-3.72 3.63.88 5.13L12 15.9l-4.6 2.41.88-5.13-3.72-3.63 5.14-.75L12 4Z" />
            </svg>
        )
    },
    {
        title: 'Register a Resource',
        description: 'Register an Algorithm or Dataset',
        href: '/workspace/charts',
        tone: 'red',
        delay: '0.2s',
        icon: (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M8 17 16 7M10 7H16V13" />
            </svg>
        )
    }
];

const publicQuickActions = [
    {
        title: 'Contact',
        description: 'Reach the MaaSAI team for support and onboarding',
        href: '/home/Contact',
        tone: 'blue',
        delay: '0.08s',
        icon: (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M4 7h16v10H4z" />
                <path d="m5 8 7 5 7-5" />
            </svg>
        )
    },
    {
        title: 'Help',
        description: 'Read the project overview and usage context',
        href: '/home/Help',
        tone: 'green',
        delay: '0.14s',
        icon: (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 17h.01" />
                <path d="M9.1 9a3 3 0 1 1 4.73 2.46c-.9.62-1.33 1.08-1.33 2.04" />
                <circle cx="12" cy="12" r="9" />
            </svg>
        )
    },
    {
        title: 'Sign In',
        description: 'Authenticate with Keycloak to unlock the workspace',
        tone: 'red',
        delay: '0.2s',
        action: 'login',
        icon: (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M10 17l5-5-5-5" />
                <path d="M15 12H4" />
                <path d="M13 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4" />
            </svg>
        )
    },
    {
        title: 'Project Website',
        description: 'Visit the official MaaSAI project website',
        href: 'https://maasai-project.eu/',
        external: true,
        tone: 'purple',
        delay: '0.26s',
        icon: (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 3c4.97 0 9 4.03 9 9s-4.03 9-9 9-9-4.03-9-9 4.03-9 9-9Z" />
                <path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" />
            </svg>
        )
    }
];

const DashboardContent = () => {
    const { authenticated, login } = useAuth();
    const quickActions = authenticated ? privateQuickActions : publicQuickActions;

    const handleActionClick = (action, event) => {
        if (action.action !== 'login') {
            return;
        }

        event.preventDefault();
        login().catch((error) => {
            console.error('Error during login:', error);
        });
    };

    return (
        <div className="dashboard-page">
            <section className="dashboard-banner">
                <div className="dashboard-banner__copy">
                    <h1>Welcome to the MaaSAI template</h1>
                    <p>
                        Empowering the manufacturing process through autonomous AI. Manage projects, register
                        algorithms and datasets, and monitor your industrial AI resources.
                    </p>
                </div>
                <Link href="https://documentation.maasai-srv.cigip.upv.es/" className="dashboard-banner__button" target="_blank" rel="noreferrer">
                    <span className="dashboard-banner__button-icon" aria-hidden="true">
                        +
                    </span>
                    <span>More info</span>
                </Link>
            </section>

            <section className="dashboard-actions">
                <div className="dashboard-section-label">Quick Actions</div>
                <div className="dashboard-actions__grid">
                    {quickActions.map((action) => (
                        <Link
                            key={action.title}
                            href={action.href || '#'}
                            className={`dashboard-action-card dashboard-action-card--${action.tone}`}
                            style={{ animationDelay: action.delay }}
                            onClick={(event) => handleActionClick(action, event)}
                            target={action.external ? '_blank' : undefined}
                            rel={action.external ? 'noreferrer' : undefined}
                        >
                            <span className="dashboard-action-card__icon" aria-hidden="true">
                                {action.icon}
                            </span>
                            <h2>{action.title}</h2>
                            <p>{action.description}</p>
                        </Link>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default DashboardContent;
