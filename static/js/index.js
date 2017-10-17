var refs;
var mobile = false;
var img_std_width = 1242;
var img_std_height = 2208;

function passRefs(r)
{
  refs = r;
  // console.log(refs);
}

$(document).ready(function()
{
  prepWindow();

  function prepWindow()
  {
    // console.log("DOCUMENT READY");
    var screenWidth = $('body').width();
    var screenHeight = $('body').height();
    console.log(screenWidth);

    // app-screenshot size: 1242x2208
    if (screenWidth < 300)
    {
      $("#info-details").css('width', screenWidth);
    }

    if (screenWidth < 400)
    {
      $("#header-image").css('left', 0);
      $("#header-image").css('width', screenWidth);
      $("#header-image").css('height', screenWidth);
      $("#header-container").css('height', screenWidth);
      $("#info-details").css('width', screenWidth);
    }

    var img_width = (screenWidth / 2) - 15;
    $(".app-screenshot").css('width', img_width);
    $(".app-screenshot").css('margin-left', 10);
    var screenshotHeight = (img_std_height / img_std_width) * img_width

    if (screenWidth < 500)
    {
      mobile = true;
      $(".app-screenshot").css('width', screenWidth);
      $(".app-screenshot").css('margin-left', 0);

      screenshotHeight = (img_std_height / img_std_width) * screenWidth
    }
    // console.log($(".app-screenshot").width());

    // screenshotHeight = $(".app-screenshot").height();
    $("#info-container").css('height', screenshotHeight + 250);

    var footerTop = $("#info-container").height() + $("#header-container").height();
    // $("#footer-container").css('position', 'absolute');
    $("#footer-container").css('margin-top', 70);
  }

  // window.addEventListener("scroll", function ()
  // {
  //
  // }, false);

  window.addEventListener('resize', function()
  {
    prepWindow();
  }, true);

});
