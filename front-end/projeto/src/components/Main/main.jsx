import s from "./styleMain.module.scss";
import { Routes, Route } from "react-router-dom";
import Home from "../../Pages/Home";
import Products from "../../Pages/Products";
import Cart from "../../Pages/Cart";
import Checkout from "../../Pages/Checkout";
import Login from "../../Pages/Login";
import Cadastro from "../../Pages/Cadastro";

export default function Main() {
  return (
    <main className={s.main}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="/login" element={<Login />} />
        <Route path="/cadastro" element={<Cadastro />} />
      </Routes>
    </main>
  );
}

