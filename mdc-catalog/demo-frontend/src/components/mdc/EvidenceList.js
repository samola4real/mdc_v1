import React from 'react';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';

const EvidenceList = ({ evidence = [], unknown = [], warnings = [], advanced = [] }) => {
    return (
        <div className="flex flex-column gap-3">
            <div>
                <div className="font-semibold text-900 mb-2">Evidence</div>
                <ul className="m-0 pl-3 text-700 line-height-3">
                    {evidence.map((item) => (
                        <li key={item}>{item}</li>
                    ))}
                </ul>
            </div>
            {unknown.length > 0 ? (
                <div>
                    <div className="font-semibold text-900 mb-2">Unknown evidence</div>
                    <ul className="m-0 pl-3 text-700 line-height-3">
                        {unknown.map((item) => (
                            <li key={item}>{item}</li>
                        ))}
                    </ul>
                </div>
            ) : null}
            {warnings.length > 0 ? (
                <div className="flex flex-column gap-2">
                    {warnings.map((warning) => (
                        <Message
                            key={warning}
                            severity="warn"
                            text={warning}
                            className="w-full justify-content-start"
                        />
                    ))}
                </div>
            ) : null}
            {advanced.length > 0 ? (
                <Panel header="Advanced/debug" toggleable collapsed>
                    <ul className="m-0 pl-3 text-700 line-height-3">
                        {advanced.map((item) => (
                            <li key={item}>{item}</li>
                        ))}
                    </ul>
                </Panel>
            ) : null}
        </div>
    );
};

export default EvidenceList;
