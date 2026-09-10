import React from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import { Button } from 'primereact/button';

/**
 * Generic "directory" table for listing domain entities (agents, robots,
 * processes, schedulers, sensors, …). It wraps PrimeReact's DataTable so you
 * get sorting, paginator and selection for free, but exposes a sensible
 * column model out of the box.
 *
 * @param {Object} props
 * @param {string} props.title         Heading shown above the table.
 * @param {Array}  props.rows          Items to render.
 * @param {Array}  props.columns       Column descriptors (see below).
 * @param {Array}  [props.toolbar]     Buttons rendered top-right (Run session, …).
 * @param {Function} [props.onRowAction] Called when the "action" button is pressed.
 * @param {string} [props.actionLabel] Label for the per-row action button.
 *
 * Column descriptor shape:
 *   { field: 'name',  header: 'Agent',  body?: fn(row), subField?: 'subtitle' }
 *   { kind: 'status', field: 'status', tones: { idle: 'info', running: 'success' } }
 *   { kind: 'config', field: 'config', formatter: row => ['line 1', 'line 2'] }
 */
const STATUS_TONES = {
    idle: 'info',
    running: 'success',
    success: 'success',
    failed: 'danger',
    error: 'danger',
    warning: 'warning',
    pending: 'warning'
};

const renderTwoLine = (row, field, subField) => (
    <div className="entity-cell">
        <strong>{row[field]}</strong>
        {subField && row[subField] ? <span>{row[subField]}</span> : null}
    </div>
);

const renderStatus = (row, field, tones = STATUS_TONES) => {
    const value = row[field];
    const tone = tones[String(value).toLowerCase()] || 'info';
    return <Tag value={value} severity={tone} rounded />;
};

const renderConfigList = (row, formatter) => {
    const lines = formatter(row) || [];
    return (
        <ul className="entity-cell__config">
            {lines.map((line, i) => <li key={i}>{line}</li>)}
        </ul>
    );
};

const EntityDirectory = ({
    title,
    rows = [],
    columns = [],
    toolbar = null,
    onRowAction,
    actionLabel = 'Configure',
    icon = 'pi pi-th-large'
}) => {
    return (
        <section className="entity-directory">
            <header className="entity-directory__head">
                <div className="entity-directory__title">
                    <span className="entity-directory__icon"><i className={icon} /></span>
                    <h2>{title}</h2>
                </div>
                {toolbar ? <div className="entity-directory__toolbar">{toolbar}</div> : null}
            </header>

            <DataTable value={rows} dataKey="id" emptyMessage="No entities yet" stripedRows>
                {columns.map((col) => {
                    if (col.kind === 'status') {
                        return (
                            <Column
                                key={col.field}
                                field={col.field}
                                header={col.header || 'Status'}
                                body={(row) => renderStatus(row, col.field, col.tones)}
                                sortable
                            />
                        );
                    }
                    if (col.kind === 'config') {
                        return (
                            <Column
                                key={col.field || col.header}
                                header={col.header || 'Configuration'}
                                body={(row) => renderConfigList(row, col.formatter)}
                            />
                        );
                    }
                    return (
                        <Column
                            key={col.field}
                            field={col.field}
                            header={col.header}
                            sortable={col.sortable !== false}
                            body={col.body || ((row) => renderTwoLine(row, col.field, col.subField))}
                        />
                    );
                })}

                {onRowAction ? (
                    <Column
                        header="Action"
                        headerStyle={{ width: '9rem' }}
                        body={(row) => (
                            <Button
                                label={actionLabel}
                                size="small"
                                outlined
                                onClick={() => onRowAction(row)}
                            />
                        )}
                    />
                ) : null}
            </DataTable>
        </section>
    );
};

export default EntityDirectory;
