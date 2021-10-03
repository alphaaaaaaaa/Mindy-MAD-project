
const endpoint = '/newsfeed/'
const delay_by_in_ms = 700
let scheduled_function = false

let ajax_call = function (endpoint, request_parameters) {
	$.getJSON(endpoint, request_parameters)
		.done(response => {
			
			// fade out the artists_div, then:
			$('.replaceable-content'+response['type']).fadeTo('slow', 0).promise().then(() => {
				// replace the HTML contents
				$('.replaceable-content'+response['type']).html(response['html_from_view'])
				// fade-in the div with new contents
				$('.replaceable-content'+response['type']).fadeTo('slow', 1)
				// stop animating search icon
				$('.search-icon').removeClass('blink')
			})
		})
}

$(document).ready(function () {
	$(".user-input").on('keyup', function () {

	const request_parameters = {
		q: $(this).val(),
		type:'user-search' // value of user_input: the HTML element with ID user-input
	}

	// start animating the search icon with the CSS class
	$('.search-icon').addClass('blink')

	// if scheduled_function is NOT false, cancel the execution of the function
	if (scheduled_function) {
		clearTimeout(scheduled_function)
	}

	// setTimeout returns the ID of the function to be executed
	scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters,type='chat-search')
})
})
$(document).ready(function () {
	$(".chat-user-input").on('keyup', function () {
    
	const request_parameters = {
		q: $(this).val(), // value of user_input: the HTML element with ID user-input
		type:'chat-search'
	}

	// start animating the search icon with the CSS class
	$('.search-icon').addClass('blink')

	// if scheduled_function is NOT false, cancel the execution of the function
	if (scheduled_function) {
		clearTimeout(scheduled_function)
	}

	// setTimeout returns the ID of the function to be executed
	scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})
})
$(document).ready(function () {
	$(".chat-group-input").on('keyup', function () {
    
	const request_parameters = {
		q: $(this).val(), // value of user_input: the HTML element with ID user-input
		type:'chat-group-search'
	}

	// start animating the search icon with the CSS class
	$('.search-icon').addClass('blink')

	// if scheduled_function is NOT false, cancel the execution of the function
	if (scheduled_function) {
		clearTimeout(scheduled_function)
	}

	// setTimeout returns the ID of the function to be executed
	scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters,type='chat-group')
})
})