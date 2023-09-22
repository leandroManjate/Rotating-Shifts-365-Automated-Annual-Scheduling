let tempoTrabalho = 0;
let cronometro;
let tempoAlertaTrabalho = 60; // 1 minute
let tempoAlertaDescanso = 30; // 30 seconds
let descanso = false;

let inicioTrabalho;
let fimTrabalho;

function iniciarCronometro() {
    let inicioInput = document.getElementById('inicioTrabalho').value.split(':');
    inicioTrabalho = new Date();
    inicioTrabalho.setHours(inicioInput[0], inicioInput[1], 0); // 9h00

    let fimInput = document.getElementById('fimTrabalho').value.split(':');
    fimTrabalho = new Date();
    fimTrabalho.setHours(fimInput[0], fimInput[1], 0); // 17h00

    cronometro = setInterval(function() {
        let agora = new Date();

        if (agora < inicioTrabalho || agora > fimTrabalho) {
            pararCronometro();
            alert("Está fora do horário de trabalho. O cronômetro irá parar.");
            return;
        }

        tempoTrabalho++;
        let segundos = tempoTrabalho % 60;
        let minutos = Math.floor(tempoTrabalho / 60) % 60;
        let horas = Math.floor(tempoTrabalho / 3600);
        document.getElementById('tempoTrabalho').innerText = `${horas.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`;

        if (!descanso && tempoTrabalho >= tempoAlertaTrabalho) {
            descanso = true;
            tempoTrabalho = 0;
            alert("Hora de descansar! Recomendamos que você se alongue e beba água.");
        } else if (descanso && tempoTrabalho >= tempoAlertaDescanso) {
            descanso = false;
            tempoTrabalho = 0;
            alert("O tempo de descanso acabou! Volte ao trabalho.");
        }
    }, 1000);
}

function pararCronometro() {
    clearInterval(cronometro);
    descanso = false;
    tempoTrabalho = 0;
    document.getElementById('tempoTrabalho').innerText = '00:00:00';
}
