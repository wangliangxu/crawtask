import React, { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';

interface LogTerminalProps {
    taskId: number;
}

const LogTerminal: React.FC<LogTerminalProps> = ({ taskId }) => {
    const terminalRef = useRef<HTMLDivElement>(null);
    const xtermRef = useRef<Terminal | null>(null);
    const fitAddonRef = useRef<FitAddon | null>(null);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!terminalRef.current) return;

        // Initialize Terminal
        const term = new Terminal({
            cursorBlink: true,
            theme: {
                background: '#1e1e1e',
                foreground: '#ffffff',
            },
            fontFamily: 'Menlo, Monaco, "Courier New", monospace',
            fontSize: 12,
        });

        const fitAddon = new FitAddon();
        term.loadAddon(fitAddon);

        term.open(terminalRef.current);
        fitAddon.fit();

        xtermRef.current = term;
        fitAddonRef.current = fitAddon;

        // Connect WS
        const wsUrl = `ws://localhost:8000/api/tasks/${taskId}/log_stream`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            // term.writeln('\r\n\x1b[32m--- Connected to Log Stream ---\x1b[0m\r\n');
        };

        ws.onmessage = (event) => {
            term.writeln(event.data);
            // Ensure we catch up to live logs if we were at the bottom? 
            // Xterm default behavior is usually fine, but let's leave it as is for now.
        };

        ws.onclose = () => {
            // term.writeln('\r\n\x1b[31m--- Connection Closed ---\x1b[0m\r\n');
        };

        ws.onerror = () => {
            // term.writeln(`\r\n\x1b[31m--- Connection Error ---\x1b[0m\r\n`);
        };

        wsRef.current = ws;

        // Resize observer
        const resizeObserver = new ResizeObserver(() => {
            fitAddon.fit();
        });
        resizeObserver.observe(terminalRef.current);

        return () => {
            if (ws.readyState === 1) ws.close();
            term.dispose();
            resizeObserver.disconnect();
        };
    }, [taskId]);

    return <div ref={terminalRef} style={{ width: '100%', height: '100%' }} />;
};

export default LogTerminal;
