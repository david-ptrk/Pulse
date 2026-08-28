import { useEffect, useRef, useState } from "react";
import CodeMirror from '@uiw/react-codemirror'
import pulseLanguage from "../pulseLanguage";
import { oneDark } from '@codemirror/theme-one-dark'
import '../online-editor.css'

const DEFAULT_CODE = `# PULSE Example Program
from models import LinearRegression

X = @[[1, 2],[3, 4]]
Y = @[0, 1]

model = LinearRegression()
data = X
labels = Y

model.train(data, labels)

prediction = model.predict(@[[5, 6]])
print(prediction)`

function OnlineEditor() {
    const [code, setCode] = useState(DEFAULT_CODE)
    const [output, setOutput] = useState('')
    const [running, setRunning] = useState(false)
    const [executionTime, setExecutionTime] = useState(null);
    
    const editorRef = useRef(null);
    
    const runCode = async () => {
        if (running) return;
        
        setRunning(true);
        setOutput('Running Pulse program...');
        setExecutionTime(null);
        
        const startTime = performance.now();
        
        try {
            const response = await fetch('http://127.0.0.1:8000/api/execute/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code }),
            })
            
            const data = await response.json()
            
            const elapsed = performance.now() - startTime;
            setExecutionTime(elapsed);
            
            if (data.exit_code === 0) {
                setOutput(data.stdout || 'Program finished successfully.')
            } else {
                setOutput(data.stderr || data.error || 'Program execution failed.')
            }
        } catch (error) {
            const elapsed = performance.now() - startTime;
            setExecutionTime(elapsed);
            
            setOutput(`Connection error: ${error.message}`)
        } finally {
            setRunning(false)
        }
    };
    
    const clearOutput = () => {
        setOutput('')
        setExecutionTime(null);
    }
    
    const resetCode = () => {
        setCode(DEFAULT_CODE);
        clearOutput();
    };
    
    useEffect(() => {
        const handleKeyboardShortcut = (event) => {
            // Ctrl + Enter -> Run
            if (event.ctrlKey && event.key === "Enter") {
                event.preventDefault();
                runCode();
            }
            
            // Ctrl + L -> Clear Output
            if (event.ctrlKey && event.key.toLowerCase() === 'l') {
                event.preventDefault();
                clearOutput();
            }
        };
        
        window.addEventListener("keydown", handleKeyboardShortcut);
        
        return () => {
            window.removeEventListener("keydown", handleKeyboardShortcut);
        };
    }, [running, code]);
    
    return (
        <main className="editor-page">
            <header className="editor-header">
                <div>
                    <h1>Pulse Online Editor</h1>
                    <p>Write, run, and experiment with Pulse.</p>
                </div>
                
                <div className="editor-actions">
                    <button className="editor-btn run-btn" onClick={runCode} disabled={running}>
                        {running ? '⏳ Running...' : '▶ Run'}
                    </button>
                    
                    <button className="editor-btn" onClick={clearOutput}>
                        Clear Output
                    </button>
                    
                    <button className="editor-btn" onClick={resetCode}>
                        Reset Code
                    </button>
                </div>
            </header>
            
            <section className="editor-workspace">
                <div className="code-panel">
                    <div className="panel-header">
                        <span>main.pul</span>
                        
                        <span className="keyboard-hint">Ctrl + Enter to run</span>
                    </div>
                    
                    <CodeMirror
                        value={code}
                        height="500px"
                        theme={oneDark}
                        extensions={[pulseLanguage]}
                        onChange={setCode}
                        basicSetup={{
                            lineNumbers: true,
                            foldGutter: true,
                            highlightActiveLine: true,
                            bracketMatching: true,
                            autocompletion: true,
                        }}
                    />
                </div>
                
                <div className="output-panel">
                    <div className="panel-header">
                        <span>Output</span>
                        
                        <div className="output-meta">
                            {running && (
                                <span>Running...</span>
                            )}
                            
                            {!running && executionTime !== null && (
                                <span>
                                    {executionTime.toFixed(0)} ms
                                </span>
                            )}
                            
                            {output && (
                                <button className="clear-output" onClick={clearOutput}>Clear</button>
                            )}
                        </div>
                    </div>
                    
                    <pre className="output-content">
                        {output || 'Run your Pulse program to see the output here.'}
                    </pre>
                </div>
            </section>
        </main>
    );
}

export default OnlineEditor;
