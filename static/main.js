$(document).ready(function() 
{
    $("form").on("submit", function(event) {
        event.preventDefault();
        $.ajax({
            url: '/schedule',
            type: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                $(".form-container").html('<h1>Agendamento Automático de Turnos</h1><p class="alert alert-success mt-3" style="background: transparent;">'+response+'</p>');
            },
            error: function(error) {
                $(".form-container").html('<h1>Agendamento Automático de Turnos</h1><p class="alert alert-danger mt-3" style="background: transparent;">'+error.responseText+'</p>');
            }
        });
    });
});
