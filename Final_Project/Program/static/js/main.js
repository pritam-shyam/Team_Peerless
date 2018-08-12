/* run on document load */
$(document).ready(function() {
    /* get pathname */
    var pathname = window.location.pathname;
    /* assign active class to menu nav */
    $('.nav  li a[href="'+pathname+'"]').parent().addClass('active');
    /* init nav searbar */
    $(".searchbar").select2();
    /* nav searchbar on click */
    $(".searchbar").on("select2:select", function(e){
        console.log(e.params.data.id)
        ticker = e.params.data.id;
        window.location.href = "http://localhost:8080/stock/"+ticker;
    });
});
