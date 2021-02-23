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

    var survey_status = $('.qualtricssurvey_block .qualtrics-message .survey-status');

    function on_finish(id) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'end_survey'),
            data: JSON.stringify({'survey_status': 'success'}),
            success: function(result) {
                survey_status.text(result.completed);
            }
        });
    }

    var handlerUrl = runtime.handlerUrl(element, 'end_survey');
    console.log("Zach test");
    console.log(handlerUrl);
    // http://ztraboo.ddns.net:18000/courses/course-v1:DEMO+AT-BR101+2020_Fall/xblock/block-v1:DEMO+AT-BR101+2020_Fall+type@qualtricssurvey+block@d35d81284f514885b0181e1c14a27aa0/handler_noauth/end_survey


}
