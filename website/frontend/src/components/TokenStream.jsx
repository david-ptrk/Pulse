const TOKENS = [
    ['IDENTIFIER', 'X', '#1D9E75', '#E1F5EE'],
    ['ASSIGN', '=', '#888780', '#F1EFE8'],
    ['TENSOR', '@', '#7F77DD', '#EEEDFE'],
    ['LEFT_BRACKET', '[', '#888780', '#F1EFE8'],
    ['LEFT_BRACKET', '[', '#888780', '#F1EFE8'],
    ['NUMBER', '1', '#BA7517', '#FAEEDA'],
    ['COMMA', ',', '#888780', '#F1EFE8'],
    ['NUMBER', '2', '#BA7517', '#FAEEDA'],
    ['RIGHT_BRACKET', ']', '#888780', '#F1EFE8'],
    ['COMMA', ',', '#888780', '#F1EFE8'],
    ['LEFT_BRACKET', '[', '#888780', '#F1EFE8'],
    ['NUMBER', '3', '#BA7517', '#FAEEDA'],
    ['COMMA', ',', '#888780', '#F1EFE8'],
    ['NUMBER', '4', '#BA7517', '#FAEEDA'],
    ['RIGHT_BRACKET', ']', '#888780', '#F1EFE8'],
    ['RIGHT_BRACKET', ']', '#888780', '#F1EFE8'],
    ['NEWLINE', '\\n', '#D85A30', '#FAECE7'],
    
    ['IDENTIFIER', 'Y', '#1D9E75', '#E1F5EE'],
    ['ASSIGN', '=', '#888780', '#F1EFE8'],
    ['TENSOR', '@', '#7F77DD', '#EEEDFE'],
    ['LEFT_BRACKET', '[', '#888780', '#F1EFE8'],
    ['NUMBER', '0', '#BA7517', '#FAEEDA'],
    ['COMMA', ',', '#888780', '#F1EFE8'],
    ['NUMBER', '1', '#BA7517', '#FAEEDA'],
    ['RIGHT_BRACKET', ']', '#888780', '#F1EFE8'],
    ['NEWLINE', '\\n', '#D85A30', '#FAECE7'],
    
    ['IDENTIFIER', 'model', '#1D9E75', '#E1F5EE'],
    ['ASSIGN', '=', '#888780', '#F1EFE8'],
    ['IDENTIFIER', 'LinearModel', '#1D9E75', '#E1F5EE'],
    ['LEFT_PAREN', '(', '#888780', '#F1EFE8'],
    ['RIGHT_PAREN', ')', '#888780', '#F1EFE8'],
    ['NEWLINE', '\\n', '#D85A30', '#FAECE7'],
    
    ['IDENTIFIER', 'data', '#1D9E75', '#E1F5EE'],
    ['ASSIGN', '=', '#888780', '#F1EFE8'],
    ['IDENTIFIER', 'X', '#1D9E75', '#E1F5EE'],
    ['NEWLINE', '\\n', '#D85A30', '#FAECE7'],
    
    ['IDENTIFIER', 'labels', '#1D9E75', '#E1F5EE'],
    ['ASSIGN', '=', '#888780', '#F1EFE8'],
    ['IDENTIFIER', 'Y', '#1D9E75', '#E1F5EE'],
    ['NEWLINE', '\\n', '#D85A30', '#FAECE7'],
    
    ['IDENTIFIER', 'model', '#1D9E75', '#E1F5EE'],
    ['DOT', '.', '#7F77DD', '#EEEDFE'],
    ['IDENTIFIER', 'train', '#1D9E75', '#E1F5EE'],
    ['LEFT_PAREN', '(', '#888780', '#F1EFE8'],
    ['IDENTIFIER', 'data', '#1D9E75', '#E1F5EE'],
    ['COMMA', ',', '#888780', '#F1EFE8'],
    ['IDENTIFIER', 'labels', '#1D9E75', '#E1F5EE'],
    ['RIGHT_PAREN', ')', '#888780', '#F1EFE8'],
    ['NEWLINE', '\\n', '#D85A30', '#FAECE7'],
    
    ['IDENTIFIER', 'prediction', '#1D9E75', '#E1F5EE'],
    ['ASSIGN', '=', '#888780', '#F1EFE8'],
    ['IDENTIFIER', 'model', '#1D9E75', '#E1F5EE'],
    ['DOT', '.', '#7F77DD', '#EEEDFE'],
    ['IDENTIFIER', 'predict', '#1D9E75', '#E1F5EE'],
    ['LEFT_PAREN', '(', '#888780', '#F1EFE8'],
    ['TENSOR', '@', '#7F77DD', '#EEEDFE'],
    ['LEFT_BRACKET', '[', '#888780', '#F1EFE8'],
    ['NUMBER', '5', '#BA7517', '#FAEEDA'],
    ['COMMA', ',', '#888780', '#F1EFE8'],
    ['NUMBER', '6', '#BA7517', '#FAEEDA'],
    ['RIGHT_BRACKET', ']', '#888780', '#F1EFE8'],
    ['RIGHT_PAREN', ')', '#888780', '#F1EFE8'],
    ['NEWLINE', '\\n', '#D85A30', '#FAECE7'],
    
    ['IDENTIFIER', 'print', '#1D9E75', '#E1F5EE'],
    ['LEFT_PAREN', '(', '#888780', '#F1EFE8'],
    ['IDENTIFIER', 'prediction', '#1D9E75', '#E1F5EE'],
    ['RIGHT_PAREN', ')', '#888780', '#F1EFE8'],
]

function TokenStream() {
    return (
        <div className="token-list">
            {TOKENS.map(([type, value, color, background], index) => (
                <span
                    className="token-pill"
                    key={`${type}-${value}-${index}`}
                    style={{
                        backgroundColor: background,
                        borderColor: color,
                        color,
                    }}
                >
                    <span className="token-type">{type}</span>
                    <strong>{value}</strong>
                </span>
            ))}
        </div>
    )
}

export default TokenStream
