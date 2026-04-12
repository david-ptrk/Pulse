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
    leftContent: `<div class="code-block">X = @[[<span class="num">1</span>, <span class="num">2</span>],
      [<span class="num">3</span>, <span class="num">4</span>]]

Y = @[<span class="num">0</span>, <span class="num">1</span>]

model = <span class="fn">LinearModel</span>()
data = X
labels = Y

model.<span class="fn">train</span>(data, labels)

prediction = model.<span class="fn">predict</span>(@[<span class="num">5</span>, <span class="num">6</span>])
<span class="fn">print</span>(prediction)</div>`,
    rightLabel: 'Supported Features',
    rightContent: `<ul class="feat-list" style="--active-color:#888780">
      <li>Native tensor literals &amp; indexing</li>
      <li>First-class functions (def keyword)</li>
      <li>Dynamic data types</li>
      <li>AI ops: matmul, softmax, relu, conv2d</li>
      <li>Comments with #</li>
      <li>Easy python like syntax</li>
    </ul>`
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
    leftContent: `<div class="token-list">
      ${[
        ['IDENTIFIER', 'X','#1D9E75','#E1F5EE'],
        ['ASSIGN', '=','#888780','#F1EFE8'],
        ['TENSOR', '@','#7F77DD','#EEEDFE'],
        ['LEFT_BRACKET', '[','#888780','#F1EFE8'],
        ['LEFT_BRACKET', '[','#888780','#F1EFE8'],
        ['NUMBER', '1','#BA7517','#FAEEDA'],
        ['COMMA', ',','#888780','#F1EFE8'],
        ['NUMBER', '2','#BA7517','#FAEEDA'],
        ['RIGHT_BRACKET', ']','#888780','#F1EFE8'],
        ['COMMA', ',','#888780','#F1EFE8'],
        ['LEFT_BRACKET', '[','#888780','#F1EFE8'],
        ['NUMBER', '3','#BA7517','#FAEEDA'],
        ['COMMA', ',','#888780','#F1EFE8'],
        ['NUMBER', '4','#BA7517','#FAEEDA'],
        ['RIGHT_BRACKET', ']','#888780','#F1EFE8'],
        ['RIGHT_BRACKET', ']','#888780','#F1EFE8'],
        ['NEWLINE', '\\n','#D85A30','#FAECE7'],
        ['IDENTIFIER', 'Y','#1D9E75','#E1F5EE'],
        ['ASSIGN', '=','#888780','#F1EFE8'],
        ['TENSOR', '@','#7F77DD','#EEEDFE'],
        ['LEFT_BRACKET', '[','#888780','#F1EFE8'],
        ['NUMBER', '0','#BA7517','#FAEEDA'],
        ['COMMA', ',','#888780','#F1EFE8'],
        ['NUMBER', '1','#BA7517','#FAEEDA'],
        ['RIGHT_BRACKET', ']','#888780','#F1EFE8'],
        ['NEWLINE', '\\n','#D85A30','#FAECE7'],
        ['IDENTIFIER', 'model','#1D9E75','#E1F5EE'],
        ['ASSIGN', '=','#888780','#F1EFE8'],
        ['IDENTIFIER', 'LinearModel','#1D9E75','#E1F5EE'],
        ['LEFT_PAREN', '(','#888780','#F1EFE8'],
        ['RIGHT_PAREN', ')','#888780','#F1EFE8'],
        ['NEWLINE', '\\n','#D85A30','#FAECE7'],
        ['IDENTIFIER', 'data','#1D9E75','#E1F5EE'],
        ['ASSIGN', '=','#888780','#F1EFE8'],
        ['IDENTIFIER', 'X','#1D9E75','#E1F5EE'],
        ['NEWLINE', '\\n','#D85A30','#FAECE7'],
        ['IDENTIFIER', 'labels','#1D9E75','#E1F5EE'],
        ['ASSIGN', '=','#888780','#F1EFE8'],
        ['IDENTIFIER', 'Y','#1D9E75','#E1F5EE'],
        ['NEWLINE', '\\n','#D85A30','#FAECE7'],
        ['IDENTIFIER', 'model','#1D9E75','#E1F5EE'],
        ['DOT', '.','#7F77DD','#EEEDFE'],
        ['IDENTIFIER', 'train','#1D9E75','#E1F5EE'],
        ['LEFT_PAREN', '(','#888780','#F1EFE8'],
        ['IDENTIFIER', 'data','#1D9E75','#E1F5EE'],
        ['COMMA', ',','#888780','#F1EFE8'],
        ['IDENTIFIER', 'labels','#1D9E75','#E1F5EE'],
        ['RIGHT_PAREN', ')','#888780','#F1EFE8'],
        ['NEWLINE', '\\n','#D85A30','#FAECE7'],
        ['IDENTIFIER', 'prediction','#1D9E75','#E1F5EE'],
        ['ASSIGN', '=','#888780','#F1EFE8'],
        ['IDENTIFIER', 'model','#1D9E75','#E1F5EE'],
        ['DOT', '.','#7F77DD','#EEEDFE'],
        ['IDENTIFIER', 'predict','#1D9E75','#E1F5EE'],
        ['LEFT_PAREN', '(','#888780','#F1EFE8'],
        ['TENSOR', '@','#7F77DD','#EEEDFE'],
        ['LEFT_BRACKET', '[','#888780','#F1EFE8'],
        ['NUMBER', '5','#BA7517','#FAEEDA'],
        ['COMMA', ',','#888780','#F1EFE8'],
        ['NUMBER', '6','#BA7517','#FAEEDA'],
        ['RIGHT_BRACKET', ']','#888780','#F1EFE8'],
        ['RIGHT_PAREN', ')','#888780','#F1EFE8'],
        ['NEWLINE', '\\n','#D85A30','#FAECE7'],
        ['IDENTIFIER', 'print','#1D9E75','#E1F5EE'],
        ['LEFT_PAREN', '(','#888780','#F1EFE8'],
        ['IDENTIFIER', 'prediction','#1D9E75','#E1F5EE'],
        ['RIGHT_PAREN', ')','#888780','#F1EFE8'],
      ].map(([type,val,c,bg])=>`<span class="token-pill" style="background:${bg};border-color:${c};color:${c}"><span style="opacity:.6;font-size:9px">${type}</span> <strong>${val}</strong></span>`).join('')}
    </div>`,
    rightLabel: 'How it works',
    rightContent: `<ul class="feat-list" style="--active-color:#7F77DD">
      <li>Reads chars one at a time via a cursor</li>
      <li>Matches keywords: def, for, return, break…</li>
      <li>Recognises AI type names as first-class tokens</li>
      <li>Handles float &amp; integer literals</li>
      <li>Skips whitespace &amp; # comments</li>
      <li>Reports unexpected character errors with line/col</li>
    </ul>`
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
    subtitle: 'Transforms token stream into an Abstract Syntax Tree',
    leftLabel: 'AST (simplified)',
    leftContent: `<div class="code-block">Program
├─ VarDecl "X"
│   └─ TensorLiteral
│       ├─ Row [<span class="num">1</span>, <span class="num">2</span>]
│       └─ Row [<span class="num">3</span>, <span class="num">4</span>]
├─ VarDecl "Y"
│   └─ TensorLiteral
│       └─ Row [<span class="num">0</span>, <span class="num">1</span>]
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
├─ VarDecl "prediction"
│   └─ CallExpr "model.predict"
│       └─ TensorLiteral
│           └─ Row [<span class="num">5</span>, <span class="num">6</span>]
└─ ExprStmt
    └─ CallExpr "print"
        └─ Ident "prediction"
</div>`,
    rightLabel: 'Grammar highlights',
    rightContent: `<ul class="feat-list" style="--active-color:#1D9E75">
      <li>Recursive-descent parser (hand-written)</li>
      <li>Precedence climbing for expressions</li>
      <li>Tensor literal grammar: nested [] lists and numpy</li>
      <li>Function declarations with typed params</li>
      <li>Detailed parse error messages with recovery</li>
    </ul>`
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
    leftContent: `<div class="code-block"><span class="cm">// Pass 1 — Global scope initialization</span>
scopes = [{}]  

<span class="cm">// Statement: X = @[[1,2],[3,4]]</span>
declare("X") → scopes[0]["X"] = False  
resolve(list literal) → no identifiers ✓  
define("X") → scopes[0]["X"] = True ✓  

<span class="cm">// Statement: Y = @[0,1]</span>
declare("Y") → scopes[0]["Y"] = False  
resolve(list literal) → no identifiers ✓  
define("Y") → scopes[0]["Y"] = True ✓  

<span class="cm">// Statement: model = LinearModel()</span>
declare("model") → scopes[0]["model"] = False  

resolve(LinearModel)
  → not found in local scopes → assumed global ✓  
  → resolve_local distance = global  

resolve(call arguments) → none ✓  

define("model") → scopes[0]["model"] = True ✓  

<span class="cm">// Statement: data = X</span>
declare("data") → scopes[0]["data"] = False  

resolve(X)
  → found in scope[0], defined = True ✓  
  → resolve_local distance = 0  

define("data") → scopes[0]["data"] = True ✓  

<span class="cm">// Statement: labels = Y</span>
declare("labels") → scopes[0]["labels"] = False  

resolve(Y)
  → found in scope[0], defined = True ✓  
  → resolve_local distance = 0  

define("labels") → scopes[0]["labels"] = True ✓  

<span class="cm">// Statement: model.train(data, labels)</span>
resolve(model)
  → found in scope[0], defined = True ✓  
  → distance = 0  

resolve(member access: train)
  → object resolved first ✓  

resolve(data)
  → found in scope[0], defined = True ✓  
  → distance = 0  

resolve(labels)
  → found in scope[0], defined = True ✓  
  → distance = 0  

<span class="cm">// Statement: prediction = model.predict(@[5,6])</span>
declare("prediction") → scopes[0]["prediction"] = False  

resolve(model)
  → found in scope[0], defined = True ✓  
  → distance = 0  

resolve(list literal @[5,6]) → no identifiers ✓  

resolve(call predict)
  → callee resolved ✓  

define("prediction") → scopes[0]["prediction"] = True ✓  

<span class="cm">// Statement: print(prediction)</span>
resolve(print)
  → not found in local scopes → assumed global ✓  

resolve(prediction)
  → found in scope[0], defined = True ✓  
  → distance = 0  

<span class="cm">// Final scope state</span>
scope[0] = {
  X: True,
  Y: True,
  model: True,
  data: True,
  labels: True,
  prediction: True
} ✓  
</div>`,
    rightLabel: 'Checks performed',
    rightContent: `<ul class="feat-list" style="--active-color:#D85A30">
      <li>Undefined variable / function detection</li>
      <li>Static tensor shape inference &amp; validation</li>
      <li>Type compatibility for AI ops</li>
      <li>Duplicate declaration errors</li>
      <li>Return type checking in function bodies</li>
      <li>Capture list building for closures</li>
    </ul>`
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
    leftContent: `<div class="code-block"><span class="cm">// Env: global</span>
eval VarDecl "X"
  → <span class="tok">Tensor</span>([[1,2],[3,4]])

eval VarDecl "Y"
  → <span class="tok">Tensor</span>([0,1])

eval VarDecl "model"
  → <span class="fn">LinearModel</span>()

eval Assign "data"
  → X

eval Assign "labels"
  → Y

<span class="cm">// Training phase</span>
eval CallExpr "model.train"
  arg[0] = data   (2×2)
  arg[1] = labels (2×1)
  → <span class="fn">train</span>(...)
  → weights updated

<span class="cm">// Prediction phase</span>
eval CallExpr "model.predict"
  arg[0] = <span class="tok">Tensor</span>([5,6])
  → <span class="fn">forward</span>(...)

<span class="cm">// Output</span>
eval CallExpr "print"
  → Output: [[p]]

</div>`,
    rightLabel: 'Runtime capabilities',
    rightContent: `<ul class="feat-list" style="--active-color:#BA7517">
      <li>Environment chain (scope stack) for variables</li>
      <li>Native tensor ops via built-in op table</li>
      <li>First-class function values &amp; closures</li>
      <li>Lazy short-circuit evaluation (and / or)</li>
      <li>Runtime error reporting with stack trace</li>
      <li>REPL mode: eval single statements interactively</li>
    </ul>`
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
    leftContent: `<div class="code-block"><span class="fn">$ </span> py .\\pulse.py .\\tests\\code.pul<br>
  <span class="cm">Pulse v1.0 — AI-native language</span>
  <span class="str">Interpreting pulse</span><br>
  <span class="kw">Output:</span> Tensor([
    [<span class="num">0.72</span>]
  ])<br>
  <span class="cm">Elapsed: 0.6ms   Peak mem: 1.4 KB</span>
</div>`,
    rightLabel: 'Output modes',
    rightContent: `<ul class="feat-list" style="--active-color:#639922">
      <li>CLI,batch execution</li>
      <li>REPL: pulse repl, interactive prompt</li>
      <li>Tensor pretty-print with shape annotation</li>
      <li>Structured runtime error messages</li>
      <li>Timing &amp; memory stats (--profile flag)</li>
      <li>Exit codes for pipeline integration</li>
    </ul>`
  }
];

