const reasons = [
    {
        title: 'Designed specifically for AI & ML',
        text: 'Pulse is tailored to efficiently handle AI and Machine Learning workflows.',
    },
    {
        title: 'Native tensor and matrix operations',
        text: 'The language provides built-in support for tensors and matrix operations for numerical computing.',
    },
    {
        title: 'Python-like syntax',
        text: 'Offers simple and readable Python-like syntax, making it easy to learn and use.',
    },
    {
        title: 'C++/Rust-like speed through optimized backend',
        text: 'Optimized backend ensures high performance comparable to C++ or Rust.',
    },
    {
        title: 'Simple, clean, modern language',
        text: 'Designed with clarity and modern programming practices in mind.',
    },
]

function WhyPulse() {
    return (
        <section className="why-pulse section" id="why-pulse">
            <div className="section-title">
                <h3>Why Pulse Exists</h3>
            </div>
            
            <ol className="why-pulse-cards">
                {reasons.map((reason, index) => (
                    <li className="why-pulse-card" key={reason.title}>
                        <div className="why-pulse-content">
                            <div className="why-pulse-number">
                                {String(index + 1).padStart(2, '0')}
                            </div>
                            
                            <div>
                                <h4>{reason.title}</h4>
                                <p>{reason.text}</p>
                            </div>
                        </div>
                    </li>
                ))}
            </ol>
        </section>
    )
}

export default WhyPulse
