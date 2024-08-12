import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from 'react-router-dom'; 

const ItemDetails = () => {
  const [item, setItem] = useState(null);
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [commentData, setCommentData] = useState({
    item_comment_author_nickname: '',
    item_comment_rating: 1,
    item_comment_title: '',
    item_comment_caption: ''
  });
  const { item_uuid } = useParams();
  const navigate = useNavigate();

  const getItemDetails = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/item/details", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_uuid })
      });
      if (response.ok) {
        const result = await response.json();
        setItem(result);
      } else {
        console.log("Error:", response.status);
        console.log("Error:", await response.text());
      }
    } catch (error) {
      console.error("Failed to fetch item details:", error);
    }
  };

  const deleteItem = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/item/delete", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uuid: item_uuid })
      });

      if (response.ok) {
        navigate('/'); // Замените '/' на нужный вам путь
      } else {
        console.log("Error:", response.status);
        console.log("Error:", await response.text());
      }
    } catch (error) {
      console.error("Failed to delete item:", error);
    }
  };

  const handleCommentChange = (e) => {
    const { name, value } = e.target;
    setCommentData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmitComment = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/item/comment/add", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from_item_item_uuid: item_uuid, // Используем item_uuid
          ...commentData
        })
      });

      if (response.ok) {
        console.log("Комментарий успешно добавлен");
        await getItemDetails(); // Обновление данных о товаре
      } else {
        console.log("Ошибка при добавлении комментария:", response.status);
        console.log("Ошибка:", await response.text());
      }
    } catch (error) {
      console.error("Ошибка при отправке комментария:", error);
    }

    setIsPopupOpen(false); // Закрыть поп-ап после отправки
  };

  useEffect(() => {
    getItemDetails();
  }, [item_uuid]);

  if (!item) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <button onClick={() => navigate(-1)}>Назад</button>
      <h2>{item.item_title}</h2>
      <p>Описание: {item.item_caption}</p>
      <p>Категория: {item.item_category}</p>
      <p>Автор: {item.item_author_nickname}</p>
      <p>Дата создания: {item.item_create_date}</p>
      <button onClick={deleteItem}>Удалить</button>
      <button onClick={() => setIsPopupOpen(true)}>Добавить комментарий</button>

      <h3>Комментарии:</h3>
      <ul>
        {item.comments.map((comment) => (
          <li key={comment.item_comment_uuid}>
            <h4>{comment.item_comment_author_nickname}</h4>
            <p>{comment.item_comment_caption}</p>
            <p>Рейтинг: {comment.item_comment_rating}</p>
            <p>Дата: {comment.item_comment_create_date}</p>
          </li>
        ))}
      </ul>

      {/* Поп-ап окно */}
      {isPopupOpen && (
        <div className="popup">
          <div className="popup-content">
            <h3>Добавить комментарий</h3>
            <form onSubmit={(e) => { e.preventDefault(); handleSubmitComment(); }}>
              <input 
                type="text" 
                name="item_comment_author_nickname" 
                placeholder="Ваш никнейм" 
                value={commentData.item_comment_author_nickname} 
                onChange={handleCommentChange} 
                required 
              />
              <input 
                type="number" 
                name="item_comment_rating" 
                min="1" 
                max="5" 
                placeholder="Рейтинг (1-5)" 
                value={commentData.item_comment_rating} 
                onChange={handleCommentChange} 
                required 
              />
              <input 
                type="text" 
                name="item_comment_title" 
                placeholder="Заголовок комментария" 
                value={commentData.item_comment_title} 
                onChange={handleCommentChange} 
                required 
              />
              <textarea 
                name="item_comment_caption" 
                placeholder="Текст комментария" 
                value={commentData.item_comment_caption} 
                onChange={handleCommentChange} 
                required 
              />
              <button type="button" onClick={() => setIsPopupOpen(false)}>Отменить</button>
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
        input, textarea {
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

export default ItemDetails;