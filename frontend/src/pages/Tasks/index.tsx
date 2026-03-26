import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, message, Space, Tag, Drawer, Select, Switch, Tabs } from 'antd';
import { PlusOutlined, DeleteOutlined, PlayCircleOutlined, StopOutlined, CodeOutlined, EditOutlined } from '@ant-design/icons';
import type { Task, Node } from '../../types';
import { getTasks, createTask, updateTask, deleteTask, executeTaskAction, getNodes } from '../../services/api';
import LogTerminal from '../../components/LogTerminal';

const TasksPage: React.FC = () => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [nodes, setNodes] = useState<Node[]>([]);
    const [loading, setLoading] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isLogOpen, setIsLogOpen] = useState(false);
    const [currentTaskId, setCurrentTaskId] = useState<number | null>(null);
    const [form] = Form.useForm();
    const [submitting, setSubmitting] = useState(false);
    const [editingTask, setEditingTask] = useState<Task | null>(null);
    const [activeTab, setActiveTab] = useState('all');

    const fetchData = async () => {
        setLoading(true);
        try {
            const [tasksData, nodesData] = await Promise.all([getTasks(), getNodes()]);
            setTasks(tasksData);
            setNodes(nodesData);
        } catch (error) {
            message.error('Failed to fetch data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        // Polling interaction for status updates (simple version)
        const interval = setInterval(() => {
            getTasks().then(setTasks).catch(() => { });
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleDelete = async (id: number) => {
        try {
            await deleteTask(id);
            message.success('Task deleted');
            fetchData();
        } catch (error) {
            message.error('Failed to delete task');
        }
    };

    const handleAction = async (id: number, action: string) => {
        try {
            message.loading({ content: `Executing ${action}...`, key: 'action' });
            await executeTaskAction(id, action);
            message.success({ content: `Action ${action} successful`, key: 'action' });
            fetchData();
        } catch (error: any) {
            message.error({ content: `Action failed: ${error.response?.data?.detail}`, key: 'action' });
        }
    };

    const handleToggleEnabled = async (id: number, enabled: boolean) => {
        try {
            await updateTask(id, { is_enabled: enabled });
            message.success(`Task ${enabled ? 'enabled' : 'disabled'}`);
            fetchData();
        } catch (error) {
            message.error('Failed to update task status');
        }
    };

    const handleToggleGroupEnabled = async (name: string, enabled: boolean) => {
        try {
            const groupTasks = tasks.filter(t => t.name === name);
            message.loading({ content: `Updating ${groupTasks.length} tasks...`, key: 'group_toggle' });
            
            await Promise.all(groupTasks.map(t => updateTask(t.id, { is_enabled: enabled })));
            
            message.success({ content: `All '${name}' tasks ${enabled ? 'enabled' : 'disabled'}`, key: 'group_toggle' });
            fetchData();
        } catch (error) {
            message.error({ content: `Failed to update tasks for '${name}'`, key: 'group_toggle' });
        }
    };

    const handleSave = async (values: any) => {
        setSubmitting(true);
        try {
            // Transform form data to match API (handle health rules if needed)
            const payload: any = {
                ...values,
                health_rules: values.health_keyword ? [{ rule_type: 'keyword', rule_content: values.health_keyword }] : []
            };

            if (editingTask) {
                await updateTask(editingTask.id, payload);
                message.success('Task updated');
            } else {
                await createTask(payload);
                message.success('Task created');
            }
            setIsModalOpen(false);
            setEditingTask(null);
            form.resetFields();
            fetchData();
        } catch (error) {
            message.error(editingTask ? 'Failed to update task' : 'Failed to create task');
        } finally {
            setSubmitting(false);
        }
    };

    const handleEdit = (task: Task) => {
        setEditingTask(task);
        // Extract health keyword if exists
        const healthKeyword = task.health_rules?.find(r => r.rule_type === 'keyword')?.rule_content;

        form.setFieldsValue({
            ...task,
            health_keyword: healthKeyword,
            node_ids: task.node_id ? [task.node_id] : [] // Assuming single node for edit for now, or handle appropriately
        });
        setIsModalOpen(true);
    };

    const uniqueNames = React.useMemo(() => {
        return Array.from(new Set(tasks.map(t => t.name)));
    }, [tasks]);

    const columns = [
        { title: 'ID', dataIndex: 'id', key: 'id' },
        { title: 'Name', dataIndex: 'name', key: 'name' },
        {
            title: 'Node',
            key: 'node',
            render: (_: any, record: Task) => {
                if (!record.node_id) return 'N/A';
                return nodes.find(n => n.id === record.node_id)?.name || record.node_id;
            }
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status?: string) => {
                const s = status || 'unknown';
                return (
                    <Tag color={s === 'running' ? 'green' : s === 'stopped' ? 'red' : 'default'}>
                        {s.toUpperCase()}
                    </Tag>
                );
            }
        },
        {
            title: 'Health',
            dataIndex: 'health_status',
            key: 'health_status',
            render: (status?: string) => {
                const s = status || 'unknown';
                return (
                    <Tag color={s === 'healthy' ? 'green' : s === 'error' ? 'red' : 'orange'}>
                        {s.toUpperCase()}
                    </Tag>
                );
            }
        },
        {
            title: 'Online',
            key: 'is_enabled',
            dataIndex: 'is_enabled',
            render: (val: boolean, record: Task) => (
                <Switch
                    checked={val !== false} // Default to true if undefined
                    onChange={(checked) => handleToggleEnabled(record.id, checked)}
                />
            )
        },
        {
            title: 'Last Log Time',
            dataIndex: 'last_log_time',
            key: 'last_log_time',
            render: (time: string | undefined, record: Task) => {
                if (!time) return '-';
                const date = new Date(time);
                const timeStr = date.toLocaleString();

                // Check if node is stopped and last log time is > 24h
                if (record.status === 'stopped') {
                    const now = new Date();
                    const diffMs = now.getTime() - date.getTime();
                    const diffHours = diffMs / (1000 * 60 * 60);

                    if (diffHours > 24) {
                        return <Tag color="green">{timeStr}</Tag>;
                    }
                }
                return timeStr;
            }
        },
        {
            title: 'Action',
            key: 'action',
            render: (_: any, record: Task) => (
                <Space size="small">
                    <Button
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(record)}
                    />
                    <Button
                        size="small"
                        icon={<PlayCircleOutlined />}
                        onClick={() => handleAction(record.id, 'start')}
                        disabled={record.status === 'running'}
                    />
                    <Button
                        size="small"
                        danger
                        icon={<StopOutlined />}
                        onClick={() => handleAction(record.id, 'stop')}
                        disabled={record.status === 'stopped'}
                    />
                    <Button
                        size="small"
                        icon={<CodeOutlined />}
                        onClick={() => {
                            setCurrentTaskId(record.id);
                            setIsLogOpen(true);
                        }}
                    >
                        Logs
                    </Button>
                    <Button
                        size="small"
                        icon={<DeleteOutlined />}
                        onClick={() => handleDelete(record.id)}
                    />
                </Space>
            ),
        },
    ];

    return (
        <div>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2>Task Management</h2>
                <Space>
                    {((uniqueNames.length === 1) || (uniqueNames.length > 1 && activeTab !== 'all')) && (() => {
                        const currentName = uniqueNames.length === 1 ? uniqueNames[0] : activeTab;
                        const groupTasks = tasks.filter(t => t.name === currentName);
                        const isAllEnabled = groupTasks.length > 0 && groupTasks.every(t => t.is_enabled !== false);
                        
                        return (
                            <div style={{ marginRight: 16 }}>
                                <span>Batch Toggle '{currentName}': </span>
                                <Switch 
                                    checked={isAllEnabled} 
                                    onChange={(checked) => handleToggleGroupEnabled(currentName, checked)} 
                                />
                            </div>
                        );
                    })()}
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
                        Add Task
                    </Button>
                </Space>
            </div>

            {uniqueNames.length > 1 && (
                <Tabs
                    activeKey={activeTab}
                    onChange={setActiveTab}
                    items={[
                        { key: 'all', label: 'All Tasks' },
                        ...uniqueNames.map(name => ({ key: name, label: name }))
                    ]}
                    style={{ marginBottom: 16 }}
                />
            )}

            <Table
                columns={columns}
                dataSource={activeTab === 'all' ? tasks : tasks.filter(t => t.name === activeTab)}
                rowKey="id"
                loading={loading}
            />

            {/* Create/Edit Modal */}
            <Modal
                title={editingTask ? "Edit Task" : "Add New Task"}
                open={isModalOpen}
                onCancel={() => {
                    setIsModalOpen(false);
                    setEditingTask(null);
                    form.resetFields();
                }}
                footer={null}
            >
                <Form layout="vertical" form={form} onFinish={handleSave}>
                    <Form.Item name="name" label="Task Name" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name="node_ids" label="Node" rules={[{ required: true }]}>
                        <Select mode="multiple" disabled={!!editingTask}>
                            {nodes.map(node => (
                                <Select.Option key={node.id} value={node.id}>
                                    {node.name} ({node.host})
                                </Select.Option>
                            ))}
                        </Select>
                    </Form.Item>
                    <Form.Item name="log_file_path" label="Log File Path" rules={[{ required: true }]}>
                        <Input placeholder="/var/log/app.log" />
                    </Form.Item>
                    <Form.Item name="start_command" label="Start Command">
                        <Input placeholder="systemctl start app" />
                    </Form.Item>
                    <Form.Item name="stop_command" label="Stop Command">
                        <Input placeholder="systemctl stop app" />
                    </Form.Item>
                    <Form.Item name="health_keyword" label="Health Check: Error Keyword">
                        <Input placeholder="Enter keyword to trigger Error status (e.g. Exception)" />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={submitting} block>
                            {editingTask ? "Update" : "Create"}
                        </Button>
                    </Form.Item>
                </Form>
            </Modal>


            {/* Log Viewer Drawer */}
            <Drawer
                title={`Live Logs (Task ID: ${currentTaskId})`}
                placement="bottom"
                height="60vh"
                onClose={() => setIsLogOpen(false)}
                open={isLogOpen}
                bodyStyle={{ padding: 0, backgroundColor: '#1e1e1e', overflow: 'hidden' }}
            >
                {isLogOpen && currentTaskId && (
                    <LogTerminal taskId={currentTaskId} />
                )}
            </Drawer>
        </div>
    );
};

export default TasksPage;
