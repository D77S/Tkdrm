import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './Home';
import AllList from './All_list'; // Изменили имя импорта на PascalCase (AllList вместо All_list)

function App() {
  return (
    <Router>
      <div style={{ fontFamily: 'sans-serif', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        
        {/* Общий хедер для всех страниц проекта */}
        <header style={{ 
          borderBottom: '1px solid #ccc', 
          padding: '15px 20px', 
          backgroundColor: '#f8f9fa',
          marginBottom: '20px'
        }}>
          <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', gap: '20px', fontWeight: 'bold', alignItems: 'center' }}>
            <Link to="/" style={{ color: '#007bff', textDecoration: 'none' }}>Главная</Link>
            <Link to="/all_list/by_cpl5/" style={{ color: '#007bff', textDecoration: 'none' }}>Общий перечень</Link>
            
            {/* Строго заданный текст для будущей ссылки */}
            <span style={{ color: '#6c757d', cursor: 'not-allowed', userSelect: 'none' }}>
              Создать прибор
            </span>
          </div>
        </header>

        {/* Основной контент страниц */}
        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            {/* Используем здесь AllList с заглавной буквы */}
            <Route path="/all_list/by_cpl5/" element={<AllList />} />
          </Routes>
        </div>

      </div>
    </Router>
  );
}

export default App;