import { Link } from "react-router-dom"

function Hero() {
    return (
        <section className="hero-section">
            <div className="hero-rings" aria-hidden="true">
                <span />
                <span />
                <span />
            </div>
            
            <div className="hero-badge">Built for AI. Powered by Pulse.</div>
            
            <div className="hero-title">
                <h2>
                    The <span className="gradient-text">AI-Native</span> Programming Language
                </h2>
            </div>
            
            <div className="hero-subtitle">
                <h3>Build, train and run AI with language-native speed</h3>
            </div>
            
            <div className="hero-buttons">
                <a href="#learn" className="hero-button primary">
                    Learn Pulse
                </a>
                
                <Link to="/editor" className="hero-button">
                    Online Editor
                </Link>
            </div>
            
            <svg
                className="hero-pulse-line"
                viewBox="0 0 600 80"
                aria-hidden="true"
            >
                <defs>
                    <linearGradient id="pulse-gradient" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#8b5cf6" />
                        <stop offset="100%" stopColor="#22d3ee" />
                    </linearGradient>
                </defs>
                <path d="M0 40 H190 L215 40 L235 8 L262 72 L285 24 L300 40 H600" />
            </svg>
        </section>
    )
}

export default Hero;