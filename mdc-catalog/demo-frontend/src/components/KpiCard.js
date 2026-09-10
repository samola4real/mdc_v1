import React from 'react';

/**
 * Single KPI / metric card. Use a 2x2 or 1xN grid of them next to a hero.
 *
 * @example
 *   <KpiCard
 *     icon="pi pi-users"
 *     label="Providers in session"
 *     value={2}
 *     sublabel="Across 2 negotiations"
 *     tone="navy"
 *   />
 */
const TONE_CLASS = {
    navy: 'kpi-card--navy',
    orange: 'kpi-card--orange',
    sand: 'kpi-card--sand',
    ok: 'kpi-card--ok',
    error: 'kpi-card--error'
};

const KpiCard = ({ icon, label, value, sublabel, tone = 'navy', className = '' }) => (
    <div className={`kpi-card ${TONE_CLASS[tone] || ''} ${className}`}>
        {icon ? (
            <span className="kpi-card__icon" aria-hidden="true">
                <i className={icon} />
            </span>
        ) : null}
        <div className="kpi-card__body">
            <span className="kpi-card__label">{label}</span>
            <strong className="kpi-card__value">{value ?? '–'}</strong>
            {sublabel ? <span className="kpi-card__sublabel">{sublabel}</span> : null}
        </div>
    </div>
);

export default KpiCard;
