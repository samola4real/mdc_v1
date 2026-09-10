import React from 'react';

/**
 * Tiny inline SVG sparkline. Use inside KPI cards / table cells to show the
 * recent trend of a metric without pulling a full chart library.
 *
 * @example
 *   <Sparkline data={[12, 14, 11, 18, 22, 19, 24]} color="#E78C3A" />
 */
const Sparkline = ({
    data = [],
    width = 96,
    height = 28,
    color = 'currentColor',
    fill = true,
    strokeWidth = 1.6,
    responsive = false   // when true, svg fills its container width via viewBox
}) => {
    if (!data.length) {
        const w = responsive ? '100%' : width;
        return <svg width={w} height={height} aria-hidden="true" />;
    }

    // We always compute geometry in the canonical `width` coordinate space and
    // let the viewBox stretch it to the container when responsive=true.
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    const stepX = data.length > 1 ? width / (data.length - 1) : 0;

    const points = data.map((v, i) => {
        const x = i * stepX;
        const y = height - ((v - min) / range) * (height - strokeWidth) - strokeWidth / 2;
        return [x, y];
    });

    const linePath = points.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`).join(' ');
    const areaPath = `${linePath} L${width},${height} L0,${height} Z`;

    return (
        <svg
            width={responsive ? '100%' : width}
            height={height}
            viewBox={`0 0 ${width} ${height}`}
            preserveAspectRatio={responsive ? 'none' : 'xMidYMid meet'}
            aria-hidden="true"
        >
            {fill ? <path d={areaPath} fill={color} opacity={0.12} /> : null}
            <path
                d={linePath}
                fill="none"
                stroke={color}
                strokeWidth={responsive ? strokeWidth * 1.3 : strokeWidth}
                strokeLinejoin="round"
                strokeLinecap="round"
                vectorEffect="non-scaling-stroke"
            />
        </svg>
    );
};

export default Sparkline;
