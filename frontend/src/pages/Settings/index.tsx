import React, { useEffect, useState } from 'react';
import { Form, InputNumber, Button, message, Card } from 'antd';
import { getSystemSettings, updateSystemSettings } from '../../services/api';
import type { SystemSettings } from '../../types';

const SettingsPage: React.FC = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            const data = await getSystemSettings();
            form.setFieldsValue(data);
        } catch (error) {
            message.error('Failed to fetch settings');
        }
    };

    const handleSave = async (values: SystemSettings) => {
        setLoading(true);
        try {
            await updateSystemSettings(values);
            message.success('Settings updated');
        } catch (error) {
            message.error('Failed to update settings');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
            <h2>System Settings</h2>
            <Card title="Task Inspection">
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSave}
                >
                    <Form.Item
                        name="inspection_interval"
                        label="Inspection Interval (Seconds)"
                        rules={[{ required: true, message: 'Please input interval' }]}
                        help="Time between automatic health checks for all tasks."
                    >
                        <InputNumber min={10} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={loading} block>
                            Save Settings
                        </Button>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    );
};

export default SettingsPage;
