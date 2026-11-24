import React, { useEffect, useRef, useState } from 'react';
import Image from 'next/image';

const accentCycle = ['orange', 'blue', 'green', 'purple', 'teal', 'red'];

const contacts = [
    {
        name: 'Jose Martinez Lastra',
        organization: 'Tampere University — FAST-Lab',
        organizationShort: 'TAU',
        type: 'University',
        role: 'Unit Head',
        email: 'jose.martinezlastra@tuni.fi',
        website: 'https://research.tuni.fi/fast/',
        websiteLabel: 'FAST-Lab homepage'
    },
    {
        name: 'Samuel Afolaranmi',
        organization: 'Tampere University — FAST-Lab',
        organizationShort: 'TAU',
        type: 'University',
        role: 'Developer, MaaS Dynamic Catalogue',
        email: 'samuel.afolaranmi@tuni.fi',
        website: 'https://documentation.maasai-srv.cigip.upv.es/solutions/mdc/',
        websiteLabel: 'MDC documentation'
    },
    {
        name: 'Miguel Angel Mateo-Casali',
        organization: 'Universitat Politecnica de Valencia (CIGIP)',
        organizationShort: 'UPV',
        type: 'University',
        email: 'mmateo@cigip.upv.es',
        imageSrc: '/layout/images/02_UPV.png'
    },
    {
        name: 'Georgia Apostolou',
        organization: 'CERTH - Information Technologies Institute',
        organizationShort: 'CERTH',
        type: 'University',
        email: 'gapostolou@iti.gr',
        imageSrc: '/layout/images/01_CERTH.png'
    }
];

const badgeToneByType = {
    University: 'contact-badge--university',
    Industry: 'contact-badge--industry',
    Research: 'contact-badge--research'
};

const ContactLogo = ({ src, alt, initials }) => {
    const [hasError, setHasError] = useState(false);

    if (!src || hasError) {
        return <span className="contact-logo__fallback">{initials}</span>;
    }

    return (
        <Image
            src={src}
            alt={alt}
            width={120}
            height={120}
            onError={() => setHasError(true)}
            style={{ width: '100%', height: 'auto', objectFit: 'contain' }}
        />
    );
};

const Contact = () => {
    const [copiedEmail, setCopiedEmail] = useState('');
    const [toastMessage, setToastMessage] = useState('');
    const timeoutRef = useRef(null);

    useEffect(() => {
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, []);

    const handleCopyEmail = async (email) => {
        try {
            await navigator.clipboard.writeText(email);
            setCopiedEmail(email);
            setToastMessage(`Copied ${email}`);

            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }

            timeoutRef.current = setTimeout(() => {
                setCopiedEmail('');
                setToastMessage('');
            }, 2000);
        } catch (error) {
            console.error('Error copying email:', error);
            setToastMessage('Clipboard access failed');
        }
    };

    return (
        <div className="contact-page">
            <section className="contact-page__header">
                <div>
                    <h1>Contact Detail</h1>
                    <p>Project team and participating organisations in MaaSAI.</p>
                </div>
            </section>

            <section className="contact-grid">
                {contacts.map((contact, index) => {
                    const accent = accentCycle[index % accentCycle.length];
                    const isCopied = copiedEmail === contact.email;

                    return (
                        <article key={contact.email} className={`contact-card contact-card--${accent}`}>
                            <div className="contact-card__logo">
                                <ContactLogo
                                    src={contact.imageSrc}
                                    alt={contact.organization}
                                    initials={contact.organizationShort}
                                />
                            </div>

                            <div className="contact-card__body">
                                <div className="contact-card__top">
                                    <div>
                                        <h2>{contact.name}</h2>
                                        <p>{contact.organization}</p>
                                        {contact.role && <p>{contact.role}</p>}
                                    </div>
                                    <span className={`contact-badge ${badgeToneByType[contact.type]}`}>{contact.type}</span>
                                </div>

                                {contact.website && (
                                    <a href={contact.website} className="contact-card__website" target="_blank" rel="noreferrer">
                                        <i className="pi pi-external-link" aria-hidden="true" />
                                        {contact.websiteLabel}
                                    </a>
                                )}

                                <div className="contact-card__footer">
                                    <a href={`mailto:${contact.email}`} className="contact-card__email">
                                        {contact.email}
                                    </a>
                                    <button
                                        type="button"
                                        className={`contact-copy ${isCopied ? 'contact-copy--copied' : ''}`}
                                        onClick={() => handleCopyEmail(contact.email)}
                                        aria-label={`Copy ${contact.email}`}
                                    >
                                        {isCopied ? (
                                            <svg viewBox="0 0 24 24" aria-hidden="true">
                                                <path d="m5 13 4 4L19 7" />
                                            </svg>
                                        ) : (
                                            <svg viewBox="0 0 24 24" aria-hidden="true">
                                                <rect x="9" y="9" width="10" height="10" rx="2" />
                                                <path d="M15 9V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2" />
                                            </svg>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </article>
                    );
                })}
            </section>

            <div className={`contact-toast ${toastMessage ? 'contact-toast--visible' : ''}`} aria-live="polite">
                {toastMessage}
            </div>
        </div>
    );
};

export default Contact;
