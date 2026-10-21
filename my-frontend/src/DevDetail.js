import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

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

      <h2>Детальная информация о приборе № {device.id}</h2>

      {/* Основная сетка параметров девайса */}
      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '25px' }}>
        
        {/* Блок 1: Характеристики прибора */}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Характеристики прибора</h3>
          <p><strong>Тип:</strong> {device.type?.title || '—'}</p>
          <p><strong>Категория типа:</strong> {device.type?.category?.title || '—'}</p>
          <p><strong>Уровень категории (cat_l1):</strong> {device.type?.category?.cat_l1?.title || '—'}</p>
          <p><strong>Нормативный срок службы (lifetime):</strong> {device.type?.lifetime ? `${device.type.lifetime} лет` : '—'}</p>
          <p><strong>Подтип прибора (sub_type):</strong> {device.sub_type || '—'}</p>
          <p><strong>Серийный номер (serial):</strong> {device.serial || '—'}</p>
          <p><strong>Инвентарный номер (inventary):</strong> {device.inventary || '—'}</p>
          <p><strong>Категория ТСТК коммерческая (cat_number_c):</strong> {device.cat_number_c ?? '—'}</p>
          <p><strong>Категория ТСТК фактическая (cat_number_f):</strong> {device.cat_number_f ?? '—'}</p>
          <p><strong>Состояние прибора (condition - исправен):</strong> {device.condition ? '🟢 Исправен' : '🔴 Неисправен'}</p>
          <p><strong>Средство измерений (is_si):</strong> {device.is_si ? 'Да' : 'Нет'}</p>
          <p><strong>Учебный прибор (is_stud):</strong> {device.is_stud ? 'Да' : 'Нет'}</p>
          <p><strong>Статус использования (status_use):</strong> {device.status_use?.title || '—'}</p>
          <p><strong>Вид текущего обслуживания (service_type):</strong> {device.service_type?.title || '—'}</p>
          <p><strong>Источник финансирования (sour_type):</strong> {device.sour_type?.title || '—'}</p>
          <p><strong>Балансовая стоимость (cost):</strong> {device.cost || '—'}</p>
          <p><strong>Родительский прибор (upper_id):</strong> {device.upper_id || '—'}</p>
        </div>

        {/* Блок 2: Эксплуатационные сроки */}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Сроки и эксплуатация</h3>
          <p><strong>Дата производства (date_prod):</strong> {device.date_prod || '—'}</p>
          <p><strong>Дата ввода в эксплуатацию (date_expl):</strong> {device.date_expl || '—'}</p>
          <p><strong>Дата продления ресурса (date_prolong):</strong> {device.date_prolong || '—'}</p>
          <p><strong>Гарантийный период в месяцах (warr_period):</strong> {device.warr_period || '—'}</p>
          <p><strong>Дата истечения срока службы (date_prod_expired):</strong> {device.date_prod_expired || '—'}</p>
          <p><strong>Дата очередной поверки (date_verif):</strong> {device.date_verif || '—'}</p>
        </div>

        {/* Блок 3: Хранитель / Ответственное лицо */}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Ответственное лицо (Хранитель)</h3>
          {device.holder ? (
            <>
              <p><strong>Имя пользователя (username):</strong> {device.holder.username || '—'}</p>
              <p><strong>Фамилия:</strong> {device.holder.last_name || '—'}</p>
              <p><strong>Имя:</strong> {device.holder.first_name || '—'}</p>
              <p><strong>Отчество:</strong> {device.holder.pater_name || '—'}</p>
              <p><strong>Электронная почта (email):</strong> {device.holder.email || '—'}</p>
              <p><strong>Активен в системе (is_active):</strong> {device.holder.is_active ? 'Да' : 'Нет'}</p>
              <p><strong>Отдел сотрудника (dept):</strong> {device.holder.dept?.title || '—'}</p>
              
              <h4 style={{ marginBottom: '5px', marginTop: '15px' }}>Место службы сотрудника (empl):</h4>
              <p><strong>РТУ:</strong> {device.holder.empl?.rtuv2 || '—'}</p>
              <p><strong>Таможня:</strong> {device.holder.empl?.custhousev2 || '—'}</p>
              <p><strong>Таможенный пост:</strong> {device.holder.empl?.custpostv2 || '—'}</p>
            </>
          ) : <p style={{ color: '#6c757d', fontStyle: 'italic' }}>Ответственное лицо не назначено.</p>}
        </div>

        {/* Блок 4: Балансовый учет и примечания */}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Балансовый учет подразделения</h3>
          <p><strong>Балансодержатель (cp1_acc) -> РТУ:</strong> {device.cp1_acc?.rtuv2 || '—'}</p>
          <p><strong>Балансодержатель (cp1_acc) -> Таможня:</strong> {device.cp1_acc?.custhousev2 || '—'}</p>
          <p><strong>Балансодержатель (cp1_acc) -> Пост:</strong> {device.cp1_acc?.custpostv2 || '—'}</p>
          
          <h4 style={{ marginBottom: '5px', marginTop: '15px' }}>Текстовые примечания</h4>
          <p><strong>Примечание 1:</strong> {device.note1 || '—'}</p>
          <p><strong>Примечание 2:</strong> {device.note2 || '—'}</p>
          <p><strong>Примечание 3:</strong> {device.note3 || '—'}</p>
        </div>

      </div>

      {/* ТАБЛИЦА С ЦИКЛОМ: Связанные места эксплуатации (rels_of_work) */}
      <div style={{ marginBottom: '30px', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
        <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>
          Связанные места эксплуатации (rels_of_work) [Всего записей: {device.rels_of_work?.length || 0}]
        </h3>
        {device.rels_of_work && device.rels_of_work.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', fontSize: '14px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'left' }}>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '40px', textAlign: 'center' }}>№</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>РТУ подразделения</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Таможня подразделения</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Таможенный пост</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Наименование локации (locname)</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Тип локации (loctype)</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '140px', textAlign: 'center' }}>Флаг основного места</th>
              </tr>
            </thead>
            <tbody>
              {device.rels_of_work.map((rel, idx) => (
                <tr key={idx}>
                  <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>{idx + 1}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{rel.cust_pl1?.rtuv2 || '—'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{rel.cust_pl1?.custhousev2 || '—'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{rel.cust_pl1?.custpostv2 || '—'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{rel.loc?.locname || '—'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{rel.loc?.loctype || '—'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                    {rel.is_main_for_cust ? '🟢 Главное (True)' : 'Нет (False)'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#6c757d', fontStyle: 'italic' }}>Записи о местах эксплуатации отсутствуют в массиве.</p>
        )}
      </div>

      {/* ТАБЛИЦА С ЦИКЛОМ: Связанные госконтракты (rels_of_contracts) */}
      <div style={{ marginBottom: '40px', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
        <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>
          Связанные государственные контракты (rels_of_contracts) [Всего записей: {device.rels_of_contracts?.length || 0}]
        </h3>
        {device.rels_of_contracts && device.rels_of_contracts.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', fontSize: '14px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f4f4f4', textAlign: 'left' }}>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '40px', textAlign: 'center' }}>№</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Название контракта (title)</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '90px' }}>Номер</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '110px' }}>Дата контракта</th>
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Назначение работ (to_doing)</th>
                <th style={{ padding: '8px', border: '1px solid #ddd', width: '220px' }}>Временные отметки исполнения (basis)</th>
              </tr>
            </thead>
            <tbody>
              {device.rels_of_contracts.map((contractRel, idx) => (
                <tr key={idx}>
                  <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>{idx + 1}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{contractRel.to_contract?.title || '—'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{contractRel.to_contract?.number || '—'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{contractRel.to_contract?.date_of || '—'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{contractRel.to_doing?.title || '—'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                    {/* Вложенный цикл обработки массива basis [] */}
                    {contractRel.basis && contractRel.basis.length > 0 ? (
                      <ul style={{ margin: 0, paddingLeft: '16px' }}>
                        {contractRel.basis.map((b, bIdx) => (
                          <li key={bIdx} style={{ marginBottom: '2px' }}>
                            {b.exact_moment ? new Date(b.exact_moment).toLocaleString() : '—'}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <span style={{ color: '#999', fontStyle: 'italic' }}>Отметки отсутствуют (пустой массив)</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#6c757d', fontStyle: 'italic' }}>Записи о государственных контрактах отсутствуют в массиве.</p>
        )}
      </div>

    </div>
  );
}

export default DeviceDetail;
