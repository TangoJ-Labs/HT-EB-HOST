var appVersion = '2.0.0';

var refs;
var spots;
var map;
var mobile = false;

var allSpots = [];
var filteredSpots = [];
var allSpotRequests = [];
var filteredSpotRequests = [];
var allHazards = [];
var filteredHazards = [];
var allStructures = [];
var filteredStructures = [];
var allRepairs = [];
var lastStructureRepairs = [];

var spotMarkers = [];
var spotCircles = [];
var spotRequestMarkers = [];
var hazardMarkers = [];
var structureMarkers = [];

var repairSettings = [];
var userSkills = [];
var skillLevels = {};
var skillTypes = {};

// USER DATA
var userId = '';
var facebookId = '';
var facebookName = '';
var cognitoId = '';
var serverToken = '';
var previouslyLoggedIn = false;
var showTutorial = true;

var downloadingStructures = false;
var downloadingSpots = false;
var downloadingHazards = false;

var menuToggle = false;
var menuTrafficToggle = false;
var menuStructureToggle = false;
var menuSpotToggle = false;
var menuHazardToggle = false;
var spotToggle = false;
var structureToggle = false;
var repairToggle = false;
var profileToggle = false;

// Track if a map item is clicked to prevent normal map events from overriding item events
var circleClick = false;
var markerClick = false;
var structureClick = false;

var structureMatch = false;

// Store the last item clicked to ensure other data is not displayed
var lastSpotSelected = '';
var lastStructureSelected = {};
var lastRepairSelected = {};

// Store the link for the user image for the latest Structure selected
var lastStructureSelectedUserLink = '';

var secondsDay = 60 * 60 * 24;
var secondsWeek = secondsDay * 7;
var secondsMonth = secondsDay * 30;
var secondsYear = secondsDay * 365;
var menuFilterSetting = 3; // Defaults to "Past Month"
var menuFilterSeconds = secondsMonth; // Defaults to "Past Month"

var mapZoomToggleSpotMarkers = 15;

var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

// console.log('MAP JS - PRE');

function passRefs(r)
{
  refs = r;
  // console.log(refs);
}
function passSpots(s)
{
  spots = s;
  // console.log(spots);
}

function createMarker(width, height, radius, color)
{
  var canvas, context;
  canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;

  context = canvas.getContext("2d");
  context.beginPath();
  context.arc(width / 2, height / 2, radius, 0, 2 * Math.PI, false);
  context.fillStyle = color;
  context.fill();
  context.lineWidth = 1;
  context.strokeStyle = color;
  context.globalAlpha = 0.4
  context.stroke();

  return canvas.toDataURL();
}


// TUTORIAL FUNCTIONS

function sleep(ms)
{
  return new Promise(resolve => setTimeout(resolve, ms));
}
async function bannerReturn()
{
  // console.log("BANNER RETURN");
  await sleep(3000);
  $('#banner').animate({
    'top': '-50px'
  }, 700);
}
async function tutorialMain()
{
  // console.log("SHOW TUTORIAL");
  await sleep(2000);
  $('#banner').animate({
    'top': '0px'
  }, 700, function()
  {
    bannerReturn();
  });
}
async function structureUserTutorialReturn()
{
  // console.log("STRUCT USER RETURN");
  await sleep(3000);
  $('#structure-user-tutorial').animate({
    'width': '50px'
  }, 700, function()
  {
    $('#structure-user-tutorial-text').css('visibility', 'hidden');
  });
}
async function structureUserTutorialMain()
{
  // console.log("SHOW STRUCT USER TUTORIAL");
  await sleep(2000);
  $('#structure-user-tutorial').animate({
    'width': '170px'
  }, 700, function()
  {
    $('#structure-user-tutorial-text').css('visibility', 'visible');
    structureUserTutorialReturn();
  });
}
function tutorialScreen()
{
  var click = 0;
  $('#tutorial-screen').css('visibility', 'visible');
  $('#tutorial-main-text').css('visibility', 'visible');
  $('#tutorial-screen').click(function()
  {
    // console.log("TUTORIAL SCREEN CLICKED");
    if (click == 0)
    {
      $('#tutorial-main-text').css('visibility', 'hidden');
      $('#tutorial-menu-text').css('visibility', 'visible');
      click += 1;
    }
    else if (click == 1)
    {
      $('#tutorial-menu-text').css('visibility', 'hidden');
      $('#tutorial-profile-text').css('visibility', 'visible');
      click += 1;
    }
    else if (click == 2)
    {
      $('#tutorial-profile-text').css('visibility', 'hidden');
      $('#tutorial-screen').css('visibility', 'hidden');
      tutorialMain();
      click = 0;
    }
  });
}

// COGNITO FUNCTIONS
function cognitoLogin(fbResponse)
{
  // console.log('FB LOGIN AUTH IN PROCESS');
  // console.log(fbResponse);
  FB.api('/me', function(apiResponse)
  {
    // console.log(apiResponse);
    // Store the token for secure access temporarily
    serverToken = fbResponse.authResponse.accessToken;
    // serverTokenExpiresAt = (Date.now() / 1000) + loginResponse.authResponse.expiresIn;

    // Save the user profile name
    facebookName = apiResponse.name
    $('#profile-name').text(facebookName);

    // Request Cognito credentials to perform secure requests
    requestCognitoCredentials(fbResponse.authResponse.userID, serverToken);
  });
}

