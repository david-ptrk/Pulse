const features = [
    {
        icon: '⚡',
        title: 'Tensor-Native Syntax',
        description: 'Tensors are first-class values, written naturally in the language.',
    },
    {
        icon: '🧠',
        title: 'Built-In AI Ops',
        description: 'Common AI operations ship with the language, no extra libraries needed.',
    },
    {
        icon: '🪶',
        title: 'Lightweight Interpreter',
        description: 'Small, fast to start, and easy to embed or run anywhere.',
    },
    {
        icon: '🔀',
        title: 'Static + Dynamic Typing Hybrid',
        description: 'Move quickly while prototyping, then add types where safety matters.',
    },
]

function Features() {
    return (
        <section className="features-section">
            <div className="section-title">
                <h3>Key Features</h3>
            </div>
            
            <div className="feature-cards">
                {features.map((feature) => (
                    <article className="feature-card card" key={feature.title}>
                        <div className="feature-icon" aria-hidden="true">
                            {feature.icon}
                        </div>
                        <h4>{feature.title}</h4>
                        <p>{feature.description}</p>
                    </article>
                ))}
            </div>
        </section>
    )
}

export default Features;