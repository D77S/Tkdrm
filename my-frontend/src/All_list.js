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