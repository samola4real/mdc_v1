import React, { useMemo, useRef, useState } from 'react';
import { Toast } from 'primereact/toast';
import { Button } from 'primereact/button';
import { Chart } from 'primereact/chart';
import { Sidebar } from 'primereact/sidebar';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import StatusStrip from '@/components/StatusStrip';
import KpiCard from '@/components/KpiCard';
import FilterBar from '@/components/FilterBar';
import Sparkline from '@/components/Sparkline';


const DIMENSIONS = ['Production line', 'Product family', 'Shift', 'Operator'];
const GRANULARITIES = ['Hour', 'Day', 'Week', 'Month'];

const MOCK_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const series = {
    throughput:    [142, 160, 154, 178, 190, 184, 210, 220, 215, 232, 245, 258],
    energy:        [3.4, 3.6, 3.5, 3.8, 3.7, 3.9, 4.1, 4.3, 4.2, 4.0, 4.4, 4.5],
    oee:           [72, 74, 78, 80, 82, 81, 84, 85, 83, 86, 88, 87],
    reuseRate:     [22, 24, 26, 28, 30, 33, 35, 36, 38, 40, 42, 44]
};

const detailRows = [
    { id: 1, line: 'Line A', batch: 'B-1842', units: 1200, defects: 14, oee: 0.84, energy: 412 },
    { id: 2, line: 'Line A', batch: 'B-1843', units: 1180, defects: 12, oee: 0.83, energy: 405 },
    { id: 3, line: 'Line B', batch: 'B-1844', units: 1010, defects: 22, oee: 0.79, energy: 376 },
    { id: 4, line: 'Line B', batch: 'B-1845', units: 1140, defects: 16, oee: 0.86, energy: 388 },
    { id: 5, line: 'Line C', batch: 'B-1846', units: 1290, defects:  9, oee: 0.91, energy: 432 },
    { id: 6, line: 'Line C', batch: 'B-1847', units: 1310, defects: 11, oee: 0.90, energy: 441 }
];

/* ------------------------------------------------------------ */

