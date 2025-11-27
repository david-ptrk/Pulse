const code = `// PULSE Example Program
start:
    let message = "Welcome to PULSE"
    func show(msg) {
        print(msg)
    }
    show(message)
end;`;

let index = 0;
const speed = 25;
const lineDelay = 500; // pause after each line (ms)
const element = document.getElementById("typewriter");

function loopTypewriter() {
    element.textContent = "";
    index = 0;

    function type() {
        if (index < code.length) {
            element.textContent += code.charAt(index);

            // If the next character is a newline, add extra delay
            let delay = speed;
            if (code.charAt(index) === "\n") delay += lineDelay;

            index++;
            setTimeout(type, delay);
        } else {
            setTimeout(loopTypewriter, 1500); // restart after pause
        }
    }

    type();
}

loopTypewriter();
