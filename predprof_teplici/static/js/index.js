// ссылка для получения данных с сенсоров
const url = "http://127.0.0.1:80/api/sensors_data?time_period=100";
// ссылка для получения состояний систем (полива, окна, увлажнения)
const url_states = "http://127.0.0.1:80/api/state";
// ссылка для получения устновленных параметров T, H, Hb
const url_system = `http://127.0.0.1:80/api/parameters`;
// ссылка для ручного ввода показаний с датчиков
const url_set_sensors_data = "http://127.0.0.1:80/api/add_data";

let ctx = document.getElementById('GRAAAPH').getContext("2d");
let table = document.getElementById('table');

let parameters_form = document.forms.set_parameters_form;
let new_data_form = document.forms.set_new_data;

let current_graph = {
    name: 'AirMean',
    id: 0
};
function addZeros(x){
    // Добавление нулей для получения двузначного числа
    // ("0" + x).slice(-2) == 1 -> 01 == 12 -> 12
    return ("0" + x).slice(-2)
}
function toDateTime(millisecs) {
    // Миллисекунды в дату ( 2023-02-17 20:38:05 )
    var t = new Date(0);
    t.setMilliseconds(millisecs);
    let date = t.getFullYear() + '-' + addZeros(t.getMonth()+1) + '-' + addZeros(t.getDate());
    let time = addZeros(t.getHours()) + ':' + addZeros(t.getMinutes()) + ':' + addZeros(t.getSeconds());
    return  date + ' ' + time;
}

function timeLabels(arr_of_times){
    // Преобразование времени в дату
    let times = arr_of_times.slice()
    for(let i = 0; i < times.length; i++){
        times[i] = toDateTime(times[i]);
    }
    return times;
}

var dataset = {
    'AirMean': {},
    'AirSensors': [
        {},
        {},
        {},
        {}
    ],
    'GroundSensors': [
        {},
        {},
        {},
        {},
        {},
        {}
    ]
}
var states = {};
var states_elements = {};
var sensors_elements = {};
var data = [];
        
class Parametr_Element {
    constructor(name, value=0) {
        this.elements = new Array();
        for(var element of document.getElementsByName(name)){
            this.elements.push(element);
        }
        this.text = this.elements[0].innerHTML;
        this.value = value;
    }
    set_value(value) {
        this.value = value;
        if (this.value != null){
            for(let i = 0; i<this.elements.length; i++){
                this.elements[i].innerHTML = this.text + " " + this.value;
            }
        }else{
            for(let i = 0; i<this.elements.length; i++){
                this.elements[i].innerHTML = this.text + " " + "-";
            }
        }
    }

}
/*
class Parametr_Element {
    constructor(id, value=0) {
        this.element = document.getElementsById(id);
        this.text = this.element.innerHTML;
        this.value = value;
    }
    set_value(value) {
        this.value = value;
        if (this.value != null){
            this.element.innerHTML = this.text + " " + this.value;
        }else{
            this.element.innerHTML = this.text + " " + "-";
        }
    }

}
*/
class State_System_Element {
    constructor(id, state=0) {
        this.element = document.getElementById(id);
        this.state = state;
    }

