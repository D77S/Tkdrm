# Полный контекст сеанса генерации: Фронтенд на React для Django-проекта ТКДРМ

В данном документе собран весь наработанный контекст взаимодействия, итоговый протестированный код компонентов, решенные системные проблемы и архитектурные решения по созданию фронтенд-интерфейса.

---

## 1. Главная страница (`src/Home.js`)

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
          <li><strong>Создать прибор</strong> — добавление нового технического средства (в разработке).</li>
        </ul>

        <p>
          В разделе <strong>«Общий перечень»</strong> представлена краткая сводка о каждом приборе: 
          орган эксплуатации, тип и заводской номер. Для просмотра полной информации о конкретном 
          техническом средстве предусмотрена ссылка «Подробнее».
        </p>
      </main>
    </div>
  );
}

export default Home;
```

---

## 2. Общий список приборов (`src/All_list.js`)
Компонент выводит расширенную таблицу приборов, занимающую 96% ширины экрана, с двухуровневой шапкой для эксплуатирующих органов (РТУ, Таможня, Пост). Пагинация является полностью динамической и рассчитывается на основе параметров `count`, `next` и `previous` от DRF, автоматически подстраиваясь под любой размер страницы (например, 20 или 500 элементов).

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

// Единый стиль для всех иконок-подсказок в проекте
const tooltipIconStyle = {
  display: 'inline-block',
  borderRadius: '50%',
  backgroundColor: '#007bff',
  color: '#fff',
  width: '16px',
  height: '16px',
  textAlign: 'center',
  lineHeight: '16px',
  fontSize: '11px',
  marginLeft: '6px',
  cursor: 'help'
};

function All_list() {
  const [devices, setDevices] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  
  // Дефолтный размер страницы (на случай, если страниц всего 1 и ссылок next/prev нет)
  const [pageSize, setPageSize] = useState(20); 

  useEffect(() => {
    setLoading(true);
    axios.get(`http://localhost:8000/all_list/by_cpl5/?page=${currentPage}`)
      .then(response => {
        const { count, next, previous, results } = response.data;
        
        const dataResults = results || response.data;
        const totalCount = count || dataResults.length;
        
        // Переменная для хранения вычисленного на этом шаге размера страницы
        let currentStepPageSize = 20; 

        const targetUrl = next || previous;
        if (targetUrl) {
          try {
            const urlObj = new URL(targetUrl);
            const limitParam = urlObj.searchParams.get('limit');
            
            if (limitParam) {
              currentStepPageSize = parseInt(limitParam, 10);
            } else if (dataResults.length > 0 && next) { 
              currentStepPageSize = dataResults.length;
            }
          } catch (e) {
            console.error("Не удалось распарсить URL от бэкенда", e);
          }
        }

        // Обновляем состояние размера страницы
        setPageSize(prev => {
          if (!next && !targetUrl) return prev;
          return currentStepPageSize;
        });

        setDevices(dataResults);
        setTotalPages(Math.ceil(totalCount / currentStepPageSize));
        setLoading(false);
      })
      .catch(error => {
        console.error("Критическая ошибка запроса к Django API:", error);
        alert(`Не удалось загрузить данные с бэкенда!\nПричина: ${error.message}`);
        setLoading(false);
      });
  }, [currentPage]); 

