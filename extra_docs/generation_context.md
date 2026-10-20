# ИСТОРИЯ СЕАНСА ГЕНЕРАЦИИ: ФРОНТЕНД НА REACT ДЛЯ ПРОЕКТА ТКДРМ

## 1. СТРУКТУРА И МАРШРУТИЗАЦИЯ ПРОЕКТА (src/App.js)
Компонент верхнего уровня. Содержит глобальный хедер, видимый на всех страницах.
- Ссылки в хедере: "Главная", "Общий перечень", "Создать прибор" (текст, неактивный).
- Путь для списка приборов настроен на: `/all_list/by_cpl5/`
- Исправлен ворнинг PascalCase для импорта AllList.

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './Home';
import AllList from './All_list';

function App() {
  return (
    <Router>
      <div style={{ fontFamily: 'sans-serif', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <header style={{ borderBottom: '1px solid #ccc', padding: '15px 20px', backgroundColor: '#f8f9fa', marginBottom: '20px' }}>
          <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', gap: '20px', fontWeight: 'bold', alignItems: 'center' }}>
            <Link to="/" style={{ color: '#007bff', textDecoration: 'none' }}>Главная</Link>
            <Link to="/all_list/by_cpl5/" style={{ color: '#007bff', textDecoration: 'none' }}>Общий перечень</Link>
            <span style={{ color: '#6c757d', cursor: 'not-allowed', userSelect: 'none' }}>Создать прибор</span>
          </div>
        </header>
        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/all_list/by_cpl5/" element={<AllList />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}
export default App;
```

## 2. ГЛАВНАЯ СТРАНИЦА (src/Home.js)
```jsx
import React from 'react';

function Home() {
  return (
    <div style={{ padding: '0 20px', maxWidth: '1000px', margin: '0 auto', lineHeight: '1.6' }}>
      <main>
        <h2>Тестовый проект по учету технических средств ТКДРМ</h2>
        <p>В верхней части экрана (в хедере) доступно меню со следующими разделами:</p>
        <ul style={{ paddingLeft: '20px', marginBottom: '20px' }}>
          <li><strong>Главная страница</strong> — текущее описание системы.</li>
          <li><strong>Общий перечень технических средств ТКДРМ</strong> — краткая информация о приборах с пагинацией.</li>
          <li><strong>Создать новый прибор в базе данных</strong> — добавление нового технического средства (в разработке).</li>
        </ul>
        <p>В разделе «Общий перечень» представлена краткая сводка о каждом приборе: орган эксплуатации, тип и заводской номер. Для просмотра полной информации о конкретном техническом средстве предусмотрена ссылка «Подробнее».</p>
      </main>
    </div>
  );
}
export default Home;
```

## 3. СТРАНИЦА ОБЩЕГО СПИСКА ПРИБОРОВ (src/All_list.js)
Особенности реализации:
- **Широкая верстка:** Таблица занимает 96% ширины экрана, применено свойство `tableLayout: 'fixed'`.
- **Динамическая пагинация:** Размер страницы определяется автоматически на основе длины массива `results` с бэкенда (`setPageSize`), устраняя хардкод и неверный подсчет страниц при смене настроек Django.
- **Расширенный блок страниц:** Выводит кнопки Назад/Вперед, Первую/Последнюю/Предпоследнюю страницы, многоточия `...` и широкий центральный диапазон (4 страницы вокруг текущей).
- **Обработка `is_main_for_cust`:** Если есть объект с `is_main_for_cust === true` — выводится он. Если нет — выводится первый из массива с `false`. Если массив пуст — ячейки остаются пустыми.
- **Корректный эндпоинт:** `http://localhost:8000/all_list/by_cpl5/?page=${currentPage}` с поддержкой trailing slash.

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function All_list() {
  const [devices, setDevices] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [pageSize, setPageSize] = useState(20); 

  useEffect(() => {
    setLoading(true);
    axios.get(`http://localhost:8000/all_list/by_cpl5/?page=${currentPage}`)
      .then(response => {
        const dataResults = response.data.results || response.data;
        const totalCount = response.data.count || dataResults.length;
        
        if (dataResults.length > 0 && currentPage === 1) {
          setPageSize(dataResults.length);
        }

        setDevices(dataResults);
        const actualPageSize = dataResults.length > 0 ? dataResults.length : pageSize;
        setTotalPages(Math.ceil(totalCount / actualPageSize));
        setLoading(false);
      })
      .catch(error => {
        console.error("Критическая ошибка запроса к Django API:", error);
        alert(`Не удалось загрузить данные с бэкенда!
Причина: ${error.message}`);
        setLoading(false);
      });
  }, [currentPage, pageSize]);

  if (loading) return <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>Загрузка данных из базы...</div>;

  return (
    <div style={{ padding: '0 2%', maxWidth: '96%', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2>Общий перечень технических средств ТКДРМ</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '20px', fontSize: '14px', tableLayout: 'fixed' }}>
        <thead>
          <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'center' }}>
            <th rowSpan="2" style={{ padding: '10px', border: '1px solid #ddd', width: '60px' }}>№</th>
            <th colSpan="3" style={{ padding: '10px', border: '1px solid #ddd' }}>Эксплуатирующий т.орган</th>
            <th rowSpan="2" style={{ padding: '10px', border: '1px solid #ddd', width: '150px' }}>Тип</th>
            <th rowSpan="2" style={{ padding: '10px', border: '1px solid #ddd', width: '120px' }}>Сер. номер</th>
            <th rowSpan="2" style={{ padding: '10px', border: '1px solid #ddd', width: '240px' }}>Дополнительно</th>
          </tr>
          <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'center' }}>
            <th style={{ padding: '8px', border: '1px solid #ddd', width: '25%' }}>РТУ</th>
            <th style={{ padding: '8px', border: '1px solid #ddd', width: '25%' }}>Таможня</th>
            <th style={{ padding: '8px', border: '1px solid #ddd', width: '25%' }}>Пост</th>
          </tr>
        </thead>
        <tbody>
          {devices.map((device, index) => {
            const globalIndex = (currentPage - 1) * pageSize + index + 1;
            let targetRel = null;
            if (device.rels_of_work && device.rels_of_work.length > 0) {
              const mainRel = device.rels_of_work.find(rel => rel.is_main_for_cust === true);
              targetRel = mainRel ? mainRel : device.rels_of_work[0];
            }
            const custPlace = targetRel?.cust_pl1;

            return (
              <tr key={device.id || index} style={{ textAlign: 'left' }}>
                <td style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'center' }}>{globalIndex}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{custPlace?.rtuv2 || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{custPlace?.custhousev2 || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{custPlace?.custpostv2 || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{device.type?.title || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{device.serial || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'center' }}>
                  <span style={{ color: '#007bff', cursor: 'pointer', marginRight: '12px', fontWeight: '500' }}>Подробно</span>
                  <span style={{ color: '#28a745', cursor: 'pointer', marginRight: '12px', fontWeight: '500' }}>Редактировать</span>
                  <span style={{ color: '#dc3545', cursor: 'pointer', fontWeight: '500' }}>Удалить</span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Пагинация */}
      <div style={{ display: 'flex', gap: '6px', alignItems: 'center', justifyRules: 'center', justifyContent: 'center', marginTop: '25px', marginBottom: '40px' }}>
        <button onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))} disabled={currentPage === 1} style={{ padding: '6px 14px', marginRight: '12px', border: '1px solid #ccc', backgroundColor: currentPage === 1 ? '#e9ecef' : '#fff', cursor: currentPage === 1 ? 'not-allowed' : 'pointer', borderRadius: '4px' }}>Назад</button>
        {(() => {
          const pages = [];
          const range = 4; 
          for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || i === totalPages - 1 || (i >= currentPage - range && i <= currentPage + range)) {
              pages.push(
                <button key={i} onClick={() => setCurrentPage(i)} style={{ padding: '6px 12px', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: currentPage === i ? '#007bff' : '#fff', color: currentPage === i ? '#fff' : '#007bff', fontWeight: currentPage === i ? 'bold' : 'normal', cursor: 'pointer', minWidth: '40px' }}>{i}</button>
              );
            } else if (i === 2 && currentPage > range + 2) {
              pages.push(<span key="dots-start" style={{ padding: '0 10px', color: '#6c757d' }}>...</span>);
            } else if (i === totalPages - 2 && currentPage < totalPages - range - 2) {
              pages.push(<span key="dots-end" style={{ padding: '0 10px', color: '#6c757d' }}>...</span>);
            }
          }
          return pages;
        })()}
        <button onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))} disabled={currentPage === totalPages} style={{ padding: '6px 14px', marginLeft: '12px', border: '1px solid #ccc', backgroundColor: currentPage === totalPages ? '#e9ecef' : '#fff', cursor: currentPage === totalPages ? 'not-allowed' : 'pointer', borderRadius: '4px' }}>Вперед</button>
      </div>
    </div>
  );
}
export default All_list;
```

## 4. ОШИБКИ И ИХ РЕШЕНИЯ В ДАННОЙ СЕССИИ
1. **Ошибка Node/NPM (EBADENGINE):** Старая Node.js v16 не поддерживала npm v12. Решено рекомендацией обновления Node.js до LTS (v22+).
2. **Ошибка 'module has no exports':** Отсутствовали строки `export default`. Добавлены во все файлы.
3. **Ошибка Network Error (AxiosError):** Запросы блокировались из-за CORS и разницы хостов `127.0.0.1`/`localhost`. Решено добавлением `CORS_ALLOW_ALL_ORIGINS = True` в Django `settings.py` и исправлением строки запроса на `localhost:8000` с добавлением замыкающего слэша (`/`).
4. **Ошибка искажения строки `http://127.0.0{currentpage}`:** Возникала из-за некорректных кавычек в строке запроса. Зафиксирован полностью исправный синтаксис шаблонной строки.
5. **Ворнинг ESLint (react/jsx-pascal-case):** Исправлен путем изменения имени импортируемого JSX-компонента в `App.js` на `AllList` (PascalCase).
6. **Ворнинг DeprecationWarning (fs.F_OK):** Описаны способы подавления через добавление флага `--no-deprecation` в `package.json`.
