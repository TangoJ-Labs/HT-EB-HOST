var refs;
var spots;
var map;
var mobile = false;

console.log('MAP JS - PRE');

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

  var image = 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png';
  var canvas = document.createElement("canvas");
  canvas.width = 200;
  canvas.height = 200;
  var url = canvas.toDataURL();
  for (i = 0; i < spots.length; i++)
  {
    print(spots[i].lat)
    // Add the circle for this city to the map.
    var spotCircle = new google.maps.Circle({
      strokeColor: '#FF0000',
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: '#FF0000',
      fillOpacity: 0.35,
      map: map,
      center: {lat: spots[i].lat, lng: spots[i].lng},
      radius: 100
    });

    var spotMarker = new google.maps.Marker({
      position: {lat: spots[i].lat, lng: spots[i].lng},
      map: map,
      icon: url
    });
  }
}

$(document).ready(function()
{
  console.log('MAP JS - DOC READY');
});
