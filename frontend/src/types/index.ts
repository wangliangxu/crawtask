export interface Node {
    id: number;
    name: string;
    host: string;
    port: number;
    username?: string;
    ssh_key_path?: string;
    // Password is write-only typically
    is_center?: boolean;
}

export interface NodeCreate {
    name: string;
    host: string;
    port?: number;
    username?: string;
    password?: string;
    ssh_key_path?: string;
    is_center?: boolean;
}

export interface HealthRule {
    id?: number;
    rule_type: 'keyword' | 'latency' | 'regex';
    rule_content: string;
}

export interface Task {
    id: number;
    node_id?: number;
    name: string;
    log_file_path: string;
    start_command?: string;
    stop_command?: string;
    check_interval?: number;
    status?: 'running' | 'stopped' | 'unknown';
    health_status?: 'healthy' | 'warning' | 'error' | 'unknown';
    last_check_time?: string;
    last_log_time?: string;
    is_enabled?: boolean;
    health_rules: HealthRule[];
}

export interface TaskCreate {
    name: string;
    node_ids: number[];
    log_file_path: string;
    start_command?: string;
    stop_command?: string;
    check_interval?: number;
    is_enabled?: boolean;
    health_rules: HealthRule[];
}

export interface SystemSettings {
    inspection_interval: number;
}
