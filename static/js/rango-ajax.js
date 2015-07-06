$(document).ready( function() {

    $('#likes').click(function(){
        var catid;
        catid = $(this).attr("data-catid");
        $.get('/rango/like_category/', {category_id: catid}, function(data){
                   $('#like_count').html(data);
                   $('#likes').hide();
        });
    });
    
    $('#suggestion').keyup(function(){
        var query;
        query = $(this).val();
        actid = $(this).attr("data-actid");
        $.get('/rango/suggest_category/', {suggestion: query, actid: actid}, function(data){
         $('#cats').html(data);
        });
    });

});