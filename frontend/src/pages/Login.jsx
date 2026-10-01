import { useState } from "react";
import { api } from "../api";

export default function Login({ onLogin }) {
  const [f, setF] = useState({ username: "", password: "" });
  const [err, setErr] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    try {
      const { token, user } = await api("/login", { method: "POST", body: f });
      localStorage.setItem("token", token);           // sent with every later request
      localStorage.setItem("user", JSON.stringify(user));
      onLogin(user);
    } catch (e) { setErr(e.message); }
  };

  return (
    <form className="login" onSubmit={submit}>
      <h1>Asset Command</h1>
      <p>Sign in to manage bases, transfers and assignments.</p>
      <input placeholder="Username" value={f.username} onChange={(e) => setF({ ...f, username: e.target.value })} />
      <input placeholder="Password" type="password" value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} />
      {err && <div className="err">{err}</div>}
      <button>Sign in</button>
    </form>
  );
}
