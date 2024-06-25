import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import RegisterForm from './components/register';
import LoginForm from './components/login';
import { Nav, Header } from './components/nav';
import Home from './components/home';
import Logout from './components/logout';
import ChatComponent from './components/chat';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Nav />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<chat />} />
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/login" element={<LoginForm />} />
        </Routes>
        <Logout /> 
      </div>
    </Router>
  );
}
export default App;