import { useEffect, useState } from "react";

const code = `# PULSE Example Program
from models import LinearRegression

X = @[[1, 2], [3, 4]]
Y = @[0, 1]

model = LinearRegression()
data = X
labels = Y
model.train(data, labels)

prediction = model.predict(@[[5, 6]])
print(prediction)
`

const SPEED = 25
const LINE_DELAY = 500
const RESTART_DELAY = 1500

function CodeExample() {
    const [displayedCode, setDisplayedCode] = useState('')
    
    useEffect(() => {
        let index = 0
        let timeoutId
        
        function type() {
            if (index < code.length) {
                const character = code.charAt(index)
                setDisplayedCode((current) => current + character)
                
                let delay = SPEED
                
                if (character === '\n') {
                    delay += LINE_DELAY
                }
                
                index += 1
                timeoutId = setTimeout(type, delay)
            } else {
                timeoutId = setTimeout(() => {
                    setDisplayedCode('')
                    index = 0
                    type()
                }, RESTART_DELAY)
            }
        }
        
        type()
        
        return () => {
            clearTimeout(timeoutId)
        }
    }, [])
    
    return (
        <section className="code-example">
            <div className="section-title">
                <h3>Pulse: Code Example</h3>
            </div>
            
            <div className="pulse-code">
                <pre>{displayedCode}</pre>
            </div>
        </section>
    )
}

export default CodeExample
