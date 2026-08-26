import { Link } from "react-router-dom"

function Navbar() {
    return (
        <nav className="navbar">
            <div className="logo-wrapper">
                <div className="logo">
                    <img src="/logo.png" alt="Pulse logo" />
                </div>
                
                <h1 className="logo-title">Pulse</h1>
            </div>
            
            <ul>
                <li>
                    <a href="/" className="active">
                        Home
                    </a>
                </li>
                
                <li>
                    <a href="/docs">Documentation</a>
                </li>
                
                <li>
                    <Link to="/architecture">Project Architecture</Link>
                </li>
                
                <li>
                    <a href="/about">About</a>
                </li>
            </ul>
        </nav>
    )
}

export default Navbar
