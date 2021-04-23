

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
  
  var earned_score_html = $('.qualtricssurvey_block .qualtrics-message .grade .earned_score')
  var max_score_html = $('.qualtricssurvey_block .qualtrics-message .grade .max_score')
  var status_html = $('.qualtricssurvey_block .qualtrics-message .grade .status')
  
  var handlerUrl = runtime.handlerUrl(element, 'get_survey_status');

    function updateView(event) {
      setTimeout(function() { 
        $.ajax({
          method: "POST",
          url: handlerUrl,
          data: JSON.stringify({}),
          success: function (data) {
            if (data.survey_status == "Complete") {
              $element.find(earned_score_html).text(data.earned_score)
              $element.find(max_score_html).text(data.max_score)
              $element.find(status_html).text("Graded")
            }
            else {
              updateView()
            }
          }
        });
      }, 3000)
    }

    updateView();
  }
