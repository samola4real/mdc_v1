import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/layout/context/AuthContext';

const welcomeContent = {
    maasai: {
        heading: 'Welcome to MaaSAI',
        description: 'MaaSAI advances Manufacturing as a Service by enabling connected, intelligent and collaborative manufacturing ecosystems. The project supports digital manufacturing services, interoperability and collaboration between manufacturing providers and consumers.',
        href: 'https://documentation.maasai-srv.cigip.upv.es/'
    },
    mdc: {
        heading: 'Welcome to MaaS Dynamic Catalogue',
        description: 'The MaaS Dynamic Catalogue (MDC) enables manufacturing providers to publish, manage and update their manufacturing services and capabilities. Through ontology-based data harmonization and semantic service discovery, MDC supports the identification of suitable manufacturing services based on consumer requirements.',
        href: 'https://documentation.maasai-srv.cigip.upv.es/solutions/mdc/'
    }
};

const informationCards = [
    {
        title: 'Contact',
        description: 'Contact the MDC development team for technical information and enquiries.',
        href: '/home/Contact',
        delay: '0.08s',
        icon: (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M4 7h16v10H4z" />
                <path d="m5 8 7 5 7-5" />
            </svg>
        )
    },
    {
        title: 'Project Website',
        description: 'Explore the MaaSAI project, its objectives, activities and results.',
        href: 'https://maasai-project.eu/',
        external: true,
        delay: '0.14s',
        icon: (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 3c4.97 0 9 4.03 9 9s-4.03 9-9 9-9-4.03-9-9 4.03-9 9-9Z" />
                <path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" />
            </svg>
        )
    }
];

const DashboardContent = () => {
    const { authenticated, isInitialized, isLoading } = useAuth();
    const welcome = isInitialized && !isLoading && authenticated ? welcomeContent.mdc : welcomeContent.maasai;

    return (
        <div className="dashboard-page">
            <section className="dashboard-banner">
                <div className="dashboard-banner__copy">
                    <h1>{welcome.heading}</h1>
                    <p>{welcome.description}</p>
                </div>
                <Link href={welcome.href} className="dashboard-banner__button" target="_blank" rel="noreferrer">
                    <span className="dashboard-banner__button-icon pi pi-info-circle" aria-hidden="true" />
                    <span>More info</span>
                </Link>
            </section>

            <section className="dashboard-actions">
                <div className="dashboard-section-label">Project information</div>
                <div className="dashboard-actions__grid">
                    {informationCards.map((card) => (
                        <Link
                            key={card.title}
                            href={card.href}
                            className="dashboard-action-card"
                            style={{ animationDelay: card.delay }}
                            target={card.external ? '_blank' : undefined}
                            rel={card.external ? 'noreferrer' : undefined}
                        >
                            <span className="dashboard-action-card__icon" aria-hidden="true">
                                {card.icon}
                            </span>
                            <h2>{card.title}</h2>
                            <p>{card.description}</p>
                        </Link>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default DashboardContent;
