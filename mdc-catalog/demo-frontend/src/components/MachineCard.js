import React from 'react';
import Sparkline from './Sparkline';

/**
 * Single asset/machine status tile with live metric + sparkline.
 *
 * Props:
 *   name          — display name (e.g. "Press #4")
 *   subtitle      — optional secondary line (location, type, …)
 *   status        — 'ok' | 'warn' | 'error' | 'idle'
 *   value         — current metric value
 *   unit          — metric unit (string)
 *   trend         — array of recent values for the sparkline
 *   onClick       — handler when the card is clicked
 *   meta          — array of { label, value } for the footer grid
 *
 * Status colours map to the same --status-ok / --status-warn / --status-error
 * CSS variables defined in _main.scss, so the card respects the active theme.
 */
const STATUS_LABEL = {
    ok:    'Running',
    warn:  'Warning',
    error: 'Alarm',
    idle:  'Idle'
};

/**
 * Defensive formatter — never show 17 decimals on the shop floor.
 * Integers render as-is; floats are clamped to 1 decimal.
 * Anything non-numeric is passed through (already-formatted strings).
 */
const formatValue = (v) => {
    if (v == null) return '—';
    if (typeof v === 'number') {
        if (!Number.isFinite(v)) return '—';
        return Number.isInteger(v) ? v.toString() : v.toFixed(1);
    }
    return String(v);
};

const MachineCard = ({
    name,
    subtitle,
    status = 'idle',
    value,
    unit,
    trend = [],
    meta = [],
    onClick
}) => {
    return (
        <button
            type="button"
            className={`machine-card machine-card--${status}`}
            onClick={onClick}
            aria-label={`${name} — ${STATUS_LABEL[status]}`}
        >
            <header className="machine-card__head">
                <div>
                    <strong>{name}</strong>
                    {subtitle ? <span>{subtitle}</span> : null}
                </div>
                <span className="machine-card__pulse" aria-hidden="true" />
            </header>

            <div className="machine-card__metric">
                <div className="machine-card__value">
                    <span>{formatValue(value)}</span>
                    {unit ? <small>{unit}</small> : null}
                </div>
                <Sparkline data={trend} width={86} height={26} color="currentColor" />
            </div>

            {meta.length > 0 ? (
                <dl className="machine-card__meta">
                    {meta.map((m) => (
                        <div key={m.label}>
                            <dt>{m.label}</dt>
                            <dd>{m.value}</dd>
                        </div>
                    ))}
                </dl>
            ) : null}

            <footer className="machine-card__footer">
                <span className="machine-card__status">{STATUS_LABEL[status]}</span>
            </footer>
        </button>
    );
};

export default MachineCard;