function initMap()
{
  console.log('MAP JS - MAP INIT');
  map = new google.maps.Map(document.getElementById('map'),
  {
    center: {lat: 29.758624, lng: -95.366795},
    zoom: 8,
    zoomControl: true,
    mapTypeControl: false,
    scaleControl: false,
    streetViewControl: false,
    rotateControl: true,
    fullscreenControl: false
  });

  map.addListener('zoom_changed', function()
  {
    // console.log(map.getZoom());
    // Only check the zoom if the Spot Markers are toggled on
    if (menuSpotToggle)
    {
      // If the map zoom is "mapZoomToggleSpotMarkers" or greater, remove the Spot markers (the circles are large enough to see)
      if (map.getZoom() >= mapZoomToggleSpotMarkers)
      {
        spotMarkersMapNull();
      }
      else if (map.getZoom() < mapZoomToggleSpotMarkers)
      {
        spotMarkersMapSet();
      }
    }
  });

  // // Add the Spots to the map
  // addSpots();

  $(document).ready(function()
  {
    // console.log('MAP JS - DOC READY');
    $("#menu-toggle-traffic").css("background-image", 'url("img/icons/icon_traffic.png")');
    $("#menu-toggle-structures").css("background-image", 'url("img/markers/marker_icon_structure.svg")');
    $("#menu-toggle-spots").css("background-image", 'url("img/markers/marker_icon_camera_yellow.svg")');
    $("#menu-toggle-hazards").css("background-image", 'url("img/icons/icon_hazard.svg")');
    $(".menu-toggle-check").css("background-image", 'url("img/icons/icon_check_orange.png")');
    $(".menu-filter-check").css("background-image", 'url("img/icons/icon_check_orange.png")');

    // Set the default menu filter check mark as visible
    $('#menu-filter-check-' + menuFilterSetting).css('visibility', 'visible');

    // Request the default data
    requestSpots();
    requestHazards();
    requestStructures();

    // Initialize FB
    window.fbAsyncInit = function()
    {
      FB.init({
        appId            : '149434858974947',
        autoLogAppEvents : true,
        xfbml            : true,
        version          : 'v2.11'
      });

      // Check the user's facebook login status
      try
      {
        FB.getLoginStatus(function(response)
        {
          // console.log("FB GET LOGIN STATUS:");
          // console.log(response);
          if (response.status === 'connected')
          {
            // the user is logged in and has authenticated your
            // app, and response.authResponse supplies
            // the user's ID, a valid access token, a signed
            // request, and the time the access token
            // and signed request each expire
            var uid = response.authResponse.userID;
            var accessToken = response.authResponse.accessToken;
            showTutorial = false;
            previouslyLoggedIn = true;
            // console.log(uid, accessToken);
            cognitoLogin(response);
          }
          else if (response.status === 'not_authorized')
          {
            // the user is logged in to Facebook,
            // but has not authenticated your app
            // tutorialMain();
            // tutorialScreen();
          }
          else
          {
            // the user isn't logged in to Facebook.
            // tutorialMain();
            // tutorialScreen();
          }
       });
      }
      catch (e)
      {
        console.log("FB LOGIN STATUS CHECK ERROR:");
        console.log(e);
      }
    };

    (function(d, s, id)
    {
       var js, fjs = d.getElementsByTagName(s)[0];
       if (d.getElementById(id)) {return;}
       js = d.createElement(s); js.id = id;
       js.src = "https://connect.facebook.net/en_US/sdk.js";
       fjs.parentNode.insertBefore(js, fjs);
     }(document, 'script', 'facebook-jssdk'));

     if (showTutorial)
     {
       tutorialScreen();
     }
     else
     {
        tutorialMain();
     }

    // Register the click events
    $("#map-menu-button").click(function()
    {
      // console.log("MAP MENU BUTTON CLICKED");
      if (menuToggle)
      {
        $('#map-container').animate({
          'left': '0px'
        }, 200, function()
        {
          menuToggle = false;
        });
      }
      else
      {
        $('#map-container').animate({
          'left': '100px'
        }, 200, function()
        {
          menuToggle = true;
        });
      }

      // Ensure that the data containers are closed
      if (spotToggle)
      {
        $('#spot-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          spotToggle = false;
        });
      }
      if (structureToggle)
      {
        $('#structure-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          structureToggle = false;
        });
      }
      if (profileToggle)
      {
        $('#profile-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          profileToggle = false;
        });
      }
      if (repairToggle)
      {
        $('#repair-container-sub').animate({
          'right': '-200px'
        }, 200, function()
        {
          repairToggle = false;
        });
      }
    });

    $("#map-profile-button").click(function()
    {
      // console.log("MAP PROFILE BUTTON CLICKED");
      try
      {
        FB.login(function(loginResponse)
        {
          if (loginResponse.authResponse)
          {
            cognitoLogin(loginResponse);
          }
          else
          {
            console.log('FB LOGIN - USER CANCELLED OR DID NOT AUTH');
          }
        });
      }
      catch (e)
      {
        alert("Hey, I'm your Harveytown App!\n\nI'm sorry, but I can't load Facebook login due to your security settings.\n\nPlease check that Tracking Protection is not enabled.\n\nThanks!");
      }

      if (spotToggle)
      {
        $('#spot-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          spotToggle = false;
        });
      }
      if (structureToggle)
      {
        $('#structure-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          structureToggle = false;
        });
      }
      if (repairToggle)
      {
        $('#repair-container-sub').animate({
          'right': '-200px'
        }, 200, function()
        {
          repairToggle = false;
        });
      }
      if (!profileToggle)
      {
        $('#profile-container-all').animate({
          'right': '0px'
        }, 200, function()
        {
          profileToggle = true;
        });
      }
      else
      {
        $('#profile-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          profileToggle = false;
        });
      }
    });

    $("#profile-logout").click(function()
    {
      // Close the profile view
      $('#profile-container-all').animate({
        'right': '-200px'
      }, 200, function()
      {
        profileToggle = false;
      });

      // Log out the user
      FB.logout();

      // Clear the user data
      userSkills = [];
      $('#profile-image').css('background-image', '');
      $('#profile-name').text('');

      // Reset the map data
      refreshCurrentData();
      // hide the structure match info box
      $('#map-structure-match-container').css('visibility', 'hidden');
    });

    // Ensure that the data containers are closed when the map or menu are clicked
    $("#map").click(function()
    {
      // console.log("MAP CLICKED");
      if (spotToggle && !markerClick && !circleClick)
      {
        $('#spot-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          spotToggle = false;
        });
      }
      if (structureToggle && !structureClick)
      {
        $('#structure-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          structureToggle = false;
        });
      }
      if (profileToggle)
      {
        $('#profile-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          profileToggle = false;
        });
      }

      if (repairToggle)
      {
        $('#repair-container-sub').animate({
          'right': '-200px'
        }, 200, function()
        {
          repairToggle = false;
        });
      }
    });
    $("#menu").click(function()
    {
      // console.log("MENU CLICKED");
      if (spotToggle)
      {
        $('#spot-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          spotToggle = false;
        });
      }
      if (structureToggle)
      {
        $('#structure-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          structureToggle = false;
        });
      }
      if (profileToggle)
      {
        $('#profile-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          profileToggle = false;
        });
      }
      if (repairToggle)
      {
        $('#repair-container-sub').animate({
          'right': '-200px'
        }, 200, function()
        {
          repairToggle = false;
        });
      }
    });

    var trafficLayer = new google.maps.TrafficLayer();
    $("#menu-toggle-container-traffic").click(function()
    {
      if (menuTrafficToggle)
      {
        trafficLayer.setMap(null);
        menuTrafficToggle = false;
        $('#menu-toggle-check-traffic').css('visibility', 'hidden');
      }
      else
      {
        trafficLayer.setMap(map);
        menuTrafficToggle = true;
        $('#menu-toggle-check-traffic').css('visibility', 'visible');
      }
    });

    $("#menu-toggle-container-structures").click(function()
    {
      if (menuStructureToggle)
      {
        structuresMapNull()
        menuStructureToggle = false;
        $('#menu-toggle-check-structures').css('visibility', 'hidden');

        // hide the structure match info box
        $('#map-structure-match-container').css('visibility', 'hidden');
      }
      else
      {
        structuresMapSet()
        menuStructureToggle = true;
        $('#menu-toggle-check-structures').css('visibility', 'visible');

        // If needed, show the structure match info box
        if (structureMatch)
        {
          $('#map-structure-match-container').css('visibility', 'visible');
        }
      }
    });

    $("#menu-toggle-container-spots").click(function()
    {
      if (menuSpotToggle)
      {
        spotCirclesMapNull()
        spotMarkersMapNull()
        spotRequestsMapNull()
        menuSpotToggle = false;
        $('#menu-toggle-check-spots').css('visibility', 'hidden');
      }
      else
      {
        spotCirclesMapSet()
        // Only add the spotMarkers if the zoom is less than the toggle setting
        if (map.getZoom() < mapZoomToggleSpotMarkers)
        {
          spotMarkersMapSet()
        }
        spotRequestsMapSet()
        menuSpotToggle = true;
        $('#menu-toggle-check-spots').css('visibility', 'visible');
      }
    });

    $("#menu-toggle-container-hazards").click(function()
    {
      if (menuHazardToggle)
      {
        hazardsMapNull()
        menuHazardToggle = false;
        $('#menu-toggle-check-hazards').css('visibility', 'hidden');
      }
      else
      {
        hazardsMapSet()
        menuHazardToggle = true;
        $('#menu-toggle-check-hazards').css('visibility', 'visible');
      }
    });

    $("#menu-filter-dot-container-1").click(function()
    {
      // Hide all other filter check marks and show this one
      $('#menu-filter-check-1').css('visibility', 'visible');
      $('#menu-filter-check-2').css('visibility', 'hidden');
      $('#menu-filter-check-3').css('visibility', 'hidden');
      $('#menu-filter-check-4').css('visibility', 'hidden');

      // Change the filter setting and refresh the data
      menuFilterSeconds = secondsDay;
      refreshCurrentData();
    });
    $("#menu-filter-dot-container-2").click(function()
    {
      // Hide all other filter check marks and show this one
      $('#menu-filter-check-1').css('visibility', 'hidden');
      $('#menu-filter-check-2').css('visibility', 'visible');
      $('#menu-filter-check-3').css('visibility', 'hidden');
      $('#menu-filter-check-4').css('visibility', 'hidden');

      // Change the filter setting and refresh the data
      menuFilterSeconds = secondsWeek;
      refreshCurrentData();
    });
    $("#menu-filter-dot-container-3").click(function()
    {
      // Hide all other filter check marks and show this one
      $('#menu-filter-check-1').css('visibility', 'hidden');
      $('#menu-filter-check-2').css('visibility', 'hidden');
      $('#menu-filter-check-3').css('visibility', 'visible');
      $('#menu-filter-check-4').css('visibility', 'hidden');

      // Change the filter setting and refresh the data
      menuFilterSeconds = secondsMonth;
      refreshCurrentData();
    });
    $("#menu-filter-dot-container-4").click(function()
    {
      // Hide all other filter check marks and show this one
      $('#menu-filter-check-1').css('visibility', 'hidden');
      $('#menu-filter-check-2').css('visibility', 'hidden');
      $('#menu-filter-check-3').css('visibility', 'hidden');
      $('#menu-filter-check-4').css('visibility', 'visible');

      // Change the filter setting and refresh the data
      menuFilterSeconds = secondsYear;
      refreshCurrentData();
    });
  });

  // When the Structure data container's user image is clicked, redirect to the FB page of the latest user
  $("#structure-user").click(function()
  {
    // window.location.href = lastStructureSelectedUserLink;
    window.open(lastStructureSelectedUserLink, '_blank');
    // return false;
  });

  // When either tab is selected, change the tab classes, hide the opposite data container, and show the needed data container
  $("#user-skills-tab").click(function()
  {
    $("#user-skills-tab").removeClass("user-data-tab-unselected");
    $("#user-skills-tab").addClass("user-data-tab-selected");
    $("#user-structure-tab").removeClass("user-data-tab-selected");
    $("#user-structure-tab").addClass("user-data-tab-unselected");

    $("#user-structure-container").css("z-index", "305");
    $("#user-skills-container").css("z-index", "306");
  });
  $("#user-structure-tab").click(function()
  {
    $("#user-structure-tab").removeClass("user-data-tab-unselected");
    $("#user-structure-tab").addClass("user-data-tab-selected");
    $("#user-skills-tab").removeClass("user-data-tab-selected");
    $("#user-skills-tab").addClass("user-data-tab-unselected");

    $("#user-skills-container").css("z-index", "305");
    $("#user-structure-container").css("z-index", "306");
  });

  // If a structure detail is showing, and a repair is selected, show the repair screen
  $('body').on('click', '.repair-container', function ()
  {
    // console.log("REPAIR CLICKED");
    var repairClicked = $(this).data("repair");
    var repairStageHtml = $(this).find('.repair-stage').clone();
    var repairIconHtml = $(this).find('img').clone();

    // console.log(repairStageHtml[0].outerHTML);
    // console.log(repairIconHtml[0].outerHTML);

    // Update the repair view header
    $('#repair-container-sub-header').html('');
    $('#repair-image-container').html('');
    var repairTitleInteriorHtml = repairStageHtml[0].outerHTML +
      '<div class="repair-detail">' +
        repairIconHtml[0].outerHTML +
        '<div class="repair-title">' + repairClicked + '</div>' +
        '<div class="repair-exit">&#x2715;</div>' +
      '</div>'
      $('#repair-container-sub-header').append(repairTitleInteriorHtml);
    // console.log(repairTitleInteriorHtml);

    // Show the loading indicator
    $('#repair-container-loader').css('visibility', 'visible');

    if (!repairToggle)
    {
      $('#repair-container-sub').animate({
        'right': '0px'
      }, 200, function()
      {
        repairToggle = true;
        // console.log(repairClicked);
        // console.log(lastStructureRepairs);
        // The last Structure selected should have the repair saved - find the exact repair clicked and request all images for that repair
        for (i = 0; i < lastStructureRepairs.length; i++)
        {
          // console.log(lastStructureRepairs[i].repair);
          if (lastStructureRepairs[i].repair == repairClicked)
          {
            // Save the repair clicked
            lastRepairSelected = lastStructureRepairs[i];
            // console.log(lastStructureRepairs[i].repair_images);
            for (img = 0; img < lastStructureRepairs[i].repair_images.length; img++)
            {
              // console.log(lastStructureRepairs[i].repair_images[img]);
              requestImageForKey(lastStructureRepairs[i].repair_images[img].image_id, lastStructureRepairs[i]);
            }
          }
        }
      });
    }
  });

  // If a repair exit is clicked, close the repair screen
  $('body').on('click', '.repair-exit', function ()
  {
    if (repairToggle)
    {
      $('#repair-container-sub').animate({
        'right': '-200px'
      }, 200, function()
      {
        repairToggle = false;
      });
    }
  });

  $('body').on('click', '.skill-container', function ()
  {
    // console.log("SKILL CLICKED");
    var skillClicked = $(this).data("skill");

    // Loop through the global user skill list to find the skill clicked, then change the level (increment)
    var skillLevelNew = 0;
    var skillExists = false;
    for (s = 0; s < userSkills.length; s++)
    {
      if (userSkills[s].skill == skillClicked)
      {
        skillExists = true;
        if (userSkills[s].level == 2)
        {
          skillLevelNew = 0;
        }
        else
        {
          skillLevelNew = userSkills[s].level + 1;
        }
        userSkills[s].level = skillLevelNew
      }
    }
    // If the skill does not exist, add an entry
    if (!skillExists)
    {
      // The skill was selected, so iterate the skill level
      skillLevelNew += 1;

      var newSkill = {};
      newSkill['skill_id'] = userId + '-' + skillClicked;
      newSkill['user_id'] = userId;
      newSkill['skill'] = skillClicked;
      newSkill['level'] = skillLevelNew;
      newSkill['status'] = 'active';
      userSkills.push(newSkill);
    }

    // Now refresh the list to show the change
    refreshSkillList();

    // Upload the change to the server
    putSkillLevel(skillClicked, skillLevelNew, userId, cognitoId, serverToken);
  });
}

