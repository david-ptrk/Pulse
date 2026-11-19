import { Link, NavLink } from "react-router-dom"

function Navbar() {
    return (
        <nav className="navbar">
            <Link to="/" className="logo-wrapper">
                <div className="logo">
                    <img src="/logo.png" alt="Pulse logo" />
                </div>
                
                <h1 className="logo-title">Pulse</h1>
            </Link>
            
            <ul>
                <li>
                    <NavLink to="/" end>
                        Home
                    </NavLink>
                </li>
                
                <li>
                    <a href="/docs">Documentation</a>
                </li>
                
                <li>
                    <NavLink to="/architecture">Project Architecture</NavLink>
                </li>
                
                <li>
                    <NavLink to="/about">About</NavLink>
                </li>
            </ul>
        </nav>
    )
}

export default Navbar;