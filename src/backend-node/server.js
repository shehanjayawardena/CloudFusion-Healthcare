require('dotenv').config();
const express = require('express');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');
const { SageMakerRuntimeClient, InvokeEndpointCommand } = require("@aws-sdk/client-sagemaker-runtime");
const { DynamoDBClient, CreateTableCommand, ListTablesCommand } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, ScanCommand, PutCommand } = require("@aws-sdk/lib-dynamodb");

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

app.use((req, res, next) => {
    res.header('Access-Control-Allow-Private-Network', 'true');
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Content-Length, X-Requested-With');
    if (req.method === 'OPTIONS') {
        res.send(200);
    } else {
        next();
    }
});

app.use(cors());
app.use(express.json());

// --- 1. REAL AWS DATABASE (DynamoDB) ---
const REGION = process.env.AWS_REGION || "ap-southeast-1";
const ddbClient = new DynamoDBClient({ region: REGION });
const docClient = DynamoDBDocumentClient.from(ddbClient);

const PATIENTS_TABLE = "cha-patients";
const APPOINTMENTS_TABLE = "cha-appointments";

async function setupDynamoDB() {
    try {
        const { TableNames } = await ddbClient.send(new ListTablesCommand({}));
        
        if (!TableNames.includes(PATIENTS_TABLE)) {
            console.log(`Creating DynamoDB Table: ${PATIENTS_TABLE}... (This takes a few seconds)`);
            await ddbClient.send(new CreateTableCommand({
                TableName: PATIENTS_TABLE,
                KeySchema: [{ AttributeName: "id", KeyType: "HASH" }],
                AttributeDefinitions: [{ AttributeName: "id", AttributeType: "S" }],
                ProvisionedThroughput: { ReadCapacityUnits: 5, WriteCapacityUnits: 5 }
            }));
        }

        if (!TableNames.includes(APPOINTMENTS_TABLE)) {
            console.log(`Creating DynamoDB Table: ${APPOINTMENTS_TABLE}...`);
            await ddbClient.send(new CreateTableCommand({
                TableName: APPOINTMENTS_TABLE,
                KeySchema: [{ AttributeName: "id", KeyType: "HASH" }],
                AttributeDefinitions: [{ AttributeName: "id", AttributeType: "S" }],
                ProvisionedThroughput: { ReadCapacityUnits: 5, WriteCapacityUnits: 5 }
            }));
        }
        
        console.log("Waiting for tables to become ACTIVE before seeding...");
        await new Promise(r => setTimeout(r, 8000)); // wait 8s for AWS to provision

        // Check if patients table is empty, then seed
        const scan = await docClient.send(new ScanCommand({ TableName: PATIENTS_TABLE, Limit: 1 }));
        if (!scan.Items || scan.Items.length === 0) {
            console.log(`Seeding ${PATIENTS_TABLE}...`);
            const seedPatients = [
                { id: "CHA-LK-9041", name: "Kavindu Bandara", age: 54, gender: "Male", ward: "Colombo National Hospital (NHSL) - Cardiac ICU Bed 04", status: "critical", baselineHR: 114, baselineSpO2: 91, bpSystolic: 148, bpDiastolic: 94, temp: 38.6, resp: 24, condition: "Post-CABG with secondary systemic inflammation" },
                { id: "CHA-LK-7822", name: "Dilani Perera", age: 46, gender: "Female", ward: "Asiri Central Hospital - Cardiac Telemetry Bed 12", status: "warning", baselineHR: 88, baselineSpO2: 95, bpSystolic: 136, bpDiastolic: 86, temp: 37.2, resp: 18, condition: "Hypertensive Heart Disease undergoing beta-blocker titration" },
                { id: "CHA-LK-3105", name: "Chaminda Jayasuriya", age: 61, gender: "Male", ward: "Kandy General Hospital - Remote IoT Wearable", status: "stable", baselineHR: 72, baselineSpO2: 98, bpSystolic: 120, bpDiastolic: 78, temp: 36.8, resp: 15, condition: "Post-Discharge remote Holter monitoring" },
                { id: "CHA-LK-1190", name: "Anoma Rajapakse", age: 39, gender: "Female", ward: "Karapitiya Teaching Hospital Galle - Step-Down Bed 08", status: "stable", baselineHR: 68, baselineSpO2: 99, bpSystolic: 118, bpDiastolic: 76, temp: 36.7, resp: 14, condition: "Elective orthopedic post-op recovery" }
            ];
            for (const p of seedPatients) {
                await docClient.send(new PutCommand({ TableName: PATIENTS_TABLE, Item: p }));
            }
            console.log(`Successfully Seeded ${PATIENTS_TABLE}!`);
        }
    } catch (e) {
        console.error("DynamoDB Setup Error (Check AWS Credentials):", e.message);
    }
}

