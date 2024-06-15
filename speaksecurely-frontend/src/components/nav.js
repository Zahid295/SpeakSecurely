import React from 'react';
import { Link } from 'react-router-dom';

function Nav() {
  return (
    <nav>
      <ul>
        <li><Link to="/register">Register</Link></li>
        <li><Link to="/login">Login</Link></li>
      </ul>
    </nav>
  );
}

function Header() {
  return (
    <header>
      <h1>Encrypted Communications App</h1>
    </header>
  );
}

function Footer() {
  return (
    <footer>
      <p>© 2024 Encrypted Communications App</p>
    </footer>
  );
}

export { Nav, Header, Footer };
