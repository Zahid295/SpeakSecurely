import React from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import RegisterForm from './components/register';
import LoginForm from './components/login';
import { Nav, Header, Footer } from './components/Layout';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Nav />
        <Route path="/register" component={RegisterForm} />
        <Route path="/login" component={LoginForm} />
        <Footer />
      </div>
    </Router>
  );
}

export default App;