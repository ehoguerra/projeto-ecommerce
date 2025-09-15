import s from "./styleHeader.module.scss";
import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header className={s.header}>
      <nav>
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/products">Produtos</Link></li>
          <li><Link to="/cart">Carrinho</Link></li>
          <li><Link to="/checkout">Checkout</Link></li>
          <li><Link to="/login">Login</Link></li>
        </ul>
      </nav>
    </header>
  );
}
