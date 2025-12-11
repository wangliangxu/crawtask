import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, InputNumber, message, Space, Checkbox, Tag } from 'antd';
import { PlusOutlined, DeleteOutlined, ApiOutlined, EditOutlined } from '@ant-design/icons';
import type { Node, NodeCreate } from '../../types';
import { getNodes, createNode, deleteNode, testNodeConnection, testNodeConnectionById, updateNode } from '../../services/api';

const NodesPage: React.FC = () => {
    const [nodes, setNodes] = useState<Node[]>([]);
    const [loading, setLoading] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [form] = Form.useForm();
    const [submitting, setSubmitting] = useState(false);
    const [testingConnection, setTestingConnection] = useState(false);
    const [testingNodeId, setTestingNodeId] = useState<number | null>(null);
    const [editingNode, setEditingNode] = useState<Node | null>(null);

    const fetchNodes = async () => {
        setLoading(true);
        try {
            const data = await getNodes();
            setNodes(data);
        } catch (error) {
            message.error('Failed to fetch nodes');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNodes();
    }, []);

    const handleDelete = async (id: number) => {
        try {
            await deleteNode(id);
            message.success('Node deleted');
            fetchNodes();
        } catch (error) {
            message.error('Failed to delete node');
        }
    };

    const handleSave = async (values: NodeCreate) => {
        setSubmitting(true);
        try {
            if (editingNode) {
                await updateNode(editingNode.id, values);
                message.success('Node updated');
            } else {
                await createNode(values);
                message.success('Node created');
            }
            setIsModalOpen(false);
            setEditingNode(null);
            form.resetFields();
            fetchNodes();
        } catch (error) {
            message.error(editingNode ? 'Failed to update node' : 'Failed to create node');
        } finally {
            setSubmitting(false);
        }
    };

    const handleEdit = (record: Node) => {
        setEditingNode(record);
        form.setFieldsValue({
            ...record,
            is_center: !!record.is_center, // Convert number to boolean for Checkbox
            password: '', // Don't fill password for security, make it optional
        });
        setIsModalOpen(true);
    };

    const handleCancel = () => {
        setIsModalOpen(false);
        setEditingNode(null);
        form.resetFields();
    };

    const handleTestConnection = async () => {
        try {
            // Validate fields required for connection (at least host)
            const values = await form.validateFields(['name', 'host', 'port', 'username', 'password', 'ssh_key_path', 'is_center']);
            setTestingConnection(true);
            const res = await testNodeConnection(values);
            message.success(res.message);
        } catch (error: any) {
            const msg = error.response?.data?.detail || 'Connection failed';
            message.error(msg);
        } finally {
            setTestingConnection(false);
        }
    };

    const handleTestNodeById = async (nodeId: number) => {
        setTestingNodeId(nodeId);
        try {
            const res = await testNodeConnectionById(nodeId);
            message.success(res.message);
        } catch (error: any) {
            const msg = error.response?.data?.detail || 'Connection failed';
            message.error(msg);
        } finally {
            setTestingNodeId(null);
        }
    };

    const columns = [
        { title: 'ID', dataIndex: 'id', key: 'id' },
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
            render: (text: string, record: Node) => (
                <Space>
                    {text}
                    {record.is_center && <Tag color="blue">Center Node</Tag>}
                </Space>
            ),
        },
        { title: 'Host', dataIndex: 'host', key: 'host' },
        { title: 'Port', dataIndex: 'port', key: 'port' },
        { title: 'Username', dataIndex: 'username', key: 'username' },
        {
            title: 'Action',
            key: 'action',
            render: (_: any, record: Node) => (
                <Space size="middle">
                    <Button
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(record)}
                        style={{ marginRight: 8 }}
                    />
                    <Button
                        icon={<ApiOutlined />}
                        onClick={() => handleTestNodeById(record.id)}
                        loading={testingNodeId === record.id}
                        style={{ marginRight: 8 }}
                    />
                    <Button
                        danger
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
                <h2>Node Management</h2>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingNode(null); form.resetFields(); setIsModalOpen(true); }}>
                    Add Node
                </Button>
            </div>

            <Table
                columns={columns}
                dataSource={nodes}
                rowKey="id"
                loading={loading}
            />

            <Modal
                title={editingNode ? "Edit Node" : "Add New Node"}
                open={isModalOpen}
                onCancel={handleCancel}
                footer={null}
            >
                <Form layout="vertical" form={form} onFinish={handleSave}>
                    <Form.Item name="name" label="Name" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name="host" label="Host" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name="port" label="Port">
                        <InputNumber style={{ width: '100%' }} placeholder="Optional (uses 22 or config)" />
                    </Form.Item>
                    <Form.Item name="username" label="Username">
                        <Input placeholder="Optional (uses local user or .ssh/config)" />
                    </Form.Item>
                    <Form.Item name="password" label="Password">
                        <Input.Password placeholder="Optional if using SSH Key" />
                    </Form.Item>
                    <Form.Item name="ssh_key_path" label="SSH Key Path">
                        <Input placeholder="Optional (defaults to ~/.ssh/id_rsa)" />
                    </Form.Item>
                    <Form.Item name="is_center" valuePropName="checked">
                        <Checkbox>Is Center Node (All other nodes will connect via this one)</Checkbox>
                    </Form.Item>
                    <Form.Item>
                        <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                            <Button onClick={handleTestConnection} loading={testingConnection}>
                                Test Connection
                            </Button>
                            <Button type="primary" htmlType="submit" loading={submitting}>
                                {editingNode ? "Update" : "Create"}
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default NodesPage;
