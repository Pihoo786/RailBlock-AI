import { useState } from "react";
import { useAuth } from "../context/useAuth";
import { DEPARTMENT_FIELDS } from "../data/departmentFields";
import { createRequest } from "../api/requestsApi";
import { CheckCircle2 } from "lucide-react";

const MAINTENANCE_TYPES = ["Preventive", "Corrective", "Emergency"];

export default function NewRequestPage({ onSubmitted }) {
  const { user } = useAuth();
  const [form, setForm] = useState({
    asset_id: "",
    section: "",
    category: "",
    severity: "MEDIUM",
    description: "",
    required_duration: "",
    maintenance_type: MAINTENANCE_TYPES[0],
    urgency_remarks: "",
  });
  const [deptData, setDeptData] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const extraFields = DEPARTMENT_FIELDS[user.role] || [];

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
      await createRequest({
        ...form,
        department: user.role,
        submitted_by: user.username,
        department_fields: deptData,
      });
      setSuccess(true);
      setForm({
        asset_id: "", section: "", category: "", severity: "MEDIUM",
        description: "", required_duration: "", maintenance_type: MAINTENANCE_TYPES[0], urgency_remarks: "",
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
      <h1 className="text-xl font-bold text-gray-800 mb-4">New Maintenance Request</h1>

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
        <Field label="Severity">
          <select value={form.severity} onChange={(e) => updateField("severity", e.target.value)} className={inputCls}>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
          </select>
        </Field>
        <Field label="Description / Notes">
          <textarea value={form.description} onChange={(e) => updateField("description", e.target.value)} rows={3} className={inputCls} />
        </Field>
        <Field label="Required Duration (minutes)">
          <input type="number" value={form.required_duration} onChange={(e) => updateField("required_duration", e.target.value)} className={inputCls} />
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