// Reset the Structure container (so old data does not show when opened)
function resetStructureContainer()
{
  // Clear the user image and show the temp icon
  $('#structure-user').css('background-image', '');
  $('#structure-user').html('&#x1F4AC;');
  // Clear the Structure image
  $('#structure-image').css('background-image', '');
  // Clear the repair container
  $('#structure-repair-container').html('');
}


// MAP FUNCTIONS
// Refresh all data with currently downloaded data
function refreshCurrentData()
{
  if (menuSpotToggle)
  {
    addSpots();
    addSpotRequests();
  }
  if (menuHazardToggle)
  {
    addHazards();
  }

  if (menuStructureToggle)
  {
    addStructures();
  }
}

// Add Spots to the map
function addSpots()
{
  // Remove the current circles and markers from the map
  spotCirclesMapNull();
  spotMarkersMapNull();

  // Clear the current SpotCircles, SpotMarker, and filtered Spots arrays
  spotMarkers = [];
  spotCircles = [];
  filteredSpots = [];

  for (i = 0; i < allSpots.length; i++)
  {
    // Create a Spot Object
    var spot = allSpots[i];

    // Only add the entity if the timestamp is newer than the current filter setting
    var secondsOld = Math.floor(Date.now() / 1000) - spot.timestamp;
    if (secondsOld <= menuFilterSeconds)
    {
      // console.log(spot.lat)
      filteredSpots.push(spot);

      addSpotCircleForSpot(spot);
      addSpotMarkerForSpot(spot);
    }
  }
  menuSpotToggle = true;
  $('#menu-toggle-check-spots').css('visibility', 'visible');
}
function addSpotCircleForSpot(spot)
{
  // NOTE:  No need to check the time filter - the timestamp should already have been checked before this function is called

  // Add the circle for this city to the map.
  var spotCircle = new google.maps.Circle({
    strokeColor: '#EB6D24',
    strokeOpacity: 0.4,
    strokeWeight: 1,
    fillColor: '#EB6D24',
    fillOpacity: 0.4,
    map: map,
    center: {lat: spot.lat, lng: spot.lng},
    radius: 50,
    optimized: false,
    zIndex: 1
  });

  spotCircle.addListener('click', function()
  {
    circleClick = true;
    // console.log('CIRCLE: ' + spotCircle.getCenter());
    map.setCenter(spotCircle.getCenter());

    // Request the Spot Content with image data
    requestSpotContentFor(spot.spot_id);
    lastSpotSelected = spot.spot_id;

    // Open the data panel and display the item's data - ensure the other data containers are closed
    if (structureToggle)
    {
      $('#structure-container-all').animate({
        'right': '-200px'
      }, 200, function()
      {
        structureToggle = false;
      });
    }
    if (repairToggle)
    {
      $('#repair-container-sub').animate({
        'right': '-200px'
      }, 200, function()
      {
        repairToggle = false;
      });
    }
    if (profileToggle)
    {
      $('#profile-container-all').animate({
        'right': '-200px'
      }, 200, function()
      {
        profileToggle = false;
      });
    }

    // Open the container
    if (!spotToggle)
    {
      $('#spot-container-all').animate({
        'right': '0px'
      }, 200, function()
      {
        spotToggle = true;
        circleClick = false;
      });
    }
  });

  spotCircles.push(spotCircle);
}
function addSpotMarkerForSpot(spot)
{
  // NOTE:  No need to check the time filter - the timestamp should already have been checked before this function is called

  var spotMarker = new google.maps.Marker({
    position: {lat: spot.lat, lng: spot.lng},
    map: map,
    icon: {
      url: createMarker(20, 20, 10, '#EB6D24'),
      // size: new google.maps.Size(36, 36),
      // origin: new google.maps.Point(0, 0),
      anchor: new google.maps.Point(10, 10),
      // scaledSize: new google.maps.Size(25, 25)
    },
    optimized: false,
    zIndex: 3
  });

  spotMarker.addListener('click', function()
  {
    markerClick = true;
    // console.log('MARKER: ' + spotMarker.getPosition());
    map.setCenter(spotMarker.getPosition());

    // Request the Spot Content with image data
    requestSpotContentFor(spot.spot_id);
    lastSpotSelected = spot.spot_id;

    // Clear the content from the spot container
    $('#spot-container').html('');

    // Open the data panel and display the item's data - ensure the other data container is closed
    if (structureToggle)
    {
      $('#structure-container-all').animate({
        'right': '-200px'
      }, 200, function()
      {
        structureToggle = false;
      });
    }
    if (repairToggle)
    {
      $('#repair-container-sub').animate({
        'right': '-200px'
      }, 200, function()
      {
        repairToggle = false;
      });
    }
    if (profileToggle)
    {
      $('#profile-container-all').animate({
        'right': '-200px'
      }, 200, function()
      {
        profileToggle = false;
      });
    }

    // Open the container
    if (!spotToggle)
    {
      $('#spot-container-all').animate({
        'right': '0px'
      }, 200, function()
      {
        spotToggle = true;
        markerClick = false;
      });
    }
  });

  spotMarkers.push(spotMarker);
}

