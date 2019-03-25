function logout() {
    if (confirm('Logout?')) {
        $.ajax({
            url: $$._root + '/logout/',
            success: function () {
                window.location.reload();
            }
        })
    }
}

function send_cmd(name, params) {
    $.ajax({
        url: $$._root + '/host/cmd/',
        method: 'post',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({name: name, params: params}),
        success: function () {
            var modal = $$.alertModal({
                msg:'Command send ...',
                caption:'Close',
                action:function () {
                    clearInterval(timer);
                    $("#ajax_status").addClass('ERROR').html('Cancelled');
                },
                action_on_close:true
            });
            var timer = setInterval( function () {
                $.ajax({
                    url: $$._root + '/host/cmd_waiting/',
                    success: function (response) {
                        console.log(response);
                        if (response=='0') {
                            modal.close();
                            window.location.reload(true);
                        }
                    }
                })
            }, 1000);
        }
    })
}

function msg_read(msg_ids) {
    $.ajax({
        url: $$._root + '/host/msg_read/',
        method: 'post',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({msg_ids: msg_ids}),
        success: function () {
            setInterval( window.location.reload(true), 1000);
        }
    })
}

