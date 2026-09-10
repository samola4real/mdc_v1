import React, { useCallback, useMemo, useRef, useState } from 'react';

/**
 * GanttBoard — minimal yet practical scheduler.
 *
 * Renders resources on the Y axis, time on the X axis, and tasks as
 * draggable bars. Supports day / week / month zoom. No external deps.
 *
 *   <GanttBoard
 *     resources={[{ id, name, role }]}
 *     tasks={[{ id, resourceId, start: Date, end: Date, label, tone }]}
 *     view="week" | "day" | "month"
 *     onMoveTask={({ id, deltaCells }) => ...}
 *     onSelectTask={task => ...}
 *   />
 *
 * `tone` values map to the same CSS variables as status colours
 * (ok / warn / error / info / muted), so it stays theme-aware.
 */

const VIEW_CONFIG = {
    day:   { cellLabel: (i) => `${i}:00`, cells: 24,  unitMs: 60 * 60 * 1000,    title: 'Day · hourly' },
    week:  { cellLabel: (i) => `D${i + 1}`, cells: 7,   unitMs: 24 * 60 * 60 * 1000, title: 'Week · daily' },
    month: { cellLabel: (i) => `W${i + 1}`, cells: 12,  unitMs: 7 * 24 * 60 * 60 * 1000, title: '12 weeks · weekly' }
};

const TONE_CLASS = {
    info:  'gantt-bar--info',
    ok:    'gantt-bar--ok',
    warn:  'gantt-bar--warn',
    error: 'gantt-bar--error',
    muted: 'gantt-bar--muted'
};

const toCellIndex = (date, origin, unitMs) =>
    Math.round((date.getTime() - origin.getTime()) / unitMs);

const GanttBoard = ({
    resources = [],
    tasks = [],
    view = 'week',
    origin,
    onMoveTask,
    onSelectTask,
    todayIndex
}) => {
    const config = VIEW_CONFIG[view] || VIEW_CONFIG.week;
    const wrapperRef = useRef(null);
    const dragRef = useRef(null);
    const [dragPreview, setDragPreview] = useState(null); // { id, deltaCells }

    /* Compute origin date if not provided (start at midnight today). */
    const computedOrigin = useMemo(() => {
        if (origin) return origin;
        const d = new Date();
        d.setHours(0, 0, 0, 0);
        return d;
    }, [origin]);

    /* Translate every task into grid coordinates. */
    const placedTasks = useMemo(() => tasks.map((t) => {
        const startCell = toCellIndex(t.start, computedOrigin, config.unitMs);
        const endCell = Math.max(startCell + 1, toCellIndex(t.end, computedOrigin, config.unitMs));
        return { ...t, startCell, span: Math.max(1, endCell - startCell) };
    }), [tasks, computedOrigin, config.unitMs]);

    const handleMouseDown = (event, task) => {
        const board = wrapperRef.current;
        if (!board) return;
        const cellWidth = board.querySelector('.gantt-row__cells')?.getBoundingClientRect().width / config.cells;
        if (!cellWidth) return;

        dragRef.current = {
            id: task.id,
            startX: event.clientX,
            cellWidth
        };
        setDragPreview({ id: task.id, deltaCells: 0 });

        const onMove = (e) => {
            if (!dragRef.current) return;
            const delta = Math.round((e.clientX - dragRef.current.startX) / dragRef.current.cellWidth);
            setDragPreview({ id: dragRef.current.id, deltaCells: delta });
        };
        const onUp = () => {
            if (dragRef.current && dragPreview && onMoveTask) {
                onMoveTask({ id: dragRef.current.id, deltaCells: dragPreview.deltaCells });
            }
            // Use the latest preview from state by reading the closure on the
            // next tick is brittle; we rely on dragPreview that React captured.
            dragRef.current = null;
            setDragPreview(null);
            window.removeEventListener('mousemove', onMove);
            window.removeEventListener('mouseup', onUp);
        };
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
    };

    const todayCol = typeof todayIndex === 'number'
        ? todayIndex
        : toCellIndex(new Date(), computedOrigin, config.unitMs);

    return (
        <div className="gantt" ref={wrapperRef}>
            <div className="gantt__head">
                <div className="gantt__resource-head">Resource</div>
                <div className="gantt__cells gantt__cells--head">
                    {Array.from({ length: config.cells }, (_, i) => (
                        <span key={i} className={`gantt__col-head ${i === todayCol ? 'gantt__col-head--today' : ''}`}>
                            {config.cellLabel(i)}
                        </span>
                    ))}
                </div>
            </div>

            <div className="gantt__body">
                {resources.map((r) => {
                    const rowTasks = placedTasks.filter((t) => t.resourceId === r.id);
                    return (
                        <div key={r.id} className="gantt-row">
                            <div className="gantt-row__resource">
                                <strong>{r.name}</strong>
                                {r.role ? <span>{r.role}</span> : null}
                            </div>
                            <div
                                className="gantt-row__cells"
                                style={{ gridTemplateColumns: `repeat(${config.cells}, minmax(0, 1fr))` }}
                            >
                                {Array.from({ length: config.cells }, (_, i) => (
                                    <span
                                        key={i}
                                        className={`gantt-row__cell ${i === todayCol ? 'gantt-row__cell--today' : ''}`}
                                        aria-hidden="true"
                                    />
                                ))}
                                {rowTasks.map((task) => {
                                    const previewDelta =
                                        dragPreview && dragPreview.id === task.id ? dragPreview.deltaCells : 0;
                                    const col = Math.max(0, task.startCell + previewDelta);
                                    return (
                                        <button
                                            key={task.id}
                                            type="button"
                                            className={`gantt-bar ${TONE_CLASS[task.tone] || 'gantt-bar--info'}`}
                                            style={{
                                                gridColumn: `${col + 1} / span ${task.span}`,
                                                cursor: 'grab'
                                            }}
                                            onMouseDown={(e) => handleMouseDown(e, task)}
                                            onClick={() => onSelectTask?.(task)}
                                        >
                                            <span className="gantt-bar__label">{task.label}</span>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default GanttBoard;