const Analytics = () => {
    const toast = useRef(null);
    const [filters, setFilters] = useState({
        range: null,
        dimension: 'Production line',
        granularity: 'Month'
    });
    const [drillOpen, setDrillOpen] = useState(false);
    const [drillTitle, setDrillTitle] = useState('');

    /* Chart configs — colours come from the brand palette. */
    const chartData = useMemo(() => ({
        throughput: {
            labels: MOCK_MONTHS,
            datasets: [{
                label: 'Units / hour',
                data: series.throughput,
                borderColor: '#223F61',
                backgroundColor: 'rgba(34, 63, 97, 0.14)',
                tension: 0.35,
                fill: true,
                pointBackgroundColor: '#223F61'
            }]
        },
        energy: {
            labels: MOCK_MONTHS,
            datasets: [{
                label: 'MWh / day',
                data: series.energy,
                backgroundColor: '#E78C3A',
                borderRadius: 6,
                maxBarThickness: 22
            }]
        },
        oee: {
            labels: MOCK_MONTHS,
            datasets: [{
                label: 'OEE %',
                data: series.oee,
                borderColor: '#2BA86F',
                backgroundColor: 'rgba(43, 168, 111, 0.14)',
                tension: 0.35,
                fill: true,
                pointBackgroundColor: '#2BA86F'
            }]
        },
        mix: {
            labels: ['Line A', 'Line B', 'Line C'],
            datasets: [{
                data: [42, 31, 27],
                backgroundColor: ['#223F61', '#E78C3A', '#D8D1BE'],
                borderWidth: 0,
                hoverOffset: 8
            }]
        }
    }), []);

    const baseOptions = {
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } },
        scales: {
            x: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { color: '#666' } },
            y: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { color: '#666' } }
        }
    };

    const openDrill = (label) => {
        setDrillTitle(label);
        setDrillOpen(true);
        toast.current?.show({ severity: 'info', summary: 'Drill-down', detail: `${label} — showing detail rows`, life: 1500 });
    };

    const exportCsv = () => {
        toast.current?.show({ severity: 'success', summary: 'Exported', detail: 'CSV download started.', life: 1800 });
    };

    return (
        <div className="analytics-page">
            <Toast ref={toast} position="top-right" />

            <StatusStrip
                connection={{ label: 'Warehouse', value: 'Synced', tone: 'ok' }}
                pills={[
                    { label: 'Records analysed', value: '12.4k', tone: 'info' },
                    { label: 'Last refresh',     value: '2m', tone: 'muted' }
                ]}
            />

            <section className="analytics-hero">
                <div>
                    <span className="analytics-hero__tag">Workspace · Analytics</span>
                    <h1>Operations analytics</h1>
                    <p>
                        Explore throughput, energy and OEE across lines and shifts. Click any chart
                        to drill down into the underlying batches and export the data.
                    </p>
                </div>
            </section>

            <FilterBar
                values={filters}
                onChange={setFilters}
                filters={[
                    { name: 'range',       kind: 'daterange', label: 'Period' },
                    { name: 'dimension',   kind: 'dropdown',  label: 'Group by',     options: DIMENSIONS, clearable: true },
                    { name: 'granularity', kind: 'dropdown',  label: 'Granularity',  options: GRANULARITIES }
                ]}
                actions={
                    <>
                        <Button label="Apply" icon="pi pi-filter" />
                        <Button label="Export CSV" icon="pi pi-download" outlined onClick={exportCsv} />
                    </>
                }
            />

            <section className="analytics-kpis">
                <KpiCard icon="pi pi-bolt"        label="Avg throughput"   value="198 u/h" tone="navy"   sublabel="↑ 8% vs last period" />
                <KpiCard icon="pi pi-chart-line"  label="OEE"              value="84%"     tone="ok"     sublabel="Target: 85%" />
                <KpiCard icon="pi pi-sun"         label="Energy intensity" value="0.42 kWh/u" tone="orange" sublabel="↓ 3% vs last period" />
                <KpiCard icon="pi pi-replay"      label="Reuse rate"       value="38%"     tone="sand"   sublabel="R3 toolkit" />
            </section>

            <section className="analytics-grid">
                <article className="analytics-card analytics-card--wide" onClick={() => openDrill('Throughput')}>
                    <header>
                        <h2>Throughput</h2>
                        <span>Units per hour · {filters.granularity}</span>
                    </header>
                    <div className="analytics-card__chart">
                        <Chart type="line" data={chartData.throughput} options={baseOptions} />
                    </div>
                </article>

                <article className="analytics-card" onClick={() => openDrill('Energy')}>
                    <header>
                        <h2>Energy use</h2>
                        <span>MWh / day</span>
                    </header>
                    <div className="analytics-card__chart">
                        <Chart type="bar" data={chartData.energy} options={baseOptions} />
                    </div>
                </article>

                <article className="analytics-card" onClick={() => openDrill('OEE')}>
                    <header>
                        <h2>OEE trend</h2>
                        <span>Overall equipment effectiveness</span>
                    </header>
                    <div className="analytics-card__chart">
                        <Chart type="line" data={chartData.oee} options={baseOptions} />
                    </div>
                </article>

                <article className="analytics-card" onClick={() => openDrill('Output mix')}>
                    <header>
                        <h2>Output mix</h2>
                        <span>By production line</span>
                    </header>
                    <div className="analytics-card__chart analytics-card__chart--narrow">
                        <Chart type="doughnut" data={chartData.mix} options={{
                            maintainAspectRatio: false,
                            cutout: '62%',
                            plugins: { legend: { position: 'right' } }
                        }} />
                    </div>
                </article>

                <article className="analytics-card analytics-card--strip" onClick={() => openDrill('Reuse rate')}>
                    <header>
                        <h2>Reuse rate</h2>
                        <span>R3 toolkit — last 12 months</span>
                    </header>
                    <div className="analytics-card__sparkrow">
                        <Sparkline
                            data={series.reuseRate}
                            width={420}
                            height={88}
                            color="#E78C3A"
                            responsive
                        />
                        <strong>{series.reuseRate.at(-1)}%</strong>
                    </div>
                </article>
            </section>

            <Sidebar visible={drillOpen} onHide={() => setDrillOpen(false)} position="right" className="analytics-drawer">
                <h2>{drillTitle}</h2>
                <p>Underlying records for the selected segment.</p>
                <DataTable value={detailRows} dataKey="id" stripedRows paginator rows={5} className="analytics-drawer__table">
                    <Column field="batch" header="Batch" sortable />
                    <Column field="line"  header="Line"  sortable />
                    <Column field="units" header="Units" sortable />
                    <Column field="defects" header="Defects" sortable />
                    <Column field="oee" header="OEE" body={(r) => `${Math.round(r.oee * 100)}%`} sortable />
                    <Column field="energy" header="Energy (kWh)" sortable />
                </DataTable>
                <Button label="Export this segment" icon="pi pi-download" onClick={exportCsv} />
            </Sidebar>
        </div>
    );
};

export default Analytics;
