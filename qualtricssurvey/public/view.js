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

    // function on_finish(id) {
    //     $.ajax({
    //         type: "POST",
    //         url: runtime.handlerUrl(element, 'end_survey'),
    //         data: JSON.stringify({'survey_status': 'success'}),
    //         success: function(result) {
    //             survey_status.text(result.completed);
    //         }
    //     });
    // }

    var handlerUrl = runtime.handlerUrl(element, 'end_survey');
    console.log("Zach test");
    console.log(handlerUrl);
    // http://ztraboo.ddns.net:18000/courses/course-v1:DEMO+AT-BR101+2020_Fall/xblock/block-v1:DEMO+AT-BR101+2020_Fall+type@qualtricssurvey+block@d35d81284f514885b0181e1c14a27aa0/handler_noauth/end_survey

    // ------------------------------------------------------------------------
    // Attempt 1 

    var waitForEl = function(selector, callback) {
        console.log("$(selector).length = " + $(selector).length);
        if ($(selector).length > 0) {
          callback();
        } else {
          setTimeout(function() {
            console.log("Qualtrics.SurveyEngine – Survey In-Progress 2.")
            waitForEl(selector, callback);
          }, 100);
        }
      };

      function checkIframeLoaded() {
        // Get a handle to the iframe element
        var elementXBlockChildren = element.children;
        if(elementXBlockChildren.length > 0) {
            var iframe = elementXBlockChildren[0].getElementsByTagName("iframe")[0];

            // var iframe = document.getElementById('i_frame');
            // Error was happening iframe.contentWindow.document
            // Security Error – https://stackoverflow.com/questions/25098021/securityerror-blocked-a-frame-with-origin-from-accessing-a-cross-origin-frame
            /*
                DOMException: Blocked a frame with origin "http://localhost:18010" from accessing a cross-origin frame.
    at checkIframeLoaded (http://localhost:18010/xblock/resource/qualtricssurvey/public/view.js:64:76)
            */
            var iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        
            // Check if loading is complete
            if (  iframeDoc.readyState  == 'complete' ) {
                //iframe.contentWindow.alert("Hello");
                iframe.contentWindow.onload = function(){
                    alert("I am loaded");
                };
                // The loading is complete, call the function we want executed once the iframe is loaded
                afterLoading();
                return;
            } 
        }
        
        // If we are here, it is not loaded. Set things up so we check   the status again in 100 milliseconds
        window.setTimeout(checkIframeLoaded, 100);
    }
    
    function afterLoading(){
        alert("I am here");
    }
    
    $(document).ready(function(){
        // $('#survey_ends_here').exists(function(){
        //     if ($('#survey_ends_here').length) {
        //         /*Place your JavaScript here to run when the page is fully displayed*/
        //         console.log("Qualtrics.SurveyEngine – Survey Complete.");
        //     } else {
        //         console.log("Qualtrics.SurveyEngine – Survey In-Progress.")
        //     }
        // });

        checkIframeLoaded();
          // #EndOfSurvey
        //   let elementXBlockChildren = element.children;
        //   if(elementXBlockChildren.length > 0) {
        //       let elementXBlockIframe = elementXBlockChildren[0].getElementsByTagName("iframe");
        //       if(elementXBlockIframe.length > 0) {

        //         // waitForEl(elementXBlockIframe[0].getElementById("EndOfSurvey"), function() {
        //         //     // work the magic
        
        //         //     /*Place your JavaScript here to run when the page is fully displayed*/
        //         //     console.log("Qualtrics.SurveyEngine – Survey Complete.");
        
        //         //   });
        //       }
        //   }
    });

    // ------------------------------------------------------------------------
    // Attempt 2

    // let waitForSomeElement = () => {
    //     const container = document.getElementById('EndOfSurvey'); //survey_ends_here
    //     if (!container) {
    //         setTimeout(waitForSomeElement , 50); // give everything some time to render
    //         console.log("Qualtrics.SurveyEngine – Survey In-Progress.");
    //     }
    //     else {
    //         console.log("Qualtrics.SurveyEngine – Survey Complete.");
    //     }
    // }; 

    // $(document).ready(function(){
    //     // $($element).on('load', function() {
    //         waitForSomeElement();
    //     // });
    // });

    // ------------------------------------------------------------------------
    // Attempt 3
    // https://www.qualtrics.com/community/discussion/14518/embedded-survey-is-there-a-way-to-detect-end-of-survey
    // End of Survey – Hidden End (Library Message)
    /*
       Thanks for taking the time to complete this survey.<br />
       <br />
       &nbsp;
       <div id="survey_ends_here" style="display:none;">End of Survey</div>
    */
    // https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage

    // if (window.addEventListener) {
    //     window.addEventListener("message", onMessage, false);        
    // } 
    // else if (window.attachEvent) {
    //     window.attachEvent("onmessage", onMessage, false);
    // }
    
    // function onMessage(event) {
    //     // Check sender origin to be trusted
    //     // if (event.origin !== "http://example.com") return;
    
    //     var data = event.data;
    
    //     if (typeof(window[data.func]) == "function") {
    //         window[data.func].call(null, data.message);
    //     }
    // }
    
    // // Function to be called from iframe
    // function parentFunc(message) {
    //     console.log(message);
    // }
    // window.addEventListener("message", receiveMessage, false);
    // function receiveMessage(event) {
    //     if(event.data.includes("End of Survey")){
    //         // You stuff here
    //     }
    // }
    // window.addEventListener("message", (event) => {
    //     if (event.origin !== "http://ztraboo.ddns.net:18010")
    //       return;
      
    //     // ...
    //   }, false);
}
