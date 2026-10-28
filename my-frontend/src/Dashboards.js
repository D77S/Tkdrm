import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer 
} from 'recharts';

function Dashboards() {
  const [conditionData, setConditionData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    axios.get('http://127.0.0.1:8000/all_list/dash/?dashname=device_conditions')
      .then(response => {
        setConditionData(response.data || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Критическая ошибка запроса к Django API:", err);
        setError(`Ошибка сети! Проверьте, запущен ли Django-сервер на порту 8000. Причина: ${err.message}`);
        setLoading(false);
      });
  }, []);

  if (loading) return <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>Загрузка данных дашборда...</div>;
  if (error) return <div style={{ padding: '20px', fontFamily: 'sans-serif', color: '#dc3545' }}>{error}</div>;

  return (
    <div style={{ padding: '0 2%', maxWidth: '1200px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2>Аналитические дашборды ТКДРМ</h2>

      {/* Расширенный контейнер (maxWidth: 900px), чтобы длинные подписи секторов не обрезались */}
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
                    
                    return <Cell key={`cell-${index}`} fill={cellColor} />;
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