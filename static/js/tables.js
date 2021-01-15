/**
 * Created by german on 17/03/16.
 */

function tabla (url) {
    $('#table').bootgrid({
        caseSensitive: false,
        labels:{
            all:"Todos",
            loading:"Cargando...",
            noResults:"No se encontraron Resultados!",
            refresh:"Refrescar",
            search:"Buscar",
        },
         formatters: {
            "commands": function(column, row) {
                console.log(url);
                return "<button type=\"button\" class=\"btn btn-primary btn-xs btn-default command-edit\" data-row-id=\"" + row.id + "\" onClick=\"window.location.href='" + url.replace(0,row.id) + "'\"><span class=\"fa fa-pencil\"></span></button> "
            }
        }
    })
}