    update() {
        if (this.state == 0){
            this.element.style.border = '2px solid red';
            this.element.style.boxShadow = '0 0 10px 0 red';
        }
        if (this.state == 1){
            this.element.style.border = '2px solid green';
            this.element.style.boxShadow = '0 0 10px 0 green';
        }
        if (this.state == 2){
            this.element.style.border = '2px solid white';
            this.element.style.boxShadow = '0 0 0 0 white';
        }
    }
    set_state(state) {
        this.state = state;
        this.update();
    }

}
function get_last_elem(arr){
    return arr[arr.length - 1]
}
async function update_last_data_from_sensors_elements(){
    // установка последних данных с сенсеров всем элементам 
    //arr[arr.length - 1]
    sensors_elements["mean_temp_air_sensor"].set_value(get_last_elem(data.air[4][0]));
    sensors_elements["mean_hum_air_sensor"].set_value(get_last_elem(data.air[4][1]));
    sensors_elements["air_temp_sensor_1"].set_value(get_last_elem(data.air[0][0]));
    sensors_elements["air_temp_sensor_2"].set_value(get_last_elem(data.air[1][0]));
    sensors_elements["air_temp_sensor_3"].set_value(get_last_elem(data.air[2][0]));
    sensors_elements["air_temp_sensor_4"].set_value(get_last_elem(data.air[3][0]));
    
    sensors_elements["air_hum_sensor_1"].set_value(get_last_elem(data.air[0][1]));
    sensors_elements["air_hum_sensor_2"].set_value(get_last_elem(data.air[1][1]));
    sensors_elements["air_hum_sensor_3"].set_value(get_last_elem(data.air[2][1]));
    sensors_elements["air_hum_sensor_4"].set_value(get_last_elem(data.air[3][1]));
    
    sensors_elements["groud_hum_sensor"][0].set_value(get_last_elem(data.ground[0][0]));
    sensors_elements["groud_hum_sensor"][1].set_value(get_last_elem(data.ground[1][0]));
    sensors_elements["groud_hum_sensor"][2].set_value(get_last_elem(data.ground[2][0]));
    sensors_elements["groud_hum_sensor"][3].set_value(get_last_elem(data.ground[3][0]));
    sensors_elements["groud_hum_sensor"][4].set_value(get_last_elem(data.ground[4][0]));
    sensors_elements["groud_hum_sensor"][5].set_value(get_last_elem(data.ground[5][0]));


}
/*
{
    air: [
        [ - 1 sensor
            [value, value, value, value...], - T
            [value, value, value, value...], - Hum
            [time, time, time, time...] - Time
        ],
        ...
        ...
        ...
        [ - mean of data
            [value, value, value, value...], - T
            [value, value, value, value...], - Hum
            [time, time, time, time...] - Time
        ]
    ],
    ground: [
        [ - 1 sensor
            [value, value, value, value...], - Hum
            [time, time, time, time...] - Time
        ],
        ...
        ...
        ...
        ...
        ...
        [ - mean of data
            [value, value, value, value...], - Hum
            [time, time, time, time...] - Time
        ]
    ]
}
*/
function initiate_dataset(){
    // создание заготовки стиля для графиков
    let default_dot_color = 'rgba(0, 0, 0, 0)';
    let color_air_temperature = 'rgb(235, 62, 54)';
    let color_air_humidity = 'rgb(54, 102, 235)';
    let color_ground_humidity = 'rgb(54, 102, 235)';

    dataset.AirMean.data = {
        labels: [],
        datasets: [
        {
            label: 'Ср. температура воздуха °C',
            backgroundColor: color_air_temperature,
            borderColor: color_air_temperature,
            data: [],
            fill: false,
            pointBorderColor: default_dot_color,
            pointBackgroundColor: default_dot_color,
            pointHoverBackgroundColor: color_air_temperature,
            pointHoverBorderColor: color_air_temperature,
        },
        {
            label: 'Ср. влажность воздуха %',
            backgroundColor: color_air_humidity,
            borderColor: color_air_humidity,
            data: [],
            fill: false,
            pointBorderColor: default_dot_color,
            pointBackgroundColor: default_dot_color,
            pointHoverBackgroundColor: color_air_humidity,
            pointHoverBorderColor: color_air_humidity,
        },
        ]
    };

    for(let i = 0; i < 4; i++){
        dataset.AirSensors[i].data = {
            labels: [],
            datasets: [
            {
                //lineTension: 0,
                label: 'Температура воздуха °C ( Датчик ' + (i+1) + ' )',
                backgroundColor: color_air_temperature,
                borderColor: color_air_temperature,
                data: [],
                fill: false,
                pointBorderColor: default_dot_color,
                pointBackgroundColor: default_dot_color,
                pointHoverBackgroundColor: color_air_temperature,
                pointHoverBorderColor: color_air_temperature,
            },
            {
                //lineTension: 0,
                label: 'Влажность воздуха % ( Датчик ' + (i+1) + ' )',
                backgroundColor: color_air_humidity,
                borderColor: color_air_humidity,
                data: [],
                fill: false,
                pointBorderColor: default_dot_color,
                pointBackgroundColor: default_dot_color,
                pointHoverBackgroundColor: color_air_humidity,
                pointHoverBorderColor: color_air_humidity,
            }
            ]
        }
    }
    
    for(let i = 0; i < 6; i++){
        dataset.GroundSensors[i].data = {
            labels: [],
            datasets: [
            {
                label: 'Влажность почвы % ( Датчик ' + (i+1) + ' )',
                backgroundColor: color_ground_humidity,
                borderColor: color_ground_humidity,
                data: [],
                fill: false,
                pointBorderColor: default_dot_color,
                pointBackgroundColor: default_dot_color,
                pointHoverBackgroundColor: color_ground_humidity,
                pointHoverBorderColor: color_ground_humidity,
            }
            ]
        }
    }
    
}
function initiate_states_elements(){
    states_elements["fork_drive"] = new State_System_Element('fork_drive_element');
    states_elements["total_hum"] = new State_System_Element('total_hum_element');
    states_elements["emergency"] = new State_System_Element('emergency_element');
    states_elements["watering"] = [];
    for(let i = 0; i < 6; i++){
    states_elements["watering"][i] = new State_System_Element(`watering_${i+1}_element`)
    }
}
function initiate_params_elements(){
    states_elements["T_element"] = new Parametr_Element('T_element');
    states_elements["H_element"] = new Parametr_Element('H_element');
    states_elements["Hb_element"] = new Parametr_Element('Hb_element');
}
function initiate_sensors_elements(){
    sensors_elements["mean_temp_air_sensor"] = new Parametr_Element('mean_temp_air_sensor');
    sensors_elements["mean_hum_air_sensor"] = new Parametr_Element('mean_hum_air_sensor');
    sensors_elements["air_temp_sensor_1"] = new Parametr_Element('air_temp_sensor_1');
    sensors_elements["air_temp_sensor_2"] = new Parametr_Element('air_temp_sensor_2');
    sensors_elements["air_temp_sensor_3"] = new Parametr_Element('air_temp_sensor_3');
    sensors_elements["air_temp_sensor_4"] = new Parametr_Element('air_temp_sensor_4');
    
    sensors_elements["air_hum_sensor_1"] = new Parametr_Element('air_hum_sensor_1');
    sensors_elements["air_hum_sensor_2"] = new Parametr_Element('air_hum_sensor_2');
    sensors_elements["air_hum_sensor_3"] = new Parametr_Element('air_hum_sensor_3');
    sensors_elements["air_hum_sensor_4"] = new Parametr_Element('air_hum_sensor_4');
    
    sensors_elements["groud_hum_sensor"] = [];
    sensors_elements["groud_hum_sensor"][0] = new Parametr_Element('groud_hum_sensor_1');
    sensors_elements["groud_hum_sensor"][1] = new Parametr_Element('groud_hum_sensor_2');
    sensors_elements["groud_hum_sensor"][2] = new Parametr_Element('groud_hum_sensor_3');
    sensors_elements["groud_hum_sensor"][3] = new Parametr_Element('groud_hum_sensor_4');
    sensors_elements["groud_hum_sensor"][4] = new Parametr_Element('groud_hum_sensor_5');
    sensors_elements["groud_hum_sensor"][5] = new Parametr_Element('groud_hum_sensor_6');
}
function update_states(){
    states_elements["fork_drive"].set_state(states["fork_drive"]);
    states_elements["total_hum"].set_state(states["total_hum"]);
    states_elements["emergency"].set_state(states["emergency"]);
    if (states["fork_drive"] == 0 && sensors_elements["mean_temp_air_sensor"].value < states_elements["T_element"].value && states_elements["T_element"].value != null){
        states_elements["fork_drive"].set_state(2);
    }
    if (states["total_hum"] == 0 && sensors_elements["mean_hum_air_sensor"].value > states_elements["H_element"].value && states_elements["H_element"].value != null){
        states_elements["total_hum"].set_state(2);
    }
    for(let i = 0; i < 6; i++){
    states_elements["watering"][i].set_state(states["watering"][i]);
    if (states["watering"][i] == 0 && sensors_elements["groud_hum_sensor"][i].value > states_elements["Hb_element"].value && states_elements["Hb_element"].value != null){
        states_elements["watering"][i].set_state(2);
    }
    }
}
function update_params(){
    states_elements["T_element"].set_value(states["parameters"]["T"]);
    states_elements["H_element"].set_value(states["parameters"]["H"]);
    states_elements["Hb_element"].set_value(states["parameters"]["Hb"]);
}
async function get_data_from_api(){
    let response = await fetch(url);

    if (response.ok){
        let json = await response.json();
        console.log(json);
        data = json.result;
        draw_graph(current_graph.name, current_graph.id);
        await update_last_data_from_sensors_elements();
        await api_update_states_and_params();
        
    }
}
async function update_params_in_form(){
    parameters_form.max_temp.value = states["parameters"]["T"];
    parameters_form.min_hum.value = states["parameters"]["H"];
    parameters_form.min_ground_hum.value = states["parameters"]["Hb"];
}
async function api_update_states_and_params(){
    let response = await fetch(url_states);

    if (response.ok){
        let json = await response.json();
        states = json.result;
        update_params();
        update_states();
    }
}
initiate_dataset();
initiate_states_elements();
initiate_params_elements();
initiate_sensors_elements();

