import logo from './logo.svg';
import './App.css';
import Login from './AuthPages/login';
import ForgotPasswordPage from './AuthPages/forgotpassword';
import { Routes, useNavigate } from 'react-router-dom';
import { HashRouter, Route } from 'react-router-dom';

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path='/' element={<Login />} />
        <Route path='/forgot' element={<ForgotPasswordPage />} />
      </Routes>
    </HashRouter>
  );
}

export default App;
