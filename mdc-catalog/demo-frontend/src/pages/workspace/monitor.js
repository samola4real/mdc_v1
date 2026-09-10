import React, { useCallback, useMemo, useRef, useState } from 'react';
import { Toast } from 'primereact/toast';
import { useLiveData } from '@/hooks/useLiveData';
import StatusStrip from '@/components/StatusStrip';
import MachineCard from '@/components/MachineCard';
import AlarmFeed from '@/components/AlarmFeed';
import CommandPanel from '@/components/CommandPanel';
import KpiCard from '@/components/KpiCard';

const MACHINES = [
    { id: 'press-04',  name: 'Press #4',        subtitle: 'Forming · Line A',  unit: 'units/h' },
    { id: 'lathe-12',  name: 'Lathe #12',       subtitle: 'Turning · Line A',  unit: 'rpm' },
    { id: 'cnc-07',    name: 'CNC #7',          subtitle: 'Milling · Line B',  unit: '°C' },
    { id: 'agv-21',    name: 'AGV #21',         subtitle: 'Internal logistics', unit: '% batt' },
    { id: 'oven-02',   name: 'Tempering Oven',  subtitle: 'Heat treat · Line B', unit: '°C' },
    { id: 'pack-01',   name: 'Pack Cell',       subtitle: 'Outbound',           unit: 'pkg/min' }
];

/* Deterministic mock generators so the page looks alive without a backend.
   Replace these by hooking the hook to your real telemetry source. */
const sineish = (centre, amp, periodMs, phase = 0) => () => {
    const t = (Date.now() + phase) / periodMs;
    return Math.round((centre + Math.sin(t) * amp + (Math.random() - 0.5) * amp * 0.3) * 10) / 10;
};

const round1 = (v) => Math.round(v * 10) / 10;

const generators = {
    'press-04': sineish(64, 6, 4000),
    'lathe-12': sineish(2400, 120, 3000, 500),
    'cnc-07':   sineish(58, 4, 5000, 900),
    'agv-21':   () => round1(Math.max(8, 72 - ((Date.now() / 4000) % 64))),
    'oven-02':  sineish(180, 8, 6000, 1500),
    'pack-01':  sineish(14, 3, 3500, 700)
};

const statusFromValue = (id, v) => {
    if (id === 'agv-21') return v < 15 ? 'error' : v < 30 ? 'warn' : 'ok';
    if (id === 'oven-02') return v > 195 ? 'error' : v > 188 ? 'warn' : 'ok';
    if (id === 'cnc-07')  return v > 62 ? 'warn' : 'ok';
    return 'ok';
};

const INITIAL_ALARMS = [
    {
        id: 'a1',
        severity: 'critical',
        title: 'AGV #21 battery critical',
        source: 'Energy monitor',
        timestamp: Date.now() - 42 * 1000,
        message: 'Vehicle returning to charging dock automatically.'
    },
    {
        id: 'a2',
        severity: 'warning',
        title: 'Tempering Oven approaching upper bound',
        source: 'Process safety',
        timestamp: Date.now() - 4 * 60 * 1000,
        message: 'Reduce setpoint by 5°C to avoid thermal runaway.'
    },
    {
        id: 'a3',
        severity: 'info',
        title: 'Press #4 shift change recorded',
        source: 'MES sync',
        timestamp: Date.now() - 18 * 60 * 1000
    }
];

/* ------------------------------------------------------------ */

/**
 * Cell — one MachineCard wired to its own useLiveData subscription.
 * Each card is independent: failing one will not stop the others.
 */
const MachineCell = ({ machine, onSelect }) => {
    const generator = useMemo(() => generators[machine.id], [machine.id]);
    const { data, history, connected } = useLiveData(machine.id, {
        mockGenerator: generator,
        interval: 1500
    });

    const trend = history.map((h) => h.v);
    const status = !connected ? 'idle' : statusFromValue(machine.id, data);

    return (
        <MachineCard
            name={machine.name}
            subtitle={machine.subtitle}
            status={status}
            value={data != null ? data : null}
            unit={machine.unit}
            trend={trend}
            meta={[
                { label: 'Trend (30s)', value: trend.length ? `${trend.length} pts` : '—' },
                { label: 'Updates', value: connected ? 'Live' : 'Offline' }
            ]}
            onClick={() => onSelect(machine)}
        />
    );
};

