import React from 'react';

/**
 * Top-of-page status strip with a connection dot and pill counters.
 * Domain-agnostic: pass whatever indicators are relevant for your subsystem.
 *
 * @example
 *   <StatusStrip
 *     connection={{ label: 'Broker connection', value: 'Connected', tone: 'ok' }}
 *     pills={[
 *       { label: 'Active negotiations', value: 2, tone: 'info' },
 *       { label: 'Pending notifications', value: 0, tone: 'muted' }
 *     ]}
 *   />
 */
const TONE_DOT = {
    ok: '#2BA86F',
    warn: '#E8903E',
    error: '#E06040',
    muted: '#A6A6A6'
};

const TONE_PILL = {
    info: 'status-pill--info',
    ok: 'status-pill--ok',
    warn: 'status-pill--warn',
    error: 'status-pill--error',
    muted: 'status-pill--muted'
};

const StatusStrip = ({ connection, pills = [], className = '' }) => {
    return (
        <div className={`status-strip ${className}`}>
            {connection ? (
                <span className="status-strip__connection">
                    <span
                        className="status-strip__dot"
                        style={{ background: TONE_DOT[connection.tone] || TONE_DOT.muted }}
                        aria-hidden="true"
                    />
                    <span className="status-strip__label">{connection.label}:</span>
                    <strong>{connection.value}</strong>
                </span>
            ) : null}

            {pills.map((pill) => (
                <span key={pill.label} className={`status-pill ${TONE_PILL[pill.tone] || ''}`}>
                    <span className="status-pill__value">{pill.value}</span>
                    <span className="status-pill__label">{pill.label}</span>
                </span>
            ))}
        </div>
    );
};

export default StatusStrip;
