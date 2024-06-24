import React from 'react';
import  { useNavigate }from 'react-router-dom';

export default function Logout() {
    const navigate = useNavigate();;

    const handleLogout = () => {
        localStorage.removeItem('userToken');
        localStorage.removeItem('userProfile');
        navigate('/login');
    };

    return (
        <button onClick={handleLogout}>Logout</button>
    );
}