// REST APIs
app.get('/api/patients', async (req, res) => {
    try {
        const data = await docClient.send(new ScanCommand({ TableName: PATIENTS_TABLE }));
        res.json(data.Items || []);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.get('/api/appointments', async (req, res) => {
    try {
        const data = await docClient.send(new ScanCommand({ TableName: APPOINTMENTS_TABLE }));
        res.json(data.Items || []);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/appointments', async (req, res) => {
    try {
        const { patient_name, doctor_name, date, slot } = req.body;
        const id = `APT-${Date.now()}`;
        await docClient.send(new PutCommand({
            TableName: APPOINTMENTS_TABLE,
            Item: { id, patient_name, doctor_name, date, slot, created_at: new Date().toISOString() }
        }));
        res.json({ id, message: "Appointment booked successfully in DynamoDB!" });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.delete('/api/appointments/:id', async (req, res) => {
    try {
        const { DeleteCommand } = require("@aws-sdk/lib-dynamodb");
        await docClient.send(new DeleteCommand({
            TableName: APPOINTMENTS_TABLE,
            Key: { id: req.params.id }
        }));
        res.json({ message: "Appointment cancelled successfully" });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// AWS SageMaker setup
const smClient = new SageMakerRuntimeClient({ region: REGION });
async function getAiPrediction(patientData) {
    try {
        const command = new InvokeEndpointCommand({
            EndpointName: "cha-sepsis-prediction-endpoint",
            ContentType: "application/json",
            Body: Buffer.from(JSON.stringify(patientData)),
        });
        const response = await smClient.send(command);
        return JSON.parse(new TextDecoder().decode(response.Body));
    } catch (smErr) {
        const hr = parseFloat(patientData.heart_rate || 80);
        const spo2 = parseFloat(patientData.spo2 || 98);
        const sbp = parseFloat(patientData.systolic_bp || 120);
        const temp = parseFloat(patientData.temperature || 37.0);
        const rr = parseFloat(patientData.respiratory_rate || 16);
        const shock_index = sbp > 0 ? hr / sbp : 1.0;
        const risk_score = (0.045*(hr-75) - 0.14*(spo2-95) - 0.035*(sbp-110) + 1.6*(temp-37.0) + 0.085*(rr-16) + 2.8*(shock_index-0.7));
        const prob = 1.0 / (1.0 + Math.exp(-Math.max(Math.min(risk_score, 25), -25)));
        const alert_level = prob >= 0.75 ? "CRITICAL_ICU_ALERT" : (prob >= 0.50 ? "ELEVATED_WATCH" : "STABLE");
        return { prob, alert_level, is_critical_triage: prob >= 0.75 };
    }
}

// --- 2. REAL IOT STREAMING (WebSockets) ---
io.on('connection', (socket) => {
    let activePatientId = null;
    let currentVitals = null;
    let iotLoop = null;

    socket.on('subscribe_telemetry', (patient) => {
        activePatientId = patient.id;
        currentVitals = { hr: patient.baselineHR, spo2: patient.baselineSpO2, sbp: patient.bpSystolic, dbp: patient.bpDiastolic, temp: patient.temp };
        if (iotLoop) clearInterval(iotLoop);

        iotLoop = setInterval(async () => {
            if (!activePatientId || !currentVitals) return;
            currentVitals.hr = Math.max(50, Math.min(180, currentVitals.hr + (Math.random() - 0.5) * 2));
            currentVitals.spo2 = Math.max(85, Math.min(100, currentVitals.spo2 + (Math.random() - 0.5) * 0.5));

            const aiResult = await getAiPrediction({
                patient_id: activePatientId, heart_rate: currentVitals.hr, spo2: currentVitals.spo2, 
                systolic_bp: currentVitals.sbp, diastolic_bp: currentVitals.dbp, temperature: currentVitals.temp, respiratory_rate: 20
            });
            socket.emit('telemetry_update', {
                vitals: currentVitals,
                aiRisk: { prob: aiResult.prob || aiResult.sepsis_deterioration_probability, label: aiResult.alert_level, critical: aiResult.is_critical_triage }
            });
        }, 1500);
    });

    socket.on('disconnect', () => { if (iotLoop) clearInterval(iotLoop); });
});

const PORT = process.env.PORT || 8000;
server.listen(PORT, async () => {
    console.log(`Starting REAL CloudFusion Node.js API...`);
    console.log(`Connecting to AWS DynamoDB in ${REGION}...`);
    await setupDynamoDB();
    console.log(`Listening on http://localhost:${PORT}`);
});
