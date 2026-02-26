import './App.css';
import Login from './AuthPages/login';
import ForgotPasswordPage from './AuthPages/forgotpassword';
import { Routes } from 'react-router-dom';
import { HashRouter, Route } from 'react-router-dom';
import AppLayout from './layout/layout';
import Dashboard from './pages/dashboard';
import AdminPanel from './pages/AdminPanel';
import { useEffect, useState } from 'react';
import { AuthProvider } from './context/AuthProvider';
import { useAuth } from './context/useAuth';
import RoleManagementPage from './pages/rolemanagement';



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
  const { token, loggedin } = useAuth();
  return (
    <Routes>

      {!token ?
        <Route path='/' element={<Login />} /> :
        <Route path='/' element={
          <AppLayout> <Dashboard /></AppLayout>
        } />
      }
      <Route path='/dashboard' element={
        <AppLayout> <Dashboard /></AppLayout>
      } />
      {/* <Route path='/' element={<Login />} /> */}
      <Route path='/forgot' element={<ForgotPasswordPage />} />
      <Route path='/roles' element={
        <AppLayout> <RoleManagementPage /></AppLayout>
      } />
    </Routes>
  )

}

export default App;