const handleDelete = (id) => {
  if (window.confirm(`Вы уверены, что хотите безвозвратно удалить прибор № ${id}?`)) {
    axios.delete(`http://localhost:8000/all_list/by_cpl5/${id}/`)
      .then(() => {
        alert('Прибор успешно удален.');
        // Перезагружаем (редиректим) на текущую страницу списка, чтобы обновить данные с бэкенда
        window.location.reload();
      })
      .catch(error => {
        console.error("Ошибка при удалении прибора:", error);
        alert(`Не удалось удалить прибор!\nПричина: ${error.message}\nПроверьте права доступа на бэкенде.`);
      });
  }
};

  if (loading) return <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>Загрузка данных из базы...</div>;

  return (
    <div style={{ padding: '0 2%', maxWidth: '96%', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2>Общий перечень технических средств ТКДРМ</h2>
      
      <table style={{ 
        width: '100%', 
        borderCollapse: 'collapse', 
        marginBottom: '20px', 
        fontSize: '14px',
        tableLayout: 'fixed'
      }}>
        <colgroup>
        <col style={{ width: '60px' }} />   {/* 1. № */}
        <col style={{ width: '23%' }} />  {/* 2. РТУ */}
        <col style={{ width: '15%' }} />  {/* 3. Таможня */}
        <col style={{ width: '21%' }} />  {/* 4. Пост */}
        <col style={{ width: '80px' }} />   {/* 5. Тип сайта (под ваши 6 символов) */}
        <col style={{ width: '25%' }} />  {/* 6. Название сайта */}
        <col style={{ width: '8%' }} />  {/* 7. Тип прибора */}
        <col style={{ width: '8%' }} />  {/* 8. Сер. номер */}
        <col style={{ width: '260px' }} />  {/* 9. Дополнительно (кнопки действий) */}
        </colgroup>
        <thead>
          <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'center' }}>
            <th rowSpan="2" style={{ padding: '10px', border: '1px solid #ddd', width: '50px' }}>№</th>
            <th colSpan="3" style={{ padding: '10px', border: '1px solid #ddd' }}>
              Эксплуатирующий т.орган
              <span style={tooltipIconStyle}
                title='Он может быть не единственный. Но среди всех задано сочетание одного основного т.органа с одним 
                основным сайтом эксплуатации (п.пропуска, ММПО, СВХ,...). 
                Оно тут и показано. Остальные - по ссылке "Подробно"'>?
              </span>
            </th>
            <th colSpan="2" style={{ padding: '10px', border: '1px solid #ddd' }}>
              Сайт эксплуатации
              <span style={tooltipIconStyle}
                title='Он может быть не единственный. Но среди всех задано сочетание одного основного т.органа с одним 
                основным сайтом эксплуатации (п.пропуска, ММПО, СВХ,...). 
                Оно тут и показано. Остальные - по ссылке "Подробно"'>?
              </span>
            </th>
            <th rowSpan="2" style={{ padding: '10px', border: '1px solid #ddd', width: '130px' }}>Тип прибора</th>
            <th rowSpan="2" style={{ padding: '10px', border: '1px solid #ddd', width: '110px' }}>Сер. номер</th>
            <th rowSpan="2" style={{ padding: '10px', border: '1px solid #ddd', width: '240px' }}>Дополнительно</th>
          </tr>
          <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'center' }}>
            <th style={{ padding: '8px', border: '1px solid #ddd'}}>РТУ</th>
            <th style={{ padding: '8px', border: '1px solid #ddd'}}>Таможня</th>
            <th style={{ padding: '8px', border: '1px solid #ddd'}}>Пост</th>
            <th style={{ padding: '8px', border: '1px solid #ddd'}}>Тип</th>
            <th style={{ padding: '8px', border: '1px solid #ddd'}}>Название</th>
          </tr>
        </thead>
        <tbody>
          {devices.map((device, index) => {
            const globalIndex = (currentPage - 1) * pageSize + index + 1;
            
            // Алгоритм приоритетного выбора объекта по флагу main_for_dev
            let targetRel = null;
            if (device.rels_of_work && device.rels_of_work.length > 0) {
              // Ищем первую запись, у которой флаг main_for_dev равен true
              const mainRel = device.rels_of_work.find(rel => rel.main_for_dev === true);
              if (mainRel) {
                targetRel = mainRel;
              } else {
                targetRel = device.rels_of_work[0]; // Если такого флага нет, берем самую первую запись
              }
            }

            const custPlace = targetRel?.cust_pl1;
            const locationInfo = targetRel?.loc;

            return (
              <tr key={device.id || index} style={{ textAlign: 'left' }}>
                <td style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'center' }}>{globalIndex}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{custPlace?.rtuv2 || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{custPlace?.custhousev2 || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{custPlace?.custpostv2 || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{locationInfo?.loctype || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{locationInfo?.locname || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{device.type?.title || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', wordBreak: 'break-word' }}>{device.serial || ''}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'center' }}>
                  <Link to={`/devices/${device.id}`} style={{ color: '#007bff', textDecoration: 'underline', marginRight: '12px', fontWeight: '500' }}>Подробно</Link>
                  <span style={{ color: '#28a745', cursor: 'pointer', marginRight: '12px', fontWeight: '500' }}>Редактировать</span>
                  <span onClick={() => handleDelete(device.id)} style={{ color: '#dc3545', cursor: 'pointer', fontWeight: '500', textDecoration: 'underline'}}>
                    Удалить
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Пагинация */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center', justifyContent: 'center', marginTop: '25px', marginBottom: '40px' }}>
          <button 
            onClick={() => { setCurrentPage(prev => Math.max(prev - 1, 1)); window.scrollTo({ top: 0, behavior: 'smooth' }); }} 
            disabled={currentPage === 1}
            style={{ padding: '6px 14px', marginRight: '12px', border: '1px solid #ccc', backgroundColor: currentPage === 1 ? '#e9ecef' : '#fff', cursor: currentPage === 1 ? 'not-allowed' : 'pointer', borderRadius: '4px' }}
          >
            Назад
          </button>

          {(() => {
            const pages = [];
            const range = 2; 
            for (let i = 1; i <= totalPages; i++) {
              if (i === 1 || i === totalPages || (i >= currentPage - range && i <= currentPage + range)) {
                pages.push(
                  <button key={i} onClick={() => { setCurrentPage(i); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                    style={{ padding: '6px 12px', border: '1px solid #ddd', borderRadius: '4px', backgroundColor: currentPage === i ? '#007bff' : '#fff', color: currentPage === i ? '#fff' : '#007bff', fontWeight: currentPage === i ? 'bold' : 'normal', cursor: 'pointer', minWidth: '40px' }}
                  >
                    {i}
                  </button>
                );
              } else if (i === 2 && currentPage > range + 2) {
                pages.push(<span key="dots-start" style={{ padding: '0 10px', color: '#6c757d' }}>...</span>);
                i = currentPage - range - 1; 
              } else if (i === currentPage + range + 1 && i < totalPages) {
                pages.push(<span key="dots-end" style={{ padding: '0 10px', color: '#6c757d' }}>...</span>);
                i = totalPages - 1; 
              }
            }
            return pages;
          })()}

          <button 
            onClick={() => { setCurrentPage(prev => Math.min(prev + 1, totalPages)); window.scrollTo({ top: 0, behavior: 'smooth' }); }} 
            disabled={currentPage === totalPages}
            style={{ padding: '6px 14px', marginLeft: '12px', border: '1px solid #ccc', backgroundColor: currentPage === totalPages ? '#e9ecef' : '#fff', cursor: currentPage === totalPages ? 'not-allowed' : 'pointer', borderRadius: '4px' }}
          >
            Вперед
          </button>
        </div>
      )}
    </div>
  );
}

export default All_list;
```

---

## 3. Корневой маршрутизатор и Хедер (`src/App.js`)
В `App.js` реализована глобальная структура приложения. Навигационная панель оформлена в виде верхнего хедера. Также добавлена строго заданная неактивная ссылка **«Создать прибор»**. Компонент импортирован с заглавной буквы (`AllList`) для соответствия правилам ESLint PascalCase.

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './Home';
import AllList from './All_list';
import DeviceDetail from './DevDetail'; // Импортируем новый файл детальной страницы

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
            <Link to="/" style={{ color: '#007bff', textDecoration: 'none' }}>Главная страница</Link>
            <Link to="/all_list/by_cpl5/" style={{ color: '#007bff', textDecoration: 'none' }}>Общий перечень</Link>
            <span style={{ color: '#6c757d', cursor: 'not-allowed', userSelect: 'none' }}>
              Создать прибор
            </span>
          </div>
        </header>

        {/* Основной контент страниц */}
        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/all_list/by_cpl5/" element={<AllList />} />
            {/* Динамический маршрут для детальной страницы */}
            <Route path="/devices/:id" element={<DeviceDetail />} />
          </Routes>
        </div>

      </div>
    </Router>
  );
}

export default App;
```

---

## 4. Детальная карточка прибора (`src/DevDetail.js`)
Компонент извлекает `id` из URL, запрашивает детальный JSON и выводит все характеристики. Для списков `rels_of_work`, `rels_of_contracts` и глубоко вложенного массива `basis` реализованы полноценные циклы обработки на базе метода `.map()`. Это обеспечивает вывод неограниченного числа записей (от 0 до 100+) без поломки интерфейса. Системные суррогатные ключи `id` скрыты.

*(Полный код данного компонента вынесен в отдельный поставляемый файл DevDetail.js)*

```jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

// Единый стиль для всех иконок-подсказок в проекте
const tooltipIconStyle = {
  display: 'inline-block',
  borderRadius: '50%',
  backgroundColor: '#007bff',
  color: '#fff',
  width: '16px',
  height: '16px',
  textAlign: 'center',
  lineHeight: '16px',
  fontSize: '11px',
  marginLeft: '6px',
  cursor: 'help'
};

function DeviceDetail() {
  const { id } = useParams();
  const [device, setDevice] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    axios.get(`http://localhost:8000/all_list/by_cpl5/${id}/`)
      .then(response => {
        setDevice(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Ошибка при получении детальных данных прибора:", error);
        alert(`Не удалось загрузить данные прибора!\nПричина: ${error.message}`);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>Загрузка детальной информации...</div>;
  if (!device) return <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>Прибор не найден.</div>;

  return (
    <div style={{ padding: '0 2%', maxWidth: '96%', margin: '0 auto', fontFamily: 'sans-serif', lineHeight: '1.5' }}>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/all_list/by_cpl5/" style={{ color: '#007bff', textDecoration: 'none', fontWeight: 'bold' }}>
          ← Вернуться к списку
        </Link>
      </div>

      <h2>Детальная информация о приборе, ID которого в базе данных: {device.id}</h2>

      {/* Основная сетка параметров девайса */}
      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '25px' }}>
        
        {/* Блок 1: Характеристики прибора */}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Характеристики прибора</h3>
          <p><strong>Тип: </strong>
            <span style={{ whiteSpace: 'nowrap' }}>{device.type?.title || 'Данных нет'}
              <span style={tooltipIconStyle} title="Конкретная модель, например Янтарь-1А или РМ1203М и т.п. и т.п.">?</span>
            </span>
          </p>
          <p><strong>Вышестоящий тип: </strong>
            <span style={{ whiteSpace: 'nowrap' }}>{device.type?.category?.title || 'Данных нет'}
              <span style={tooltipIconStyle} title="Например СТСО, Поисковые, Дозиметры и т.п. и т.п.">?</span>
            </span>
          </p>
          <p><strong>Вышестоящий тип: </strong>
            <span style={{ whiteSpace: 'nowrap' }}>{device.type?.category?.cat_l1?.title || 'Данных нет'}
              <span style={tooltipIconStyle} title="Стационарные или Переносные">?</span>
            </span>
          </p>
          <p><strong>Нормативный срок службы: </strong> {device.type?.lifetime ? `${device.type.lifetime} лет` : 'Данных нет'}</p>
          <p><strong>Подтип прибора (если есть): </strong> {device.sub_type || 'Данных нет'}</p>
          <p><strong>Серийный номер: </strong> {device.serial || 'Данных нет'}</p>
          <p><strong>Инвентарный номер: </strong> {device.inventary || 'Данных нет'}</p>
          <p><strong>Категория прибора вычисленная: </strong> {device.cat_number_c ?? 'Данных нет'}</p>
          <p><strong>Категория прибора фактическая: </strong> {device.cat_number_f ?? 'Данных нет'}</p>
          <p>
            <strong>Категорий соответствие выч. и факт.: </strong>
            {device.cats_corresp ? '🟢 Соотв. друг другу' : '🔴 Несоотв. друг другу'}
          </p>
          <p><strong>Состояние прибора: </strong> {device.condition ? '🟢 Исправен' : '🔴 Неисправен'}</p>
          <p><strong>Является ли прибор средством измерения: </strong> {device.is_si ? 'Да' : 'Нет'}</p>
          <p><strong>Является ли прибор учебным: </strong> {device.is_stud ? 'Да' : 'Нет'}</p>
          <p><strong>Статус использования: </strong> {device.status_use?.title || 'Данных нет'}</p>
          <p><strong>Статус по включению в централизованные ГК: </strong> {device.service_type?.title || 'Данных нет'}</p>
          <p><strong>Собственник прибора: </strong> {device.sour_type?.title || 'Данных нет'}</p>
          <p><strong>Балансовая стоимость (если известно конкретно на данный прибор): </strong> {device.cost || 'Данных нет'}</p>
          <p><strong>Вышестоящий прибор (если есть и известно): </strong>{' '}
            {device.upper_id ? (
              <Link to={`/devices/${device.upper_id}`} style={{ color: '#007bff', textDecoration: 'none', fontWeight: '500' }}>
              Прибор № {device.upper_id}
              </Link>
            ) : ('Данных нет')}
          </p>
        </div>

        {/* Блок 2: Эксплуатационные сроки */}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Даты по эксплуатации</h3>
          <p><strong>Дата изготовления:</strong> {device.date_prod || 'Данных нет'}</p>
          <p><strong>Дата ввода в эксплуатацию (первоначальная после изготовления):</strong> {device.date_expl || 'Данных нет'}</p>
          <p><strong>Дата продления ср.службы (последняя из нескольких, и если продления были):</strong> {device.date_prolong || 'Данных нет'}</p>
          <p><strong>Гарантийный срок при поставке, месяцев:</strong> {device.warr_period  || 'Данных нет'}</p>
          <p><strong>Дата истечения срока службы:</strong> {device.date_prod_expired || 'Данных нет'}</p>
          <p><strong>Дата окончания последней поверки:</strong> {device.date_verif || 'Данных нет'}</p>
        </div>

        {/* Блок 3: Лицо, ответственное за эксплуатацию прибора*/}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Лицо, ответственное за эксплуатацию прибора</h3>
          {device.holder ? (
            <>
              <p><strong>Login:</strong> {device.holder.username || 'Данных нет'}</p>
              <p><strong>Фамилия:</strong> {device.holder.last_name || 'Данных нет'}</p>
              <p><strong>Имя:</strong> {device.holder.first_name || 'Данных нет'}</p>
              <p><strong>Отчество:</strong> {device.holder.pater_name || 'Данных нет'}</p>
              <p><strong>Электронная почта:</strong> {device.holder.email || 'Данных нет'}</p>
              <p><strong>Статус в данном ПО:</strong> {device.holder.is_active ? 'Активен' : 'Временно деактивирован'}</p>
              <p><strong>Отдел таможенного органа:</strong> {device.holder.dept?.title || 'Данных нет'}</p>
              
              <h4 style={{ marginBottom: '5px', marginTop: '15px' }}>Т.орган, в котором числится:</h4>
              <p><strong>РТУ:</strong> {device.holder.empl?.rtuv2 || ''}</p>
              <p><strong>Таможня:</strong> {device.holder.empl?.custhousev2 || ''}</p>
              <p><strong>Таможенный пост:</strong> {device.holder.empl?.custpostv2 || ''}</p>
            </>
          ) : <p style={{ color: '#6c757d', fontStyle: 'italic' }}>Данные о лице отсутствуют</p>}
        </div>

        {/* Блок 4: (За)балансовый учет и примечания */}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>(За)балансовый учет и примечания</h3>
          <p><strong>Т.орган, в котором прибор на балансовом, либо забалансовом, учёте:</strong></p>
          <p><strong>РТУ:</strong> {device.cp1_acc?.rtuv2 || ''}</p>
          <p><strong>Таможня:</strong> {device.cp1_acc?.custhousev2 || ''}</p>
          <p><strong>Таможенный пост:</strong> {device.cp1_acc?.custpostv2 || ''}</p>
          <br></br>
          <h4 style={{ marginBottom: '5px', marginTop: '15px' }}>Примечания:</h4>
          <p><strong>Примечание 1:</strong> {device.note1 || 'Данных нет'}</p>
          <p><strong>Примечание 2:</strong> {device.note2 || 'Данных нет'}</p>
          <p><strong>Примечание 3:</strong> {device.note3 || 'Данных нет'}</p>
        </div>

      </div>

      {/* ТАБЛИЦА С ЦИКЛОМ: Связанные места эксплуатации (rels_of_work) */}
      <div style={{ marginBottom: '30px', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
        <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>
          Места эксплуатации (сочетание т.орган и локация). Всего мест по данному прибору: {device.rels_of_work?.length || 0}
        </h3>
        {device.rels_of_work && device.rels_of_work.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', fontSize: '14px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'left' }}>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '40px', textAlign: 'center', verticalAlign: 'top'}}>№</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center', verticalAlign: 'top'}}>РТУ</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center', verticalAlign: 'top' }}>Таможня</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center', verticalAlign: 'top' }}>Таможенный пост</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center', verticalAlign: 'top' }}>Тип локации</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center', verticalAlign: 'top' }}>Наименование локации</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '140px', textAlign: 'center', verticalAlign: 'top' }}>
                  Является ли локация основной для т.органа</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '140px', textAlign: 'center', verticalAlign: 'top' }}>
                  Является ли место эксплуатации основным для прибора</th>
              </tr>
            </thead>
            <tbody>
              {device.rels_of_work.map((rel, idx) => (
                <tr key={idx}>
                  <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>{idx + 1}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{rel.cust_pl1?.rtuv2 || ''}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{rel.cust_pl1?.custhousev2 || ''}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{rel.cust_pl1?.custpostv2 || ''}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{rel.loc?.loctype || ''}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{rel.loc?.locname || ''}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>{rel.is_main_for_cust ? 'Основная' : 'Неосновная'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>{rel.main_for_dev ? 'Основное' : 'Неосновное'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#6c757d', fontStyle: 'italic' }}> Данные о местах эксплуатации отсутствуют</p>
        )}
      </div>

      {/* ТАБЛИЦА С ЦИКЛОМ: Вхождение прибора в госконтракты */}
      <div style={{ marginBottom: '40px', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
        <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>
          Входит в централизованные гос.контракты по услугам с ним. 
          Всего вхождений по данному прибору: {device.rels_of_contracts?.length || 0}
        </h3>
        {device.rels_of_contracts && device.rels_of_contracts.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', fontSize: '14px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'left' }}>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '40px', textAlign: 'center' }}>№</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Тип контракта</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '90px' }}>Номер</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '110px' }}>Дата контракта</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Тип услуг</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '220px' }}>Фактические услуги/работы с прибором</th>
              </tr>
            </thead>
            <tbody>
              {device.rels_of_contracts.map((contractRel, idx) => (
                <tr key={idx}>
                  <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>{idx + 1}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{contractRel.to_contract?.title || 'Данных нет'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{contractRel.to_contract?.number || 'Данных нет'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{contractRel.to_contract?.date_of || 'Данных нет'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{contractRel.to_doing?.title || 'Данных нет'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                    {/* Вложенный цикл обработки массива basis [] */}
                    {contractRel.basis && contractRel.basis.length > 0 ? (
                      <ul style={{ margin: 0, paddingLeft: '16px' }}>
                        {contractRel.basis.map((b, bIdx) => (
                          <li key={bIdx} style={{ marginBottom: '2px' }}>
                            {b.exact_moment ? new Date(b.exact_moment).toLocaleString() : 'Данных нет'}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <span style={{ color: '#999', fontStyle: 'italic' }}>Услуг/работ не было либо данных по ним нет</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#6c757d', fontStyle: 'italic' }}>Вхождений не было либо данные о них отсутствуют</p>
        )}
      </div>

    </div>
  );
}

export default DeviceDetail;
```



## 5. База знаний: Решенные проблемы сеанса