/*get_data_from_api();
setTimeout(
    () => {
        console.log(states);
        update_params_in_form();
    }, 1000
);*/
get_data_from_api().then(
    () => {
        update_params_in_form();
    }
);
var chart = new Chart(ctx, {
    type: 'line',
    data: dataset.AirMean.data,
    
    options:{
        animation: {
            duration: 0
        },
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'index',
            intersect: false
        },
        scales: {
            xAxes: [{         
                ticks: {
                    autoSkip: false,
                    maxRotation: 0,
                    minRotation: 0
                },
                
                afterTickToLabelConversion: function(data){
                    let xLabels = data.ticks;

                    xLabels.forEach(function (labels, i) {
                        if (i % 5 != 0){
                            xLabels[i] = '';
                        }
                    });
                } 
            }],
            yAxes: [{
                display: true,
                ticks: {
                    beginAtZero: true
                },
                /*
                ticks: {
                    suggestedMin: 20,
                    suggestedMax: 80,
                },
                afterTickToLabelConversion: function(data){
                    let xLabels = data.ticks;

                    xLabels.forEach(function (labels, i) {
                        xLabels[i] = xLabels[i] + ' °C';
                    });
                } 
                */
            }]
            
        }
    }
}); 
/*
<tr>
    <th scope="col">Time</th>
    <th scope="col">1</th>
</tr>
<tr>
    <th scope="row">Monday</th>
    <td>35</td>
</tr>
*/
function update_table(){
    if (current_graph.name != "GroundSensors"){
        table.innerHTML = `
            <tr>
                <th scope="col">Время</th>
                <th scope="col">1</th>
                <th scope="col">2</th>
                <th scope="col">3</th>
                <th scope="col">4</th>
                <th scope="col">Ср. температура</th>
                <th scope="col">1</th>
                <th scope="col">2</th>
                <th scope="col">3</th>
                <th scope="col">4</th>
                <th scope="col">Ср. влажность</th>
            </tr>
        `;
        for(let i = 0; i < data.air[4][2].length; i++){
            table.innerHTML += 
            `
            <tr>
                <th scope="row">${toDateTime(data.air[4][2][i])}</th>
                <td>${data.air[0][0][i]}</td>
                <td>${data.air[1][0][i]}</td>
                <td>${data.air[2][0][i]}</td>
                <td>${data.air[3][0][i]}</td>
                <td>${data.air[4][0][i]}</td>

                <td>${data.air[0][1][i]}</td>
                <td>${data.air[1][1][i]}</td>
                <td>${data.air[2][1][i]}</td>
                <td>${data.air[3][1][i]}</td>
                <td>${data.air[4][1][i]}</td>
            </tr>
            `
            ;
        }
    }else{
        table.innerHTML = `
            <tr>
                <th scope="col">Время</th>
                <th scope="col">1</th>
                <th scope="col">2</th>
                <th scope="col">3</th>
                <th scope="col">4</th>
                <th scope="col">5</th>
                <th scope="col">6</th>
            </tr>
        `;
        for(let i = 0; i < data.air[4][2].length; i++){
            table.innerHTML += `
            <tr>
                <th scope="row">${toDateTime(data.air[4][2][i])}</th>
                <td>${data.ground[0][0][i]}</td>
                <td>${data.ground[1][0][i]}</td>
                <td>${data.ground[2][0][i]}</td>
                <td>${data.ground[3][0][i]}</td>
                <td>${data.ground[4][0][i]}</td>
                <td>${data.ground[5][0][i]}</td>
            </tr>
            `;
        }
    }
}

