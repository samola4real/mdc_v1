import React, { useRef, useState } from 'react';
import { Toast } from 'primereact/toast';
import { Button } from 'primereact/button';
import { SelectButton } from 'primereact/selectbutton';
import GanttBoard from '@/components/GanttBoard';
import StatusStrip from '@/components/StatusStrip';
import KpiCard from '@/components/KpiCard';


const RESOURCES = [
    { id: 'press-04', name: 'Press #4',     role: 'Forming · Line A'      },
    { id: 'lathe-12', name: 'Lathe #12',    role: 'Turning · Line A'      },
    { id: 'cnc-07',   name: 'CNC #7',       role: 'Milling · Line B'      },
    { id: 'oven-02',  name: 'Tempering',    role: 'Heat treat · Line B'   },
    { id: 'qc-01',    name: 'QC Cell',      role: 'Inspection'            },
    { id: 'pack-01',  name: 'Pack Cell',    role: 'Outbound'              }
];

const today = (() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
})();

const day = (offsetDays) => {
    const d = new Date(today);
    d.setDate(d.getDate() + offsetDays);
    return d;
};

const INITIAL_TASKS = [
    { id: 't1',  resourceId: 'press-04', start: day(0), end: day(2),  label: 'Order #4821 (5k units)',   tone: 'info' },
    { id: 't2',  resourceId: 'press-04', start: day(2), end: day(4),  label: 'Order #4822 (3k units)',   tone: 'info' },
    { id: 't3',  resourceId: 'lathe-12', start: day(0), end: day(1),  label: 'Setup + warm-up',          tone: 'muted' },
    { id: 't4',  resourceId: 'lathe-12', start: day(1), end: day(5),  label: 'Order #4811 (shafts)',     tone: 'ok' },
    { id: 't5',  resourceId: 'cnc-07',   start: day(0), end: day(3),  label: 'Order #4815 (housings)',   tone: 'info' },
    { id: 't6',  resourceId: 'cnc-07',   start: day(3), end: day(4),  label: 'Maintenance',              tone: 'warn' },
    { id: 't7',  resourceId: 'cnc-07',   start: day(4), end: day(6),  label: 'Order #4830',              tone: 'info' },
    { id: 't8',  resourceId: 'oven-02',  start: day(1), end: day(2),  label: 'Heat treat batch 18',      tone: 'info' },
    { id: 't9',  resourceId: 'oven-02',  start: day(3), end: day(4),  label: 'Heat treat batch 19',      tone: 'info' },
    { id: 't10', resourceId: 'qc-01',    start: day(2), end: day(3),  label: 'Sample QC · batch 18',     tone: 'ok' },
    { id: 't11', resourceId: 'qc-01',    start: day(4), end: day(5),  label: 'Sample QC · batch 19',     tone: 'ok' },
    { id: 't12', resourceId: 'pack-01',  start: day(3), end: day(6),  label: 'Outbound order #4815',     tone: 'info' }
];

const VIEW_OPTIONS = [
    { label: 'Day',   value: 'day'   },
    { label: 'Week',  value: 'week'  },
    { label: 'Month', value: 'month' }
];

const TASK_TONES = [
    { value: 'info',  label: 'Production' },
    { value: 'ok',    label: 'On schedule' },
    { value: 'warn',  label: 'Maintenance' },
    { value: 'error', label: 'Blocked' },
    { value: 'muted', label: 'Setup' }
];

/* ------------------------------------------------------------ */

