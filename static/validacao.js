function validateForm() {
    var form = document.forms["scheduleForm"];
    for(var i=0; i < form.elements.length; i++) {
        if(form.elements[i].value === "" && form.elements[i].name !== "") {
            alert("Todos os campos devem ser preenchidos");
            return false;
        }
    }
    return true;
}