// Add/Remove the SpotCircles from the map
function spotCirclesMapNull()
{
  for (i = 0; i < spotCircles.length; i++)
  {
    spotCircles[i].setMap(null);
  }
}
function spotCirclesMapSet()
{
  for (i = 0; i < spotCircles.length; i++)
  {
    spotCircles[i].setMap(map);
  }
}
// Add/Remove the SpotMarkers from the map
function spotMarkersMapNull()
{
  for (i = 0; i < spotMarkers.length; i++)
  {
    spotMarkers[i].setMap(null);
  }
}
function spotMarkersMapSet()
{
  for (i = 0; i < spotMarkers.length; i++)
  {
    spotMarkers[i].setMap(map);
  }
}

// Add SpotRequests to the map
function addSpotRequests()
{
  // Remove the current SpotRequests from the map and clear the arrays
  spotRequestsMapNull();
  spotRequestMarkers = [];
  filteredSpotRequests = [];

  // Create a common infowindow for all markers
  var infowindow = new google.maps.InfoWindow(
    {
      content: 'Photo Requested<br><br>APP ONLY: Take photos by location in the iPhone app.'
  });

  for (i = 0; i < allSpotRequests.length; i++)
  {(function (spotRequest)
    {
      // Only add the entity if the timestamp is newer than the current filter setting
      var secondsOld = Math.floor(Date.now() / 1000) - allSpotRequests[i].timestamp;
      if (secondsOld <= menuFilterSeconds)
      {
        var icon = {
          url: 'img/markers/marker_icon_camera_yellow@3x.png',
          scaledSize: new google.maps.Size(50, 50), // scaled size
          origin: new google.maps.Point(0,0), // origin
          anchor: new google.maps.Point(25,50) // anchor
        };
        // console.log(allSpotRequests[i].lat)
        var spotRequestMarker = new google.maps.Marker({
          position: {lat: allSpotRequests[i].lat, lng: allSpotRequests[i].lng},
          map: map,
          icon: icon,
          optimized: false,
          zIndex: 4
        });

        spotRequestMarker.addListener('click', function()
        {
          infowindow.open(map, this);
        });

        spotRequestMarkers.push(spotRequestMarker);
        filteredSpotRequests.push(allSpotRequests[i]);
      }
    })(allSpotRequests[i])
  }
}

// Add/Remove the SpotRequestMarkers from the map
function spotRequestsMapNull()
{
  for (i = 0; i < spotRequestMarkers.length; i++)
  {
    spotRequestMarkers[i].setMap(null);
  }
}
function spotRequestsMapSet()
{
  for (i = 0; i < spotRequestMarkers.length; i++)
  {
    spotRequestMarkers[i].setMap(map);
  }
}

