// One reusable page for Purchases, Transfers and Assignments:
// filter bar + "record new" form + history table. Config comes from App.jsx.
import { useEffect, useState } from "react";
import { api, qs } from "../api";
import Filters from "./Filters.jsx";

export default function Ledger({ title, endpoint, fields, columns, meta, user }) {
  const [rows, setRows] = useState([]);
  const [f, setF] = useState({});
  const [form, setForm] = useState({});
  const [msg, setMsg] = useState({ text: "", bad: false });

  const load = () => api(`/${endpoint}?` + qs(f)).then(setRows).catch((e) => setMsg({ text: e.message, bad: true }));
  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    const body = { ...form };
    fields.forEach(([k, , t]) => { if (["base", "equipment", "number"].includes(t)) body[k] = Number(body[k]); });
    try {
      await api(`/${endpoint}`, { method: "POST", body });
      setMsg({ text: "Saved.", bad: false }); setForm({}); load();
    } catch (e) { setMsg({ text: e.message, bad: true }); }
  };

  const input = ([k, label, type]) => {
    const props = { value: form[k] || "", onChange: (e) => setForm({ ...form, [k]: e.target.value }), required: true };
    let el;
    if (type === "base") el = <select {...props}><option value="">Select</option>{meta.bases.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}</select>;
    else if (type === "equipment") el = <select {...props}><option value="">Select</option>{meta.equipment.map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}</select>;
    else if (type === "kind") el = <select {...props}><option value="">Select</option><option value="assigned">Assigned</option><option value="expended">Expended</option></select>;
    else el = <input type={type === "number" ? "number" : type} min={type === "number" ? 1 : undefined} {...props} />;
    return <label key={k}>{label}{el}</label>;
  };

  return (
    <section>
      <h2>{title}</h2>
      <form className="form" onSubmit={submit}>{fields.map(input)}<button>Save record</button></form>
      {msg.text && <div className={msg.bad ? "err" : "ok"}>{msg.text}</div>}
      <h3>History</h3>
      <Filters f={f} setF={setF} meta={meta} user={user} onApply={load} />
      <table><thead><tr>{columns.map(([, h]) => <th key={h}>{h}</th>)}</tr></thead>
        <tbody>{rows.length ? rows.map((r) => <tr key={r.id}>{columns.map(([k]) => <td key={k}>{String(r[k] ?? "").replace("T", " ").slice(0, 19)}</td>)}</tr>)
          : <tr><td colSpan={columns.length}>No records yet.</td></tr>}</tbody></table>
    </section>
  );
}
