const features = [
    'Tensor-Native Syntax',
    'Built-In AI Ops',
    'Lightweight Interpreter',
    'Static + Dynamic Typing Hybrid',
]

function Features() {
    return (
        <section className="features-section">
            <div className="section-title">
                <h3>Key Features</h3>
            </div>
            
            <div className="feature-cards">
                {features.map((feature) => (
                    <article className="feature-card" key={feature}>
                        <h4>{feature}</h4>
                    </article>
                ))}
            </div>
        </section>
    )
}

export default Features
