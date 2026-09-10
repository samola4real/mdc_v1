import React, { useEffect, useState } from 'react';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { SelectButton } from 'primereact/selectbutton';
import { Tag } from 'primereact/tag';

/**
 * Generic configuration dialog. You give it a `schema` describing the fields
 * to render and it produces a controlled form, with Save / Cancel buttons.
 *
 * Why not just use react-hook-form / formik?
 * — Industrial dashboards typically have flat shape configs (numbers,
 *   dropdowns, ranges, toggles), and the cognitive cost of a full form
 *   library outweighs the benefit. This stays purposefully tiny.
 *
 * Supported field kinds:
 *   - 'dropdown'  → Dropdown with options
 *   - 'number'    → InputNumber
 *   - 'range'     → 2x InputNumber (min/max) in a single row
 *   - 'select'    → SelectButton (segmented control)
 *   - 'group'     → Container that renders N children side by side
 *
 * @example
 *   <ConfigureDialog
 *     visible={isOpen}
 *     onHide={() => setOpen(false)}
 *     onSave={(values) => save(values)}
 *     title="Configure MCA_A_1"
 *     tags={['Consumer agent', 'neg-001', 'Counterpart: MPA_A_1']}
 *     description="Changes are applied next time the session runs."
 *     initialValues={agent.config}
 *     schema={[
 *       { name: 'profile', label: 'Negotiation profile', kind: 'dropdown',
 *         options: ['Neutral', 'Competitive', 'Cooperative'] },
 *       { kind: 'group', children: [
 *         { name: 'reserved', label: 'Reserved value', kind: 'number', min: 0, max: 1, step: 0.1 },
 *         { name: 'concession', label: 'Concession e', kind: 'number', min: 0, step: 0.1 }
 *       ]},
 *       { name: 'priceRange', label: 'Price', kind: 'range' },
 *       { name: 'pricePref', label: 'Price', kind: 'select',
 *         options: [{label:'Prefer lower', value:'lower'},{label:'Prefer higher', value:'higher'}] }
 *     ]}
 *   />
 */
const ConfigureDialog = ({
    visible,
    onHide,
    onSave,
    title,
    tags = [],
    description,
    initialValues = {},
    schema = []
}) => {
    const [values, setValues] = useState(initialValues);

    // Sync external changes (e.g., user selects a different entity)
    useEffect(() => {
        if (visible) setValues(initialValues);
    }, [visible, initialValues]);

    const setField = (name, value) => setValues((current) => ({ ...current, [name]: value }));

    const renderField = (field) => {
        if (field.kind === 'group') {
            return (
                <div key={field.label || Math.random()} className="config-dialog__group">
                    {field.children.map(renderField)}
                </div>
            );
        }

        if (field.kind === 'dropdown') {
            return (
                <div key={field.name} className="config-dialog__field">
                    <label htmlFor={field.name}>{field.label}</label>
                    <Dropdown
                        inputId={field.name}
                        value={values[field.name]}
                        options={field.options}
                        onChange={(e) => setField(field.name, e.value)}
                        placeholder={field.placeholder || 'Select...'}
                    />
                </div>
            );
        }

        if (field.kind === 'number') {
            return (
                <div key={field.name} className="config-dialog__field">
                    <label htmlFor={field.name}>{field.label}</label>
                    <InputNumber
                        inputId={field.name}
                        value={values[field.name]}
                        onValueChange={(e) => setField(field.name, e.value)}
                        min={field.min}
                        max={field.max}
                        step={field.step ?? 1}
                        minFractionDigits={field.fractionDigits}
                        maxFractionDigits={field.fractionDigits}
                        showButtons={field.showButtons}
                    />
                </div>
            );
        }

        if (field.kind === 'range') {
            const range = values[field.name] || { min: 0, max: 0 };
            return (
                <div key={field.name} className="config-dialog__field">
                    <label>{field.label}</label>
                    <div className="config-dialog__range">
                        <div>
                            <span>Min</span>
                            <InputNumber
                                value={range.min}
                                onValueChange={(e) => setField(field.name, { ...range, min: e.value })}
                                min={field.min}
                                step={field.step ?? 1}
                            />
                        </div>
                        <div>
                            <span>Max</span>
                            <InputNumber
                                value={range.max}
                                onValueChange={(e) => setField(field.name, { ...range, max: e.value })}
                                max={field.max}
                                step={field.step ?? 1}
                            />
                        </div>
                    </div>
                </div>
            );
        }

        if (field.kind === 'select') {
            return (
                <div key={field.name} className="config-dialog__field">
                    <label>{field.label}</label>
                    <SelectButton
                        value={values[field.name]}
                        options={field.options}
                        onChange={(e) => setField(field.name, e.value)}
                        unselectable={false}
                    />
                </div>
            );
        }

        return null;
    };

    const footer = (
        <div className="config-dialog__footer">
            <Button label="Cancel" outlined onClick={onHide} />
            <Button label="Save changes" onClick={() => onSave?.(values)} />
        </div>
    );

    return (
        <Dialog
            visible={visible}
            onHide={onHide}
            header={title}
            footer={footer}
            modal
            style={{ width: '560px' }}
            breakpoints={{ '960px': '85vw', '641px': '95vw' }}
            className="config-dialog"
        >
            {tags.length > 0 ? (
                <div className="config-dialog__tags">
                    {tags.map((tag) => <Tag key={tag} value={tag} rounded />)}
                </div>
            ) : null}

            {description ? <p className="config-dialog__desc">{description}</p> : null}

            <div className="config-dialog__body">
                {schema.map(renderField)}
            </div>
        </Dialog>
    );
};

export default ConfigureDialog;
