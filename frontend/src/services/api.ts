import axios from 'axios';
import type { Node, NodeCreate, Task, TaskCreate, SystemSettings } from '../types';

const api = axios.create({
    baseURL: 'http://localhost:8000/api',
});

export const getNodes = async () => (await api.get<Node[]>('/nodes/')).data;
export const createNode = async (data: NodeCreate) => (await api.post<Node>('/nodes/', data)).data;
export const updateNode = async (id: number, data: Partial<NodeCreate>) => (await api.put<Node>(`/nodes/${id}`, data)).data;
export const deleteNode = async (id: number) => (await api.delete(`/nodes/${id}`)).data;
export const testNodeConnection = async (data: NodeCreate) => (await api.post<{ status: string; message: string }>('/nodes/test-connection', data)).data;
export const testNodeConnectionById = async (id: number) => (await api.post<{ status: string; message: string }>(`/nodes/${id}/test-connection`)).data;

export const getTasks = async () => (await api.get<Task[]>('/tasks/')).data;
export const createTask = async (data: TaskCreate) => (await api.post<Task[]>('/tasks/', data)).data;
export const updateTask = async (id: number, data: Partial<TaskCreate>) => (await api.put<Task>(`/tasks/${id}`, data)).data;
export const deleteTask = async (id: number) => (await api.delete(`/tasks/${id}`)).data;
export const getTask = async (id: number) => (await api.get<Task>(`/tasks/${id}`)).data;


export const executeTaskAction = async (id: number, action: string) =>
    (await api.post(`/tasks/${id}/action`, { action })).data;

export const getSystemSettings = async () => (await api.get<SystemSettings>('/system/settings')).data;
export const updateSystemSettings = async (data: SystemSettings) => (await api.post<SystemSettings>('/system/settings', data)).data;
