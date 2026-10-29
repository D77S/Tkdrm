import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

function Dashboards() {
  const [mobilityData, setMobilityData] = useState([]); 
  const [catL1Data, setCatL1Data] = useState([]);
  const [stsoData, setStsoData] = useState([]);         
  const [conditionData, setConditionData] = useState([]); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    console.log("=== ОТЛАДКА: Запуск Promise.all запросов к бэкенду ===");

    Promise.all([
      axios.get('http://127.0.0.1:8000/all_list/dash/?dashname=dev_cat_l2'),
      axios.get('http://127.0.0.1:8000/all_list/dash/?dashname=dev_cat_l1'),
      axios.get('http://127.0.0.1:8000/all_list/dash/?dashname=dev_type_cat_l1_Y'),
      axios.get('http://127.0.0.1:8000/all_list/dash/?dashname=device_conditions')
    ])
      .then(([mobilityResponse, catL1Response, stsoResponse, conditionResponse]) => {
        console.log("1. Данные мобильности:", mobilityResponse.data);
        console.log("2. Дашборд2:", catL1Response.data);
        console.log("3. СТСО сырые данные:", stsoResponse.data);
        console.log("4. Данные исправности:", conditionResponse.data);

        setMobilityData(mobilityResponse.data || []);

        // Форматирование и жесткая сортировка для дашборда Категорий L1
        const formattedCatL1 = (catL1Response.data || []).map((item, idx) => ({
          name: item.name || `Категория #${idx + 1}`,
          value: Number(item.value || 0)
        }));
        formattedCatL1.sort((a, b) => b.value - a.value);
        setCatL1Data(formattedCatL1);

        // 2. Форматирование и жесткая сортировка для дашборда СТСО
        const formattedStso = (stsoResponse.data || []).map((item, idx) => ({
          name: item.type_title || item.name || `Тип #${idx + 1}`,
          value: Number(item.count || item.value || 0)
        }));
        formattedStso.sort((a, b) => b.value - a.value);
        setStsoData(formattedStso);

        setConditionData(conditionResponse.data || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Критическая ошибка во время отладки сетевых запросов:", err);
        setError(`Ошибка сети! Проверьте, запущен ли Django-сервер на порту 8000. Причина: ${err.message}`);
        setLoading(false);
      });
  }, []);

  const totalCatL1 = catL1Data.reduce((sum, item) => sum + item.value, 0);
  const totalStso = stsoData.reduce((sum, item) => sum + item.value, 0);

  if (loading) return <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>Загрузка данных дашборда...</div>;
  if (error) return <div style={{ padding: '20px', fontFamily: 'sans-serif', color: '#dc3545' }}>{error}</div>;

  return (
    <div style={{ padding: '0 2%', maxWidth: '1200px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2>Аналитические дашборды ТКДРМ</h2>

 {/* ДИАГРАММА 1: Мобильность */}
      <div style={{ 
        maxWidth: '900px', 
        margin: '0 auto 30px auto', 
        border: '1px solid #ddd', 
        padding: '25px', 
        borderRadius: '6px', 
        backgroundColor: '#fff', 
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)' 
      }}>
        <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '10px', color: '#333', textAlign: 'center' }}>
          Cостав парка приборов по категориям 2-го уровня (стационарные/переносные)
        </h3>
        
        <div style={{ width: '100%', height: 350, marginTop: '15px' }}>
          {mobilityData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={mobilityData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, value, percent }) => `${name}: ${value} шт. (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {mobilityData.map((entry, index) => {
                    const categoryName = entry.name?.toLowerCase() || '';
                    let cellColor = '#6c757d';
                    if (categoryName.includes('переносные')) {
                      cellColor = '#fd7e14';
                    } else if (categoryName.includes('стационарные')) {
                      cellColor = '#007bff';
                    }
                    return <Cell key={`mobility-cell-${index}`} fill={cellColor} />;
                  })}
                </Pie>
                <Tooltip formatter={(value) => [`${value} шт.`, 'Количество']} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#6c757d', fontStyle: 'italic' }}>
              База данных вернула пустой массив для этого графика.
            </div>
          )}
        </div>
      </div>

  {/* ДАШБОРД2: Категории уровня 1 с независимой HTML-легендой */}
      <div style={{ 
        maxWidth: '900px', 
        margin: '0 auto 30px auto', 
        border: '1px solid #ddd', 
        padding: '25px', 
        borderRadius: '6px', 
        backgroundColor: '#fff', 
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)' 
      }}>
        <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '10px', color: '#333', textAlign: 'center' }}>
          Состав парка приборов по категориям 1-го уровня
        </h3>
        
        {catL1Data.length > 0 ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '15px', height: 400 }}>
            
            {/* Круговой график */}
            <div style={{ width: '50%', height: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={catL1Data}
                    cx="50%" 
                    cy="50%"
                    labelLine={false} 
                    label={false}     
                    outerRadius={130} 
                    fill="#8884d8"
                    dataKey="value"
                    startAngle={90}
                    endAngle={-270}
                  >
                    {catL1Data.map((entry, index) => {
                      // Случайные цвета по золотому сечению на основе индекса
                      const randomHue = (index * 222.5) % 360; 
                      return <Cell key={`catl1-cell-${index}`} fill={`hsl(${randomHue}, 70%, 45%)`} />;
                    })}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} шт.`, 'Количество']} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Независимый HTML контейнер легенды (справа) */}
            <div style={{ 
              width: '45%', 
              maxHeight: '380px', 
              overflowY: 'auto', 
              fontSize: '13px', 
              paddingRight: '10px',
              fontFamily: 'sans-serif',
              lineHeight: '1.8'
            }}>
              {catL1Data.map((item, index) => {
                const randomHue = (index * 222.5) % 360;
                const color = `hsl(${randomHue}, 70%, 45%)`;
                const percentage = totalCatL1 > 0 ? ((item.value / totalCatL1) * 100).toFixed(1) : 0;

                return (
                  <div key={`catl1-leg-${index}`} style={{ display: 'flex', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ 
                      display: 'inline-block', 
                      width: '12px', 
                      height: '12px', 
                      backgroundColor: color, 
                      marginRight: '8px',
                      flexShrink: 0,
                      borderRadius: '2px'
                    }}></span>
                    <span style={{ color: '#333' }}>
                      <strong>{item.name}</strong>: {item.value} шт. ({percentage}%)
                    </span>
                  </div>
                );
              })}
            </div>

          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, color: '#6c757d', fontStyle: 'italic' }}>
            База данных вернула пустой массив для этого графика.
          </div>
        )}
      </div>

      {/* ДИАГРАММА 3: СТСО с независимой HTML-легендой */}
      <div style={{ 
        maxWidth: '900px', 
        margin: '0 auto 30px auto', 
        border: '1px solid #ddd', 
        padding: '25px', 
        borderRadius: '6px', 
        backgroundColor: '#fff', 
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)' 
      }}>
        <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '10px', color: '#333', textAlign: 'center' }}>
          Состав парка СТСО по типам СТСО
        </h3>
        
        {stsoData.length > 0 ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '15px', height: 400 }}>
            
            {/* График занимает левую часть */}
            <div style={{ width: '50%', height: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stsoData}
                    cx="50%" 
                    cy="50%"
                    labelLine={false} 
                    label={false}     
                    outerRadius={130} 
                    fill="#8884d8"
                    dataKey="value"
                    startAngle={90}
                    endAngle={-270}
                  >
                    {stsoData.map((entry, index) => {
                      const randomHue = (index * 137) % 360; 
                      return <Cell key={`stso-cell-${index}`} fill={`hsl(${randomHue}, 75%, 45%)`} />;
                    })}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} шт.`, 'Количество']} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Независимый HTML контейнер легенды (справа) */}
            <div style={{ 
              width: '45%', 
              maxHeight: '380px', 
              overflowY: 'auto', 
              fontSize: '13px', 
              paddingRight: '10px',
              fontFamily: 'sans-serif',
              lineHeight: '1.8'
            }}>
              {stsoData.map((item, index) => {
                const randomHue = (index * 137) % 360;
                const color = `hsl(${randomHue}, 75%, 45%)`;
                const percentage = totalStso > 0 ? ((item.value / totalStso) * 100).toFixed(1) : 0;

                return (
                  <div key={`html-leg-${index}`} style={{ display: 'flex', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ 
                      display: 'inline-block', 
                      width: '12px', 
                      height: '12px', 
                      backgroundColor: color, 
                      marginRight: '8px',
                      flexShrink: 0,
                      borderRadius: '2px'
                    }}></span>
                    <span style={{ color: '#333' }}>
                      <strong>{item.name}</strong>: {item.value} шт. ({percentage}%)
                    </span>
                  </div>
                );
              })}
            </div>

          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, color: '#6c757d', fontStyle: 'italic' }}>
            База данных вернула пустой массив для этого графика.
          </div>
        )}
      </div>

      {/* ДИАГРАММА 4: Исправность (выведена ниже) */}
      <div style={{ 
        maxWidth: '900px', 
        margin: '0 auto',
        border: '1px solid #ddd', 
        padding: '25px', 
        borderRadius: '6px', 
        backgroundColor: '#fff', 
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)' 
      }}>
        <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '10px', color: '#333', textAlign: 'center' }}>
          Состояние парка приборов по исправности
        </h3>
        
        <div style={{ width: '100%', height: 350, marginTop: '15px' }}>
          {conditionData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={conditionData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, value, percent }) => `${name}: ${value} шт. (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {conditionData.map((entry, index) => {
                    const isBroken = entry.name?.toLowerCase().includes('неисправен');
                    const cellColor = isBroken ? '#dc3545' : '#28a745';
                    
                    return <Cell key={`condition-cell-${index}`} fill={cellColor} />;
                  })}
                </Pie>
                <Tooltip formatter={(value) => [`${value} шт.`, 'Количество']} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#6c757d', fontStyle: 'italic' }}>
              База данных вернула пустой массив для этого графика.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboards;