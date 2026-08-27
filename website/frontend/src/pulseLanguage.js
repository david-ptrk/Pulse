import { StreamLanguage } from '@codemirror/language'

const pulseLanguage = StreamLanguage.define({
    token(stream) {
        // Whitespace
        if (stream.eatSpace()) {
            return null
        }
        
        // Comments
        if (stream.match(/^#.*/)) {
            return 'comment'
        }
        
        // Tensor prefix
        if (stream.match(/^@/)) {
            return 'keyword'
        }
        
        // Numbers
        if (stream.match(/^\d+(\.\d+)?/)) {
            return 'number'
        }
        
        // Strings
        if (stream.match(/^"(?:[^"\\]|\\.)*"/)) {
            return 'string'
        }
        
        if (stream.match(/^'(?:[^'\\]|\\.)*'/)) {
            return 'string'
        }
        
        // Keywords
        if (
            stream.match(
                /^(def|return|if|else|for|while|break|continue|and|or|not|True|False|None)\b/
            )
        ) {
            return 'keyword'
        }
        
        // AI / ML types
        if (
            stream.match(
                /^(LinearModel|LogisticModel|Tensor|Matrix)\b/
            )
        ) {
            return 'typeName'
        }
        
        // Function calls
        if (stream.match(/^[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()/)) {
            return 'function'
        }
        
        // Identifiers
        if (stream.match(/^[a-zA-Z_][a-zA-Z0-9_]*/)) {
            return 'variableName'
        }
        
        // Operators
        if (stream.match(/^(==|!=|<=|>=|=>|\+|-|\*|\/|%|=|<|>)/)) {
            return 'operator'
        }
        
        // Punctuation
        if (stream.match(/^[()[\]{},.:]/)) {
            return 'punctuation'
        }
        
        stream.next()
        return null
    },
    
    startState() {
        return {}
    },
})

export default pulseLanguage
