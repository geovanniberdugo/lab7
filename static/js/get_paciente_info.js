/**
 * Created by tania on 2/10/16.
 */
function get_paciente_info(url){
    $('#id_paciente-identificacion').focusout(function(){
        if(!$('#id_paciente-sin_identificacion').prop('checked')){
            var id = $(this).val();
            $.getJSON(url.replace(0, id), function(response){
                console.log(response);
                if(response != null)
                {
                    var paciente = response;
                    $('#id_paciente-tipo_identificacion').val(paciente.tipo_identificacion).select2();
                    $('#id_paciente-nombre').val(paciente.nombre);
                    $('#id_paciente-apellido').val(paciente.apellido);
                    $('#id_paciente-edad').val(paciente.edad);
                    $('#id_paciente-tipo_edad').val(paciente.tipo_edad).select2();
                    $('#id_paciente-direccion').val(paciente.direccion);
                    $('#id_paciente-eps').val(paciente.eps).select2();
                    $('#id_paciente-sexo').val(paciente.sexo).select2();
                    $('#usuario_nuevo').css("display","none"); //Oculta el div de Usuario Nuevo
                }
            })
            .fail(function(jqxhr, textStatus, error){
                $('#id_paciente-tipo_identificacion').val("").select2();
                $('#id_paciente-nombre').val("");
                $('#id_paciente-apellido').val("");
                $('#id_paciente-edad').val("");
                $('#id_paciente-tipo_edad').val("").select2();
                $('#id_paciente-direccion').val("");
                $('#id_paciente-eps').val("").select2();
                $('#id_paciente-sexo').val("").select2();
                $('#usuario_nuevo').css("display","block"); //Muestra el div de Usuario Nuevo
            });
        }
    });
}

function sin_identificar(click, tag){
    if($('#id_' + tag + '-tipo_identificacion').val()=="NN" && !click){
        $('#id_' + tag + '-sin_identificacion').prop('checked', true);
    }

    if($('#id_' + tag + '-sin_identificacion').prop('checked')){
            $('#id_' + tag + '-identificacion').val("-------").attr('readonly', true);
            $('#id_' + tag + '-tipo_identificacion').val("NN").trigger('change').prop('disabled', true);
            $('#p-tipo-id').append('<input type="hidden" name="' + tag + '-tipo_identificacion" id="hidden-tipo_identificacion" value="NN" />')
        }
        else{
            $('#id_' + tag + '-identificacion').attr('readonly', false);
            $('#id_' + tag + '-tipo_identificacion').prop('disabled', false);
            $('#hidden-tipo_identificacion').remove();
        }
}

$(document).ready(function(){
    
    sin_identificar(false);

    $('#id_paciente-sin_identificacion').click(function(){
        console.log($(this).prop('checked'));
        
        sin_identificar(true, 'paciente');
    });

    $('#id_eeid-sin_identificacion').click(function(){
        console.log($(this).prop('checked'));
        
        sin_identificar(true, 'eeid');
    });
});