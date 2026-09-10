import React from 'react';
import Link from "next/link";

const Help = () => {
    return (
        <div className="dashboard-page">
            <section className="dashboard-banner">
                <div className="dashboard-banner__copy">
                    <h1>MaaSAI Help</h1>
                    <p>
                        The MaaSAI project aims to revolutionise the manufacturing process by facilitating access to a
                        Manufacturing as a Service business model through autonomous AI.
                    </p>
                </div>
                <Link href="/" className="dashboard-banner__button">
                    <span>Back to Home</span>
                </Link>
            </section>

            <section className="dashboard-actions">
                <div className="dashboard-section-label">Overview</div>
                <div className="dashboard-banner">
                    <div className="dashboard-banner__copy">
                        <p>
                            MaaSAI reduces the investment required to set up and maintain operations by enabling
                            on-demand manufacturing through autonomous agents that negotiate manufacturing capacity
                            between providers and consumers dynamically.
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Help;
