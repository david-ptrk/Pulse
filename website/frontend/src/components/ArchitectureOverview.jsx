import { Link } from "react-router-dom"

const stages = [
    {
        name: 'Source Code',
        description: 'Pulse program written by the developer.',
    },
    {
        name: 'Lexer',
        description: 'Converts source code into a stream of tokens.',
    },
    {
        name: 'Parser',
        description: 'Builds the program structure from the tokens.',
    },
    {
        name: 'Interpreter',
        description: 'Executes the parsed Pulse program.',
    },
]

function ArchitectureOverview() {
    return (
        <section className="architecture-section">
            <div className="section-title">
                <h3>Architecture Overview</h3>
            </div>
            
            <div className="architecture-pipeline">
                {stages.map((stage, index) => (
                    <div className="architecture-stage-wrapper" key={stage.name}>
                        <article className="architecture-stage">
                            <span className="architecture-stage-number">
                                {String(index + 1).padStart(2, '0')}
                            </span>
                            
                            <h4>{stage.name}</h4>
                            <p>{stage.description}</p>
                        </article>
                        
                        {index < stages.length - 1 && (
                            <span className="architecture-arrow" aria-hidden="true">
                                →
                            </span>
                        )}
                    </div>
                ))}
            </div>
            
            <div className="architecture-link">
                <Link to="/architecture">View Full Architecture</Link>
            </div>
        </section>
    )
}

export default ArchitectureOverview