const Scheduler = () => {
    const toast = useRef(null);
    const [tasks, setTasks] = useState(INITIAL_TASKS);
    const [view, setView] = useState('week');
    const [selectedTask, setSelectedTask] = useState(null);

    const handleMove = ({ id, deltaCells }) => {
        if (deltaCells === 0) return;
        const unitMs = view === 'day' ? 60 * 60 * 1000
                     : view === 'week' ? 24 * 60 * 60 * 1000
                     : 7 * 24 * 60 * 60 * 1000;

        setTasks((curr) => curr.map((t) => {
            if (t.id !== id) return t;
            return {
                ...t,
                start: new Date(t.start.getTime() + deltaCells * unitMs),
                end:   new Date(t.end.getTime()   + deltaCells * unitMs)
            };
        }));

        toast.current?.show({
            severity: 'info',
            summary: 'Task rescheduled',
            detail: `Moved by ${deltaCells} ${view === 'day' ? 'hour(s)' : view === 'week' ? 'day(s)' : 'week(s)'}.`,
            life: 1800
        });
    };

    const totalCount = tasks.length;
    const blockedCount = tasks.filter((t) => t.tone === 'error').length;
    const maintenanceCount = tasks.filter((t) => t.tone === 'warn').length;

    return (
        <div className="scheduler-page">
            <Toast ref={toast} position="top-right" />

            <StatusStrip
                connection={{ label: 'Planner sync', value: 'Connected', tone: 'ok' }}
                pills={[
                    { label: 'Scheduled tasks', value: totalCount, tone: 'info' },
                    { label: 'Maintenance',     value: maintenanceCount, tone: 'warn' },
                    { label: 'Blocked',         value: blockedCount, tone: 'error' }
                ]}
            />

            <section className="scheduler-hero">
                <div className="scheduler-hero__copy">
                    <span className="scheduler-hero__tag">Workspace · Scheduler</span>
                    <h1>Production schedule</h1>
                    <p>
                        Drag any task left or right to reschedule. Switch zoom to see hours,
                        days, or whole weeks. Click a bar to open its detail drawer.
                    </p>
                    <div className="scheduler-hero__actions">
                        <SelectButton value={view} onChange={(e) => setView(e.value)} options={VIEW_OPTIONS} unselectable={false} />
                        <Button label="New task" icon="pi pi-plus" outlined />
                        <Button label="Export plan" icon="pi pi-download" text />
                    </div>
                </div>
                <div className="scheduler-hero__kpis">
                    <KpiCard icon="pi pi-bolt"       label="Utilisation"     value="82%"  tone="navy"   sublabel="This week"/>
                    <KpiCard icon="pi pi-clock"      label="Avg cycle"       value="3.2d" tone="orange" />
                    <KpiCard icon="pi pi-flag"       label="On-time SLA"     value="94%"  tone="ok"     />
                    <KpiCard icon="pi pi-exclamation-circle" label="Conflicts" value={blockedCount} tone={blockedCount > 0 ? 'error' : 'sand'} />
                </div>
            </section>

            <section className="scheduler-board">
                <header className="scheduler-board__head">
                    <div>
                        <h2>{view === 'day' ? 'Today · hourly' : view === 'week' ? 'This week · daily' : 'Next 12 weeks · weekly'}</h2>
                        <span>Drag a bar to reschedule</span>
                    </div>
                    <ul className="scheduler-legend">
                        {TASK_TONES.map((t) => (
                            <li key={t.value} className={`scheduler-legend__dot scheduler-legend__dot--${t.value}`}>
                                <span /> {t.label}
                            </li>
                        ))}
                    </ul>
                </header>

                <GanttBoard
                    resources={RESOURCES}
                    tasks={tasks}
                    view={view}
                    onMoveTask={handleMove}
                    onSelectTask={setSelectedTask}
                />
            </section>

            {selectedTask ? (
                <aside className="scheduler-drawer">
                    <div className="scheduler-drawer__inner">
                        <header>
                            <strong>{selectedTask.label}</strong>
                            <button type="button" onClick={() => setSelectedTask(null)} aria-label="Close detail">×</button>
                        </header>
                        <dl>
                            <div><dt>Resource</dt><dd>{RESOURCES.find((r) => r.id === selectedTask.resourceId)?.name}</dd></div>
                            <div><dt>Start</dt><dd>{selectedTask.start.toLocaleString()}</dd></div>
                            <div><dt>End</dt><dd>{selectedTask.end.toLocaleString()}</dd></div>
                            <div><dt>Status</dt><dd>{TASK_TONES.find((t) => t.value === selectedTask.tone)?.label || selectedTask.tone}</dd></div>
                        </dl>
                        <div className="scheduler-drawer__actions">
                            <Button label="Open work order" icon="pi pi-external-link" />
                            <Button label="Reassign" icon="pi pi-arrows-h" outlined />
                            <Button label="Cancel task" icon="pi pi-times" severity="danger" outlined />
                        </div>
                    </div>
                </aside>
            ) : null}
        </div>
    );
};

export default Scheduler;
