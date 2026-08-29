import { NavLink } from "react-router-dom";

export default function Nav() {
  return (
    <header className="nav">
      <NavLink to="/" className="nav__brand">
        海子诗歌图谱
        <span className="en">Haizi Poetry Atlas</span>
      </NavLink>
      <nav className="nav__links">
        <NavLink to="/" end>
          图谱
        </NavLink>
        <NavLink to="/poems">诗篇</NavLink>
        <NavLink to="/about">关于</NavLink>
      </nav>
    </header>
  );
}
