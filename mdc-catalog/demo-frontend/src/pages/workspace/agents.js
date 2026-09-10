import React, { useEffect, useRef, useState } from 'react';
import { Toast } from 'primereact/toast';
import { Button } from 'primereact/button';
import StatusStrip from '@/components/StatusStrip';
import KpiCard from '@/components/KpiCard';
import EntityDirectory from '@/components/EntityDirectory';
import ConfigureDialog from '@/components/ConfigureDialog';

const INITIAL_AGENTS = [
    {
        id: 'MCA_A_1', name: 'MCA_A_1', subtitle: 'MCOA_A',
        type: 'Consumer', typeSubtitle: 'Neutral',
        negotiation: 'neg-001', negotiationSubtitle: 'Counterpart: MPA_A_1',
        status: 'idle',
        config: { profile: 'Neutral', reserved: 0.3, concession: 2,
                  priceWeight: 0.5, quantityWeight: 0.2, deliveryWeight: 0.3,
                  priceRange: { min: 0, max: 10 }, quantityRange: { min: 1, max: 10 }, deliveryRange: { min: 0, max: 10 },
                  pricePref: 'lower', quantityPref: 'lower', deliveryPref: 'shorter' }
    },
    {
        id: 'MPA_A_1', name: 'MPA_A_1', subtitle: 'MPOA_A',
        type: 'Provider', typeSubtitle: 'Competitive',
        negotiation: 'neg-001', negotiationSubtitle: 'Counterpart: MCA_A_1',
        status: 'idle',
        config: { profile: 'Competitive', reserved: 0.4, concession: 2.8,
                  priceWeight: 0.6, quantityWeight: 0.25, deliveryWeight: 0.15,
                  priceRange: { min: 0, max: 10 }, quantityRange: { min: 1, max: 10 }, deliveryRange: { min: 0, max: 10 },
                  pricePref: 'higher', quantityPref: 'higher', deliveryPref: 'longer' }
    },
    {
        id: 'MCA_A_2', name: 'MCA_A_2', subtitle: 'MCOA_A',
        type: 'Consumer', typeSubtitle: 'Neutral',
        negotiation: 'neg-002', negotiationSubtitle: 'Counterpart: MPA_B_1',
        status: 'idle',
        config: { profile: 'Neutral', reserved: 0.3, concession: 2,
                  priceWeight: 0.5, quantityWeight: 0.2, deliveryWeight: 0.3,
                  priceRange: { min: 0, max: 10 }, quantityRange: { min: 1, max: 10 }, deliveryRange: { min: 0, max: 10 },
                  pricePref: 'lower', quantityPref: 'lower', deliveryPref: 'shorter' }
    },
    {
        id: 'MPA_B_1', name: 'MPA_B_1', subtitle: 'MPOA_B',
        type: 'Provider', typeSubtitle: 'Neutral',
        negotiation: 'neg-002', negotiationSubtitle: 'Counterpart: MCA_A_2',
        status: 'idle',
        config: { profile: 'Neutral', reserved: 0.3, concession: 2,
                  priceWeight: 0.5, quantityWeight: 0.3, deliveryWeight: 0.2,
                  priceRange: { min: 0, max: 10 }, quantityRange: { min: 1, max: 10 }, deliveryRange: { min: 0, max: 10 },
                  pricePref: 'higher', quantityPref: 'higher', deliveryPref: 'longer' }
    }
];

const INITIAL_SESSIONS = [
    { id: 'neg-001', pair: 'MCA_A_1 | MPA_A_1', round: 0, totalRounds: 15, providerProfile: 'Competitive', agreement: 'Pending', state: 'idle', selectedProvider: '—' },
    { id: 'neg-002', pair: 'MCA_A_2 | MPA_B_1', round: 0, totalRounds: 15, providerProfile: 'Neutral',     agreement: 'Pending', state: 'idle', selectedProvider: '—' }
];

const INITIAL_SESSION_CONFIG = {
    scenario: 'Standard session',
    simultaneous: 2,
    focus: 'neg-001',
    rounds: 15,
    timeLimit: 30,
    tieThreshold: 0.02
};

const PROFILES = ['Neutral', 'Competitive', 'Cooperative'];
const SCENARIOS = ['Standard session', 'Fast track', 'Stress test'];
const PRICE_PREF = [
    { label: 'Prefer lower',  value: 'lower'  },
    { label: 'Prefer higher', value: 'higher' }
];
const TIME_PREF = [
    { label: 'Prefer shorter', value: 'shorter' },
    { label: 'Prefer longer',  value: 'longer'  }
];

