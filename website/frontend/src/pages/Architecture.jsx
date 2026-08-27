import { useEffect, useState } from "react";
import TokenStream from "../components/TokenStream";
import '../architecture.css'

const STAGES = [
    {
        id: 'source',
        name: 'Source Code',
        sub: '.pul file',
        icon: '📄',
        color: '#888780',
        bg: '#F1EFE8',
        dark: '#2C2C2A',
        title: 'Source Code',
        subtitle: 'Raw Pulse program text',
        leftLabel: 'Sample Program',
        leftContent: (
            <pre className="code-block">{`X = @[[1, 2], [3, 4]]
Y = @[0, 1]

model = LinearModel()
data = X
labels = Y

model.train(data, labels)

prediction = model.predict(@[5, 6])
print(prediction)
`}</pre>
        ),
        rightLabel: 'Supported Features',
        rightContent: [
            'Native tensor literals & indexing',
            'First-class functions (def keyword)',
            'Dynamic data types',
            'AI ops: matmul, softmax, relu, conv2d',
            'Comments with #',
            'Easy Python-like syntax',
        ],
    },
    
    {
        id: 'lexer',
        name: 'Lexer',
        sub: 'Tokenization',
        icon: '✂️',
        color: '#7F77DD',
        bg: '#EEEDFE',
        dark: '#26215C',
        title: 'Lexer (Tokenizer)',
        subtitle: 'Breaks source into a flat stream of tokens',
        leftLabel: 'Token Stream',
        leftContent: <TokenStream />,
        rightLabel: 'How it works',
        rightContent: [
            'Reads chars one at a time via a cursor',
            'Matches keywords: def, for, return, break…',
            'Recognises AI type names as first-class tokens',
            'Handles float & integer literals',
            'Skips whitespace & # comments',
            'Reports unexpected character errors with line/col',
        ],
    },
    
    {
        id: 'parser',
        name: 'Parser',
        sub: 'AST Builder',
        icon: '🌳',
        color: '#1D9E75',
        bg: '#E1F5EE',
        dark: '#04342C',
        title: 'Parser (AST Builder)',
        subtitle:
            'Transforms token stream into an Abstract Syntax Tree',
        leftLabel: 'AST (simplified)',
        leftContent: (
            <pre className="code-block">{`Program
├─ VarDecl "X"
│   └─ TensorLiteral
│       ├─ Row [1, 2]
│       └─ Row [3, 4]
├─ VarDecl "Y"
│   └─ TensorLiteral
│       └─ Row [0, 1]
├─ VarDecl "model"
│   └─ CallExpr "LinearModel"
├─ VarDecl "data"
│   └─ Ident "X"
├─ VarDecl "labels"
│   └─ Ident "Y"
├─ ExprStmt
│   └─ CallExpr "model.train"
│       ├─ Ident "data"
│       └─ Ident "labels"
└─ VarDecl "prediction"
└─ CallExpr "model.predict"
`}</pre>
        ),
        rightLabel: 'Grammar highlights',
        rightContent: [
            'Recursive-descent parser (hand-written)',
            'Precedence climbing for expressions',
            'Tensor literal grammar: nested [] lists and NumPy',
            'Function declarations with typed params',
            'Detailed parse error messages with recovery',
        ],
    },
    
    {
        id: 'resolver',
        name: 'Resolver',
        sub: 'Semantic Analysis',
        icon: '🔍',
        color: '#D85A30',
        bg: '#FAECE7',
        dark: '#4A1B0C',
        title: 'Resolver (Semantic Analyser)',
        subtitle: 'Validates names, types, and tensor shapes',
        leftLabel: 'Resolver passes',
        leftContent: (
            <pre className="code-block">{`// Pass 1 — Global scope initialization

scopes = [&#123;&#125;]

// Statement: X = @[[1,2],[3,4]]
declare("X")
define("X")

// Statement: Y = @[0,1]
declare("Y")
define("Y")

// Statement: model = LinearModel()
declare("model")
resolve(LinearModel)
define("model")

// Statement: data = X
declare("data")
resolve(X)
define("data")

// Statement: labels = Y
declare("labels")
resolve(Y)
define("labels")

// Statement: model.train(data, labels)
resolve(model)
resolve(data)
resolve(labels)

// Statement: prediction = model.predict(@[5,6])
declare("prediction")
resolve(model)
resolve(predict)
define("prediction")

// Final scope state
X: True
Y: True
model: True
data: True
labels: True
prediction: True
`}</pre>
        ),
        rightLabel: 'Checks performed',
        rightContent: [
            'Undefined variable / function detection',
            'Static tensor shape inference & validation',
            'Type compatibility for AI ops',
            'Duplicate declaration errors',
            'Return type checking in function bodies',
            'Capture list building for closures',
        ],
    },

    {
        id: 'interpreter',
        name: 'Interpreter',
        sub: 'Tree-walk Eval',
        icon: '⚡',
        color: '#BA7517',
        bg: '#FAEEDA',
        dark: '#412402',
        title: 'Interpreter (Tree-walk Evaluator)',
        subtitle: 'Evaluates the resolved AST and produces output',
        leftLabel: 'Execution trace',
        leftContent: (
            <pre className="code-block">{`// Env: global

eval VarDecl "X"
→ Tensor([[1,2],[3,4]])

eval VarDecl "Y"
→ Tensor([0,1])

eval VarDecl "model"
→ LinearModel()

eval Assign "data"
→ X

eval Assign "labels"
→ Y

// Training phase
eval CallExpr "model.train"
→ train(...)
→ weights updated

// Prediction phase
eval CallExpr "model.predict"
→ forward(...)

// Output
eval CallExpr "print"
→ Output: [[p]]
`}</pre>
        ),
        rightLabel: 'Runtime capabilities',
        rightContent: [
            'Environment chain (scope stack) for variables',
            'Native tensor ops via built-in op table',
            'First-class function values & closures',
            'Lazy short-circuit evaluation (and / or)',
            'Runtime error reporting with stack trace',
            'REPL mode: eval single statements interactively',
        ],
    },
    
    {
        id: 'output',
        name: 'Output',
        sub: 'Result / REPL',
        icon: '✅',
        color: '#639922',
        bg: '#EAF3DE',
        dark: '#173404',
        title: 'Output',
        subtitle: 'Program result, printed values, or REPL response',
        leftLabel: 'Example output',
        leftContent: (
            <pre className="code-block">{`$ python pulse.py tests/code.pul

Pulse v1.0 — AI-native language

Interpreting pulse

Output: Tensor([
[0.72]
])

Elapsed: 0.6ms
Peak mem: 1.4 KB
`}</pre>
        ),
        rightLabel: 'Output modes',
        rightContent: [
            'CLI, batch execution',
            'REPL: pulse repl, interactive prompt',
            'Tensor pretty-print with shape annotation',
            'Structured runtime error messages',
            'Timing & memory stats (--profile flag)',
            'Exit codes for pipeline integration',
        ],
    },
]

