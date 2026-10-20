import React, { useState, useEffect } from 'react';
import axios from 'axios';

function All_list() {
  const [devices, setDevices] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  
  // Создаем переменную в состоянии для динамического хранения размера страницы
  const [pageSize, setPageSize] = useState(20); 

  useEffect(() => {
    setLoading(true);
    axios.get(`http://localhost:8000/all_list/by_cpl5/?page=${currentPage}`)
      .then(response => {
        const dataResults = response.data.results || response.data;
        const totalCount = response.data.count || dataResults.length;
        
        // Динамически определяем, сколько элементов отдал бэкенд.
        // Если мы на первой странице, количество пришедших элементов и есть наш размер страницы (например, 500).
        if (dataResults.length > 0 && currentPage === 1) {
          setPageSize(dataResults.length);
        }

        setDevices(dataResults);
        
        // Теперь деление идет на реальный размер страницы, полученный от бэкенда
        const actualPageSize = dataResults.length > 0 ? dataResults.length : pageSize;
        setTotalPages(Math.ceil(totalCount / actualPageSize));
        
        setLoading(false);
      })
      .catch(error => {
        console.error("Критическая ошибка запроса к Django API:", error);
        alert(`Не удалось загрузить данные с бэкенда!\nПричина: ${error.message}\nПроверьте CORS или консоль F12.`);
        setLoading(false);
      });
  }, [currentPage, pageSize]);

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
            // Расчет сквозного номера теперь тоже завязан на динамический размер страницы pageSize
            const globalIndex = (currentPage - 1) * pageSize + index + 1;
            
            let targetRel = null;
            if (device.rels_of_work && device.rels_of_work.length > 0) {
              const mainRel = device.rels_of_work.find(rel => rel.is_main_for_cust === true);
              if (mainRel) {
                targetRel = mainRel;
              } else {
                targetRel = device.rels_of_work[0];
              }
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

      {/* Блок пагинации */}
     <div style={{ 
        display: 'flex', 
        gap: '6px', 
        alignItems: 'center', 
        justifyContent: 'center', 
        marginTop: '25px', 
        marginBottom: '40px',
        fontFamily: 'sans-serif'
      }}>
        {/* Кнопка НАЗАД */}
        <button 
          onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))} 
          disabled={currentPage === 1}
          style={{ 
            padding: '6px 14px', 
            marginRight: '12px',
            border: '1px solid #ccc',
            backgroundColor: currentPage === 1 ? '#e9ecef' : '#fff',
            cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
            borderRadius: '4px',
            fontSize: '14px'
          }}
        >
          Назад
        </button>

        {/* Генерация номеров страниц */}
        {(() => {
          const pages = [];
          
          // Увеличили радиус: теперь выводится по 4 страницы до и после текущей (всего до 9 страниц в центре)
          const range = 4; 

          for (let i = 1; i <= totalPages; i++) {
            // Всегда выводим первую, последнюю, предпоследнюю и широкий диапазон вокруг текущей
            if (
              i === 1 || 
              i === totalPages || 
              i === totalPages - 1 || 
              (i >= currentPage - range && i <= currentPage + range)
            ) {
              pages.push(
                <button
                  key={i}
                  onClick={() => setCurrentPage(i)}
                  style={{
                    padding: '6px 12px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: currentPage === i ? '#007bff' : '#fff',
                    color: currentPage === i ? '#fff' : '#007bff',
                    fontWeight: currentPage === i ? 'bold' : 'normal',
                    cursor: 'pointer',
                    minWidth: '40px',
                    fontSize: '14px'
                  }}
                >
                  {i}
                </button>
              );
            } 
            // Первое многоточие, если между первой страницей и левой границей диапазона есть разрыв
            else if (i === 2 && currentPage > range + 2) {
              pages.push(<span key="dots-start" style={{ padding: '0 10px', color: '#6c757d', userSelect: 'none', fontSize: '14px' }}>...</span>);
            } 
            // Второе многоточие, если между правой границей диапазона и предпоследней страницей есть разрыв
            else if (i === totalPages - 2 && currentPage < totalPages - range - 2) {
              pages.push(<span key="dots-end" style={{ padding: '0 10px', color: '#6c757d', userSelect: 'none', fontSize: '14px' }}>...</span>);
            }
          }
          return pages;
        })()}

        {/* Кнопка ВПЕРЕД */}
        <button 
          onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))} 
          disabled={currentPage === totalPages}
          style={{ 
            padding: '6px 14px', 
            marginLeft: '12px',
            border: '1px solid #ccc',
            backgroundColor: currentPage === totalPages ? '#e9ecef' : '#fff',
            cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
            borderRadius: '4px',
            fontSize: '14px'
          }}
        >
          Вперед
        </button>
      </div>
    </div>
  );
}

export default All_list;