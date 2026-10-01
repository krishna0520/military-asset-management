import { useEffect, useState } from "react";
import { api } from "./api";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Ledger from "./pages/Ledger.jsx";

// Which pages each role can see (the backend enforces this too - the UI just hides links)
const PAGES = {
  admin: ["Dashboard", "Purchases", "Transfers", "Assignments", "Audit log"],
  base_commander: ["Dashboard", "Purchases", "Transfers", "Assignments"],
  logistics_officer: ["Purchases", "Transfers"],
};

const CONFIG = {
  Purchases: { endpoint: "purchases", fields: [["base_id", "Base", "base"], ["equipment_type_id", "Equipment", "equipment"], ["quantity", "Quantity", "number"], ["date", "Date", "date"]],
    columns: [["date", "Date"], ["base_name", "Base"], ["equipment_name", "Equipment"], ["quantity", "Qty"]] },
  Transfers: { endpoint: "transfers", fields: [["from_base_id", "From base", "base"], ["to_base_id", "To base", "base"], ["equipment_type_id", "Equipment", "equipment"], ["quantity", "Quantity", "number"], ["date", "Date", "date"]],
    columns: [["date", "Date"], ["created_at", "Recorded at"], ["from_base_name", "From"], ["to_base_name", "To"], ["equipment_name", "Equipment"], ["quantity", "Qty"]] },
  Assignments: { endpoint: "assignments", fields: [["base_id", "Base", "base"], ["equipment_type_id", "Equipment", "equipment"], ["personnel", "Personnel", "text"], ["kind", "Type", "kind"], ["quantity", "Quantity", "number"], ["date", "Date", "date"]],
    columns: [["date", "Date"], ["base_name", "Base"], ["equipment_name", "Equipment"], ["personnel", "Personnel"], ["kind", "Type"], ["quantity", "Qty"]] },
};

export default function App() {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("user") || "null"));
  const [meta, setMeta] = useState({ bases: [], equipment: [] });
  const [page, setPage] = useState(null);

  useEffect(() => {
    if (user) {
      setPage(PAGES[user.role][0]);
      api("/meta").then(setMeta).catch(() => logout());
    }
  }, [user]);

  const logout = () => { localStorage.clear(); setUser(null); };
  if (!user) return <Login onLogin={(u) => setUser(u)} />;

  return (
    <div>
      <header className="top">
        <h1>Asset Command</h1>
        <nav>{PAGES[user.role].map((p) => (
          <button key={p} className={p === page ? "on" : ""} onClick={() => setPage(p)}>{p}</button>))}
        </nav>
        <span className="who">{user.username} ({user.role.replace("_", " ")}) <button onClick={logout}>Log out</button></span>
      </header>
      <main>
        {page === "Dashboard" && <Dashboard meta={meta} user={user} />}
        {CONFIG[page] && <Ledger key={page} title={page} meta={meta} user={user} {...CONFIG[page]} />}
        {page === "Audit log" && <AuditLog />}
      </main>
    </div>
  );
}

function AuditLog() {
  const [rows, setRows] = useState([]);
  useEffect(() => { api("/audit-logs").then(setRows); }, []);
  return (
    <section><h2>Audit log</h2>
      <table><thead><tr><th>Time</th><th>User</th><th>Action</th><th>Detail</th></tr></thead>
        <tbody>{rows.map((r, i) => <tr key={i}><td>{r.time}</td><td>{r.user}</td><td>{r.action}</td><td>{r.detail}</td></tr>)}</tbody>
      </table>
    </section>
  );
}
