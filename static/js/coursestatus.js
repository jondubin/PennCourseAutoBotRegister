$( ".hide" ).hide();

$(document).ready(function() {
    $.ajax({
        url: 'static/courses.json',
        method: 'get',
        dataType: 'json'
    }).done(function(jdata) {
        var json = jdata;
        json.sort();

        $( ".typeahead" ).keyup(function(e) {
            if (e.which == 13) {
                var value =$( this ).val();
                if (json.indexOf(value) != -1){
                    value = value.replace(/\s/g, '');
                    console.log(value);
                    $.ajax({
                        url: '/closed_status?' + 'courseid=' +  value,
                        method: 'get',
                        dataType: 'text'
                    }).done(function(data) {
                        console.log(data);

                        if (data === "Closed") {
                            $(".hide").hide();
                            $( "#status" ).text("This course is closed.");
                            $( "#status" ).attr('class', 'red');
                            $( "#submit" ).text("Register when open");
                            $( "#explanation" ).text("Would you liked to be auto-registered for the course when it opens?");
                            $( "#explanation" ).hide();
                            $( "#status" ).show();
                        } else {
                            $( "#status" ).text("This course is open.");
                            $( "#status" ).attr('class', 'green');
                            $( "#submit" ).text("Register now");
                            $( "#explanation" ).text("Would you liked to be registered for the course now? \
                                                     Make sure you have an open credit on InTouch \
                                                     and that the course is credit-bearing.");
                            $( ".hide" ).show();
                        }

                    });
                }
            }
        });


        $('.typeahead').autocomplete({
            source: function( request, response ) {
                var matches = $.map( json, function(json) {
                    if ( json.toUpperCase().indexOf(request.term.toUpperCase()) === 0 ) {
                        return json;
                    }
                });
                response(matches.slice(0, 10));
            }
        });
    });
});
