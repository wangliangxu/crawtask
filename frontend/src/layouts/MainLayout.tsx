import React, { useState } from 'react';
import { Layout, Menu, theme } from 'antd';
import { DesktopOutlined, FileOutlined, SettingOutlined } from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import logo from '../assets/logo.svg';
import ThemeSwitcher from '../components/ThemeSwitcher';

const { Header, Content, Footer, Sider } = Layout;

const MainLayout: React.FC = () => {
    const [collapsed, setCollapsed] = useState(false);
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();
    const navigate = useNavigate();
    const location = useLocation();

    const items = [
        { key: '/nodes', icon: <DesktopOutlined />, label: 'Nodes' },
        { key: '/tasks', icon: <FileOutlined />, label: 'Tasks' },
        { key: '/settings', icon: <SettingOutlined />, label: 'Settings' },
    ];

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
                <div style={{ height: 32, margin: 16, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <img src={logo} alt="Logo" style={{ height: '100%', width: 'auto' }} />
                </div>
                <Menu
                    theme="dark"
                    defaultSelectedKeys={['/nodes']}
                    selectedKeys={[location.pathname]}
                    mode="inline"
                    items={items}
                    onClick={({ key }) => navigate(key)}
                />
            </Sider>
            <Layout>
                <Header style={{ 
                    padding: '0 24px', 
                    background: colorBgContainer,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                }}>
                    <div />
                    <ThemeSwitcher />
                </Header>
                <Content style={{ margin: '0 16px' }}>
                    <div
                        style={{
                            padding: 24,
                            minHeight: 360,
                            background: colorBgContainer,
                            borderRadius: borderRadiusLG,
                            marginTop: 16
                        }}
                    >
                        <Outlet />
                    </div>
                </Content>
                <Footer style={{ textAlign: 'center' }}>
                    Crawler Task Manager ©{new Date().getFullYear()}
                </Footer>
            </Layout>
        </Layout>
    );
};

export default MainLayout;