// Add Hazards to the map
function addHazards()
{
  // Remove the current Hazards from the map and clear the arrays
  hazardsMapNull();
  hazardMarkers = [];
  filteredHazards = [];

  // Create a common infowindow for all markers
  var infowindow = new google.maps.InfoWindow(
    {
      content: 'Hazard Reported'
  });

  for (i = 0; i < allHazards.length; i++)
  {
    // Only add the entity if the timestamp is newer than the current filter setting
    var secondsOld = Math.floor(Date.now() / 1000) - allHazards[i].timestamp;
    if (secondsOld <= menuFilterSeconds)
    {
      // console.log(allHazards[i].lat)
      var icon = {
        url: 'img/icons/icon_hazard@3x.png',
        scaledSize: new google.maps.Size(50,50), // scaled size
        origin: new google.maps.Point(0,0), // origin
        anchor: new google.maps.Point(25,50) // anchor
      };
      var hazardMarker = new google.maps.Marker({
        position: {lat: allHazards[i].lat, lng: allHazards[i].lng},
        map: map,
        icon: icon,
        optimized: false,
        zIndex: 2
      });

      hazardMarker.addListener('click', function()
      {
        infowindow.open(map, this);
      });

      hazardMarkers.push(hazardMarker);
      filteredHazards.push(allHazards[i]);
    }
  }
  menuHazardToggle = true;
  $('#menu-toggle-check-hazards').css('visibility', 'visible');
}

// Add/Remove the Hazards from the map
function hazardsMapNull()
{
  for (i = 0; i < hazardMarkers.length; i++)
  {
    hazardMarkers[i].setMap(null);
  }
}
function hazardsMapSet()
{
  for (i = 0; i < hazardMarkers.length; i++)
  {
    hazardMarkers[i].setMap(map);
  }
}

// Add Structures to the map
function addStructures()
{
  // Remove the current Structures from the map and clear the arrays
  structuresMapNull();
  structureMarkers = [];
  filteredStructures = [];

  for (i = 0; i < allStructures.length; i++)
  {
    // Only add the entity if the timestamp is newer than the current filter setting
    var secondsOld = Math.floor(Date.now() / 1000) - allStructures[i].timestamp;
    if (secondsOld <= menuFilterSeconds)
    {
      // console.log(allStructures[i].lat)
      filteredStructures.push(allStructures[i]);

      addMarkerForStructure(allStructures[i]);
    }
  }
  menuStructureToggle = true;
  $('#menu-toggle-check-structures').css('visibility', 'visible');
}

function addMarkerForStructure(structure)
{
  // NOTE:  No need to check the time filter - the timestamp should already have been checked before this function is called

  // console.log("ADDING STRUCTURE MARKER");
  // Check whether the structure has a repair that matches the user's skill (if logged in)
  // Reset the skill match toggle variable
  structureMatch = false;
  var iconImage = 'img/markers/marker_icon_structure@3x.png';
  var iconSize = 50;
  for (s = 0; s < userSkills.length; s++)
  {
    for (r = 0; r < structure.repairs.length; r++)
    {
      var thisRepair = structure.repairs[r].repair
      for (sk = 0; sk < repairSettings.types[thisRepair].skills.length; sk++)
      {
        if (userSkills[s].skill == repairSettings.types[thisRepair].skills[sk] && userSkills[s].level > 0)
        {
          // Use the skill-matching structure icon
          iconImage = 'img/markers/marker_icon_structure_skill_match@3x.png';
          iconSize = 70;

          // At least one structure was matched to the user's skills, so show the info box
          structureMatch = true;
        }
      }
    }
  }

  // If needed, show the structure match info box
  if (structureMatch)
  {
    // console.log("DISPLAY STRUCTURE MATCH INFO BOX");
    $('#map-structure-match-container').css('visibility', 'visible');
  }
  else
  {
    $('#map-structure-match-container').css('visibility', 'hidden');
  }

  var icon = {
    url: iconImage,
    scaledSize: new google.maps.Size(iconSize,iconSize), // scaled size
    origin: new google.maps.Point(0,0), // origin
    anchor: new google.maps.Point(iconSize/2,iconSize) // anchor
  };
  var structureMarker = new google.maps.Marker({
    position: {lat: structure.lat, lng: structure.lng},
    map: map,
    icon: icon,
    optimized: false,
    zIndex: 5
  });

  structureMarker.addListener('click', function()
  {
      structureClick = true;
      // console.log('MARKER: ' + structureMarker.getPosition());
      //   map.setZoom(8);
      map.setCenter(structureMarker.getPosition());

      // Request the Repair data
      requestRepairsForStructure(structure);
      // Record the last structure clicked so that the latest data is displayed
      lastStructureSelected = structure

      // Start all structure loaders
      $('#structure-image-loader').css('visibility', 'visible');
      $('#structure-user-loader').css('visibility', 'visible');
      $('#structure-repair-loader').css('visibility', 'visible');

      // Reset the Structure container to not show old data
      resetStructureContainer();

      // Open the data panel and display the item's data - ensure that the other data containers are closed
      if (spotToggle)
      {
        $('#spot-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          spotToggle = false;
        });
      }
      if (profileToggle)
      {
        $('#profile-container-all').animate({
          'right': '-200px'
        }, 200, function()
        {
          profileToggle = false;
        });
      }

      // Open the container
      if (!structureToggle)
      {
        $('#structure-container-all').animate({
          'right': '0px'
        }, 200, function()
        {
          structureToggle = true;
          structureClick = false;

          structureUserTutorialMain();
        });
      }
  });

  structureMarkers.push(structureMarker);
}
// Add/Remove the Structures from the map
function structuresMapNull()
{
  for (i = 0; i < structureMarkers.length; i++)
  {
    structureMarkers[i].setMap(null);
  }
}
function structuresMapSet()
{
  for (i = 0; i < structureMarkers.length; i++)
  {
    structureMarkers[i].setMap(map);
  }
}

// Reload the user's skill list using the global variables
function refreshSkillList()
{
  // Clear the skill container
  $('#user-skills-container').html('');
  // Ensure the loader is showing
  $('#profile-container-loader').css('visibility', 'visible');

  // 1 - Loop the same number of times as the skill settings count
  // 1 - Loop through the skill settings and find the next skill (in order)
  // 2 - Find the user's skill that matches that next skill setting
  // 3 - If the user's skill level is more than 0, add that skill html to the skill container
  for (i = 0; i < Object.keys(skillTypes).length; i++)
  {
    $.each(skillTypes, function(sKey, sVal)
    {
      if (sVal.order == i)
      {
        // Assign the default skill level
        var userSkillLevel = 0;
        // Check whether the user has already registered the skill
        for (s = 0; s < userSkills.length; s++)
        {
          if (userSkills[s].skill == sKey)
          {
            userSkillLevel = userSkills[s].level;
          }
        }
        // console.log("ADD SKILL: " + sKey + " WITH LEVEL: " + userSkillLevel);
        var skillHtml = '<div class="skill-container" data-skill="' + sKey + '">' +
            '<div class="skill-stage" style="background-color:' + skillLevels[userSkillLevel]['color'] +
            '">' + sVal.title + '</div>' +
            '<div class="skill-detail">' +
              '<img border="0" src="img/repairs/' + sVal.image + '" class="skill-icon">' +
              '<div class="skill-title">' + skillLevels[userSkillLevel]['title'] + '</div>' +
            '</div>' +
          '</div>'
        $('#user-skills-container').append(skillHtml);
      }
    });
  }

  // Now hide the loader
  $('#profile-container-loader').css('visibility', 'hidden');

  // Refresh the map data to ensure that any skill matching occurs
  refreshCurrentData();
}


