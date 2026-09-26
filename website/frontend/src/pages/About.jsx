import '../about.css'

const OBJECTIVES = [
    {
        title: 'AI-Native Syntax',
        color: '#7F77DD',
        bg: '#EEEDFE',
        text: 'Built-in support for tensors, matrices, and common AI operations, reducing the need for external libraries.',
    },
    {
        title: 'Fast Program Execution',
        color: '#1D9E75',
        bg: '#E1F5EE',
        text: 'An interpreter designed to execute Pulse programs efficiently, completing typical AI tasks within minimal runtime.',
    },
    {
        title: 'Sample AI Programs',
        color: '#D85A30',
        bg: '#FAECE7',
        text: 'Ready-to-run example applications, like chatbots and ML models, so developers can see results in minutes.',
    },
    {
        title: 'Readable, Simple Syntax',
        color: '#BA7517',
        bg: '#FAEEDA',
        text: 'Python-like readability paired with DSL-level precision, reducing code complexity for AI tasks.',
    },
    {
        title: 'Error Handling & Debugging',
        color: '#639922',
        bg: '#EAF3DE',
        text: 'Syntax validation and clear runtime feedback, helping developers detect and fix errors quickly.',
    },
    {
        title: 'Python Backend Integration',
        color: '#888780',
        bg: '#F1EFE8',
        text: 'A bridge to the Python ecosystem, so Pulse can call existing Python functions for advanced computations.',
    },
]

function About() {
    return (
        <main className="about-wrap">
            <section className="about-hero">
                <h1 className="about-title">About Pulse</h1>
                <p className="about-lede">
                    Pulse is an AI-native programming language with Python-like syntax,
                    built to make AI and machine learning prototyping fast, readable, and
                    accessible - without wrestling with external library setup before
                    you've written a single model.
                </p>
            </section>
            
            <section className="about-section">
                <h2>Why Pulse</h2>
                <p>
                    Most AI development today happens in general-purpose languages glued
                    together with external libraries - numpy for tensors, scikit-learn for
                    models, pandas for data handling. Pulse takes a different approach: tensor
                    literals, matrix operations, and common ML workflows are part of the
                    language itself, so a working regression or classification model can be a
                    few dozen lines of code with nothing to install first.
                </p>
            </section>
            
            <section className="about-section">
                <h2>Project Objectives</h2>
                <div className="about-grid">
                    {OBJECTIVES.map((obj) => (
                        <div
                            className="about-card"
                            key={obj.title}
                            style={{
                                '--card-color': obj.color,
                                '--card-bg': obj.bg,
                            }}
                        >
                            <h3>{obj.title}</h3>
                            <p>{obj.text}</p>
                        </div>
                    ))}
                </div>
            </section>
            
            <section className="about-section">
                <h2>The Project</h2>
                <p>
                    Pulse is developed as a Final Year Project, covering the full language
                    pipeline - lexer, parser, resolver, and interpreter - alongside an
                    AI/ML-focused standard library and a Python interoperability layer for
                    calling into the wider Python ecosystem when needed.
                </p>
            </section>
        </main>
    )
}

export default About