const DELAYS = [0, 300, 600, 900, 1200, 1500]

function Architecture() {
    const [visibleStages, setVisibleStages] = useState([])
    const [activeStage, setActiveStage] = useState(null)
    const [running, setRunning] = useState(false)
    
    const startPipeline = () => {
        if (running) return
        
        setRunning(true)
        setActiveStage(null)
        setVisibleStages([])
        
        STAGES.forEach((stage, index) => {
            setTimeout(() => {
                setVisibleStages((current) => [...current, stage.id])
                
                if (index === STAGES.length - 1) {
                    setTimeout(() => {
                        setRunning(false)
                        setActiveStage(0)
                    }, 400)
                }
            }, DELAYS[index])
        })
    }
    
    const resetPipeline = () => {
        setRunning(false)
        setVisibleStages([])
        setActiveStage(null)
    }
    
    useEffect(() => {
        return () => {
            setVisibleStages([])
        }
    }, [])
    
    return (
        <main className="arch-wrap">
            <h1 className="arch-title">
                Pulse - Language Architecture
            </h1>
            
            <div className="pipeline-wrap">
                <div className="pipeline">
                    {STAGES.map((stage, index) => (
                        <div className="stage-wrapper" key={stage.id}>
                            <div
                                className={`stage ${
                                    visibleStages.includes(stage.id)
                                        ? 'visible'
                                        : ''
                                } ${
                                    activeStage === index ? 'active' : ''
                                }`}
                                style={{
                                    '--stage-color': stage.color,
                                    '--stage-bg': stage.bg,
                                    '--stage-dark': stage.dark,
                                }}
                                onClick={() => setActiveStage(index)}
                            >
                                <div className="stage-box">
                                    <div className="stage-icon">
                                        {stage.icon}
                                    </div>
                                    
                                    <div className="stage-name">
                                        {stage.name}
                                    </div>
                                    
                                    <div className="stage-sub">
                                        {stage.sub}
                                    </div>
                                </div>
                            </div>
                            
                            {index < STAGES.length - 1 && (
                                <div
                                    className={`connector ${
                                        visibleStages.includes(STAGES[index + 1].id)
                                            ? 'visible'
                                            : ''
                                    }`}
                                >
                                    <div className="conn-line">
                                        <div
                                            className={`conn-pulse ${
                                                visibleStages.includes(stage.id) &&
                                                visibleStages.includes(STAGES[index + 1].id)
                                                    ? 'running'
                                                    : ''
                                            }`}
                                        />
                                    </div>
                                    <div className="conn-arrow" />
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
            
            <div className="controls">
                <button
                    className="btn primary"
                    onClick={startPipeline}
                    disabled={running}
                >
                    {running ? '⏳ Running…' : '▶ Run Pipeline'}
                </button>
                
                <button
                    className="btn"
                    onClick={resetPipeline}
                >
                    ↺ Reset
                </button>
            </div>
            
            {activeStage !== null && (
                <section
                    className="detail-panel"
                    style={{
                        '--active-color': STAGES[activeStage].color,
                    }}
                >
                    <div className="detail-inner">
                        <div className="detail-header">
                            <div className="detail-dot" />
                            
                            <div>
                                <div className="detail-title">{STAGES[activeStage].title}</div>
                                <div className="detail-subtitle">{STAGES[activeStage].subtitle}</div>
                            </div>
                        </div>
                        
                        <div className="detail-col">
                            <h4>{STAGES[activeStage].leftLabel}</h4>
                            {STAGES[activeStage].leftContent}
                        </div>
                        
                        <div className="detail-col">
                            <h4>{STAGES[activeStage].rightLabel}</h4>
                            <ul className="feat-list">
                                {STAGES[activeStage].rightContent.map(
                                    (item) => (
                                        <li key={item}>{item}</li>
                                    ),
                                )}
                            </ul>
                        </div>
                    </div>
                </section>
            )}
        </main>
    )
}

export default Architecture
