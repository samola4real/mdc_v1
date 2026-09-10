import { useEffect, useRef, useState } from 'react';

/**
 * useLiveData — generic real-time data subscription.
 *
 * This hook is the cornerstone of any MaaSAI dashboard that needs to react
 * to live telemetry: production KPIs, agent state, sensor readings, alarms.
 * The implementation here is a MOCK that periodically calls `mockGenerator`
 * to keep the UI alive without a backend. Swap the body of the `useEffect`
 * for your real transport (WebSocket, SSE, MQTT, polling).
 *
 * Returned shape:
 *   {
 *     data,        // latest payload (whatever your generator returns)
 *     history,     // rolling buffer of past payloads (last `historySize` items)
 *     connected,   // boolean — true while subscribed
 *     error,       // last error from the subscription, if any
 *     lastUpdate,  // ms timestamp of last data update
 *     latency      // estimated ms since last update (UI badge)
 *   }
 *
 * Example — REST polling:
 *   useLiveData(`/api/machines/${id}`, {
 *       fetcher: () => fetch(`/api/machines/${id}`).then(r => r.json()),
 *       interval: 2000
 *   });
 *
 * Example — WebSocket (replace the mock block below):
 *   const ws = new WebSocket(`wss://broker/${topic}`);
 *   ws.onopen    = () => setConnected(true);
 *   ws.onmessage = e => { setData(JSON.parse(e.data)); setLastUpdate(Date.now()); };
 *   ws.onclose   = () => setConnected(false);
 *   ws.onerror   = setError;
 *   return () => ws.close();
 *
 * Example — MQTT with mqtt.js:
 *   const client = mqtt.connect('wss://broker.maasai-srv.cigip.upv.es');
 *   client.on('connect', () => { setConnected(true); client.subscribe(topic); });
 *   client.on('message', (_, payload) => {
 *       setData(JSON.parse(payload.toString()));
 *       setLastUpdate(Date.now());
 *   });
 *   client.on('error', setError);
 *   return () => client.end();
 */
export const useLiveData = (topic, options = {}) => {
    const {
        mockGenerator,
        fetcher,
        interval = 1500,
        historySize = 30,
        enabled = true
    } = options;

    const [data, setData] = useState(null);
    const [history, setHistory] = useState([]);
    const [connected, setConnected] = useState(false);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [latency, setLatency] = useState(0);

    // Keep history size bound without re-allocating each tick.
    const historyRef = useRef([]);
    historyRef.current = history;

    useEffect(() => {
        if (!enabled) return undefined;

        setConnected(true);
        setError(null);

        const push = (payload) => {
            if (payload == null) return;
            const now = Date.now();
            setData(payload);
            setLastUpdate(now);
            setHistory((prev) => {
                const next = [...prev, { t: now, v: payload }];
                return next.length > historySize ? next.slice(-historySize) : next;
            });
        };

        const tick = async () => {
            try {
                if (fetcher) {
                    push(await fetcher(topic));
                } else if (mockGenerator) {
                    push(mockGenerator(topic, historyRef.current));
                }
            } catch (err) {
                setError(err);
                setConnected(false);
            }
        };

        // Emit immediately so the UI never shows "—" on first paint.
        tick();
        const id = setInterval(tick, interval);

        return () => {
            clearInterval(id);
            setConnected(false);
        };
    }, [topic, interval, enabled, mockGenerator, fetcher, historySize]);

    // Recompute latency every 500 ms so the staleness indicator stays fresh
    // even between data ticks.
    useEffect(() => {
        if (!lastUpdate) return undefined;
        const id = setInterval(() => setLatency(Date.now() - lastUpdate), 500);
        return () => clearInterval(id);
    }, [lastUpdate]);

    return { data, history, connected, error, lastUpdate, latency };
};
