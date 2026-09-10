import React from 'react';
import { Button } from 'primereact/button';

/**
 * Grid of operator commands. Each command has icon, label, tone, and a
 * handler. Tones: 'primary' (default), 'danger', 'warn', 'ghost'.
 *
 *   <CommandPanel commands={[
 *     { id: 'start', label: 'Start line', icon: 'pi pi-play', onClick: ... },
 *     { id: 'stop', label: 'Emergency stop', icon: 'pi pi-stop', tone: 'danger', onClick: ... }
 *   ]} />
 */
const TONE_SEVERITY = {
    primary: undefined,
    danger:  'danger',
    warn:    'warning',
    ghost:   'secondary'
};

const CommandPanel = ({ title = 'Operator commands', commands = [] }) => (
    <section className="command-panel">
        <header className="command-panel__head">
            <strong>{title}</strong>
        </header>
        <div className="command-panel__grid">
            {commands.map((cmd) => (
                <Button
                    key={cmd.id}
                    label={cmd.label}
                    icon={cmd.icon}
                    severity={TONE_SEVERITY[cmd.tone]}
                    outlined={cmd.tone === 'ghost'}
                    disabled={cmd.disabled}
                    onClick={cmd.onClick}
                />
            ))}
        </div>
    </section>
);

export default CommandPanel;
