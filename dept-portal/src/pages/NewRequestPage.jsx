import { useState } from "react";
import { useAuth } from "../context/useAuth";
import { DEPARTMENT_FIELDS } from "../data/departmentFields";
import { createRequest } from "../api/requestsApi";
import { CheckCircle2 } from "lucide-react";
import { ROLES } from "../data/roles";

const MAINTENANCE_TYPES = ["Preventive", "Corrective", "Emergency"];

export default function NewRequestPage({ onSubmitted }) {
  const { user } = useAuth();
  const [form, setForm] = useState({
  asset_id: "",
  section: "",
  description: "",
  duration_minutes: "",
  category: "",
  severity: "MEDIUM",
  maintenance_type: MAINTENANCE_TYPES[0],
  urgency_remarks: "",
});
  const [deptData, setDeptData] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const extraFields = DEPARTMENT_FIELDS[user.role] || [];

  function fillSampleData() {
    setForm({
      asset_id: "A-001",
      section: "MAS-CHE",
      description: "Repeated rail defect detected near KM 42, moderate wear observed on inner rail.",
      duration_minutes: "120",
      category: "TRACK_DEFECT",
      severity: "HIGH",
      maintenance_type: MAINTENANCE_TYPES[0],
      urgency_remarks: "Repeated defect, needs attention within 48 hours",
    });
    if (extraFields.length > 0) {
      const sampleDeptData = {};
      extraFields.forEach((f) => { sampleDeptData[f.id] = "Sample value"; });
      setDeptData(sampleDeptData);
    }
  }
  function updateField(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function updateDeptField(key, value) {
    setDeptData((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit() {
    if (!form.asset_id || !form.section || !form.category) return;
    setSubmitting(true);
    try {
      const departmentInfo = ROLES.find((r) => r.id === user.role);
      await createRequest({
        ...form,
        duration_minutes: Number(form.duration_minutes),
        department: departmentInfo.apiValue, // sends "ENGINEERING", not "Engineering"
        department_fields: deptData,
      });
      setSuccess(true);
      setForm({
        asset_id: "", section: "", description: "", duration_minutes: "",
        category: "", severity: "MEDIUM", maintenance_type: MAINTENANCE_TYPES[0], urgency_remarks: "",
      });
      setDeptData({});
      onSubmitted?.();
    } finally {
      setSubmitting(false);
    }
}

  if (success) {
    return (
      <div className="max-w-md bg-white border border-gray-200 rounded-2xl p-8 text-center">
        <CheckCircle2 className="mx-auto text-emerald-600 mb-3" size={32} />
        <p className="font-semibold text-gray-800">Request submitted</p>
        <button onClick={() => setSuccess(false)} className="mt-4 text-sm text-[#2563EB] font-medium">
          Submit another request
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-lg">
      <div className="flex items-center justify-between mb-4">
      <h1 className="text-xl font-bold text-gray-800">New Maintenance Request</h1>
      <button
        onClick={fillSampleData}
        className="text-xs font-semibold text-[#2563EB] border border-[#2563EB]/30 rounded-lg px-3 py-1.5 hover:bg-blue-50"
      >
        Fill Sample Data
      </button>
    </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
        <Field label="Asset ID">
          <input value={form.asset_id} onChange={(e) => updateField("asset_id", e.target.value)} className={inputCls} />
        </Field>
        <Field label="Section">
          <input value={form.section} onChange={(e) => updateField("section", e.target.value)} placeholder="e.g. MAS-AJJ" className={inputCls} />
        </Field>
        <Field label="Defect / Maintenance Category">
          <input value={form.category} onChange={(e) => updateField("category", e.target.value)} className={inputCls} />
        </Field>
        <Field label="Severity (your assessment)">
          <select value={form.severity} onChange={(e) => updateField("severity", e.target.value)} className={inputCls}>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </Field>
        <Field label="Description / Notes">
          <textarea value={form.description} onChange={(e) => updateField("description", e.target.value)} rows={3} className={inputCls} />
          <p className="text-xs text-gray-400 mt-1">Be specific — this description helps the system assess severity and urgency.</p>
        </Field>
        <Field label="Duration (minutes)">
          <input type="number" value={form.duration_minutes} onChange={(e) => updateField("duration_minutes", e.target.value)} className={inputCls} />
        </Field>
        <Field label="Maintenance Type">
          <select value={form.maintenance_type} onChange={(e) => updateField("maintenance_type", e.target.value)} className={inputCls}>
            {MAINTENANCE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </Field>
        <Field label="Urgency / Remarks">
          <input value={form.urgency_remarks} onChange={(e) => updateField("urgency_remarks", e.target.value)} className={inputCls} />
        </Field>

        {extraFields.length > 0 && (
          <>
            <div className="pt-2 border-t border-gray-100">
              <p className="text-xs font-semibold text-gray-400 uppercase mb-3">
                {user.role} Specific Fields
              </p>
            </div>
            {extraFields.map((f) => (
              <Field key={f.id} label={f.label}>
                <input
                  value={deptData[f.id] || ""}
                  onChange={(e) => updateDeptField(f.id, e.target.value)}
                  className={inputCls}
                />
              </Field>
            ))}
          </>
        )}

        <button
          onClick={handleSubmit}
          disabled={submitting}
          className="w-full bg-[#1E3A5F] text-white font-semibold py-2.5 rounded-lg hover:opacity-90 disabled:opacity-50"
        >
          {submitting ? "Submitting..." : "Submit Request"}
        </button>
      </div>
    </div>
  );
}

const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2563EB]";

function Field({ label, children }) {
  return (
    <div>
      <label className="text-sm text-gray-600 block mb-1">{label}</label>
      {children}
    </div>
  );
}