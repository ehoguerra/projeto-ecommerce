import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Cadastro() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const navigate = useNavigate();

  function handleCadastro(e) {
    e.preventDefault();
    // Aqui você pode adicionar a lógica de cadastro
    // Após cadastrar, redireciona para login
    navigate("/login");
  }

  return (
    <div style={{ maxWidth: 350, margin: "2rem auto", padding: 20, border: "1px solid #ccc", borderRadius: 8 }}>
      <h2>Cadastrar</h2>
      <form onSubmit={handleCadastro}>
        <input
          type="email"
          placeholder="E-mail"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
          style={{ width: "100%", marginBottom: 10, padding: 8 }}
        />
        <input
          type="password"
          placeholder="Senha"
          value={senha}
          onChange={e => setSenha(e.target.value)}
          required
          style={{ width: "100%", marginBottom: 10, padding: 8 }}
        />
        <button type="submit" style={{ width: "100%", padding: 10 }}>Cadastrar</button>
      </form>
      <p style={{ marginTop: 10, textAlign: "center" }}>
        Já tem conta? <a href="/login">Entrar</a>
      </p>
    </div>
  );
}