var socket;
$(document).ready(function(){
	$('#a-signup').click(function(){
		$.get(
			'/account/signup',
			function(data){
		    	$('#modal-container').html(data);
		    	$('#modal-signup').modal('show');
		});
	});

	$('#a-login').click(function(){
		$.get(
			'/account/login',
			function(data){
		    	$('#modal-container').html(data);
		    	$('#modal-login').modal('show');
		});
	});

	socket = io.connect('localhost', {port: 4000});

	socket.on('connect', function(){
	});

	socket.on('message', function(response) {
		resp = $.parseJSON(response);
		data = resp['data'];
		commentDiv = $(resp['div_id']);
		$(data).attr("jquery_workaround","sigh").hide().appendTo(commentDiv);
		var newstuff = commentDiv.find("[jquery_workaround=sigh]");
		newstuff.removeAttr("jquery_workaround").show("slow");
	});
});

function showErrors(formID, data){
	$('#' + formID).find('input').each(function(){
		var inputName = ($(this).attr('name'));
		if(inputName != 'csrfmiddlewaretoken'){
			$(this).parent().parent().removeClass('success');
			$(this).next('.help-inline').remove();
			if(inputName in data){
				var $span = $("<span class='help-inline small'>" + data[inputName] + "</span>").hide();
				$(this).parent().parent().addClass('error');
				$(this).after($span);
				$span.fadeIn(1000)
			}
			else {
				$(this).parent().parent().addClass('success');
				$(this).parent().parent().removeClass('error');
			}
		}
	});
}

function disableButton(buttonElement){
	$(buttonElement).text('Loading...');
	$(buttonElement).attr('disabled', 'disabled');
}

function enableButton(buttonElement, text){
	$(buttonElement).text(text);
	$(buttonElement).removeAttr('disabled');
}


/*********************************************************/
/*                       Ajax Login                      */
/*********************************************************/
$(document).on('submit', '#ajax-login-form', function(event){
	event.preventDefault();
	var formData = $(this).serialize();
	var formID = $(this).attr('id');
	var buttonElement = $('#' + formID + ' button');
	disableButton(buttonElement);
	$.post(
		'/account/login',
		formData,
		function(data){
			$('#login-error').addClass('hidden');
			if (data == 'success'){
				window.location.replace('/');
			}
			else if ('error' in data){
				$('#login-error').removeClass('hidden');
			}
			else {
				showErrors(formID, data);
			}
			enableButton(buttonElement, 'Sign in');
		}
	)
});


/*********************************************************/
/*                       Ajax Signup                     */
/*********************************************************/
$(document).on('submit', '#signup-form', function(event){
	event.preventDefault();
	var formData = $(this).serialize();
	var formID = $(this).attr('id');
	var buttonElement = $('#' + formID + ' button');
	disableButton(buttonElement);
	$.post(
		'/account/signup',
		formData,
		function(data){
			if (data != 'success'){
				showErrors(formID, data);
			}
			else {
				window.location.replace('/');
			}
			// enableButton(buttonElement, 'Sign up');
		}
	)
});


$(document).on('submit', '#update-profile-form', function(event){
	event.preventDefault();
	var formData = $(this).serialize();
	var formID = $(this).attr('id');
	var buttonElement = $('#' + formID + ' button');
	disableButton(buttonElement);
	$.post(
		'/account/settings',
		formData,
		function(data){
			if (data != 'success'){
				showErrors(formID, data);
			}
			enableButton(buttonElement, 'Save');
		}
	)
});


/*********************************************************/
/*                    Ajax Create Hashtag                */
/*********************************************************/
$(document).on('submit', '#ajax-create-hashtag', function(event){
    event.preventDefault();
    var formData = $(this).serialize();
    $(this).trigger('reset');
    $.post(
        '/hashtag/create',
        formData,
        function(data){
            var target = $('.hashtag-feed');
            $(data).attr("jquery_workaround","sigh").hide().prependTo(target);
            var newstuff = target.find("[jquery_workaround=sigh]");
            newstuff.removeAttr("jquery_workaround").show("slow");
        }
    )
});


/*********************************************************/
/*                    Ajax Create Comment                */
/*********************************************************/
$(document).on('submit', '.ajax-comment-form', function(event){
    event.preventDefault();
    var commentDiv = $(this).parent().parent().prev();
    formData = {
        'comment': $(this).find('input[name=comment]').val(),
        'hashtag_id': $(this).parent().attr('data-id')
    }
	$(this).trigger('reset');
	socket.emit('send_message', formData, function(data){
		console.log(data);
	});
});


/*********************************************************/
/*                        Ajax Votes                     */
/*********************************************************/
$(document).on('click', '.vote', function(event){
	event.preventDefault();
	var $postDiv = $(this).parent();
	formData = {
		'id': $postDiv.attr('data-id'),
		'mode': $(this).attr('name')
	}

	$.get(
		'/hashtag/vote/',
		formData,
		function(response){
			if (response['success'])
				$postDiv.find('.votes').html(response['votes']);
			else {
				if (response['unauthenticated'])
					alert('You must login to vote.');
			}
		}
	)
});