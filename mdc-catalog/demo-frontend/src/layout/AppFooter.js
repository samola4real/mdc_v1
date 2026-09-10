import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

const AppFooter = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="layout-footer">
            <Image
                src="/layout/images/MaaSAI_colour_main_letters.png"
                alt="MaaSAI"
                width={120}
                height={28}
                className="footer-logo"
            />
            <span>
                {'Copyright © '}
                <Link target="_blank" href={{ pathname: 'https://www.cigip.upv.es/' }}>
                    CIGIP
                </Link>
                {` ${currentYear}.`}
            </span>
            <span className="footer-separator">|</span>
            <span className="footer-eu-note">
                <span className="footer-eu-flag" aria-hidden="true">
                    <svg viewBox="0 0 24 16">
                        <rect width="24" height="16" rx="2" fill="#1F4AA8" />
                        <g fill="#FFCC00">
                            <circle cx="12" cy="3.2" r="0.7" />
                            <circle cx="15.1" cy="4" r="0.7" />
                            <circle cx="17.4" cy="6.2" r="0.7" />
                            <circle cx="18.2" cy="9" r="0.7" />
                            <circle cx="17.4" cy="11.8" r="0.7" />
                            <circle cx="15.1" cy="14" r="0.7" />
                            <circle cx="12" cy="14.8" r="0.7" />
                            <circle cx="8.9" cy="14" r="0.7" />
                            <circle cx="6.6" cy="11.8" r="0.7" />
                            <circle cx="5.8" cy="9" r="0.7" />
                            <circle cx="6.6" cy="6.2" r="0.7" />
                            <circle cx="8.9" cy="4" r="0.7" />
                        </g>
                    </svg>
                </span>
                <span>
                    {'Co-funded by the European Union Grant Agreement '}
                    <Link target="_blank" href={{ pathname: 'https://cordis.europa.eu/project/id/101177368' }}>
                        101177368
                    </Link>
                </span>
            </span>
        </footer>
    );
};

export default AppFooter;
