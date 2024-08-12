import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Header = ({ isAuthenticated, username, handleLogout, setIsPopupOpen, setIsRegisterPopupOpen }) => {
    const navigate = useNavigate();

    return (
        <header>
            {isAuthenticated ? (
                <button onClick={handleLogout}>{username}</button>
            ) : (
                <>
                    <button onClick={() => setIsPopupOpen(true)}>Войти</button>
                    <button onClick={() => setIsRegisterPopupOpen(true)}>Регистрация</button>
                </>
            )}
        </header>
    );
};

export default Header;