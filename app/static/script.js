// Setup MQTT client options
const clientId = "client-" + Math.random().toString(16).substr(2, 8);
const host = "mqtt.eclipseprojects.io";
const port = 80; // WebSocket Port

// Create client instance
const client = new Paho.MQTT.Client(host, port, clientId);

// Display connection status
const statusDisplay = document.getElementById("status");

// Set up connection and subscribe actions
client.connect({
    onSuccess: onConnect,
    onFailure: onFailure,
});

function onConnect() {
    statusDisplay.textContent = "Connected to broker";
    client.subscribe("evomo/telkomiot/final_data");
}

function onFailure(error) {
    statusDisplay.textContent = "Failed to connect: " + error.errorMessage;
}

// Handle incoming messages
client.onMessageArrived = function(message) {
    if (message.destinationName === "evomo/telkomiot/final_data") {
        try {
            // Parse JSON message
            const data = JSON.parse(message.payloadString);
            const active_energy_import = data.active_energy_import;
            const active_energy_export = data.active_energy_export;
            const reactive_energy_import = data.reactive_energy_import;
            const reactive_energy_export = data.reactive_energy_export;
            const apparent_energy_import = data.apparent_energy_import;
            const apparent_energy_export = data.apparent_energy_export;
            const instantaneous_voltage_L1 = data.instantaneous_voltage_L1;
            const instantaneous_voltage_L2 = data.instantaneous_voltage_L2;
            const instantaneous_voltage_L3 = data.instantaneous_voltage_L3;
            const instantaneous_current_L1 = data.instantaneous_current_L1;
            const instantaneous_current_L2 = data.instantaneous_current_L2;
            const instantaneous_current_L3 = data.instantaneous_current_L3;
            const instantaneous_power_factor = data.instantaneous_power_factor;

            // Display voltage and timestamp
            document.getElementById("active_energy_import").textContent = `${active_energy_import}`;
            document.getElementById("active_energy_export").textContent = `${active_energy_export}`;
            document.getElementById("reactive_energy_import").textContent = `${reactive_energy_import}`;
            document.getElementById("reactive_energy_export").textContent = `${reactive_energy_export}`;
            document.getElementById("apparent_energy_import").textContent = `${apparent_energy_import}`;
            document.getElementById("apparent_energy_export").textContent = `${apparent_energy_export}`;
            document.getElementById("instantaneous_voltage_L1").textContent = `${instantaneous_voltage_L1}`;
            document.getElementById("instantaneous_voltage_L2").textContent = `${instantaneous_voltage_L2}`;
            document.getElementById("instantaneous_voltage_L3").textContent = `${instantaneous_voltage_L3}`;
            document.getElementById("instantaneous_current_L1").textContent = `${instantaneous_current_L1}`;
            document.getElementById("instantaneous_current_L2").textContent = `${instantaneous_current_L2}`;
            document.getElementById("instantaneous_current_L3").textContent = `${instantaneous_current_L3}`;
            document.getElementById("instantaneous_power_factor").textContent = `${instantaneous_power_factor}`;
        } catch (e) {
            console.error("Failed to parse JSON", e);
        }
    }
};

// Time update function
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById("current-time").textContent = timeString;
}
setInterval(updateTime, 1000);
updateTime();

// Handle connection lost
client.onConnectionLost = function(responseObject) {
    if (responseObject.errorCode !== 0) {
        statusDisplay.textContent = "Connection lost: " + responseObject.errorMessage;
    }
};

// fetch weather function
async function fetchWeather() {
    const response = await fetch(`https://wttr.in/Jakarta?format=%t`); 
    const temperature = await response.text();

    if (response.ok) {
        document.getElementById("temperature").textContent = `Temperature : ${temperature}`;
    } else {
        document.getElementById("temperature").textContent = `Temperature : N/A`;
    }
}


// render chart
async function fetchVoltageData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/voltage');
        return await response.json();
    } catch (error) {
        console.error("Error fetching data:", error);
        return [];
    }
}

function convertUnixToTime(unixTimestamp) {
    const date = new Date(unixTimestamp * 1000);
    return date.toLocaleTimeString();
}

async function renderChart() {
    const data = await fetchVoltageData();
    if (data.length === 0) {
        console.error("No data available to display chart.");
        return;
    }

    const timeLabels = data.map(point => convertUnixToTime(point.time));
    const voltageValues = data.map(point => point.voltage);

    const ctx = document.getElementById('voltageChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeLabels,
            datasets: [{
                label: 'Voltage (V)',
                data: voltageValues,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2
            }]
        },
        options: {
            scales: {
                x: {
                    title: { display: true, text: 'Time' }
                },
                y: {
                    title: { display: true, text: 'Voltage (V)' },
                    beginAtZero: true
                }
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    fetchWeather();
    renderChart();
});


// Save weather
// async function saveWeather() {
//     const city = document.getElementById("cityInput").value;
//     const temperature = document.getElementById("tempInput").value;
//     const description = document.getElementById("descInput").value;

//     const response = await fetch('http://127.0.0.1:5000/save_weather', {  // Tambahkan port di sini
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({
//             city: city,
//             temperature: temperature,
//             description: description
//         })
//     });

//     if (response.ok) {
//         const data = await response.json();
//         document.getElementById('postWeatherResponse').innerText = JSON.stringify(data, null, 2);
//     } else {
//         const errorData = await response.json();
//         document.getElementById('postWeatherResponse').innerText = errorData.error;
//     }
// }