const DELAYS = [0, 300, 600, 900, 1200, 1500];

let activeStage = null;
let pipelineRunning = false;

function buildPipeline() {
  const pipe = document.getElementById('pipeline');
  pipe.innerHTML = '';

  STAGES.forEach((s, i) => {
    if (i > 0) {
      const conn = document.createElement('div');
      conn.className = 'connector';
      conn.id = `conn-${i}`;
      conn.innerHTML = `<div class="conn-line"><div class="conn-pulse" id="cpulse-${i}"></div></div><div class="conn-arrow"></div>`;
      pipe.appendChild(conn);
    }
    const el = document.createElement('div');
    el.className = 'stage';
    el.id = `stage-${s.id}`;
    el.style.setProperty('--stage-color', s.color);
    el.style.setProperty('--stage-bg', s.bg);
    el.style.setProperty('--stage-dark', s.dark);
    el.innerHTML = `
      <div class="stage-box">
        <div class="stage-icon">${s.icon}</div>
        <div class="stage-name">${s.name}</div>
        <div class="stage-sub">${s.sub}</div>
      </div>`;
    el.addEventListener('click', () => showDetail(i));
    pipe.appendChild(el);
  });
}

function startPipeline() {
  if (pipelineRunning) return;
  pipelineRunning = true;
  document.getElementById('playBtn').textContent = '⏳ Running…';
  document.getElementById('playBtn').disabled = true;

  STAGES.forEach((s, i) => {
    setTimeout(() => {
      const el = document.getElementById(`stage-${s.id}`);
      el.classList.add('visible');

      if (i > 0) {
        const cp = document.getElementById(`cpulse-${i}`);
        if (cp) {
          cp.classList.add('running');
          setTimeout(() => cp.classList.remove('running'), 1000);
        }
      }

      if (i === STAGES.length - 1) {
        setTimeout(() => {
          pipelineRunning = false;
          document.getElementById('playBtn').textContent = '▶ Run Pipeline';
          document.getElementById('playBtn').disabled = false;
          showDetail(0);
        }, 400);
      }
    }, DELAYS[i]);
  });
}

