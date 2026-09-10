import React from 'react';

/**
 * Scrollable feed of alarms / events / audit lines.
 *
 * Props:
 *   items: [{ id, severity, title, source, timestamp, message? }]
 *   onAcknowledge?: (id) => void
 *
 * Severity → colour: 'critical' | 'warning' | 'info'
 */
const SEVERITY_ICON = {
    critical: 'pi-exclamation-circle',
    warning:  'pi-exclamation-triangle',
    info:     'pi-info-circle'
};

const timeAgo = (ts) => {
    const diff = Math.max(0, Date.now() - ts);
    const s = Math.floor(diff / 1000);
    if (s < 60) return `${s}s ago`;
    const m = Math.floor(s / 60);
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    return `${h}h ago`;
};

const AlarmFeed = ({ items = [], title = 'Alarms & events', onAcknowledge }) => {
    return (
        <aside className="alarm-feed">
            <header className="alarm-feed__head">
                <div>
                    <strong>{title}</strong>
                    <span>{items.length} active</span>
                </div>
            </header>

            <ol className="alarm-feed__list">
                {items.length === 0 ? (
                    <li className="alarm-feed__empty">No alarms — all systems nominal.</li>
                ) : items.map((alarm) => (
                    <li key={alarm.id} className={`alarm-feed__item alarm-feed__item--${alarm.severity}`}>
                        <span className="alarm-feed__icon" aria-hidden="true">
                            <i className={`pi ${SEVERITY_ICON[alarm.severity] || SEVERITY_ICON.info}`} />
                        </span>
                        <div className="alarm-feed__body">
                            <div className="alarm-feed__title">
                                <strong>{alarm.title}</strong>
                                <span>{timeAgo(alarm.timestamp)}</span>
                            </div>
                            <span className="alarm-feed__source">{alarm.source}</span>
                            {alarm.message ? <p>{alarm.message}</p> : null}
                        </div>
                        {onAcknowledge ? (
                            <button
                                type="button"
                                className="alarm-feed__ack"
                                onClick={() => onAcknowledge(alarm.id)}
                            >Ack</button>
                        ) : null}
                    </li>
                ))}
            </ol>
        </aside>
    );
};

export default AlarmFeed;
