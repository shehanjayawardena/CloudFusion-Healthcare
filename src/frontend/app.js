/**
 * CloudFusion HealthPulse - Frontend Application Logic
 * Integrates:
 * 1. Real-time Patient Monitoring Platform (PMP) IoT Telemetry Engine
 * 2. Telemedicine and Patient Portal (TPP) Video & Clinical Workspace
 * 3. Appointment Booking Engine
 * 4. AWS Cloud Infrastructure Telemetry & Status Monitor
 */

// Simulated Patient Database (Aligning with Clinical Scenarios)
const PATIENTS = [
  {
    id: "CHA-PT-9041",
    name: "Sarah Jenkins",
    age: 64,
    gender: "Female",
    ward: "ICU Post-Cardiac (Bed 04)",
    status: "critical",
    statusText: "Critical Monitoring",
    baselineHR: 114,
    baselineSpO2: 91,
    bpSystolic: 148,
    bpDiastolic: 94,
    temp: 38.6,
    resp: 24,
    aiRisk: 88,
    aiRiskSummary: "High Probability of Septic Shock / Arrhythmia (AWS SageMaker)",
    condition: "Post-CABG with secondary systemic inflammation"
  },
  {
    id: "CHA-PT-7822",
    name: "Robert Chen",
    age: 58,
    gender: "Male",
    ward: "Cardiac Telemetry (Bed 12)",
    status: "warning",
    statusText: "Arrhythmia Alert",
    baselineHR: 88,
    baselineSpO2: 95,
    bpSystolic: 136,
    bpDiastolic: 86,
    temp: 37.2,
    resp: 18,
    aiRisk: 42,
    aiRiskSummary: "Moderate Risk: Intermittent Premature Ventricular Contractions",
    condition: "Hypertensive Heart Disease undergoing beta-blocker titration"
  },
  {
    id: "CHA-PT-3105",
    name: "Fatima Al-Zahra",
    age: 42,
    gender: "Female",
    ward: "Remote Wearable (Dubai Clinic)",
    status: "stable",
    statusText: "Stable Telemetry",
    baselineHR: 72,
    baselineSpO2: 98,
    bpSystolic: 120,
    bpDiastolic: 78,
    temp: 36.8,
    resp: 15,
    aiRisk: 12,
    aiRiskSummary: "Low Risk: Normal physiological parameters within 99% CI",
    condition: "Post-Discharge remote Holter monitoring"
  },
  {
    id: "CHA-PT-1190",
    name: "Marcus Vance",
    age: 51,
    gender: "Male",
    ward: "General Step-Down (Bed 08)",
    status: "stable",
    statusText: "Stable Recuperation",
    baselineHR: 68,
    baselineSpO2: 99,
    bpSystolic: 118,
    bpDiastolic: 76,
    temp: 36.7,
    resp: 14,
    aiRisk: 8,
    aiRiskSummary: "Optimal Recovery Profile: Clearance for discharge pending final rounds",
    condition: "Elective orthopedic post-op recovery"
  }
];

// Doctors List for TPP Booking
const DOCTORS = [
  {
    id: "DOC-01",
    name: "Dr. Aris Thorne, MD",
    specialty: "Cardiology & Critical Care",
    hospital: "Singapore General & CHA Cloud Clinic",
    rating: "4.9 ★ (120+ reviews)",
    slots: ["09:30 AM", "11:00 AM", "02:15 PM", "04:30 PM"]
  },
  {
    id: "DOC-02",
    name: "Dr. Evelyn Wu, MBBS",
    specialty: "Pulmonology & Respiratory Health",
    hospital: "Changi General Hospital",
    rating: "4.8 ★ (95 reviews)",
    slots: ["10:15 AM", "01:00 PM", "03:45 PM"]
  },
  {
    id: "DOC-03",
    name: "Dr. Tariq Mansour, FRCP",
    specialty: "Internal Medicine & Telemedicine",
    hospital: "Dubai Medical Center",
    rating: "5.0 ★ (210 reviews)",
    slots: ["08:45 AM", "11:30 AM", "02:00 PM", "05:15 PM"]
  }
];