// API FUNCTIONS
// Function to request Cognito credentials
function requestCognitoCredentials(fbID, token)
{
  // console.log("REQUESTING COGNITO CREDENTIALS");
  // console.log('ENDPOINT COGNITO: ' + refs['endpoint_cognito_id']);

  var xhrHT = new XMLHttpRequest();
  xhrHT.open('POST', refs['endpoint_cognito_id'], true);
  xhrHT.setRequestHeader("Content-Type", "application/json");
  xhrHT.send(JSON.stringify({
    'app_version': appVersion
    , 'fb_id': fbID
    , 'token': token
  }));
  xhrHT.onerror = function()
  {
    console.log("XHR ERROR")

    // DEV CHECK BEFORE PROD
    // // The error might be a CORS error (www) - redirect?
    // window.location = domain;
  }
  xhrHT.onreadystatechange = function()
  {
    if (xhrHT.readyState == XMLHttpRequest.DONE)
    {
      // console.log('COGNITO RESPONSE:');
      // console.log(xhrHT.responseText.toString());
      var jsonResponse = JSON.parse(xhrHT.responseText);
      // console.log(jsonResponse);

      userId = jsonResponse.user_data.user_id;
      facebookId = jsonResponse.user_data.facebook_id;
      cognitoId = jsonResponse.user_data.cognito_id;

      $('#profile-image').css('background-image', 'url("https://graph.facebook.com/' + facebookId + '/picture?type=normal")');

      requestSkills(userId, cognitoId, serverToken);
    }
  }
}

// Function to request a User's Skill data
function requestSkills(uid, identityId, token)
{
  // console.log("REQUESTING USER SKILLS");
  // console.log('ENDPOINT SKILLS: ' + refs['endpoint_skill_query']);

  // Clear the current skill list and show the loader
  $('#user-skills-container').html('');
  $('#profile-container-loader').css('visibility', 'visible');

  var xhrHT = new XMLHttpRequest();
  xhrHT.open('POST', refs['endpoint_skill_query'], true);
  xhrHT.setRequestHeader("Content-Type", "application/json");
  xhrHT.send(JSON.stringify({
    'app_version': appVersion
    , 'identity_id': identityId
    , 'login_provider': 'graph.facebook.com'
    , 'login_token': token
    , 'user_id': uid
  }));
  xhrHT.onerror = function()
  {
    console.log("XHR ERROR")

    // DEV CHECK BEFORE PROD
    // // The error might be a CORS error (www) - redirect?
    // window.location = domain;
  }
  xhrHT.onreadystatechange = function()
  {
    if (xhrHT.readyState == XMLHttpRequest.DONE)
    {
      // console.log('SKILLS RESPONSE:');
      // console.log(xhrHT.responseText.toString());
      var jsonResponse = JSON.parse(xhrHT.responseText);
      // console.log(jsonResponse);

      userSkills = jsonResponse.skills.user_skills;
      skillLevels = jsonResponse.skills.skill_levels;
      skillTypes = jsonResponse.skills.skill_types;

      refreshSkillList();
    }
  }
}

// Function to update a skill's level
function putSkillLevel(skill, level, uid, identityId, token)
{
  // console.log("PUT USER SKILL LEVEL");
  // console.log('ENDPOINT SKILL PUT: ' + refs['endpoint_skill_put']);

  var xhrHT = new XMLHttpRequest();
  xhrHT.open('POST', refs['endpoint_skill_put'], true);
  xhrHT.setRequestHeader("Content-Type", "application/json");
  xhrHT.send(JSON.stringify({
    'app_version': appVersion
    , 'identity_id': identityId
    , 'login_provider': 'graph.facebook.com'
    , 'login_token': token
    , 'user_id': uid
    , 'skill': skill
    , 'level': level
  }));
  xhrHT.onerror = function()
  {
    console.log("XHR ERROR")

    // DEV CHECK BEFORE PROD
    // // The error might be a CORS error (www) - redirect?
    // window.location = domain;
  }
  xhrHT.onreadystatechange = function()
  {
    if (xhrHT.readyState == XMLHttpRequest.DONE)
    {
      // console.log('SKILL PUT RESPONSE:');
      // console.log(xhrHT.responseText.toString());
      var jsonResponse = JSON.parse(xhrHT.responseText);
      // console.log(jsonResponse);
    }
  }
}

// Function to request Spot data
function requestSpots()
{
  // Show the loading indicator
  $('#map-loader').css('visibility', 'visible');
  // console.log("MAP LOADER VISIBLE");
  // Record the download request
  downloadingSpots = true;

  // console.log("REQUESTING SPOT DATA");
  // console.log('ENDPOINT SPOTS: ' + refs['endpoint_spot_query_active']);
  var timestamp_begin = 0;

  var xhrHT = new XMLHttpRequest();
  xhrHT.open('POST', refs['endpoint_spot_query_active'], true);
  xhrHT.setRequestHeader("Content-Type", "application/json");
  xhrHT.send(JSON.stringify({
    'app_version': appVersion
    , 'timestamp_begin': timestamp_begin
  }));
  xhrHT.onerror = function()
  {
    console.log("XHR ERROR")

    // DEV CHECK BEFORE PROD
    // // The error might be a CORS error (www) - redirect?
    // window.location = domain;
  }
  xhrHT.onreadystatechange = function()
  {
    if (xhrHT.readyState == XMLHttpRequest.DONE)
    {
      // Indicate the download is complete
      downloadingSpots = false;

      // console.log(xhrHT.responseText.toString());
      var jsonResponse = JSON.parse(xhrHT.responseText);
      allSpots = jsonResponse.spots;
      addSpots();

      allSpotRequests = jsonResponse.spot_requests;
      addSpotRequests();

      // If nothing is being downloaded currently, hide the loader
      if (!downloadingStructures && !downloadingSpots && !downloadingHazards)
      {
          $('#map-loader').css('visibility', 'hidden');
          // console.log("MAP LOADER HIDDEN");
      }
    }
  }
}

// Function to request Spot Content data & image links for the side view
function requestSpotContentFor(spotId)
{
  // Show the loading indicator
  $('#spot-container-loader').css('visibility', 'visible');
  // console.log("SPOT LOADER VISIBLE");

  // console.log("REQUESTING SPOT CONTENT DATA");
  // console.log('ENDPOINT SPOT CONTENT: ' + refs['endpoint_spot_content_query']);
  var timestamp_begin = 0;

  var xhrHT = new XMLHttpRequest();
  xhrHT.open('POST', refs['endpoint_spot_content_query'], true);
  xhrHT.setRequestHeader("Content-Type", "application/json");
  xhrHT.send(JSON.stringify({
    'app_version': appVersion
    , 'timestamp_begin': timestamp_begin
    , 'spot_id': spotId
  }));
  xhrHT.onerror = function()
  {
    console.log("XHR ERROR")
  }
  xhrHT.onreadystatechange = function()
  {
    if (xhrHT.readyState == XMLHttpRequest.DONE)
    {
      // Only display the data if it matches the last item selected
      if (lastSpotSelected == spotId)
      {
          // Hide the loading indicator
          $('#spot-container-loader').css('visibility', 'hidden');

          // console.log(xhrHT.responseText.toString());
          var jsonResponse = JSON.parse(xhrHT.responseText);
          // console.log(jsonResponse);

          // Clear the content from the spot container
          $('#spot-container').html('');

          // Add the content associated with the current spot marker to the container
          for (s = 0; s < jsonResponse.spot_content.length; s++)
          {
            // console.log(jsonResponse.spot_content[s]);
            var contentDatetime = new Date(jsonResponse.spot_content[s].timestamp * 1000);
            // console.log(contentDatetime);
            contentTime = dateFormat(contentDatetime);
            // var contentHtml = '<img border="0" src="' + jsonResponse.spot_content[s].image_url + '" class="content-image content-image-' + jsonResponse.spot_content[s].content_id + '" data-element-category="content-image" data-element-id="content-image-' + jsonResponse.spot_content[s].content_id + '">'
            var contentHtml = '<div class="content-image-container">' +
                    '<img border="0" src="data:;base64,' + jsonResponse.spot_content[s].image +
                        '" class="content-image content-image-' + jsonResponse.spot_content[s].content_id +
                        '" data-element-category="content-image" data-element-id="content-image-' + jsonResponse.spot_content[s].content_id +
                    '">' +
                    '<div class="content-image-time">' + contentTime + '</div>' +
                '</div>'
            $('#spot-container').append(contentHtml);
          }
      }
    }
  }
}

