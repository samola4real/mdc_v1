import React from 'react';

/**
 * Left-rail palette of draggable node types. Each item exposes its `type`
 * via the dataTransfer payload — the canvas reads it on drop and creates
 * a matching React Flow node.
 */
const DesignerPalette = ({ groups = [], onAddNode }) => {
    const onDragStart = (event, kind) => {
        event.dataTransfer.setData('application/maasai-node', kind);
        event.dataTransfer.effectAllowed = 'move';
    };

    return (
        <aside className="designer-palette">
            <header>
                <strong>Components</strong>
                <span>Drag onto the canvas</span>
            </header>

            {groups.map((group) => (
                <section key={group.label}>
                    <h3>{group.label}</h3>
                    <ul>
                        {group.items.map((item) => (
                            <li key={item.kind}>
                                <button
                                    type="button"
                                    className={`designer-palette__item designer-palette__item--${item.tone || 'navy'}`}
                                    draggable
                                    onDragStart={(e) => onDragStart(e, item.kind)}
                                    onClick={() => onAddNode?.(item.kind)}
                                >
                                    <span className="designer-palette__icon"><i className={item.icon} /></span>
                                    <div>
                                        <strong>{item.label}</strong>
                                        {item.description ? <span>{item.description}</span> : null}
                                    </div>
                                </button>
                            </li>
                        ))}
                    </ul>
                </section>
            ))}
        </aside>
    );
};

export default DesignerPalette;
