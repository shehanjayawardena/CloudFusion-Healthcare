import React, { useState, useEffect } from 'react';
import { Activity, Heart, Thermometer, ShieldAlert, Video, Calendar, Cloud, Stethoscope, LogOut } from 'lucide-react';
import { io } from 'socket.io-client';
import clsx, { type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const DOCTORS = [
  {
    id: "DOC-LK-01", name: "Dr. Ruwan Gunawardena, MD, MRCP", initials: "RG",
    specialty: "Consultant Cardiologist & Critical Care", hospital: "National Hospital of Sri Lanka (NHSL) & CloudFusion Clinic",
    rating: "4.9 ★ (180+ reviews)", slots: ["09:30 AM", "11:00 AM", "02:15 PM", "04:30 PM"]
  },
  {
    id: "DOC-LK-02", name: "Dr. Chathurika Senanayake, MBBS, MD", initials: "CS",
    specialty: "Consultant Pulmonologist & Respiratory Specialist", hospital: "Asiri Surgical & Lanka Hospitals Colombo",
    rating: "4.9 ★ (140+ reviews)", slots: ["10:15 AM", "01:00 PM", "03:45 PM"]
  },
  {
    id: "DOC-LK-03", name: "Dr. Kasun Wickramasinghe, MBBS, FRCS", initials: "KW",
    specialty: "Emergency Medicine & Telehealth Director", hospital: "Colombo South Teaching Hospital (Kalubowila)",
    rating: "5.0 ★ (240+ reviews)", slots: ["08:45 AM", "11:30 AM", "02:00 PM", "05:15 PM"]
  }
];

// Patients will be fetched dynamically from the SQLite Database now
export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [patients, setPatients] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState('telemetry');
  const [activeIdx, setActiveIdx] = useState(0);
  const patient = patients[activeIdx] || null;

  const [selectedDocId, setSelectedDocId] = useState(DOCTORS[0].id);
  const [selectedSlot, setSelectedSlot] = useState(DOCTORS[0].slots[0]);

  const [vitals, setVitals] = useState({ hr: 0, spo2: 0, sbp: 0, dbp: 0, temp: 0 });
  const [aiRisk, setAiRisk] = useState<{prob: number, label: string, critical: boolean} | null>(null);

  // 1. Fetch Data from REST API (DynamoDB)
  useEffect(() => {
    fetch("http://localhost:8000/api/patients")
      .then(res => res.json())
      .then(data => {
        setPatients(data);
        if (data.length > 0) {
          setVitals({ hr: data[0].baselineHR, spo2: data[0].baselineSpO2, sbp: data[0].bpSystolic, dbp: data[0].bpDiastolic, temp: data[0].temp });
        }
      })
      .catch(console.error);

    fetch("http://localhost:8000/api/appointments")
      .then(res => res.json())
      .then(data => setAppointments(data))
      .catch(console.error);
  }, []);

  // 2. Real-time IoT WebSockets
  useEffect(() => {
    if (!patient) return;

    // Connect to Node.js backend
    const socket = io("http://localhost:8000");

    // Tell backend which patient we are monitoring
    socket.emit("subscribe_telemetry", patient);

    // Listen for the live data stream being piped from backend/AI
    socket.on("telemetry_update", (data) => {
      setVitals(data.vitals);
      setAiRisk(data.aiRisk);
    });

    return () => {
      socket.disconnect();
    };
  }, [patient]);

  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }

  if (!patient) return <div className="h-screen flex items-center justify-center text-slate-500 font-bold">Booting Real Cloud Architecture...</div>;

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
        <div className="p-6 border-b border-slate-100 flex items-center gap-3">
          <div className="bg-sky-500 text-white p-2 rounded-lg">
            <Activity size={24} />
          </div>
          <h1 className="font-bold text-lg text-slate-800 leading-tight">CloudFusion<br/><span className="text-sm font-normal text-slate-500 uppercase tracking-widest">HealthPulse</span></h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <NavItem icon={<Heart />} label="Patient Telemetry (PMP)" active={activeTab === 'telemetry'} onClick={() => setActiveTab('telemetry')} />
          <NavItem icon={<Video />} label="Telemedicine Suite" active={activeTab === 'telemed'} onClick={() => setActiveTab('telemed')} />
          <NavItem icon={<Calendar />} label="Appointment Portal" active={activeTab === 'booking'} onClick={() => setActiveTab('booking')} />
          <NavItem icon={<Cloud />} label="AWS Cloud Topology" active={activeTab === 'cloud'} onClick={() => setActiveTab('cloud')} />
        </nav>
        <div className="p-4 border-t border-slate-100 flex flex-col gap-3">
          <button 
            onClick={() => setIsAuthenticated(false)}
            className="w-full flex items-center justify-center gap-2 bg-slate-50 hover:bg-slate-100 text-slate-600 hover:text-slate-800 border border-slate-200 py-2 rounded-lg font-bold text-sm transition-colors"
          >
            <LogOut size={16} />
            Secure Logout
          </button>
          <div className="text-[10px] text-slate-400 flex items-center gap-2 justify-center bg-slate-50 py-1.5 rounded-md border border-slate-100">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
            AWS Multi-AZ (ap-southeast-1)
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-8 shadow-sm z-10">
          <h2 className="text-xl font-semibold text-slate-800">Intensive Care & Telemetry Center</h2>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-sky-50 text-sky-700 rounded-full text-sm font-medium border border-sky-100">
              <Cloud size={16} /> Edge: 12ms to CloudFront
            </div>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-slate-800 text-white flex items-center justify-center font-bold shadow-sm">SJ</div>
              <div className="text-sm">
                <p className="font-bold text-slate-800">Dr. Shehan Jayawardena</p>
                <p className="text-slate-500 text-xs">Lead Clinical Architect</p>
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Body */}
        {activeTab === 'telemetry' && (
        <div className="flex-1 p-6 flex gap-6 overflow-hidden">
          {/* Patient Roster */}
          <div className="w-80 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
              <h3 className="font-semibold text-slate-800">Live Patient Cohort</h3>
              <span className="text-xs font-semibold text-sky-600 bg-sky-100 px-2 py-1 rounded-full">{patients.length} Monitored</span>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-3">
              {patients.map((p, idx) => (
                <div 
                  key={p.id} 
                  onClick={() => setActiveIdx(idx)}
                  className={cn(
                    "p-4 rounded-lg cursor-pointer transition-all border",
                    activeIdx === idx 
                      ? "bg-sky-50 border-sky-200 shadow-sm ring-1 ring-sky-500" 
                      : "bg-white border-slate-100 hover:border-slate-300 hover:bg-slate-50"
                  )}
                >
                  <div className="flex justify-between items-start mb-1">
                    <h4 className="font-semibold text-slate-800">{p.name}</h4>
                    <span className={cn(
                      "text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full border",
                      p.status === 'critical' ? "bg-red-50 text-red-600 border-red-200" :
                      p.status === 'warning' ? "bg-amber-50 text-amber-600 border-amber-200" :
                      "bg-emerald-50 text-emerald-600 border-emerald-200"
                    )}>{p.status}</span>
                  </div>
                  <div className="text-xs text-slate-500 mb-2">{p.id} &bull; {p.gender}, {p.age}y</div>
                  <div className="flex justify-between items-end">
                    <span className="text-xs text-slate-500 w-32 truncate">{p.ward}</span>
                    <span className="font-bold text-sky-600">{p.baselineHR} BPM</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Telemetry Detail */}
          <div className="flex-1 flex flex-col gap-6 overflow-y-auto">
            {/* Patient Header */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex justify-between items-center relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-sky-500"></div>
              <div>
                <h2 className="text-2xl font-bold text-slate-800">{patient.name}</h2>
                <div className="flex items-center gap-3 text-sm text-slate-500 mt-1">
                  <span className="font-mono text-sky-600 bg-sky-50 px-2 py-0.5 rounded">{patient.id}</span>
                  <span>{patient.ward}</span>
                </div>
                <p className="text-sm text-slate-600 mt-2 flex items-center gap-2"><Stethoscope size={16} className="text-slate-400"/> {patient.condition}</p>
              </div>
              <button className="bg-sky-600 hover:bg-sky-700 text-white px-6 py-2.5 rounded-lg font-semibold flex items-center gap-2 transition-colors shadow-sm" onClick={() => setActiveTab('telemed')}>
                <Video size={18} /> Launch Teleconsult
              </button>
            </div>

            {/* Vitals Grid */}
            <div className="grid grid-cols-4 gap-4">
              <VitalCard title="HEART RATE" icon={<Heart size={18}/>} value={Math.round(vitals.hr)} unit="BPM" color="text-rose-500" />
              <VitalCard title="OXYGEN SATURATION" icon={<Activity size={18}/>} value={Math.round(vitals.spo2)} unit="% SpO₂" color="text-sky-500" />
              <VitalCard title="BLOOD PRESSURE" icon={<Activity size={18}/>} value={`${Math.round(vitals.sbp)}/${Math.round(vitals.dbp)}`} unit="mmHg" color="text-amber-500" />
              <VitalCard title="BODY TEMPERATURE" icon={<Thermometer size={18}/>} value={vitals.temp.toFixed(1)} unit="°C" color="text-emerald-500" />
            </div>

            {/* Live ECG Chart */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-40">
              <div className="px-4 py-2 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-sky-600 shadow-[0_0_0_2px_rgba(2,132,199,0.2)]"></div>
                  <h4 className="font-bold text-slate-800 text-sm">Lead II Continuous Electrocardiogram (P-Q-R-S-T)</h4>
                </div>
                <div className="text-[10px] text-slate-500 font-mono">25mm/s &bull; 10mm/mV &bull; Streamed via AWS IoT Core (60s Cadence)</div>
              </div>
              <div className="flex-1 relative">
                <EcgChart hr={vitals.hr} critical={patient.status === 'critical'} />
              </div>
            </div>

            {/* AI Warning Box */}
            <div className={cn(
              "rounded-xl p-6 border shadow-sm flex items-center justify-between transition-all duration-500",
              aiRisk?.critical 
                ? "bg-red-50 border-red-200" 
                : "bg-gradient-to-r from-slate-50 to-white border-slate-200"
            )}>
              <div className="flex gap-4 items-start">
                <div className={cn(
                  "p-3 rounded-xl",
                  aiRisk?.critical ? "bg-red-100 text-red-600" : "bg-sky-100 text-sky-600"
                )}>
                  <ShieldAlert size={28} />
                </div>
                <div>
                  <h3 className={cn(
                    "font-bold text-lg",
                    aiRisk?.critical ? "text-red-700" : "text-slate-800"
                  )}>AI Early Warning Deterioration Alert (AWS SageMaker)</h3>
                  <p className={cn(
                    "text-sm mt-1",
                    aiRisk?.critical ? "text-red-600 font-medium" : "text-slate-500"
                  )}>
                    {aiRisk ? aiRisk.label : "Initializing AWS SageMaker Inference..."}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className={cn(
                  "text-4xl font-black tabular-nums transition-colors",
                  aiRisk?.critical ? "text-red-600" : "text-sky-600"
                )}>
                  {aiRisk ? (aiRisk.prob * 100).toFixed(1) : "--"}%
                </div>
                <div className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mt-1">Calculated Risk Index</div>
              </div>
            </div>
          </div>
        </div>
        )}

        {/* Telemedicine View */}
        {activeTab === 'telemed' && (
          <div className="flex-1 p-6 flex gap-6 overflow-hidden">
            <div className="flex-1 bg-slate-900 rounded-xl flex items-center justify-center relative overflow-hidden shadow-lg border border-slate-800">
              <div className="absolute top-4 left-4 bg-rose-500 text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-2 animate-pulse">
                <div className="w-2 h-2 rounded-full bg-white"></div> LIVE CONSULTATION
              </div>
              <div className="absolute top-4 right-4 bg-slate-800/80 text-white text-xs font-bold px-3 py-1 rounded-full">
                AWS KMS TLS 1.3 Encrypted
              </div>
              <div className="text-center">
                <div className="w-24 h-24 rounded-full bg-slate-700 mx-auto flex items-center justify-center mb-4">
                  <Video size={40} className="text-slate-400" />
                </div>
                <h3 className="text-white text-xl font-bold">Dr. Ruwan Gunawardena</h3>
                <p className="text-slate-400">Connecting to NHSL Network...</p>
              </div>
            </div>
            <div className="w-96 flex flex-col gap-4">
              <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex-1">
                <h3 className="font-bold text-slate-800 mb-4">Clinical Encounter Documentation</h3>
                <textarea className="w-full h-48 p-3 border border-slate-200 rounded-lg text-sm" placeholder="Record diagnostic notes..." defaultValue="Patient Kavindu Bandara reports mild sternal discomfort and persistent fever (38.6°C). Telemetry confirms sinus tachycardia at 114 bpm with isolated premature atrial contractions." />
                <button className="mt-4 w-full bg-sky-600 text-white py-2.5 rounded-lg font-bold">Sign & Commit to S3</button>
              </div>
            </div>
          </div>
        )}

        {/* Cloud Topology View */}
        {activeTab === 'cloud' && (
          <div className="flex-1 p-6 overflow-y-auto">
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Live AWS Cloud Infrastructure Monitor</h2>
            <p className="text-slate-500 mb-8">Real-time status of CloudFusion Healthcare Analytics Ltd's multi-AZ target architecture in AWS Singapore (ap-southeast-1).</p>
            <div className="grid grid-cols-3 gap-6">
              <CloudCard name="Application Load Balancer" status="ACTIVE" detail1="ALB DNS: cha-healthcare-prod-alb" detail2="Latency: 14.2 ms" />
              <CloudCard name="ECS Fargate Microservices" status="HEALTHY" detail1="Cluster: cha-healthcare-prod-ecs" detail2="Tasks: 6 Active" />
              <CloudCard name="DynamoDB Hot Telemetry" status="STREAMING" detail1="Table: cha-healthcare-telemetry" detail2="Latency: 3.4 ms" />
              <CloudCard name="S3 Healthcare Data Lake" status="ENCRYPTED" detail1="Bucket: cha-healthcare-prod-lake" detail2="Key: AWS KMS (CMK)" />
              <CloudCard name="Multi-AZ Resilient VPC" status="3 AZ ACTIVE" detail1="CIDR: 10.50.0.0/16" detail2="Zones: ap-southeast-1a, 1b, 1c" />
              <CloudCard name="AWS IoT Core & Greengrass" status="CONNECTED" detail1="Protocol: MQTT over TLS v1.3" detail2="Cadence: 60-Second Ingestion" />
            </div>
          </div>
        )}

        {/* Booking Portal View */}
        {activeTab === 'booking' && (
          <div className="flex-1 p-6 overflow-y-auto">
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm mb-6">
              <h3 className="text-xl font-bold text-slate-800">Schedule Telemedicine Consultation or Clinic Appointment</h3>
              <p className="text-sm text-slate-500 mt-1">Connect with board-certified clinical specialists across South Asia and the Middle East via AWS CloudFront low-latency routing.</p>
            </div>

            <div className="flex gap-6 items-start">
              <div className="flex-1">
                <h4 className="font-bold text-slate-800 mb-4 text-lg">Available Specialists & Consulting Physicians</h4>
                <div className="grid grid-cols-2 gap-4">
                  {DOCTORS.map(doc => {
                    const isSelected = selectedDocId === doc.id;
                    return (
                      <div 
                        key={doc.id} 
                        onClick={() => { setSelectedDocId(doc.id); setSelectedSlot(doc.slots[0]); }}
                        className={cn(
                          "bg-white rounded-xl border p-5 shadow-sm cursor-pointer transition-all",
                          isSelected ? "border-sky-500 ring-1 ring-sky-500" : "border-slate-200 hover:border-sky-300"
                        )}
                      >
                        <div className="flex gap-4">
                          <div className={cn(
                            "w-12 h-12 rounded-full flex items-center justify-center font-bold shrink-0",
                            isSelected ? "bg-sky-100 text-sky-700" : "bg-slate-100 text-slate-600"
                          )}>
                            {doc.initials}
                          </div>
                          <div>
                            <h4 className="font-bold text-slate-800 leading-tight">{doc.name}</h4>
                            <p className="text-xs text-slate-500 mt-1">{doc.specialty}</p>
                          </div>
                        </div>
                        <div className="mt-4 text-xs font-semibold text-sky-600">{doc.rating}</div>
                        <div className="text-[10px] text-slate-500 mt-1">{doc.hospital}</div>
                        <div className="flex flex-wrap gap-2 mt-4">
                          {doc.slots.map(s => (
                            <span 
                              key={s} 
                              onClick={(e) => { e.stopPropagation(); setSelectedDocId(doc.id); setSelectedSlot(s); }}
                              className={cn(
                                "text-xs font-bold px-3 py-1.5 rounded cursor-pointer",
                                isSelected && selectedSlot === s 
                                  ? "bg-sky-600 text-white" 
                                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                              )}
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="w-80 bg-white rounded-xl border border-slate-200 shadow-sm p-6 sticky top-0">
                <h3 className="font-bold text-lg text-slate-800 mb-6">Appointment Confirmation</h3>
                <div className="space-y-4 text-sm">
                  <div className="flex justify-between border-b border-slate-100 pb-2">
                    <span className="text-slate-500">Encounter Type:</span>
                    <strong className="text-sky-700">Encrypted HD Video Consult</strong>
                  </div>
                  <div className="flex justify-between border-b border-slate-100 pb-2">
                    <span className="text-slate-500">Compliance:</span>
                    <strong className="text-slate-800">HIPAA & GDPR Compliant</strong>
                  </div>
                  <div className="flex justify-between border-b border-slate-100 pb-2">
                    <span className="text-slate-500">Billing / Insurance:</span>
                    <span className="text-slate-800">Direct Provider Settlement</span>
                  </div>
                </div>
                <button 
                  onClick={() => {
                    const doc = DOCTORS.find(d => d.id === selectedDocId);
                    fetch("http://localhost:8000/api/appointments", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ patient_name: "Kavindu Bandara", doctor_name: doc?.name, date: new Date().toLocaleDateString(), slot: selectedSlot })
                    }).then(res => res.json()).then(data => {
                      alert(`DynamoDB: ${data.message}`);
                      setAppointments([...appointments, { id: data.id, patient_name: "Kavindu Bandara", doctor_name: doc?.name, date: new Date().toLocaleDateString(), slot: selectedSlot }]);
                    });
                  }}
                  className="mt-6 w-full bg-sky-600 hover:bg-sky-700 text-white font-bold py-3 rounded-lg transition-colors"
                >
                  Confirm & Reserve Appointment
                </button>
              </div>

              {/* Reserved Appointments List */}
              <div className="w-80 flex flex-col gap-4">
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                  <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                    <Calendar size={18} className="text-sky-600"/> My Reserved Appointments
                  </h3>
                  {appointments.length === 0 ? (
                    <div className="text-sm text-slate-500 italic">No appointments booked yet.</div>
                  ) : (
                    <div className="space-y-3">
                      {appointments.map(apt => (
                        <div key={apt.id} className="p-3 bg-slate-50 border border-slate-100 rounded-lg relative group">
                          <button 
                            onClick={() => {
                              fetch(`http://localhost:8000/api/appointments/${apt.id}`, { method: 'DELETE' })
                                .then(() => setAppointments(appointments.filter(a => a.id !== apt.id)))
                                .catch(console.error);
                            }}
                            className="absolute top-2 right-2 text-slate-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                            title="Cancel Appointment"
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
                          </button>
                          <div className="font-bold text-slate-800 text-sm pr-6">{apt.doctor_name}</div>
                          <div className="text-xs text-slate-500 mt-1">{apt.date} &bull; <strong className="text-sky-600">{apt.slot}</strong></div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function NavItem({ icon, label, active = false, onClick }: { icon: React.ReactNode, label: string, active?: boolean, onClick?: () => void }) {
  return (
    <div onClick={onClick} className={cn(
      "flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer transition-colors font-medium text-sm",
      active ? "bg-sky-50 text-sky-700" : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
    )}>
      {icon}
      {label}
    </div>
  );
}

function VitalCard({ title, icon, value, unit, color }: { title: string, icon: React.ReactNode, value: string | number, unit: string, color: string }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between">
      <div className="flex justify-between items-center text-slate-500 mb-4">
        <span className="text-xs font-bold tracking-wider uppercase">{title}</span>
        <span className={color}>{icon}</span>
      </div>
      <div className="flex items-baseline gap-2">
        <span className={cn("text-4xl font-bold tabular-nums tracking-tight", color)}>{value}</span>
        <span className="text-sm font-semibold text-slate-500">{unit}</span>
      </div>
    </div>
  );
}

function CloudCard({ name, status, detail1, detail2 }: { name: string, status: string, detail1: string, detail2: string }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <span className="font-bold text-slate-800">{name}</span>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-200">{status}</span>
      </div>
      <div className="text-sm text-slate-500 space-y-2 mt-auto">
        <p>{detail1}</p>
        <p>{detail2}</p>
      </div>
    </div>
  );
}

function EcgChart({ hr, critical }: { hr: number, critical: boolean }) {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let ecgX = 0;
    let ecgPhase = 0;
    const ecgPoints = new Array(canvas.width).fill(canvas.height / 2);
    let animationId: number;

    const draw = () => {
      const w = canvas.width;
      const h = canvas.height;
      const midY = h / 2;

      // Calculate speed based on HR
      const speed = (hr / 60) * 0.015;
      ecgPhase += speed;

      const t = ecgPhase % 1;
      const severityMultiplier = critical ? 1.4 : 1.0;
      let y = 0;

      if (t > 0.1 && t < 0.18) y = -10 * Math.sin(((t - 0.1) / 0.08) * Math.PI);
      else if (t >= 0.22 && t < 0.25) y = 8 * Math.sin(((t - 0.22) / 0.03) * Math.PI);
      else if (t >= 0.25 && t < 0.30) y = -52 * severityMultiplier * Math.sin(((t - 0.25) / 0.05) * Math.PI);
      else if (t >= 0.30 && t < 0.33) y = 14 * Math.sin(((t - 0.30) / 0.03) * Math.PI);
      else if (t >= 0.45 && t < 0.60) y = -14 * Math.sin(((t - 0.45) / 0.15) * Math.PI);

      y += (Math.random() - 0.5) * 1.5;
      const newY = midY + y;

      ecgPoints[ecgX] = newY;
      ecgX = (ecgX + 1) % w;

      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, w, h);

      ctx.strokeStyle = "#f1f5f9";
      ctx.lineWidth = 1;
      for (let x = 0; x < w; x += 20) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
      for (let yGrid = 0; yGrid < h; yGrid += 20) { ctx.beginPath(); ctx.moveTo(0, yGrid); ctx.lineTo(w, yGrid); ctx.stroke(); }

      ctx.beginPath();
      ctx.lineWidth = 2;
      ctx.strokeStyle = "#0284c7";
      
      let started = false;
      for (let i = 0; i < w; i++) {
        if (Math.abs(i - ecgX) < 14) continue;
        const val = ecgPoints[i] || midY;
        if (!started) { ctx.moveTo(i, val); started = true; } 
        else ctx.lineTo(i, val);
      }
      ctx.stroke();

      ctx.fillStyle = "#0284c7";
      ctx.beginPath();
      ctx.arc(ecgX, newY, 3, 0, Math.PI * 2);
      ctx.fill();

      animationId = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(animationId);
  }, [hr, critical]);

  return <canvas ref={canvasRef} width={800} height={120} className="w-full h-full bg-white" />;
}

function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (username === 'admin' && password === 'password') {
      onLogin();
    } else {
      setError(true);
      setTimeout(() => setError(false), 3000);
    }
  };

  return (
    <div className="min-h-screen w-full bg-slate-50 flex items-center justify-center relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-full opacity-60 pointer-events-none bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-sky-100 via-slate-50 to-white"></div>
      
      <div className="bg-white border border-slate-200 p-10 rounded-2xl shadow-xl shadow-slate-200/50 w-full max-w-md relative z-10">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-sky-500 rounded-2xl flex items-center justify-center shadow-lg shadow-sky-500/30 mb-4">
            <Activity size={32} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">CloudFusion Healthcare</h1>
          <p className="text-slate-500 text-sm mt-1 text-center font-medium">Secure Clinical Authentication Gateway</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Practitioner ID</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. admin"
              className="w-full bg-white border border-slate-300 rounded-lg px-4 py-3 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 transition-all shadow-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-white border border-slate-300 rounded-lg px-4 py-3 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 transition-all shadow-sm"
            />
          </div>
          
          {error && <div className="text-red-600 text-sm font-semibold text-center bg-red-50 py-2 rounded border border-red-100">Invalid Credentials. Try again.</div>}

          <button 
            type="submit" 
            className="w-full bg-sky-600 hover:bg-sky-500 text-white font-bold py-3.5 rounded-lg mt-2 transition-colors shadow-md shadow-sky-600/20"
          >
            Authenticate via AWS Cognito
          </button>
        </form>
        
        <div className="mt-8 text-center text-xs text-slate-400 border-t border-slate-100 pt-6 font-medium">
          Protected by AWS KMS Encryption &bull; HIPAA Compliant
        </div>
      </div>
    </div>
  );
}
