 // javascript / jquery to submit the ajax form to the flask to add or remove users

    $(document).ready(function () {

        $('#add_user_form').on('submit',function (event) {
                var username = $('#username_add').val();
                jQuery.ajax({
                    data : {
                        group_num: $('#group_id').val(),
                        user_name : username
                    },
                    type : 'POST',
                    url : '/process_group_edit/1'
                }).done(function (data) {
                    // if there is an error
                    if(data.error){
                        alert("Invalid username.");
                    }else if (data.already_mem)
                    {
                        alert("user is already a member in the group");
                    }else{
                        //alert("Group addition sucessfull!");
                        /* to be really cool, we should append it to the div so there
                           isn't a reload. This is what ajax is for.. */
                        var fn = data.f_name;
                        var ln = data.l_name;
                        var un = data.user_name;
                        var em = data.email;

                        var html =  "<div class='row'> <div class='col-3'> <p>"+fn+"</p> </div> <div class='col-3'><p>"+ln+"</p> </div> <div class='col-3'> <p>"+un+"</p> </div> <div class='col-3'> <p>"+em+"</p> </div> </div>"
                        // now append the html to the memberlist div
                        $('#member_list').append(html);
                    }
                });
                event.preventDefault();
        });



         $('#remove_user_form').on('submit',function (event) {
                var username = $('#username_remove').val();
                jQuery.ajax({
                    data : {
                        group_num: $('#group_id').val(),
                        user_name : username
                    },
                    type : 'POST',
                    url : '/process_group_edit/2'
                }).done(function (data) {
                    // if there is an error
                    if(data.error){
                        alert("There was an error processing the request. \nCheck if the inputted username is valid. ");
                    }else{
                        //alert("Group addition sucessfull!");
                        window.location.reload()
                    }
                });
                event.preventDefault();
        });




          $('#group_desc_form').on('submit', function (event) {

                        alert("Function called");
                        event.preventDefault();
          });
    });


