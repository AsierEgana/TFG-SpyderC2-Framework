const express = require('express');
const app = express();

app.use((req, res, next) => {
    const chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', () => {
        req.rawBody = Buffer.concat(chunks);
        next();
    });
});

app.all('*', async (req, res) => {
    console.log(`${req.method} ${req.url} body-length=${req.rawBody?.length}`);
    try {
        const headers = { ...req.headers, host: 'spyderc2' };
        delete headers['content-length'];

        const respuestaC2 = await fetch('http://spyderc2:8080' + req.url, {
            method: req.method,
            headers: headers,
            body: ['GET', 'HEAD'].includes(req.method) ? undefined : req.rawBody
        });
        const data = await respuestaC2.arrayBuffer();
        
        respuestaC2.headers.forEach((value, key) => {
            res.setHeader(key, value);
        });
        
        res.status(respuestaC2.status).send(Buffer.from(data));
    } catch (e) {
        console.error("Error contacting SpyderC2:", e);
        return res.status(404).send("Not Found");
    }
});

app.listen(3000);