function dateFormat(date)
{
    var year = date.getFullYear();
    var month = months[date.getMonth()];
    var day = date.getDate();
    // var hour = date.getHours() < 10 ? '0' + date.getHours() : date.getHours();
    var hour = date.getHours() > 12 ? date.getHours() - 12 : date.getHours();
    var am_pm = date.getHours() >= 12 ? "pm" : "am";
    // hour = hour < 10 ? '0' + hour : hour;
    // var min = date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes();
    // var sec = date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds();
    return month + ' ' + day + ', ' + year + ' ' + hour + am_pm ;
}

// Function to request Hazard data
function requestHazards()
{
  // Show the loading indicator
  $('#map-loader').css('visibility', 'visible');
  // console.log("MAP LOADER VISIBLE");
  // Record the download request
  downloadingHazards = true;

  // console.log("REQUESTING HAZARD DATA");
  // console.log('ENDPOINT HAZARDS: ' + refs['endpoint_hazard_query_active']);
  var timestamp_begin = 0;

  var xhrHT = new XMLHttpRequest();
  xhrHT.open('POST', refs['endpoint_hazard_query_active'], true);
  xhrHT.setRequestHeader("Content-Type", "application/json");
  xhrHT.send(JSON.stringify({
    'app_version': appVersion
    , 'timestamp_begin': timestamp_begin
  }));
  xhrHT.onerror = function()
  {
    console.log("XHR ERROR")

    // DEV CHECK BEFORE PROD
    // // The error might be a CORS error (www) - redirect?
    // window.location = domain;
  }
  xhrHT.onreadystatechange = function()
  {
    if (xhrHT.readyState == XMLHttpRequest.DONE)
    {
      // Indicate the download is complete
      downloadingHazards = false;

      // console.log(xhrHT.responseText.toString());
      var jsonResponse = JSON.parse(xhrHT.responseText);
      // console.log(jsonResponse.hazards);
      allHazards = jsonResponse.hazards;
      addHazards();

      // If nothing is being downloaded currently, hide the loader
      if (!downloadingStructures && !downloadingSpots && !downloadingHazards)
      {
          $('#map-loader').css('visibility', 'hidden');
          // console.log("MAP LOADER HIDDEN");
      }
    }
  }
}

// Function to request Structure data
function requestStructures()
{
  // Show the loading indicator
  $('#map-loader').css('visibility', 'visible');
  // console.log("MAP LOADER VISIBLE");
  // Record the download request
  downloadingStructures = true;

  // console.log("REQUESTING STRUCTURE DATA");
  // console.log('ENDPOINT STRUCTURES: ' + refs['endpoint_structure_query']);
  var timestamp_begin = 0;

  var xhrHT = new XMLHttpRequest();
  xhrHT.open('POST', refs['endpoint_structure_query'], true);
  xhrHT.setRequestHeader("Content-Type", "application/json");
  xhrHT.send(JSON.stringify({
    'app_version': appVersion
    , 'timestamp_begin': timestamp_begin
  }));
  xhrHT.onerror = function()
  {
    console.log("XHR ERROR")
    console.log(xhrHT.responseText.toString());
    // DEV CHECK BEFORE PROD
    // // The error might be a CORS error (www) - redirect?
    // window.location = domain;
  }
  xhrHT.onreadystatechange = function()
  {
    if (xhrHT.readyState == XMLHttpRequest.DONE)
    {
      // Indicate the download is complete
      downloadingStructures = false;

      // console.log(xhrHT.responseText.toString());
      var jsonResponse = JSON.parse(xhrHT.responseText);
      // console.log(jsonResponse);
      repairSettings = jsonResponse.repair_settings;
      allStructures = jsonResponse.structures;
      addStructures();

      // If nothing is being downloaded currently, hide the loader
      if (!downloadingStructures && !downloadingSpots && !downloadingHazards)
      {
          $('#map-loader').css('visibility', 'hidden');
          // console.log("MAP LOADER HIDDEN");
      }
    }
  }
}

// Function to request Repair data for a Structure
function requestRepairsForStructure(structure)
{
  // console.log("STRUCTURE LOADER VISIBLE");

  // console.log("REQUESTING REPAIR DATA");
  // console.log('ENDPOINT REPAIR: ' + refs['endpoint_repair_query']);

  var xhrHT = new XMLHttpRequest();
  xhrHT.open('POST', refs['endpoint_repair_query'], true);
  xhrHT.setRequestHeader("Content-Type", "application/json");
  xhrHT.send(JSON.stringify({
    'app_version': appVersion
    , 'structure_id': structure.structure_id
    , 'structure': structure
  }));
  xhrHT.onerror = function()
  {
    console.log("XHR ERROR")

    // DEV CHECK BEFORE PROD
    // // The error might be a CORS error (www) - redirect?
    // window.location = domain;
  }
  xhrHT.onreadystatechange = function()
  {
    if (xhrHT.readyState == XMLHttpRequest.DONE)
    {
      // console.log(xhrHT.responseText.toString());
      var jsonResponse = JSON.parse(xhrHT.responseText);
      // console.log(jsonResponse);
      repairSettings = jsonResponse.repair_settings;
      var allRepairs = jsonResponse.repairs;

      // Only continue the data requests the data if it matches the last structure selected
      if (lastStructureSelected.structure_id == jsonResponse.request.structure_id)
      {
          // Request the image data for the structure
          requestImageForKey(jsonResponse.request.structure.image_id, structure);
          // The response should include the user data
          // Request the image data for the user (just use the first user in the array for now)
          if (jsonResponse.request.structure.users.length > 0)
          {
              // requestImageForKey(jsonResponse.request.structure.users[0].user_id, structure);
              $('#structure-user').html('');
              $('#structure-user').css('background-image', 'url("https://graph.facebook.com/' + jsonResponse.request.structure.users[0].facebook_id + '/picture?type=normal")');

              // $('<img/>').attr('src', "https://graph.facebook.com/' + jsonResponse.request.structure.users[0].facebook_id + '/picture?type=normal").on('load', function()
              // {
              //    $(this).remove(); // prevent memory leaks
              //    $('#structure-user').css('background-image', 'url("https://graph.facebook.com/' + jsonResponse.request.structure.users[0].facebook_id + '/picture?type=normal")');
              //
              //    // Hide the loading indicator
              //    $('#structure-user-loader').css('visibility', 'hidden');
              // });

              // Set the new link for the user image
              lastStructureSelectedUserLink = jsonResponse.request.structure.users[0].user_fb_url;
          }

          // console.log("ADD REPAIRS");
          // Reset the repair container
          $('#structure-repair-container').html('');

          // Save the last clicked Structure's repairs
          lastStructureRepairs = jsonResponse.repairs;
          // console.log(jsonResponse.repair_settings);
          // Add the repairs to the list
          // Loop through the repair settings list as many times as it is long to find each in order
          // for (order = 0; order < jsonResponse.repair_settings.length; order++)
          var order = 0;
          for (var r in jsonResponse.repair_settings.types)
          {
            // console.log("REPAIR ORDER: " + order);
            // Loop through the repair settings list to find the correctly ordered entity
            for (var repair in jsonResponse.repair_settings.types)
            {
              // console.log("REPAIR: " + repair);
              // console.log("REPAIR SETTING ORDER: " + jsonResponse.repair_settings[repair].order);
              if (jsonResponse.repair_settings.types[repair].order == order)
              {
                // console.log("REPAIRS COUNT: " + jsonResponse.repairs.length);
                // Check whether that repair item exists for this structure
                for (r = 0; r < jsonResponse.repairs.length; r++)
                {
                  // console.log("REPAIR FOR ITEM: " + jsonResponse.repairs[r].repair);
                  // Only stages greater than 0 have been added
                  if (jsonResponse.repairs[r].repair == repair && jsonResponse.repairs[r].stage > 0)
                  {
                    // console.log("ADD REPAIR: " + jsonResponse.repairs[r].repair + " WITH STAGE: " + jsonResponse.repair_settings.stages[jsonResponse.repairs[r].stage]['title']);
                    var repairHtml = '<div class="repair-container" data-repair="' + jsonResponse.repairs[r].repair + '">' +
                        '<div class="repair-stage" style="background-color:' + jsonResponse.repair_settings.stages[jsonResponse.repairs[r].stage]['color'] +
                          '">' + jsonResponse.repair_settings.stages[jsonResponse.repairs[r].stage]['title'] + '</div>' +
                        '<div class="repair-detail">' +
                          '<img border="0" src="img/repairs/' + jsonResponse.repair_settings.types[repair].image + '" class="repair-icon">' +
                          '<div class="repair-title">' + jsonResponse.repair_settings.types[repair]['title'] + '</div>' +
                          '<div class="repair-arrow">&#x203A;</div>' +
                        '</div>' +
                      '</div>'
                    $('#structure-repair-container').append(repairHtml);
                  }
                }
              }
            }
            order++;
          }

          // Hide the loading indicator
          $('#structure-repair-loader').css('visibility', 'hidden');
      }
    }
  }
}

