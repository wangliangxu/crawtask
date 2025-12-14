import React from 'react';
import { Switch, Dropdown, Space, Tooltip } from 'antd';
import { BulbOutlined, MoonOutlined, DesktopOutlined } from '@ant-design/icons';
import { useTheme } from '../hooks/useTheme';
import type { ThemeMode } from '../types/theme';

const ThemeSwitcher: React.FC = () => {
  const { themeMode, toggleTheme, setTheme } = useTheme();

  // 主题切换下拉菜单项
  const themeMenuItems = [
    {
      key: 'light',
      label: (
        <Space>
          <BulbOutlined />
          亮色主题
        </Space>
      ),
      onClick: () => setTheme('light'),
    },
    {
      key: 'dark',
      label: (
        <Space>
          <MoonOutlined />
          暗色主题
        </Space>
      ),
      onClick: () => setTheme('dark'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'system',
      label: (
        <Space>
          <DesktopOutlined />
          跟随系统
        </Space>
      ),
      onClick: () => {
        // 获取系统主题
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        setTheme(systemTheme);
        localStorage.removeItem('theme-mode'); // 移除手动设置，改为跟随系统
      },
    },
  ];

  // 获取当前主题显示文本
  const getThemeLabel = (mode: ThemeMode) => {
    switch (mode) {
      case 'light':
        return '亮色主题';
      case 'dark':
        return '暗色主题';
      default:
        return '未知主题';
    }
  };

  // 获取当前主题图标
  const getThemeIcon = (mode: ThemeMode) => {
    switch (mode) {
      case 'light':
        return <BulbOutlined />;
      case 'dark':
        return <MoonOutlined />;
      default:
        return <BulbOutlined />;
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <Tooltip title={`当前: ${getThemeLabel(themeMode)}`}>
        <Switch
          checked={themeMode === 'dark'}
          onChange={toggleTheme}
          checkedChildren={<MoonOutlined />}
          unCheckedChildren={<BulbOutlined />}
          size="small"
        />
      </Tooltip>
      
      <Dropdown
        menu={{ 
          items: themeMenuItems,
          selectedKeys: [themeMode],
        }}
        placement="bottomRight"
        trigger={['click']}
      >
        <span
          style={{
            cursor: 'pointer',
            padding: '4px 8px',
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--ant-color-fill-secondary)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          {getThemeIcon(themeMode)}
          <span style={{ fontSize: 12, opacity: 0.8 }}>
            {getThemeLabel(themeMode)}
          </span>
        </span>
      </Dropdown>
    </div>
  );
};

export default ThemeSwitcher;