let activePatientIndex = 0;
let currentView = 'telemetry-view';
let selectedDoctor = DOCTORS[0];
let selectedSlot = DOCTORS[0].slots[0];

// Telemetry Real-time State
let currentHR = 114;
let currentSpO2 = 91;
let currentBPSys = 148;
let currentBPDia = 94;
let currentTemp = 38.6;

// ==========================================
// Initialization
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  renderPatientList();
  selectPatient(0);
  initEcgCanvas();
  startTelemetryTicker();
  initTelemedControls();
  renderDoctorsList();
  initCloudMetricsSimulator();
});

// ==========================================
// Navigation Controller
// ==========================================
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const targetView = item.getAttribute("data-view");
      if (!targetView) return;

      navItems.forEach(nav => nav.classList.remove("active"));
      item.classList.add("active");

      document.querySelectorAll(".view-section").forEach(view => {
        view.classList.remove("active");
      });

      const activeSection = document.getElementById(targetView);
      if (activeSection) {
        activeSection.classList.add("active");
        currentView = targetView;
      }
    });
  });
}

// ==========================================
// Patient Roster & Selection
// ==========================================
function renderPatientList() {
  const container = document.getElementById("patientRosterList");
  if (!container) return;

  container.innerHTML = PATIENTS.map((p, idx) => `
    <div class="patient-card ${idx === activePatientIndex ? 'selected' : ''}" onclick="selectPatient(${idx})">
      <div class="patient-card-top">
        <span class="patient-name-title">${p.name}</span>
        <span class="status-tag ${p.status}">${p.status.toUpperCase()}</span>
      </div>
      <div class="patient-id">${p.id} &bull; ${p.gender}, ${p.age}y</div>
      <div class="patient-card-meta" style="margin-top: 8px;">
        <span>${p.ward}</span>
        <strong style="color: var(--accent-cyan);">${p.baselineHR} BPM</strong>
      </div>
    </div>
  `).join('');
}

function selectPatient(index) {
  activePatientIndex = index;
  const p = PATIENTS[index];
  currentHR = p.baselineHR;
  currentSpO2 = p.baselineSpO2;
  currentBPSys = p.bpSystolic;
  currentBPDia = p.bpDiastolic;
  currentTemp = p.temp;

  // Update Roster Visuals
  renderPatientList();

  // Update Hero Section
  document.getElementById("heroPatientName").innerText = p.name;
  document.getElementById("heroPatientId").innerText = p.id;
  document.getElementById("heroPatientWard").innerText = p.ward;
  document.getElementById("heroPatientCondition").innerText = p.condition;

  // Update AI Risk Gauge
  document.getElementById("aiRiskScore").innerText = p.aiRisk + "%";
  document.getElementById("aiRiskSummary").innerText = p.aiRiskSummary;

  updateVitalsDisplay();
}

function updateVitalsDisplay() {
  document.getElementById("vitalHR").innerText = Math.round(currentHR);
  document.getElementById("vitalSpO2").innerText = Math.round(currentSpO2);
  document.getElementById("vitalBP").innerText = `${Math.round(currentBPSys)}/${Math.round(currentBPDia)}`;
  document.getElementById("vitalTemp").innerText = currentTemp.toFixed(1);
}

// ==========================================
// Real-time Telemetry & Micro-Fluctuations
// ==========================================
function startTelemetryTicker() {
  setInterval(() => {
    const p = PATIENTS[activePatientIndex];
    
    // Controlled physiological fluctuation around baseline
    const hrNoise = (Math.random() - 0.5) * 2;
    currentHR = Math.max(50, Math.min(180, currentHR + hrNoise * 0.4));
    
    const spo2Noise = (Math.random() - 0.5) * 0.4;
    currentSpO2 = Math.max(85, Math.min(100, currentSpO2 + spo2Noise));

    updateVitalsDisplay();
  }, 1200);
}

// ==========================================
// Live ECG Canvas Waveform Renderer
// Simulates continuous Lead II Electrocardiogram (P-Q-R-S-T)
// ==========================================
let ecgCanvas, ecgCtx;
let ecgPoints = [];
let ecgX = 0;
let ecgPhase = 0;