// Function to request any Lambda image based off of the object key
function requestImageForKey(imageKey, entityData)
{
  // console.log("REQUESTING IMAGE DATA");
  // console.log('ENDPOINT IMAGE: ' + refs['endpoint_image_data']);

  var xhrHT = new XMLHttpRequest();
  xhrHT.open('POST', refs['endpoint_image_data'], true);
  xhrHT.setRequestHeader("Content-Type", "application/json");
  xhrHT.send(JSON.stringify({
    'app_version': appVersion
    , 'image_key': imageKey
    , 'entity_data': entityData
  }));
  xhrHT.onerror = function()
  {
    console.log("XHR ERROR")

    // DEV CHECK BEFORE PROD
    // // The error might be a CORS error (www) - redirect?
    // window.location = domain;
  }
  xhrHT.onreadystatechange = function()
  {
    if (xhrHT.readyState == XMLHttpRequest.DONE)
    {
        // console.log("IMAGE DATA FOR: " + imageKey + ":");
        // console.log(xhrHT.responseText.toString());
        var jsonResponse = JSON.parse(xhrHT.responseText);
        // console.log(jsonResponse);

        // Determine if the data should still be displayed (the item was the last selected, and where the image should be placed)
        if (jsonResponse.request.entity_data.hasOwnProperty('repair_id'))
        {
            // console.log("REPAIR IMAGE RETURNED");
            // Entity is a repair image - determine if it belongs to the last selected
            if (lastRepairSelected.repair_id == jsonResponse.request.entity_data.repair_id)
            {
                // console.log(jsonResponse.image_data);
                // The repair matches, so add the image to the repair screen_popup
                var imgHtml = '<div class="repair-image-container-sub">' +
                  '<img border="0" src="data:image/jpeg;charset=utf-8;base64, ' + jsonResponse.image_data.image + '" class="repair-image">'
                '</div>' +
                $('#repair-image-container').append(imgHtml);

                // Hide the loading indicator
                $('#repair-container-loader').css('visibility', 'hidden');
            }
        }
        else if (jsonResponse.request.entity_data.hasOwnProperty('structure_id'))
        {
            // console.log("STRUCTURE IMAGE RETURNED");
            // Entity is a structure image - determine if it belongs to the last selected
            if (lastStructureSelected.structure_id == jsonResponse.request.entity_data.structure_id)
            {
                // console.log(jsonResponse.image_data);
                // Add the structure image to the element in the display container
                var img = new Image();
                img.src = "data:image/jpeg;charset=utf-8;base64, " + jsonResponse.image_data.image;
                $("#structure-image").css("background-image", "url('" + img.src + "')");

                // Hide the loading indicator
                $('#structure-image-loader').css('visibility', 'hidden');
            }
        }
    }
  }
}

// https://graph.facebook.com/10111370082136134/picture?type=normal
// function downloadFbImage(fbId)
// {
//   console.log("DOWNLOADING FB IMAGE FOR USER: " + fbId);
//
//   var xhrHT = new XMLHttpRequest();
//   xhrHT.open('GET', refs['endpoint_image_data'], true);
//   xhrHT.setRequestHeader("Content-Type", "application/json");
//   xhrHT.send(JSON.stringify({
//     'app_version': appVersion
//     , 'image_key': imageKey
//     , 'entity_data': entityData
//   }));
//   xhrHT.onerror = function()
//   {
//     console.log("XHR ERROR")
//
//     // DEV CHECK BEFORE PROD
//     // // The error might be a CORS error (www) - redirect?
//     // window.location = domain;
//   }
//   xhrHT.onreadystatechange = function()
//   {
//     if (xhrHT.readyState == XMLHttpRequest.DONE)
//     {
//         console.log("IMAGE DATA FOR: " + imageKey + ":");
//         // console.log(xhrHT.responseText.toString());
//         var jsonResponse = JSON.parse(xhrHT.responseText);
//         console.log(jsonResponse);
//
//         // Determine if the data should still be displayed (the item was the last selected, and where the image should be placed)
//         if (jsonResponse.request.entity_data.hasOwnProperty('repair_id'))
//         {
//             console.log("REPAIR IMAGE RETURNED");
//             // Entity is a repair image - determine if it belongs to the last selected
//             if (lastRepairSelected.repair_id == jsonResponse.request.entity_data.repair_id)
//             {
//                 console.log(jsonResponse.image_data);
//             }
//         }
//         else if (jsonResponse.request.entity_data.hasOwnProperty('structure_id'))
//         {
//             console.log("STRUCTURE IMAGE RETURNED");
//             // Entity is a structure image - determine if it belongs to the last selected
//             if (lastStructureSelected.structure_id == jsonResponse.request.entity_data.structure_id)
//             {
//                 console.log(jsonResponse.image_data);
//                 // Add the structure image to the element in the display container
//                 var img = new Image();
//                 img.src = "data:image/jpeg;charset=utf-8;base64, " + jsonResponse.image_data.image;
//                 $("#structure-image").css("background-image", "url('" + img.src + "')");
//             }
//         }
//     }
//   }
// }
