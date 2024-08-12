import React, { useState } from 'react';

const PopupRegister = ({ setIsRegisterPopupOpen }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/register", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        // Успешная регистрация
        setIsRegisterPopupOpen(false);
        alert('Регистрация прошла успешно!');
      } else {
        // Обработка ошибок
        const errorData = await response.json();
        alert(errorData.detail); // Вывод сообщения об ошибке
      }
    } catch (error) {
      console.error("Ошибка при регистрации:", error);
    }
  };

  return (
    <div className="popup">
      <div className="popup-content">
        <h2>Регистрация</h2>
        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="username">Никнейм:</label>
            <input 
              type="text" 
              id="username" 
              name="username" 
              value={formData.username} 
              onChange={handleChange} 
              required 
            />
          </div>
          <div>
            <label htmlFor="password">Пароль:</label>
            <input 
              type="password" 
              id="password" 
              name="password" 
              value={formData.password} 
              onChange={handleChange} 
              required 
            />
          </div>
          <button type="submit">Зарегистрироваться</button>
          <button type="button" onClick={() => setIsRegisterPopupOpen(false)}>Отменить</button>
        </form>
      </div>
    </div>
  );
};

export default PopupRegister;