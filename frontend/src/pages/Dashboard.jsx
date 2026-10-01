import { useEffect, useState } from "react";
import { api, qs } from "../api";
import Filters from "./Filters.jsx";

const Table = ({ rows, cols }) => (
  <table><thead><tr>{cols.map(([, h]) => <th key={h}>{h}</th>)}</tr></thead>
    <tbody>{rows.length ? rows.map((r) => <tr key={r.id}>{cols.map(([k]) => <td key={k}>{r[k]}</td>)}</tr>)
      : <tr><td colSpan={cols.length}>No records for these filters.</td></tr>}</tbody></table>
);

export default function Dashboard({ meta, user }) {
  const [f, setF] = useState({});
  const [d, setD] = useState(null);
  const [open, setOpen] = useState(false);   // net-movement pop-up
  const [err, setErr] = useState("");

  const load = () => api("/dashboard?" + qs(f)).then(setD).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);

  const cards = d && [
    ["Opening balance", d.opening_balance], ["Closing balance", d.closing_balance],
    ["Net movement", d.net_movement, true], ["Assigned", d.assigned], ["Expended", d.expended]];

  return (
    <section>
      <h2>Dashboard</h2>
      <Filters f={f} setF={setF} meta={meta} user={user} onApply={load} />
      {err && <div className="err">{err}</div>}
      <div className="cards">
        {cards?.map(([label, v, click]) => (
          <div key={label} className={"card" + (click ? " click" : "")} onClick={click ? () => setOpen(true) : undefined}>
            <span>{label}</span><strong>{v}</strong>{click && <small>Click for breakdown</small>}
          </div>))}
      </div>
      {d && <p className="note">Net movement = purchases ({d.purchases}) + transfers in ({d.transfer_in}) − transfers out ({d.transfer_out}).
        Closing = opening + net movement − expended.</p>}
      {open && (
        <div className="overlay" onClick={() => setOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button className="x" onClick={() => setOpen(false)}>Close</button>
            <h3>Purchases ({d.purchases})</h3>
            <Table rows={d.details.purchases} cols={[["date", "Date"], ["base_name", "Base"], ["equipment_name", "Equipment"], ["quantity", "Qty"]]} />
            <h3>Transfers in ({d.transfer_in})</h3>
            <Table rows={d.details.transfers_in} cols={[["date", "Date"], ["from_base_name", "From"], ["to_base_name", "To"], ["equipment_name", "Equipment"], ["quantity", "Qty"]]} />
            <h3>Transfers out ({d.transfer_out})</h3>
            <Table rows={d.details.transfers_out} cols={[["date", "Date"], ["from_base_name", "From"], ["to_base_name", "To"], ["equipment_name", "Equipment"], ["quantity", "Qty"]]} />
          </div>
        </div>)}
    </section>
  );
}
