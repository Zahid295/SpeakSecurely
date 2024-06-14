// src/components/RegisterForm.js
import React from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';

export default function RegisterForm() {
    const { register, handleSubmit } = useForm();

    const onSubmit = data => {
        axios.post('/register', data)
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
            <button type="submit">Register</button>
        </form>
    );
}
