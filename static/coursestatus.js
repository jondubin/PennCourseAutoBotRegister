$( "#courseSearch" ).keyup(function(e) {
    if (e.which == 13) {
        var value =$( this ).val();
        $.ajax({
            url: '/closed_status?' + 'courseid=' +  value,
            method: 'get',
            dataType: 'text'
        }).done(function(data) {
            console.log(data);
        });
    }
});