function resetPipeline() {
  pipelineRunning = false;
  document.getElementById('playBtn').textContent = '▶ Run Pipeline';
  document.getElementById('playBtn').disabled = false;
  STAGES.forEach(s => {
    const el = document.getElementById(`stage-${s.id}`);
    if (el) el.classList.remove('visible', 'active');
  });
  const dp = document.getElementById('detailPanel');
  dp.style.display = 'none';
  activeStage = null;
}

function showDetail(idx) {
  const s = STAGES[idx];

  // deactivate all
  STAGES.forEach(st => {
    const el = document.getElementById(`stage-${st.id}`);
    if (el) el.classList.remove('active');
  });

  const el = document.getElementById(`stage-${s.id}`);
  if (el) el.classList.add('active');

  const dp = document.getElementById('detailPanel');
  const inner = document.getElementById('detailInner');

  dp.style.display = 'block';
  dp.style.setProperty('--active-color', s.color);

  inner.innerHTML = `
    <div class="detail-header">
      <div class="detail-dot" style="background:${s.color}"></div>
      <div>
        <div class="detail-title">${s.title}</div>
        <div class="detail-subtitle">${s.subtitle}</div>
      </div>
    </div>
    <div class="detail-col">
      <h4>${s.leftLabel}</h4>
      ${s.leftContent}
    </div>
    <div class="detail-col">
      <h4>${s.rightLabel}</h4>
      ${s.rightContent}
    </div>
  `;

  activeStage = idx;
}

buildPipeline();