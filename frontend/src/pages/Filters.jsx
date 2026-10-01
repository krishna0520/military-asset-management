// Shared filter bar: date range, base, equipment type
export default function Filters({ f, setF, meta, user, onApply }) {
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  return (
    <div className="filters">
      <label>From <input type="date" value={f.start || ""} onChange={set("start")} /></label>
      <label>To <input type="date" value={f.end || ""} onChange={set("end")} /></label>
      {user.role === "admin" && (
        <label>Base <select value={f.base_id || ""} onChange={set("base_id")}>
          <option value="">All bases</option>{meta.bases.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}</select></label>)}
      <label>Equipment <select value={f.equipment_type_id || ""} onChange={set("equipment_type_id")}>
        <option value="">All types</option>{meta.equipment.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}</select></label>
      <button onClick={onApply}>Apply filters</button>
    </div>
  );
}
