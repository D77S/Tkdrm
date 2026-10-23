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
                      <span style={{ color: '#999', fontStyle: 'italic' }}>Услуг/работ не было, либо данных по ним нет</span>
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
