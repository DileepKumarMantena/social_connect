import logo from './logo.svg';
import './App.css';
import Login from './AuthPages/login';
import ForgotPasswordPage from './AuthPages/forgotpassword';
import { Routes, useNavigate } from 'react-router-dom';
import { HashRouter, Route } from 'react-router-dom';
import AppLayout from './layout/layout';
import Dashboard from './pages/dashboard';
import { useEffect, useState } from 'react';

function getCookie(name) {
  const value = `; ${document.cookie}`;  
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

function App() {
  const [loggedin, setLoggedin] = useState(false);
  const cookie = getCookie('token');
  useEffect(() => {
    if (!cookie) {
      setLoggedin(false)
    }
    else {
      setLoggedin(true)
    }
  }, [loggedin])

  return (
    <HashRouter>
      <Routes>

        {!loggedin ?
          <Route path='/' element={<Login />} /> :
          <Route path='/' element={
            <AppLayout> <Dashboard /></AppLayout>
          } />
        }
        <Route path='/' element={<Login />} />
        <Route path='/forgot' element={<ForgotPasswordPage />} />

      </Routes>
    </HashRouter>
  );
}

export default App;