/* ------------------------------------------------------------ */

const Monitor = () => {
    const toast = useRef(null);
    const [alarms, setAlarms] = useState(INITIAL_ALARMS);
    const [selectedMachine, setSelectedMachine] = useState(null);

    const handleAck = useCallback((id) => {
        setAlarms((curr) => curr.filter((a) => a.id !== id));
        toast.current?.show({ severity: 'success', summary: 'Acknowledged', detail: `Alarm ${id} cleared.`, life: 1800 });
    }, []);

    const handleSelectMachine = (m) => {
        setSelectedMachine(m);
        toast.current?.show({ severity: 'info', summary: m.name, detail: 'Hook this to your detail drawer.', life: 1800 });
    };

    const dispatchCommand = (label) => () => {
        toast.current?.show({ severity: 'info', summary: 'Command sent', detail: label, life: 1600 });
    };

    const commands = [
        { id: 'start',      label: 'Start line',      icon: 'pi pi-play',     onClick: dispatchCommand('Start line A')   },
        { id: 'pause',      label: 'Pause line',      icon: 'pi pi-pause',    tone: 'warn',  onClick: dispatchCommand('Pause line A') },
        { id: 'stop',       label: 'Emergency stop',  icon: 'pi pi-stop',     tone: 'danger', onClick: dispatchCommand('E-STOP triggered') },
        { id: 'calibrate',  label: 'Calibrate',       icon: 'pi pi-cog',      tone: 'ghost',  onClick: dispatchCommand('Calibration sequence') },
        { id: 'recipe',     label: 'Switch recipe',   icon: 'pi pi-list',     tone: 'ghost',  onClick: dispatchCommand('Recipe switch requested') },
        { id: 'export',     label: 'Export shift',    icon: 'pi pi-download', tone: 'ghost',  onClick: dispatchCommand('Shift report exported') }
    ];

    // Aggregate KPIs from the latest snapshot of each machine. Each cell owns
    // its own subscription, so we keep a synthetic view here for the hero.
    const okCount   = 6 - alarms.filter((a) => a.severity === 'critical').length;
    const warnCount = alarms.filter((a) => a.severity === 'warning').length;
    const critCount = alarms.filter((a) => a.severity === 'critical').length;

    return (
        <div className="monitor-page">
            <Toast ref={toast} position="top-right" />

            <StatusStrip
                connection={{ label: 'Broker connection', value: 'Connected', tone: 'ok' }}
                pills={[
                    { label: 'Machines online', value: okCount, tone: 'ok' },
                    { label: 'Warnings',        value: warnCount, tone: 'warn' },
                    { label: 'Critical',        value: critCount, tone: 'error' }
                ]}
            />

            <section className="monitor-hero">
                <div className="monitor-hero__copy">
                    <span className="monitor-hero__tag">Workspace · Live Monitor</span>
                    <h1>Shop floor overview</h1>
                    <p>
                        Real-time visibility over machines, AGVs and process cells. Each tile
                        subscribes to its own data feed; click for the detail drawer.
                    </p>
                </div>
                <div className="monitor-hero__kpis">
                    <KpiCard icon="pi pi-check-circle" label="Healthy assets"   value={`${okCount}/6`} tone="ok"     />
                    <KpiCard icon="pi pi-bell"          label="Active alarms"    value={alarms.length} tone="orange" />
                    <KpiCard icon="pi pi-history"       label="MTBF (7 d)"       value="42 h"          tone="navy"   sublabel="Mean time between failures" />
                    <KpiCard icon="pi pi-bolt"          label="Throughput"       value="148 u/h"       tone="sand"   sublabel="Last 15 minutes" />
                </div>
            </section>

            <section className="monitor-body">
                <div className="monitor-grid">
                    {MACHINES.map((m) => (
                        <MachineCell key={m.id} machine={m} onSelect={handleSelectMachine} />
                    ))}
                </div>
                <AlarmFeed items={alarms} onAcknowledge={handleAck} />
            </section>

            <CommandPanel commands={commands} />
        </div>
    );
};

export default Monitor;