function draw_graph(name="", sensor_id=0){
    if (name=="AirMean"){
        if (current_graph.name != name){
            chart.data = dataset.AirMean.data;
        }

        chart.data.datasets[0].data = data.air[4][0];
        chart.data.datasets[1].data = data.air[4][1];
        chart.data.labels = timeLabels(data.air[4][2]);
    }
    if (name=="AirSensors"){

        if (current_graph.name != name || sensor_id != current_graph.id){
            chart.data = dataset.AirSensors[sensor_id].data;
        }

        if (sensor_id <= 4 && sensor_id >= 0){
            chart.data.datasets[0].data = data.air[sensor_id][0];
            chart.data.datasets[1].data = data.air[sensor_id][1];
            chart.data.labels = timeLabels(data.air[sensor_id][2]);
        }
    }
    if (name=="GroundSensors"){

        if (current_graph.name != name || sensor_id != current_graph.id){
            chart.data = dataset.GroundSensors[sensor_id].data;
        }

        if (sensor_id <= 6 && sensor_id >= 0){
            chart.data.datasets[0].data = data.ground[sensor_id][0];
            chart.data.labels = timeLabels(data.ground[sensor_id][1]);
        }
    }
    current_graph.name = name;
    current_graph.id = sensor_id;
    
    update_table();
    chart.update();
}
function value_to_Number(x){
    return Number(Number(x).toFixed(1))
}
async function switch_system(system = '', watering_id=0){
    let url_system = `http://127.0.0.1:80/api/${system}`;
    let patch_body = {};
    let accept_switch_system = true;
    let emergency = states_elements["emergency"].state
    const toast_time = 4000;
    if (system=='watering') {
        sensors_elements["groud_hum_sensor"][watering_id].value
        patch_body = {
            state: Math.abs(states_elements[system][watering_id].state-1),
            id: watering_id+1
        };
        
        if (!emergency && (states_elements[system][watering_id].state == 0 || states_elements[system][watering_id].state == 2) &&
        sensors_elements["groud_hum_sensor"][watering_id].value > states_elements["Hb_element"].value  && states_elements["Hb_element"].value != undefined  && states_elements["Hb_element"].value != null){
            new Toast({
                title: false,
                text: `Влажность в бороздке №${watering_id+1}  больше установленного минимума для поливания`,
                theme: 'danger',
                autohide: true,
                interval: toast_time
            });
            accept_switch_system = false;
        }
        
    }else{
        if (!emergency && system == "fork_drive"){
            if ((states_elements[system].state == 0 || states_elements[system].state == 2) &&
            sensors_elements["mean_temp_air_sensor"].value < states_elements["T_element"].value && states_elements["T_element"].value){
                new Toast({
                    title: false,
                    text: 'Средняя температура воздуха меньше установленного максимума для открытия форточек',
                    theme: 'danger',
                    autohide: true,
                    interval: toast_time
                });
                accept_switch_system = false;
            }
        }
        if (!emergency && system == "total_hum"){
            if ((states_elements[system].state == 0 || states_elements[system].state == 2) &&
            sensors_elements["mean_temp_air_sensor"].value > states_elements["H_element"].value && states_elements["Hb_element"].value != undefined  && states_elements["Hb_element"].value != null){
                new Toast({
                    title: false,
                    text: 'Средняя влажность воздуха больше установленного минимума для общего увлажнения',
                    theme: 'danger',
                    autohide: true,
                    interval: toast_time
                });
                accept_switch_system = false;
            }
        }

        patch_body = {
            state: Math.abs(states_elements[system].state-1),
        };
    }
    if (!accept_switch_system){
        return;
    }
    fetch(url_system, {
        method: 'PATCH',
        body: JSON.stringify(
            patch_body
        ),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
        },
        })
        .then((response) => response.json());
    setTimeout(api_update_states_and_params, 100);
}
async function submit_parameters_form(system = '', watering_id=0){
    let patch_body = {};
    
    patch_body = {
        T:  value_to_Number(parameters_form.max_temp.value),
        H:  value_to_Number(parameters_form.min_hum.value),
        Hb: value_to_Number(parameters_form.min_ground_hum.value)
    };

    fetch(url_system, {
        method: 'PATCH',
        body: JSON.stringify(
            patch_body
        ),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
        },
        })
        .then((response) => response.json());
    setTimeout(api_update_states_and_params, 100);
}
async function submit_new_data_form(){
    let patch_body = {};
    let new_air_data = [];
    let new_ground_data = [];

    for(let i = 0; i < 4; i++){
        new_air_data.push([value_to_Number(new_data_form[`add_air_temp_sensor_${i+1}`].value),value_to_Number(new_data_form[`add_air_hum_sensor_${i+1}`].value)]);
    }

    for(let i = 0; i < 6; i++){
        new_ground_data.push(value_to_Number(new_data_form[`add_ground_hum_sensor_${i+1}`].value));
    }

    console.log(new_air_data);
    console.log(new_ground_data);
    patch_body = {
        air:  new_air_data,
        ground:  new_ground_data
    };

    fetch(url_set_sensors_data, {
        method: 'POST',
        body: JSON.stringify(
            patch_body
        ),
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
        },
        })
        .then((response) => response.json());
    setTimeout(get_data_from_api, 100);
}


setInterval(get_data_from_api, 3000);