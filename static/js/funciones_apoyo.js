/**
 * Created by tania on 11/16/15.
 */

String.prototype.toTitleCase = function () {
    return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
};

//Función para llenar las opciones de un select.
function llenar_select(select_id, list) {
    $(select_id).html("<option value=''>---------</option>");
    $(list).each(function(i) {
        var valor_json = list[i];
        $(select_id).append("<option value='" + valor_json.id + "'>" + valor_json.nombre.toTitleCase() + "</option>");
    });

    $(select_id).trigger('change');
}

//Función para llenar las opciones de un select.
function llenar_select_codigo_punto(select_id, list) {
    $(select_id).html("<option value=''>---------</option>");
    $(list).each(function(i) {
        var valor_json = list[i];
        console.log(valor_json);
        $(select_id).append("<option value='" + valor_json.id + "'>" + valor_json.codigo + "</option>");
    });
}

//Función para llenar las opciones de un select.
function llenar_select_tipo_alimento(select_id, list) {
    $(select_id).html("<option value=''>---------</option>");
    $(list).each(function(i) {
        var valor_json = list[i];
        $(select_id).append("<option value='" + valor_json.id + "'>" + valor_json.descripcion + "</option>");
    });
}

//Función para llenar un select "hijo" dependiendo de lo escogido en otro select "padre"
function llenar_select_hijo_segun_padre(url, padre_id, hijo_id) {
    $(padre_id).on("change", function(){
        var id = $(this).val();
        if(id=="") {
            llenar_select(hijo_id, []);
        }
        else {
            $.getJSON(url.replace(0, id), function(response){
                llenar_select(hijo_id, response);
            });
        }
    });
}