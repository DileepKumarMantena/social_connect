import './App.css';
import Login from './AuthPages/login';
import ForgotPasswordPage from './AuthPages/forgotpassword';
import { Routes } from 'react-router-dom';
import { HashRouter, Route } from 'react-router-dom';
import AppLayout from './layout/layout';
import Dashboard from './pages/dashboard';
import AdminPanel from './pages/AdminPanel';
import { useEffect, useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import RoleManagementPage from './pages/rolemanagement';
import CampaignsPage from './pages/campaigns';
import LeadsPage from './pages/leads';
import ChannelsPage from './pages/channels';
import AnalyticsPage from './pages/analytics';
import SchedulerPage from './pages/scheduler';
import SettingsPage from './pages/settings';
import TokenVerifier from './components/TokenVerifier';



function App() {

  return (
    <AuthProvider>
      <HashRouter>
        <ProtectedRoutes />
      </HashRouter>
    </AuthProvider>
  );
}

function ProtectedRoutes() {
  const { isAuthenticated, logout } = useAuth();
  
  const handleLogout = () => {
    logout();
    window.location.hash = '/';
  };
  
  return (
    <Routes>

      {!loggedin ?
        <Route path='/' element={<Login />} /> :
        <Route path='/' element={
          <AppLayout onLogout={handleLogout}> <Dashboard /></AppLayout>
        } />
      }
      
      {/* <Route path='/' element={<Login />} /> */}
      <Route path='/forgot' element={<ForgotPasswordPage />} />
      <Route path='/admin' element={
        <AppLayout onLogout={handleLogout}> <AdminPanel /></AppLayout>
      } />
      <Route path='/roles' element={
        <AppLayout onLogout={handleLogout}> <RoleManagementPage /></AppLayout>
      } />
      <Route path='/campaigns' element={
        <AppLayout onLogout={handleLogout}> <CampaignsPage /></AppLayout>
      } />
      <Route path='/leads' element={
        <AppLayout onLogout={handleLogout}> <LeadsPage /></AppLayout>
      } />
      <Route path='/channels' element={
        <AppLayout onLogout={handleLogout}> <ChannelsPage /></AppLayout>
      } />
      <Route path='/analytics' element={
        <AppLayout onLogout={handleLogout}> <AnalyticsPage /></AppLayout>
      } />
      <Route path='/scheduler' element={
        <AppLayout onLogout={handleLogout}> <SchedulerPage /></AppLayout>
      } />
      <Route path='/settings' element={
        <AppLayout onLogout={handleLogout}> <SettingsPage /></AppLayout>
      } />
      <Route path='/verify-token' element={
        <AppLayout onLogout={handleLogout}> <TokenVerifier /></AppLayout>
      } />
      {/* Catch all route - redirect to home */}
      <Route path='*' element={
        <AppLayout onLogout={handleLogout}> <Dashboard /></AppLayout>
      } />
    </Routes>
  )

}

export default App;
