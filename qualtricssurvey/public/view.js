/* eslint-disable no-unused-vars */
/**
 * Initialize the QualtricsSurvey student view
 * @param {Object} runtime - The XBlock JS Runtime
 * @param {Object} element - The containing DOM element for this instance of the XBlock
 * @returns {undefined} nothing
 */
function QualtricsSurveyView(runtime, element) {
    'use strict';

    var $ = window.jQuery;
    var $element = $(element);
    /* eslint-enable no-unused-vars */

    // TODO: Put your logic here

    // To find elements inside your XBlock, try:
    // var myElement = $element.find('.myElement');

    function on_finish(id) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'end_survey'),
            data: JSON.stringify({completed: true}),
            success: function(result) {
                completed_status.text(result.completed);
            }
        });
    }

    // var handlerUrl = runtime.handlerUrl(element, 'end_survey');
    // console.log("Zach test");
    // console.log(handlerUrl);
}
