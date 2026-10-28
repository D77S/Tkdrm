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
              <span style={tooltipIconStyle} title="Конкретная модель, например Янтарь-1А или РМ1203М и т.п. и т.п. , выбор из допустимых вариантов">?</span>
            </span>
          </p>
          <p><strong>Вышестоящий тип: </strong>
            <span style={{ whiteSpace: 'nowrap' }}>{device.type?.category?.title || 'Данных нет'}
              <span style={tooltipIconStyle} title="Например СТСО, Поисковые, Дозиметры и т.п. и т.п., выбор из допустимых вариантов">?</span>
            </span>
          </p>
          <p><strong>Вышестоящий тип: </strong>
            <span style={{ whiteSpace: 'nowrap' }}>{device.type?.category?.cat_l1?.title || 'Данных нет'}
              <span style={tooltipIconStyle} title="Стационарные или Переносные">?</span>
            </span>
          </p>
          <p><strong>Нормативный срок службы: </strong> <span style={{ whiteSpace: 'nowrap' }}>{device.type?.lifetime ? `${device.type.lifetime} лет` : 'Данных нет'}<span style={tooltipIconStyle} title="Берется из типа прибора и одинаков для всех приборов данного типа">?</span></span></p>
          <p><strong>Подтип прибора: </strong><span style={{ whiteSpace: 'nowrap' }}>{device.sub_type || 'Данных нет'}<span style={tooltipIconStyle} title="Если задан по конкретному прибору">?</span></span></p>
          <p><strong>Серийный номер: </strong> {device.serial || 'Данных нет'}</p>
          <p><strong>Инвентарный номер: </strong> {device.inventary || 'Данных нет'}</p>
          <p><strong>Категория прибора вычисленная: </strong> <span style={{ whiteSpace: 'nowrap' }}>{device.cat_number_c ?? 'Данных нет'}<span style={tooltipIconStyle} title="Вычисляется из сопоставления дат по прибору. Прибор между датой ввода и датой конца гарантии - кат.1, прибор между концом гарантии и концом срока службы - кат. 2, прибор за концом срока службы - кат. 3. Дат конца срока службы может быть несколько, если были продления этой даты, например по некоторым работам с прибором (ниже), тогда берется самая поздняя из этих дат.">?</span></span></p>
          <p><strong>Категория прибора фактическая: </strong> <span style={{ whiteSpace: 'nowrap' }}>{device.cat_number_f ?? 'Данных нет'}<span style={tooltipIconStyle} title="Берется из базы данных. Туда попадает если по прибору есть документальное решение (приказ, акт), которым ему установлена данная категория">?</span></span></p>
          <p>
            <strong>Категорий соответствие выч. и факт.: </strong>
            {device.cats_corresp ? '🟢 Соотв. друг другу' : '🔴 Несоотв. друг другу'}
          </p>
          <p><strong>Состояние прибора: </strong> <span style={{ whiteSpace: 'nowrap' }}>{device.condition ? '🟢 Исправен' : '🔴 Неисправен'}<span style={tooltipIconStyle} title="Берется из базы данных. Прибор исправен на дату внесения сведений в базу данных, если на эту дату он достоверно исправен на 100%, включая все его составные части. Исправный прибор, являющийся СИ, может быть не поверен, но всё равно достоверно исправен. Во всех иных случаях он должен считаться как неисправен (в том числе 'находится на ремонте', 'в процессе диагностики', 'почти исправен', 'непонятно исправен или нет', 'нельзя определить исправен или нет', 'не калибруется', 'не включается' и т.п. и т.п.).">?</span></span></p>
          <p><strong>Является ли прибор средством измерения: </strong> <span style={{ whiteSpace: 'nowrap' }}>{device.is_si ? 'Да' : 'Нет'}<span style={tooltipIconStyle} title="Конкретный экземпляр">?</span></span></p>
          <p><strong>Является ли прибор учебным: </strong> <span style={{ whiteSpace: 'nowrap' }}>{device.is_stud ? 'Да' : 'Нет'}<span style={tooltipIconStyle} title="Конкретный экземпляр">?</span></span></p>
          <p><strong>Статус использования: </strong> <span style={{ whiteSpace: 'nowrap' }}>{device.status_use?.title || 'Данных нет'}<span style={tooltipIconStyle} title="Используется, Демонтировано, На хранении, и т.п. и т.п., выбор из допустимых вариантов. Внимание, если прибор УЖЕ списан, то он должен быть вообще удалён из базы данных.">?</span></span></p>
          <p><strong>Статус по включению в централизованные ГК: </strong><span style={{ whiteSpace: 'nowrap' }}> {device.service_type?.title || 'Данных нет'}<span style={tooltipIconStyle} title="Конкретный экземпляр, подлежит ли включению в контракты, и в какие, за гос. бюджет или за сторонний, централизованные или децентрализованные, на ремонт, на т.о., или и то и то. Выбор из допустимых вариантов.">?</span></span></p>
          <p><strong>Собственник прибора: </strong><span style={{ whiteSpace: 'nowrap' }}> {device.sour_type?.title || 'Данных нет'}<span style={tooltipIconStyle} title="Конкретного экземпляра, например РФ в лице т.о., РФ в лице Росгранстрой, Сторонний (владелец СВХ, владелец аэропорта и т.п.и т.п.) Выбор из допустимых вариантов.">?</span></span></p>
          <p><strong>Балансовая стоимость: </strong><span style={{ whiteSpace: 'nowrap' }}> {device.cost || 'Данных нет'}<span style={tooltipIconStyle} title="Конкретного экземпляра, включая (если есть) все его составные части, в него входящие. Если известно. И если известно отдельно на данный прибор. В рублях.">?</span></span></p>
          <p><strong>Вышестоящий прибор: </strong><span style={{ whiteSpace: 'nowrap' }}> {device.upper_id ? (<Link to={`/devices/${device.upper_id}`} style={{ color: '#007bff', textDecoration: 'none', fontWeight: '500' }}>Прибор № {device.upper_id}</Link>) : ('Данных нет')}<span style={tooltipIconStyle} title="Конкретного экземпляра. Если известно. В виде ссылки на страничку того другого прибора. Например, для видеокамеры Янтаря может быть ссылка на Янтарь, к которому она относится. Запрещены циклические цепочки ссылок.">?</span></span></p>
        </div>

        {/* Блок 2: Эксплуатационные сроки */}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Даты по эксплуатации</h3>
          <p><strong>Дата изготовления:</strong> {device.date_prod || 'Данных нет'}</p>
          <p><strong>Дата ввода в эксплуатацию:</strong> <span style={{ whiteSpace: 'nowrap' }}>{device.date_expl || 'Данных нет'}<span style={tooltipIconStyle} title="Первоначальная. Сразу после как прибор попал в таможенный орган. Не дата ввода после очередного ремонта!">?</span></span></p>
          <p><strong>Дата продления срока службы:</strong> <span style={{ whiteSpace: 'nowrap' }}>{device.date_prolong || 'Данных нет'}<span style={tooltipIconStyle} title="Вычисляемое значение. Равно либо дате первоначального ввода, либо дате последнего продления срока службы, смотря что позднее.">?</span></span></p>
          <p><strong>Гарантийный срок при поставке, месяцев:</strong> {device.warr_period  || 'Данных нет'}</p>
          <p><strong>Дата истечения срока службы:</strong> <span style={{ whiteSpace: 'nowrap' }}>{device.date_prod_expired || 'Данных нет'}<span style={tooltipIconStyle} title="Вычисляемое значение. К дате первоначального ввода либо дате последнего продления срока службы, смотря что позднее, прибавлена величина срока службы приборов данного типа.">?</span></span></p>
          <p><strong>Дата окончания последней поверки:</strong> {device.date_verif || 'Данных нет'}</p>
        </div>

        {/* Блок 3: Лицо, ответственное за эксплуатацию прибора*/}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Лицо, ответственное за эксплуатацию прибора<span style={{ whiteSpace: 'nowrap' }}><span style={tooltipIconStyle} title="Всегда должно быть назначено для прибора. Всегда должно быть единственное по прибору. Всегда должно иметь ФИО; отдел; т.орган, где числится его отдел. Отдел - выбор из перечня вариантов.">?</span></span></h3>
          {device.holder ? (
            <>
              <p><strong>Login:</strong> {device.holder.username || 'Данных нет'}</p>
              <p><strong>Фамилия:</strong> {device.holder.last_name || 'Данных нет'}</p>
              <p><strong>Имя:</strong> {device.holder.first_name || 'Данных нет'}</p>
              <p><strong>Отчество:</strong> {device.holder.pater_name || 'Данных нет'}</p>
              <p><strong>Электронная почта:</strong> {device.holder.email || 'Данных нет'}</p>
              <p><strong>Статус в данном ПО:</strong> {device.holder.is_active ? 'Активен' : 'Временно деактивирован'}</p>
              <p><strong>Отдел таможенного органа:</strong> {device.holder.dept?.title || 'Данных нет'}</p>
              
              <h4 style={{ marginBottom: '5px', marginTop: '15px' }}>Т.орган, в котором числится его отдел:</h4>
              <p><strong>РТУ:</strong> {device.holder.empl?.rtuv2 || ''}</p>
              <p><strong>Таможня:</strong> {device.holder.empl?.custhousev2 || ''}</p>
              <p><strong>Таможенный пост:</strong> {device.holder.empl?.custpostv2 || ''}</p>
            </>
          ) : <p style={{ color: '#6c757d', fontStyle: 'italic' }}>Данные о лице отсутствуют</p>}
        </div>

        {/* Блок 4: (За)балансовый учет и примечания */}
        <div style={{ flex: '1 1 45%', border: '1px solid #ddd', padding: '15px', borderRadius: '4px', backgroundColor: '#fff' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #eee', paddingBottom: '8px' }}>(За)балансовый учет и примечания</h3>
          <p><strong>Т.орган, в котором прибор на балансовом, либо забалансовом, учёте:</strong><span style={{ whiteSpace: 'nowrap' }}><span style={tooltipIconStyle} title="Всегда должно быть назначено для прибора. Всегда должно быть единственное по прибору. Может быть либо таможней, либо РТУ, либо одним из постов непосредственного подчинения (на данный момент таких всего два, Юго-Осетинский и Абхазский).">?</span></span></p>
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
          <span style={{ whiteSpace: 'nowrap' }}><span style={tooltipIconStyle} title="По каждому прибору можеть быть от 0 (ноль) до нескольких (много) таких строк. Чаще всего строка будет одна. Выбор из заданных вариантов сочетаний т.органа и локации. Для каждого прибора можеть быть не более 1 (одного) основного (приоритетного) и любого количества неосновных (неприоритетных) сочетаний. По каждому т.органу может быть не более 1 (одной) основной (приоритетной) локации и любого количества неосновных (неприоритетных) локаций. Например, если в базе есть четыре строки по данному прибору. Прибор эксплуатируется: 1. 'Южным постом' в 'АПП Новое' и это основное для этого прибора, основное для этого поста; 2. 'Южным постом' в 'ЖДПП Старое' и это неосновное для этого прибора, неосновное для этого поста; 3. 'Северным постом' в 'АПП Новое' и это неосновное для этого прибора, основное для этого поста; 4. 'Западным постом' в 'ММПО Большое' и это неосновное для этого прибора, неосновное для этого поста. Без наличия какой-либо локации разрешено эксплуатировать РТУ, таможням, и лишь некоторым постам.">?</span></span>
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
          Входит(входил) в централизованные гос.контракты по услугам/работам с данным прибором. 
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
                <th style={{ padding: '8px', border: '1px solid #ddd' }}>Тип услуг/работ</th>
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
                            {b.exact_moment ? new Date(b.exact_moment).toLocaleDateString() : 'Данных нет'}
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
