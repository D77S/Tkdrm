import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

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
        let currentStepPageSize = 20; // дефолтное значение

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

        // Обновляем состояние через функцию. 
        // Если новое значение совпадает со старым (prev), React не будет делать лишних рендеров.
        setPageSize(prev => {
          // Если мы на последней странице (нет next) и нет параметров в URL, 
          // сохраняем предыдущий успешно определенный размер страницы
          if (!next && !targetUrl) return prev;
          return currentStepPageSize;
        });

        setDevices(dataResults);
        
        // Для расчета totalPages используем локально вычисленное на этом шаге значение,
        // а не переменную из стейта, чтобы линтер не ругался.
        setTotalPages(Math.ceil(totalCount / currentStepPageSize));
        setLoading(false);
      })
      .catch(error => {
        console.error("Критическая ошибка запроса к Django API:", error);
        alert(`Не удалось загрузить данные с бэкенда!\nПричина: ${error.message}\nПроверьте CORS или консоль F12.`);
        setLoading(false);
      });
  }, [currentPage]); // Теперь здесь честная и единственная зависимость. Ошибка ESLint исчезнет!

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
                  <Link to={`/devices/${device.id}`} style={{ color: '#007bff', textDecoration: 'none', marginRight: '12px', fontWeight: '500' }}>Подробно</Link>
                  <span style={{ color: '#28a745', cursor: 'pointer', marginRight: '12px', fontWeight: '500' }}>Редактировать</span>
                  <span style={{ color: '#dc3545', cursor: 'pointer', fontWeight: '500' }}>Удалить</span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Блок пагинации с исправленным расчетом окон */}
      {totalPages > 1 && (
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
            onClick={() => {
              setCurrentPage(prev => Math.max(prev - 1, 1));
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }} 
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

          {/* Логически верная генерация номеров страниц без дублирования точек */}
          {(() => {
            const pages = [];
            const range = 2; // Оптимальный радиус (текущая + 2 слева + 2 справа)

            for (let i = 1; i <= totalPages; i++) {
              if (
                i === 1 || 
                i === totalPages || 
                (i >= currentPage - range && i <= currentPage + range)
              ) {
                pages.push(
                  <button
                    key={i}
                    onClick={() => {
                      setCurrentPage(i);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
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
              // Контролируем вывод многоточия: ставим только ОДИН раз при переходе границы
              else if (i === 2 && currentPage > range + 2) {
                pages.push(<span key="dots-start" style={{ padding: '0 10px', color: '#6c757d', userSelect: 'none', fontSize: '14px' }}>...</span>);
                i = currentPage - range - 1; // Скачок цикла вперед к рабочей зоне
              } 
              else if (i === currentPage + range + 1 && i < totalPages) {
                pages.push(<span key="dots-end" style={{ padding: '0 10px', color: '#6c757d', userSelect: 'none', fontSize: '14px' }}>...</span>);
                i = totalPages - 1; // Скачок цикла в самый конец
              }
            }
            return pages;
          })()}

          {/* Кнопка ВПЕРЕД */}
          <button 
            onClick={() => {
              setCurrentPage(prev => Math.min(prev + 1, totalPages));
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }} 
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
      )}
    </div>
  );
}

export default All_list;