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

function AppContent() {
  const { user, loading, logout } = useAuth();
  const [loggedin, setLoggedin] = useState(false);
  
  useEffect(() => {
    setLoggedin(!!user);
  }, [user]);

  const handleLogout = () => {
    logout();
    window.location.hash = '/';
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <HashRouter>
      <Routes>
        {!loggedin ?
          <Route path='/' element={<Login />} /> :
          <Route path='/' element={
            <AppLayout onLogout={handleLogout}> <Dashboard /></AppLayout>
          } />
        }
        <Route path='/dashboard' element={
          loggedin ? 
          <AppLayout onLogout={handleLogout}> <Dashboard /></AppLayout> : 
          <Login />
        } />
        <Route path='/admin' element={
          loggedin ? 
          <AppLayout onLogout={handleLogout}> <AdminPanel /></AppLayout> : 
          <Login />
        } />
        <Route path='/forgot' element={<ForgotPasswordPage />} />
        <Route path='*' element={
          loggedin ? 
          <AppLayout onLogout={handleLogout}> <Dashboard /></AppLayout> : 
          <Login />
        } />
      </Routes>
    </HashRouter>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
