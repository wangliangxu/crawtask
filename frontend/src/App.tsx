import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, App as AntdApp, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import MainLayout from './layouts/MainLayout';
import NodesPage from './pages/Nodes';
import TasksPage from './pages/Tasks';
import SettingsPage from './pages/Settings';
import { ThemeProvider } from './contexts/ThemeProvider';
import { useTheme } from './hooks/useTheme';
import './App.css';

const AppContent: React.FC = () => {
  const { themeMode } = useTheme();

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: themeMode === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
        components: {
          Layout: {
            bodyBg: themeMode === 'dark' ? '#141414' : '#ffffff',
            headerBg: themeMode === 'dark' ? '#001529' : '#ffffff',
            siderBg: themeMode === 'dark' ? '#001529' : '#001529',
          },
          Menu: {
            darkItemBg: 'transparent',
            darkItemSelectedBg: '#1890ff',
          },
        },
      }}
    >
      <AntdApp>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/nodes" replace />} />
            <Route path="nodes" element={<NodesPage />} />
            <Route path="tasks" element={<TasksPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </AntdApp>
    </ConfigProvider>
  );
};

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;