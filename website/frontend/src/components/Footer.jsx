function Footer() {
    return (
        <footer className="footer">
            <div className="footer-social">
                <a href="#" aria-label="Facebook">
                    Facebook
                </a>
                
                <a href="#" aria-label="Instagram">
                    Instagram
                </a>
                
                <a href="#" aria-label="YouTube">
                    YouTube
                </a>
                
                <a href="#" aria-label="Twitter">
                    Twitter
                </a>
            </div>
            
            <nav className="footer-links">
                <a href="/docs">Docs</a>
                <a
                    href="https://github.com/david-ptrk/Pulse"
                    target="_blank"
                    rel="noreferrer"
                >GitHub</a>
                <a href="/terms">Terms & Conditions</a>
            </nav>
            
            <div className="footer-copyright">
                © 2025–2026 Pulse · Developed by Daud Anjum & Hafiz Muhammad Ahmad
            </div>
        </footer>
    )
}

export default Footer