function initEcgCanvas() {
  ecgCanvas = document.getElementById("ecgCanvas");
  if (!ecgCanvas) return;
  ecgCtx = ecgCanvas.getContext("2d");

  function resize() {
    ecgCanvas.width = ecgCanvas.offsetWidth;
    ecgCanvas.height = ecgCanvas.offsetHeight;
    ecgPoints = new Array(Math.floor(ecgCanvas.width)).fill(ecgCanvas.height / 2);
  }

  resize();
  window.addEventListener("resize", resize);
  requestAnimationFrame(drawEcgLoop);
}

function getEcgY(phase, midY) {
  // Normalize phase between 0 and 1
  const t = phase % 1;
  const p = PATIENTS[activePatientIndex];
  const severityMultiplier = p.status === 'critical' ? 1.4 : 1.0;

  // Baseline
  let y = 0;

  if (t > 0.1 && t < 0.18) {
    // P Wave
    y = -10 * Math.sin(((t - 0.1) / 0.08) * Math.PI);
  } else if (t >= 0.22 && t < 0.25) {
    // Q Wave (Dip)
    y = 8 * Math.sin(((t - 0.22) / 0.03) * Math.PI);
  } else if (t >= 0.25 && t < 0.30) {
    // R Peak (Tall sharp deflection)
    const normalized = (t - 0.25) / 0.05;
    y = -52 * severityMultiplier * Math.sin(normalized * Math.PI);
  } else if (t >= 0.30 && t < 0.33) {
    // S Wave (Negative deflection)
    y = 14 * Math.sin(((t - 0.30) / 0.03) * Math.PI);
  } else if (t >= 0.45 && t < 0.60) {
    // T Wave
    y = -14 * Math.sin(((t - 0.45) / 0.15) * Math.PI);
  }

  // Add micro muscular artifact noise
  y += (Math.random() - 0.5) * 1.5;

  return midY + y;
}

function drawEcgLoop() {
  if (!ecgCtx || !ecgCanvas) return;

  const w = ecgCanvas.width;
  const h = ecgCanvas.height;
  const midY = h / 2;

  // Pace dependent on current HR
  const speed = (currentHR / 60) * 0.015;
  ecgPhase += speed;

  const newY = getEcgY(ecgPhase, midY);

  ecgPoints[ecgX] = newY;
  ecgX = (ecgX + 1) % w;

  // Clear Background
  ecgCtx.fillStyle = "#04070e";
  ecgCtx.fillRect(0, 0, w, h);

  // Draw Grid Lines (Medical Calipers)
  ecgCtx.strokeStyle = "rgba(0, 240, 255, 0.04)";
  ecgCtx.lineWidth = 1;
  const gridSize = 25;
  for (let x = 0; x < w; x += gridSize) {
    ecgCtx.beginPath();
    ecgCtx.moveTo(x, 0);
    ecgCtx.lineTo(x, h);
    ecgCtx.stroke();
  }
  for (let y = 0; y < h; y += gridSize) {
    ecgCtx.beginPath();
    ecgCtx.moveTo(0, y);
    ecgCtx.lineTo(w, y);
    ecgCtx.stroke();
  }

  // Draw Neon ECG Waveform
  ecgCtx.beginPath();
  ecgCtx.lineWidth = 2;
  ecgCtx.strokeStyle = "#00f0ff";
  ecgCtx.shadowColor = "rgba(0, 240, 255, 0.8)";
  ecgCtx.shadowBlur = 8;

  let started = false;
  for (let i = 0; i < w; i++) {
    // Create lead sweep gap effect (sweep eraser cursor)
    if (Math.abs(i - ecgX) < 16) {
      continue;
    }
    const val = ecgPoints[i] || midY;
    if (!started) {
      ecgCtx.moveTo(i, val);
      started = true;
    } else {
      ecgCtx.lineTo(i, val);
    }
  }
  ecgCtx.stroke();
  ecgCtx.shadowBlur = 0; // reset

  // Glowing sweep head cursor
  ecgCtx.fillStyle = "#ffffff";
  ecgCtx.beginPath();
  ecgCtx.arc(ecgX, newY, 3, 0, Math.PI * 2);
  ecgCtx.fill();

  requestAnimationFrame(drawEcgLoop);
}

