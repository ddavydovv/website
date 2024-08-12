import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import ItemDetails from './ItemDetails';

ReactDOM.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/item/:item_uuid" element={<ItemDetails />} />
    </Routes>
  </BrowserRouter>,
  document.getElementById('root')
);