const SESSION_BADGE = {
    idle:      { label: 'Not started', tone: 'muted'  },
    running:   { label: 'Running',     tone: 'info'   },
    completed: { label: 'Agreement',   tone: 'ok'     },
    failed:    { label: 'Failed',      tone: 'error'  }
};

/* ------------------------------------------------------------ */

const AgentsWorkspace = () => {
    const toast = useRef(null);
    const directoryRef = useRef(null);
    const timersRef = useRef([]);

    const [agents, setAgents] = useState(INITIAL_AGENTS);
    const [sessions, setSessions] = useState(INITIAL_SESSIONS);
    const [sessionConfig, setSessionConfig] = useState(INITIAL_SESSION_CONFIG);
    const [editingAgent, setEditingAgent] = useState(null);
    const [sessionDialogOpen, setSessionDialogOpen] = useState(false);
    const [isRunning, setIsRunning] = useState(false);

    // Make sure pending timers don't fire after unmount
    useEffect(() => {
        return () => timersRef.current.forEach(clearTimeout);
    }, []);

    const scheduleStep = (fn, delay) => {
        const id = setTimeout(fn, delay);
        timersRef.current.push(id);
    };

    /* ---------------- Run session simulation ---------------- */

    const handleRunSession = () => {
        if (isRunning) {
            toast.current?.show({
                severity: 'warn',
                summary: 'Already running',
                detail: 'Wait for the current session to finish.',
                life: 2000
            });
            return;
        }

        setIsRunning(true);

        // T+0: agents go to running, sessions start round 1
        setAgents((curr) => curr.map((a) => ({ ...a, status: 'running' })));
        setSessions((curr) => curr.map((s) => ({
            ...s,
            state: 'running',
            round: 1,
            totalRounds: sessionConfig.rounds,
            agreement: 'In progress'
        })));
        toast.current?.show({
            severity: 'info',
            summary: 'Session started',
            detail: `Running ${sessions.length} negotiation(s) over ${sessionConfig.rounds} rounds.`,
            life: 2400
        });

        // T+1.2s: advance rounds
        scheduleStep(() => {
            setSessions((curr) => curr.map((s) => ({ ...s, round: Math.min(s.round + 4, s.totalRounds) })));
        }, 1200);

        // T+2.6s: finish — agents back to idle (or 'success'), agreement reached
        scheduleStep(() => {
            setAgents((curr) => curr.map((a) => ({ ...a, status: 'success' })));
            setSessions((curr) => curr.map((s) => ({
                ...s,
                state: 'completed',
                round: s.totalRounds,
                agreement: 'Agreement',
                selectedProvider: s.id === 'neg-001' ? 'MPA_A_1' : 'MPA_B_1'
            })));
            toast.current?.show({
                severity: 'success',
                summary: 'Session completed',
                detail: 'Agreements reached on all negotiations.',
                life: 2600
            });
            setIsRunning(false);
        }, 2600);
    };

    /* ---------------- View Agents (scroll to directory) ---------------- */

    const handleViewAgents = () => {
        directoryRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    /* ---------------- Agent configuration dialog ---------------- */

    const openAgentConfigure = (agent) => setEditingAgent(agent);
    const closeAgentConfigure = () => setEditingAgent(null);

    const saveAgentConfig = (values) => {
        setAgents((curr) =>
            curr.map((a) => (a.id === editingAgent.id ? { ...a, config: { ...a.config, ...values } } : a))
        );
        toast.current?.show({
            severity: 'success',
            summary: 'Saved',
            detail: `Configuration for ${editingAgent.name} updated.`,
            life: 2200
        });
        closeAgentConfigure();
    };

    /* ---------------- Session configuration dialog ---------------- */

    const openSessionConfigure = () => setSessionDialogOpen(true);
    const closeSessionConfigure = () => setSessionDialogOpen(false);

    const saveSessionConfig = (values) => {
        setSessionConfig(values);
        setSessionDialogOpen(false);
        toast.current?.show({
            severity: 'success',
            summary: 'Saved',
            detail: 'Session configuration updated.',
            life: 2200
        });
    };

    /* ---------------- Reset (handy when demoing) ---------------- */

    const resetState = () => {
        timersRef.current.forEach(clearTimeout);
        timersRef.current = [];
        setAgents(INITIAL_AGENTS);
        setSessions(INITIAL_SESSIONS);
        setIsRunning(false);
        toast.current?.show({ severity: 'info', summary: 'Reset', detail: 'State restored.', life: 1500 });
    };

    /* ---------------- Schemas ---------------- */

    const agentSchema = editingAgent ? [
        { name: 'profile', label: 'Negotiation profile', kind: 'dropdown', options: PROFILES },
        { kind: 'group', children: [
            { name: 'reserved',   label: 'Reserved value', kind: 'number', min: 0, max: 1, step: 0.1, fractionDigits: 2 },
            { name: 'concession', label: 'Concession e',   kind: 'number', min: 0, step: 0.1, fractionDigits: 2 }
        ]},
        { kind: 'group', children: [
            { name: 'priceWeight',    label: 'Price weight',         kind: 'number', min: 0, max: 1, step: 0.05, fractionDigits: 2 },
            { name: 'quantityWeight', label: 'Quantity weight',      kind: 'number', min: 0, max: 1, step: 0.05, fractionDigits: 2 },
            { name: 'deliveryWeight', label: 'Delivery time weight', kind: 'number', min: 0, max: 1, step: 0.05, fractionDigits: 2 }
        ]},
        { name: 'priceRange',    label: 'Price',         kind: 'range', step: 1 },
        { name: 'quantityRange', label: 'Quantity',      kind: 'range', step: 1 },
        { name: 'deliveryRange', label: 'Delivery time', kind: 'range', step: 1 },
        { name: 'pricePref',     label: 'Price preference',         kind: 'select', options: PRICE_PREF },
        { name: 'quantityPref',  label: 'Quantity preference',      kind: 'select', options: PRICE_PREF },
        { name: 'deliveryPref',  label: 'Delivery time preference', kind: 'select', options: TIME_PREF }
    ] : [];

    const sessionSchema = [
        { name: 'scenario', label: 'Scenario', kind: 'dropdown', options: SCENARIOS },
        { kind: 'group', children: [
            { name: 'simultaneous', label: 'Simultaneous negotiations', kind: 'number', min: 1, max: 10 },
            { name: 'focus',        label: 'Focus negotiation',         kind: 'dropdown', options: sessions.map((s) => s.id) }
        ]},
        { kind: 'group', children: [
            { name: 'rounds',       label: 'Number of rounds', kind: 'number', min: 1, max: 200 },
            { name: 'timeLimit',    label: 'Time limit (s)',   kind: 'number', min: 1 },
            { name: 'tieThreshold', label: 'Tie threshold',    kind: 'number', min: 0, max: 1, step: 0.01, fractionDigits: 3 }
        ]}
    ];

    /* ---------------- KPIs derived from state ---------------- */

    const completed = sessions.filter((s) => s.state === 'completed').length;
    const successRate = isRunning
        ? '…'
        : completed > 0
            ? `${Math.round((completed / sessions.length) * 100)}%`
            : '–';

    return (
        <div className="agents-page">
            <Toast ref={toast} position="top-right" />

            <StatusStrip
                connection={{ label: 'Broker connection', value: 'Connected', tone: 'ok' }}
                pills={[
                    { label: 'Active negotiations',  value: sessions.filter((s) => s.state === 'running').length, tone: 'info'  },
                    { label: 'Pending notifications', value: 0, tone: 'muted' }
                ]}
            />

            <section className="agents-hero">
                <div className="agents-hero__copy">
                    <span className="agents-hero__tag">Workspace · Agents</span>
                    <h1>MaaSAI Negotiation</h1>
                    <p>
                        Monitor negotiation sessions between consumer and provider agents, review
                        recent activity, and move directly into execution or agent management.
                    </p>
                    <div className="agents-hero__actions">
                        <Button
                            label={isRunning ? 'Running…' : 'Start Negotiation'}
                            icon={isRunning ? 'pi pi-spin pi-spinner' : 'pi pi-play'}
                            onClick={handleRunSession}
                            disabled={isRunning}
                        />
                        <Button
                            label="View Agents"
                            icon="pi pi-users"
                            outlined
                            onClick={handleViewAgents}
                        />
                        <Button
                            label="Reset"
                            icon="pi pi-refresh"
                            text
                            onClick={resetState}
                        />
                    </div>
                </div>

                <div className="agents-hero__kpis">
                    <KpiCard icon="pi pi-users"      label="Providers in session" value={agents.filter((a) => a.type === 'Provider').length} tone="navy"   />
                    <KpiCard icon="pi pi-list-check" label="Negotiations ready"   value={sessions.length} tone="orange" />
                    <KpiCard icon="pi pi-chart-bar"  label="Success rate"         value={successRate} sublabel={completed > 0 ? `${completed} / ${sessions.length} closed` : 'Not executed'} tone="sand" />
                    <KpiCard icon="pi pi-trophy"     label="Last session"         value={completed > 0 ? 'Completed' : 'Not executed'} tone="navy" />
                </div>
            </section>

            <div ref={directoryRef}>
                <EntityDirectory
                    title="Agent Directory"
                    icon="pi pi-th-large"
                    rows={agents}
                    onRowAction={openAgentConfigure}
                    actionLabel="Configure"
                    toolbar={
                        <>
                            <Button
                                label={isRunning ? 'Running…' : 'Run session'}
                                icon={isRunning ? 'pi pi-spin pi-spinner' : 'pi pi-play'}
                                onClick={handleRunSession}
                                disabled={isRunning}
                            />
                            <Button
                                label="Edit configuration"
                                icon="pi pi-pencil"
                                outlined
                                onClick={openSessionConfigure}
                            />
                        </>
                    }
                    columns={[
                        { field: 'name',        header: 'Agent',       subField: 'subtitle' },
                        { field: 'type',        header: 'Type',        subField: 'typeSubtitle' },
                        { field: 'negotiation', header: 'Negotiation', subField: 'negotiationSubtitle' },
                        { kind: 'status', field: 'status', header: 'Status' },
                        {
                            kind: 'config',
                            header: 'Configuration',
                            formatter: (row) => [
                                `Profile: ${row.config.profile}`,
                                `Reserved value: ${row.config.reserved}`,
                                `Concession e: ${row.config.concession}`,
                                `Weights: Price ${row.config.priceWeight} | Quantity ${row.config.quantityWeight} | Delivery ${row.config.deliveryWeight}`
                            ]
                        }
                    ]}
                />
            </div>

            <section className="session-overview">
                <header className="session-overview__head">
                    <h2>Negotiation Overview</h2>
                    <span>Live snapshot of every active session</span>
                </header>
                <div className="session-overview__grid">
                    {sessions.map((s) => {
                        const badge = SESSION_BADGE[s.state] || SESSION_BADGE.idle;
                        return (
                            <article key={s.id} className="session-card">
                                <header className="session-card__head">
                                    <div>
                                        <strong>{s.id}</strong>
                                        <span>{s.pair}</span>
                                    </div>
                                    <span className={`session-card__badge session-card__badge--${badge.tone}`}>{badge.label}</span>
                                </header>
                                <dl className="session-card__grid">
                                    <div>
                                        <dt>Provider</dt>
                                        <dd>{s.providerProfile}</dd>
                                    </div>
                                    <div>
                                        <dt>Current round</dt>
                                        <dd>{s.round} / {s.totalRounds}</dd>
                                    </div>
                                    <div>
                                        <dt>Agreement status</dt>
                                        <dd>{s.agreement}</dd>
                                    </div>
                                    <div>
                                        <dt>Selected provider</dt>
                                        <dd>{s.selectedProvider}</dd>
                                    </div>
                                </dl>
                            </article>
                        );
                    })}
                </div>
            </section>

            {/* Per-agent configure dialog */}
            <ConfigureDialog
                visible={Boolean(editingAgent)}
                onHide={closeAgentConfigure}
                onSave={saveAgentConfig}
                title={editingAgent ? `Configure ${editingAgent.name}` : ''}
                tags={editingAgent ? [
                    `${editingAgent.type} agent`,
                    editingAgent.negotiation,
                    `Counterpart: ${editingAgent.negotiationSubtitle?.replace('Counterpart: ', '') ?? ''}`,
                    editingAgent.subtitle,
                    editingAgent.typeSubtitle
                ] : []}
                description="Changes saved here are applied to this agent the next time the session runs."
                initialValues={editingAgent?.config || {}}
                schema={agentSchema}
            />

            {/* Session-wide configure dialog */}
            <ConfigureDialog
                visible={sessionDialogOpen}
                onHide={closeSessionConfigure}
                onSave={saveSessionConfig}
                title="Session configuration"
                tags={['Negotiation session', `${sessions.length} negotiations`]}
                description="Defines how the broker orchestrates the whole negotiation session."
                initialValues={sessionConfig}
                schema={sessionSchema}
            />
        </div>
    );
};

export default AgentsWorkspace;
