// src/components/LoginForm.js
import React from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';

export default function LoginForm() {
    const { register, handleSubmit } = useForm();

    const onSubmit = data => {
        axios.post('/login', data)
            .then(response => {
                console.log(response.data);
            })
            .catch(error => {
                console.error(error);
            });
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            <input {...register('username')} placeholder="Username" />
            <input {...register('password')} placeholder="Password" type="password" />
            <button type="submit">Login</button>
        </form>
    );
}