// ==========================================
// Telemedicine Consultation Suite
// ==========================================
function initTelemedControls() {
  const micBtn = document.getElementById("micBtn");
  const camBtn = document.getElementById("camBtn");
  const endCallBtn = document.getElementById("endCallBtn");
  const dispatchRxBtn = document.getElementById("dispatchRxBtn");

  if (micBtn) {
    micBtn.addEventListener("click", () => {
      micBtn.classList.toggle("active");
      showToast(micBtn.classList.contains("active") ? "Microphone Unmuted" : "Microphone Muted");
    });
  }

  if (camBtn) {
    camBtn.addEventListener("click", () => {
      camBtn.classList.toggle("active");
      showToast(camBtn.classList.contains("active") ? "Camera Active (1080p WebRTC)" : "Camera Video Paused");
    });
  }

  if (endCallBtn) {
    endCallBtn.addEventListener("click", () => {
      showToast("Clinical Consultation session closed. Encounter log committed to S3 Data Lake.");
    });
  }

  if (dispatchRxBtn) {
    dispatchRxBtn.addEventListener("click", () => {
      showToast("Encrypted Electronic Prescription signed via AWS KMS & dispatched to pharmacy!");
    });
  }
}

// ==========================================
// Doctor Appointment Booking
// ==========================================
function renderDoctorsList() {
  const container = document.getElementById("doctorSelectionList");
  if (!container) return;

  container.innerHTML = DOCTORS.map((doc, idx) => `
    <div class="doctor-select-card ${doc.id === selectedDoctor.id ? 'selected' : ''}" onclick="selectDoctor(${idx})">
      <div class="doc-card-header">
        <div class="doc-avatar">${doc.name.split(' ')[1][0]}W</div>
        <div class="doc-info">
          <h4>${doc.name}</h4>
          <span>${doc.specialty}</span>
        </div>
      </div>
      <div style="font-size: 0.76rem; color: var(--accent-cyan); margin-top: 10px;">${doc.rating}</div>
      <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">${doc.hospital}</div>
      <div class="time-slots-wrap">
        ${doc.slots.map(s => `
          <span class="slot-pill ${s === selectedSlot ? 'active' : ''}" onclick="event.stopPropagation(); selectSlot('${s}')">${s}</span>
        `).join('')}
      </div>
    </div>
  `).join('');
}

function selectDoctor(idx) {
  selectedDoctor = DOCTORS[idx];
  selectedSlot = selectedDoctor.slots[0];
  renderDoctorsList();
}

function selectSlot(slot) {
  selectedSlot = slot;
  renderDoctorsList();
  showToast(`Selected time slot: ${slot} with ${selectedDoctor.name}`);
}

function confirmAppointmentBooking() {
  showToast(`Appointment successfully booked for ${selectedDoctor.name} at ${selectedSlot}! Confirmation sent via AWS SNS.`);
}

// ==========================================
// AWS Cloud Infrastructure Metrics Simulator
// Connects UI to Live Architecture Topology
// ==========================================
function initCloudMetricsSimulator() {
  setInterval(() => {
    const albLatency = (14 + Math.random() * 5).toFixed(1);
    const ddbLatency = (3.2 + Math.random() * 1.5).toFixed(1);
    const ecsTasks = Math.floor(6 + Math.random() * 2);

    const albEl = document.getElementById("albLatencyMetric");
    const ddbEl = document.getElementById("ddbLatencyMetric");
    const ecsEl = document.getElementById("ecsTasksMetric");

    if (albEl) albEl.innerText = albLatency + " ms";
    if (ddbEl) ddbEl.innerText = ddbLatency + " ms";
    if (ecsEl) ecsEl.innerText = ecsTasks + " Active Tasks";
  }, 3000);
}

// ==========================================
// Toast Notifications
// ==========================================
function showToast(message) {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00f0ff" stroke-width="2">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
      <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = "all 0.3s ease";
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
