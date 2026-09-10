import { Chart } from 'primereact/chart';
import React, { useContext, useDeferredValue, useEffect, useState } from 'react';
import { LayoutContext } from '@/layout/context/layoutcontext';

const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July'];
const radarLabels = ['Eating', 'Drinking', 'Sleeping', 'Designing', 'Coding', 'Cycling', 'Running'];
const ganttColumns = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10', 'W11', 'W12'];

const ganttTasks = [
    { id: 1, title: 'Requirements workshop', owner: 'Operations', status: 'Completed', start: 1, span: 2, tone: 'green' },
    { id: 2, title: 'Data pipeline design', owner: 'Data Team', status: 'In progress', start: 2, span: 3, tone: 'blue' },
    { id: 3, title: 'Model training batch', owner: 'AI Team', status: 'In progress', start: 4, span: 4, tone: 'purple' },
    { id: 4, title: 'PLC integration tests', owner: 'Automation', status: 'Blocked', start: 6, span: 2, tone: 'red' },
    { id: 5, title: 'Operator dashboard QA', owner: 'QA Lab', status: 'Planned', start: 7, span: 3, tone: 'orange' },
    { id: 6, title: 'Go-live preparation', owner: 'PMO', status: 'Planned', start: 9, span: 3, tone: 'teal' }
];

const chartCards = [
    { key: 'line', title: 'Linear Chart', type: 'line', badge: 'Line', badgeTone: 'blue' },
    { key: 'bar', title: 'Bar Chart', type: 'bar', badge: 'Bar', badgeTone: 'purple' },
    { key: 'pie', title: 'Pie Chart', type: 'pie', badge: 'Pie', badgeTone: 'green' },
    { key: 'doughnut', title: 'Doughnut Chart', type: 'doughnut', badge: 'Doughnut', badgeTone: 'teal' },
    { key: 'polar', title: 'Polar Area Chart', type: 'polarArea', badge: 'Polar', badgeTone: 'orange' },
    { key: 'radar', title: 'Radar Chart', type: 'radar', badge: 'Radar', badgeTone: 'red' }
];

const colorPalette = {
    blue: '#4A8FD9',
    purple: '#8B5DAA',
    teal: '#2BA8A0',
    orange: '#E8903E',
    green: '#6B9E3A',
    red: '#E06040'
};

const badgeClassByTone = {
    blue: 'charts-card__badge--blue',
    purple: 'charts-card__badge--purple',
    teal: 'charts-card__badge--teal',
    orange: 'charts-card__badge--orange',
    green: 'charts-card__badge--green',
    red: 'charts-card__badge--red'
};

