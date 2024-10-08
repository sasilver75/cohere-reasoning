let currentIndex = 0;
let data = [];

function loadData() {
    fetch('/data')
        .then(response => response.json())
        .then(jsonData => {
            data = jsonData;
            displayRecord(currentIndex);
        })
        .catch(error => console.error('Error:', error));
}

function renderLatex(text) {
    return text
        .replace(/\$\$(.*?)\$\$/g, '\\[$1\\]')
        .replace(/\$(.*?)\$/g, '\\($1\\)')
        .replace(/\n/g, '<br>')
        .replace(/\\n/g, '<br>');
}

function displayRecord(index) {
    const record = data[index];
    document.getElementById('id').textContent = record.id;
    document.getElementById('question').innerHTML = renderLatex(record.question);
    document.getElementById('stepped').innerHTML = renderLatex(record.stepped);
    document.getElementById('perturbed').innerHTML = renderLatex(record.perturbed);
    document.getElementById('step').textContent = record.step;
    document.getElementById('type').textContent = record.type;
    document.getElementById('trace').textContent = record.trace;
    document.getElementById('completion').innerHTML = renderLatex(record.completion);
    document.getElementById('current-record').textContent = `Record ${index + 1} of ${data.length}`;
    MathJax.typesetPromise();
}

document.getElementById('prev').addEventListener('click', () => {
    if (currentIndex > 0) {
        currentIndex--;
        displayRecord(currentIndex);
    }
});

document.getElementById('next').addEventListener('click', () => {
    if (currentIndex < data.length - 1) {
        currentIndex++;
        displayRecord(currentIndex);
    }
});

window.onload = loadData;