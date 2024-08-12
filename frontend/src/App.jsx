import React, { useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom';
import Header from './Header';

const App = () => {
  const [data, setData] = useState({ items: [], total_count: 0, current_page: 1, total_pages: 1 });
  const [page, setPage] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [isPopupOpenAddItem, setIsPopupOpenAddItem] = useState(false);
  const [formData, setFormData] = useState({
    item_author_uuid: '',
    item_author_nickname: '',
    item_category: '',
    item_title: '',
    item_caption: ''
  });
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [loginError, setLoginError] = useState(false);
  
  const navigate = useNavigate();

  const getItems = async (category = selectedCategory, pageNum = page) => {
    try {
      let url = `http://127.0.0.1:8000/items?page=${pageNum}&limit=10`;
      if (category) {
        url += `&item_category=${category}`;
      }
      const response = await fetch(url);
      if (response.ok) {
        const result = await response.json();
        setData(result);
      } else {
        console.log("Error:", response.status);
        console.log("Error:", await response.text());
      }
    } catch (error) {
      console.error("Failed to fetch items:", error);
    }
  };

  const handleCategoryChange = (event) => {
    setSelectedCategory(event.target.value);
    setPage(1);
    getItems(event.target.value, 1);
  };

  const handleNextPage = () => {
    if (page < data.total_pages) {
      setPage(prevPage => prevPage + 1);
      getItems(selectedCategory, page + 1);
    }
  };

  const handlePrevPage = () => {
    if (page > 1) {
      setPage(prevPage => prevPage - 1);
      getItems(selectedCategory, page - 1);
    }
  };

  const handleReadClick = (item_uuid) => {
    navigate(`/item/${item_uuid}`);
  };

  const handleDelete = async (item_uuid) => {
    const response = await fetch("http://127.0.0.1:8000/item/delete", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ uuid: item_uuid })
    });
    
    if (response.ok) {
      getItems(selectedCategory);
    } else {
      console.log("Error:", await response.text());
    }
  };

  const handleComplaint = (item_uuid) => {
    navigate(`/complaint/${item_uuid}`);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:8000/item/add", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        console.log("Элемент успешно добавлен");
        setIsPopupOpenAddItem(false);
        getItems(selectedCategory);
      } else {
        console.log("Ошибка при добавлении элемента:", response.status);
        console.log("Ошибка:", await response.text());
      }
    } catch (error) {
      console.error("Ошибка при отправке формы:", error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:8000/token", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password
        })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setIsAuthenticated(true);
        setUsername(formData.username);
        setIsPopupOpen(false);
        setLoginError(false);
        getItems();
      } else {
        setLoginError(true);
      }
    } catch (error) {
      console.error("Ошибка при авторизации:", error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setUsername('');
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
      setUsername(JSON.parse(atob(token.split('.')[1])).sub);
    }
    getItems();
  }, []);


  return (
    <div>
      <Header 
        isAuthenticated={isAuthenticated} 
        username={username} 
        handleLogout={handleLogout}
        setIsPopupOpen={setIsPopupOpen}
        setIsRegisterPopupOpen={setIsPopupOpen}
      />
      <h1>Список элементов</h1>
      <button onClick={() => setIsPopupOpenAddItem(true)}>Добавить элемент</button>
      <div>
        <label htmlFor="category">Категория:</label>
        <select id="category" value={selectedCategory} onChange={handleCategoryChange}>
          <option value="">Все категории</option>
          <option value="Железо">Железо</option>
          <option value="Софт">Софт</option>
        </select>
      </div>
      <ul>
      {data.items.map((item) => (
          <li key={item.item_uuid}>
            <h2>{item.item_title}</h2>
            <p>Описание: {item.item_caption}</p>
            <p>Категория: {item.item_category}</p>
            <p>Автор: {item.item_author_nickname}</p>
            <p>Дата создания: {item.item_create_date}</p>
            <button onClick={() => handleReadClick(item.item_uuid)}>Читать</button>
            <button onClick={() => handleDelete(item.item_uuid)}>Удалить</button>
            {/* <button onClick={() => handleComplaint(item.item_uuid)}>Пожаловаться</button> */}
          </li>
        ))}
      </ul>
      <div>
  {data.items && data.items.length > 0 ? (
    <>
      <button onClick={handlePrevPage} disabled={page === 1}>Назад</button>
      <span>Страница {data.current_page} из {data.total_pages}</span>
      <button onClick={handleNextPage} disabled={page === data.total_pages}>Вперед</button>
    </>
  ) : (
    <p>Нет доступных объектов для отображения.</p>
  )}
</div>
      {/* Поп-ап окно авторизации*/}
      {isPopupOpen && (
          <div className="popup">
            <div className="popup-content">
              <h3>Вход</h3>
              <form onSubmit={handleLogin}>
                <div>
                  <label htmlFor="username">Никнейм:</label>
                  <input 
                    type="text" 
                    id="username" 
                    name="username" 
                    value={formData.username} 
                    onChange={handleInputChange} 
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
                    onChange={handleInputChange} 
                    required 
                  />
                </div>
                {loginError && <p>Неверный никнейм или пароль</p>}
                <button type="submit">Войти</button>
              </form>
              <button type="button" onClick={() => setIsPopupOpen(false)}>Закрыть</button>
            </div>
          </div>
        )}
      {/* Поп-ап окно добавления*/}
      {isPopupOpenAddItem && (
        <div className="popup">
          <div className="popup-content">
            <h3>Добавить элемент</h3>
            <form onSubmit={handleSubmit}>
              <input 
                type="text" 
                name="item_author_uuid" 
                placeholder="UUID автора" 
                value={formData.item_author_uuid} 
                onChange={handleInputChange} 
                required 
              />
              <input 
                type="text" 
                name="item_author_nickname" 
                placeholder="Никнейм автора" 
                value={formData.item_author_nickname} 
                onChange={handleInputChange} 
                required 
              />
              <select 
                name="item_category" 
                value={formData.item_category} 
                onChange={handleInputChange} 
                required
              >
                <option value="">Выберите категорию</option>
                <option value="Железо">Железо</option>
                <option value="Софт">Софт</option>
              </select>
              <input 
                type="text" 
                name="item_title" 
                placeholder="Название элемента" 
                value={formData.item_title} 
                onChange={handleInputChange} 
                required 
              />
              <textarea 
                name="item_caption" 
                placeholder="Описание элемента" 
                value={formData.item_caption} 
                onChange={handleInputChange} 
                required 
              />
              <button type="button" onClick={() => setIsPopupOpenAddItem(false)}>Отменить</button>
              <button type="submit">Отправить</button>
            </form>
          </div>
        </div>
      )}

      {/* Стили для поп-апа */}
      <style jsx>{`
        .popup {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .popup-content {
          background-color: white;
          padding: 20px;
          border-radius: 5px;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }
        input, textarea, select {
          display: block;
          margin-bottom: 10px;
          padding: 10px;
          width: 500px;
        }
        button {
          margin-right: 10px;
        }
      `}</style>
    </div>
  );
};

export default App;