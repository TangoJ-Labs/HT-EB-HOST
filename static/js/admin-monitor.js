var refs;
var vars;

function passRefs(r)
{
  refs = r;
  // console.log(refs['endpoint_admin_modify']);
}
function passVars(v)
{
  vars = v;
  // console.log(vars['code']);
}

$(document).ready(function()
{
  var monthNames = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  // Convert all timestamps to local datetime
  var datetimeElements = document.getElementsByClassName('content-datetime');
  var datetimeElementsArray = Array.prototype.slice.call(datetimeElements);
  for(var i = 0; i < datetimeElementsArray.length; i++)
  {
    var timestamp = datetimeElementsArray[i].textContent;
    var datetime = formatTimestamp(timestamp);
    datetimeElementsArray[i].textContent = datetime;
  };

  $('.content-button').on('click', function(event)
  {
    contentAction(event);
  });

  function contentAction(event)
  {
    var contentID = event.target.getAttribute('data-content-id');
    if (contentID != null)
    {
      var buttonType = event.target.getAttribute('data-button-type')
      if (buttonType != null)
      {
        if (buttonType == 'release')
        {
          // console.log('RELEASE: ' + contentID);
          grabAction('active', contentID);
          $('#content-container-' + contentID).remove();
        }
        else if (buttonType == 'delete')
        {
          // console.log('DELETE: ' + contentID);
          grabAction('delete', contentID);
          $('#content-container-' + contentID).remove();
        }
      }
    }
  }

  // Function to delete a Grab
  function grabAction(status, contentID)
  {
    var xhrFS = new XMLHttpRequest();
    xhrFS.open('POST', refs['endpoint_admin_update_spot_content'], true);
    xhrFS.setRequestHeader("Content-Type", "application/json");
    xhrFS.send(JSON.stringify({
      'user_id': ""
      , 'content_id': contentID
      , 'status': status
    }));
    // console.log(xhrFS);
    xhrFS.onreadystatechange = function()
    {
      if (xhrFS.readyState == XMLHttpRequest.DONE)
      {
        // console.log(xhrFS);
        console.log(xhrFS.responseText);
        if (xhrFS.responseText != 'success')
        {
          alert(xhrFS.responseText);
        }
      }
    }
  }

  function formatTimestamp(timestamp)
  {
    // Format the timestamp
    var date = new Date(timestamp * 1000);
    var month = monthNames[date.getMonth()];
    var day = date.getDate();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var period = "am";
    if (hours == 0)
    {
      // First, ensure that midnight is shown as 12
      hours = 12;
    }
    else if (hours == 12)
    {
      // Second, set the pm period if within the noon hour
      period = "pm";
    }
    else if (hours > 12)
    {
      // Lastly, convert all 24-hour pm times to 12-hour times
      hours = hours - 12;
      period = "pm";
    }
    var formattedTimestamp = month + ' ' + day + ', ' + hours + ":" + String("0" + minutes).slice(-2) + period;
    return formattedTimestamp
  }

});