const ChartDemo = () => {
    const [options, setOptions] = useState({});
    const [data, setChartData] = useState({});
    const [search, setSearch] = useState('');
    const deferredSearch = useDeferredValue(search);
    const { layoutConfig } = useContext(LayoutContext);

    useEffect(() => {
        const documentStyle = getComputedStyle(document.documentElement);
        const textColor = documentStyle.getPropertyValue('--text-dark').trim() || '#333333';
        const textMuted = documentStyle.getPropertyValue('--text-medium').trim() || '#666666';
        const subtleGrid = 'rgba(0, 0, 0, 0.04)';
        const commonLegend = {
            position: 'top',
            labels: {
                usePointStyle: true,
                pointStyle: 'circle',
                boxWidth: 8,
                boxHeight: 8,
                padding: 18,
                color: textMuted,
                font: {
                    family: "'Source Sans 3', sans-serif",
                    size: 12,
                    weight: '600'
                }
            }
        };

        const tooltip = {
            enabled: true,
            backgroundColor: 'rgba(26, 37, 47, 0.92)',
            titleColor: '#FFFFFF',
            bodyColor: '#F8FAFC',
            padding: 12,
            displayColors: true,
            cornerRadius: 10
        };

        const commonCartesianScales = {
            x: {
                border: {
                    display: false
                },
                ticks: {
                    color: textMuted,
                    padding: 10,
                    font: {
                        family: "'Source Sans 3', sans-serif",
                        size: 12,
                        weight: '500'
                    }
                },
                grid: {
                    color: subtleGrid,
                    drawBorder: false
                }
            },
            y: {
                beginAtZero: true,
                border: {
                    display: false
                },
                ticks: {
                    color: textMuted,
                    padding: 12,
                    font: {
                        family: "'Source Sans 3', sans-serif",
                        size: 12,
                        weight: '500'
                    }
                },
                grid: {
                    color: subtleGrid,
                    drawBorder: false
                }
            }
        };

        const lineData = {
            labels: months,
            datasets: [
                {
                    label: 'First Dataset',
                    data: [65, 59, 80, 81, 56, 55, 40],
                    fill: true,
                    tension: 0.42,
                    borderColor: colorPalette.blue,
                    backgroundColor: 'rgba(74, 143, 217, 0.16)',
                    pointBackgroundColor: colorPalette.blue,
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 2,
                    pointHoverRadius: 8,
                    pointHoverBorderWidth: 3,
                    pointRadius: 5
                },
                {
                    label: 'Second Dataset',
                    data: [28, 48, 40, 19, 86, 27, 90],
                    fill: true,
                    tension: 0.42,
                    borderColor: colorPalette.purple,
                    backgroundColor: 'rgba(139, 93, 170, 0.14)',
                    pointBackgroundColor: colorPalette.purple,
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 2,
                    pointHoverRadius: 8,
                    pointHoverBorderWidth: 3,
                    pointRadius: 5
                }
            ]
        };

        const barData = {
            labels: months,
            datasets: [
                {
                    label: 'My First Dataset',
                    backgroundColor: colorPalette.blue,
                    borderRadius: 8,
                    borderSkipped: false,
                    maxBarThickness: 20,
                    data: [65, 59, 80, 81, 56, 55, 40]
                },
                {
                    label: 'My Second Dataset',
                    backgroundColor: colorPalette.purple,
                    borderRadius: 8,
                    borderSkipped: false,
                    maxBarThickness: 20,
                    data: [28, 48, 40, 19, 86, 27, 90]
                }
            ]
        };

        const pieData = {
            labels: ['A', 'B', 'C'],
            datasets: [
                {
                    data: [540, 325, 702],
                    backgroundColor: [colorPalette.blue, colorPalette.purple, colorPalette.teal],
                    hoverBackgroundColor: [colorPalette.blue, colorPalette.purple, colorPalette.teal],
                    borderColor: '#FFFFFF',
                    borderWidth: 2,
                    hoverOffset: 8
                }
            ]
        };

        const polarData = {
            labels: ['Indigo', 'Purple', 'Teal', 'Orange'],
            datasets: [
                {
                    data: [11, 16, 7, 14],
                    backgroundColor: [
                        'rgba(74, 143, 217, 0.60)',
                        'rgba(139, 93, 170, 0.55)',
                        'rgba(43, 168, 160, 0.55)',
                        'rgba(232, 144, 62, 0.48)'
                    ],
                    borderWidth: 0,
                    hoverOffset: 8
                }
            ]
        };

        const radarData = {
            labels: radarLabels,
            datasets: [
                {
                    label: 'My First Dataset',
                    data: [65, 59, 90, 81, 56, 55, 40],
                    borderColor: colorPalette.blue,
                    backgroundColor: 'rgba(74, 143, 217, 0.18)',
                    pointBackgroundColor: colorPalette.blue,
                    pointBorderColor: '#FFFFFF',
                    pointHoverBackgroundColor: '#FFFFFF',
                    pointHoverBorderColor: colorPalette.blue,
                    pointRadius: 4,
                    pointHoverRadius: 7
                },
                {
                    label: 'My Second Dataset',
                    data: [28, 48, 40, 19, 96, 27, 100],
                    borderColor: colorPalette.purple,
                    backgroundColor: 'rgba(139, 93, 170, 0.14)',
                    pointBackgroundColor: colorPalette.purple,
                    pointBorderColor: '#FFFFFF',
                    pointHoverBackgroundColor: '#FFFFFF',
                    pointHoverBorderColor: colorPalette.purple,
                    pointRadius: 4,
                    pointHoverRadius: 7
                }
            ]
        };

        setChartData({
            line: lineData,
            bar: barData,
            pie: pieData,
            doughnut: pieData,
            polar: polarData,
            radar: radarData
        });

        setOptions({
            line: {
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: commonLegend,
                    tooltip
                },
                scales: commonCartesianScales
            },
            bar: {
                maintainAspectRatio: false,
                plugins: {
                    legend: commonLegend,
                    tooltip
                },
                scales: commonCartesianScales
            },
            pie: {
                maintainAspectRatio: false,
                plugins: {
                    legend: commonLegend,
                    tooltip
                }
            },
            doughnut: {
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: commonLegend,
                    tooltip
                }
            },
            polar: {
                maintainAspectRatio: false,
                plugins: {
                    legend: commonLegend,
                    tooltip
                },
                scales: {
                    r: {
                        border: {
                            display: false
                        },
                        angleLines: {
                            color: subtleGrid
                        },
                        grid: {
                            color: subtleGrid
                        },
                        ticks: {
                            color: textMuted,
                            backdropColor: 'transparent',
                            padding: 8
                        },
                        pointLabels: {
                            color: textMuted,
                            font: {
                                family: "'Source Sans 3', sans-serif",
                                size: 12,
                                weight: '600'
                            }
                        }
                    }
                }
            },
            radar: {
                maintainAspectRatio: false,
                plugins: {
                    legend: commonLegend,
                    tooltip
                },
                scales: {
                    r: {
                        border: {
                            display: false
                        },
                        angleLines: {
                            color: subtleGrid
                        },
                        grid: {
                            color: subtleGrid
                        },
                        ticks: {
                            color: textMuted,
                            backdropColor: 'transparent',
                            showLabelBackdrop: false,
                            padding: 8
                        },
                        pointLabels: {
                            color: textMuted,
                            font: {
                                family: "'Source Sans 3', sans-serif",
                                size: 12,
                                weight: '600'
                            }
                        }
                    }
                }
            }
        });
    }, [layoutConfig]);

    const filteredTasks = ganttTasks.filter((task) => {
        const query = deferredSearch.trim().toLowerCase();
        if (!query) {
            return true;
        }

        return [task.title, task.owner, task.status].some((value) => value.toLowerCase().includes(query));
    });

    return (
        <div className="charts-page">
            <div className="charts-page__header">
                <h1>Charts</h1>
                <p>Visual examples of the chart types available in the platform.</p>
            </div>

            <section className="charts-grid">
                {chartCards.map((card, index) => (
                    <article
                        key={card.key}
                        className="charts-card"
                        style={{ animationDelay: `${0.08 + index * 0.06}s` }}
                    >
                        <div className="charts-card__topbar">
                            <h2>{card.title}</h2>
                            <span className={`charts-card__badge ${badgeClassByTone[card.badgeTone]}`}>{card.badge}</span>
                        </div>
                        <div className="charts-card__canvas">
                            <Chart type={card.type} data={data[card.key]} options={options[card.key]} />
                        </div>
                    </article>
                ))}
            </section>

            <section className="gantt-card">
                <div className="gantt-card__header">
                    <div>
                        <h2>Production Schedule</h2>
                        <p>Invented planning data for an industrial AI deployment program.</p>
                    </div>
                    <label className="gantt-card__search">
                        <span>Search tasks</span>
                        <input
                            type="search"
                            value={search}
                            onChange={(event) => setSearch(event.target.value)}
                            placeholder="Filter by task, owner or status"
                        />
                    </label>
                </div>

                <div className="gantt-board">
                    <div className="gantt-board__head">
                        <div className="gantt-board__task-label">Task</div>
                        <div className="gantt-board__timeline-labels">
                            {ganttColumns.map((column) => (
                                <span key={column}>{column}</span>
                            ))}
                        </div>
                    </div>

                    <div className="gantt-board__body">
                        {filteredTasks.length === 0 ? (
                            <div className="gantt-board__empty">No tasks match the current search.</div>
                        ) : (
                            filteredTasks.map((task) => (
                                <div key={task.id} className="gantt-row">
                                    <div className="gantt-row__meta">
                                        <strong>{task.title}</strong>
                                        <span>{task.owner}</span>
                                    </div>
                                    <div className="gantt-row__timeline">
                                        {ganttColumns.map((column) => (
                                            <span key={`${task.id}-${column}`} className="gantt-row__cell" aria-hidden="true" />
                                        ))}
                                        <div
                                            className={`gantt-row__bar gantt-row__bar--${task.tone}`}
                                            style={{ gridColumn: `${task.start} / span ${task.span}` }}
                                        >
                                            <span>{task.status}</span>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </section>
        </div>
    );
};

export default ChartDemo;
