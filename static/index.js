var assets = {};
var notFoundUrls = [];
var numberAssets, results;

var searchInput = document.querySelector('input');
var assetsDiv = document.querySelector('.assets');
var loadingImage = document.querySelector('.loading');
var displayHiDPICheckbox = document.querySelector('#displayHiDPI');

function removeImageEventListeners(image) {
    image.removeEventListener('load', onImageLoaded);
    image.removeEventListener('error', onImageError);
}

function removeAudioEventListeners(audio) {
    audio.removeEventListener('canplay', onAudioLoaded);
}

function onAudioLoaded() {
    removeImageEventListeners(this);
    this.parentNode.parentNode.style.visibility = '';

    numberAssets++;
}

function appendAudio(url, title) {
    var asset = document.createElement('div');
    asset.classList.add('asset');
    asset.title = title;
    asset.style.visibility = 'hidden';

    var anchor = document.createElement('a');
    anchor.href = url;
    anchor.target = "_blank";
    anchor.rel = "nofollow";

    var audio = document.createElement('audio');
    audio.title = title;
    audio.controls = true;
    audio.addEventListener('canplay', onAudioLoaded);
    audio.src = url;

    anchor.appendChild(audio);
    asset.appendChild(anchor);

    var name = document.createElement('div');
    var friendlyName = url.substr(url.lastIndexOf('/')+1, url.length);
    friendlyName = friendlyName.substr(0, friendlyName.length - '.wav'.length);
    friendlyName = friendlyName.replace(/(-|_)/g, ' ');
    name.innerText = friendlyName;
    name.classList.add('name');
    asset.appendChild(name);

    assetsDiv.appendChild(asset);
}

function onImageError() {
    notFoundUrls.push(this.src);

    if ((this.src.indexOf('default_100_percent') === -1)  &&
        (this.src.indexOf('default_200_percent') !== -1)) {
        // fallback to lower resolution
        var newUrl = this.src.replace('default_200_percent', 'default_100_percent');
        for (var i = 0; i < assets.length; i++) {
            var url = assets[i][0].replace(/\\/g, '/');
            if (url === this.src)
                assets[i][0] = newUrl;
        }
        this.src = newUrl;
        this.parentNode.href = newUrl;
    } else {
        removeImageEventListeners(this);
    }
}

function onImageLoaded(event) {
    var size = document.querySelector('[title="'+ this.title +'"] [href="'+ this.src +'"]~.size');
    size.innerText = this.width +'x'+ this.height;

    removeImageEventListeners(this);
    this.parentNode.parentNode.style.visibility = '';

    numberAssets++;
}

function appendImage(url, title) {
    var asset = document.createElement('div');
    asset.classList.add('asset');
    asset.title = title;
    asset.style.visibility = 'hidden';

    var anchor = document.createElement('a');
    anchor.href = url;
    anchor.target = "_blank";
    anchor.rel = "nofollow";

    var image = new Image();
    image.title = title;
    image.addEventListener('load', onImageLoaded);
    image.addEventListener('error', onImageError);
    image.src = url;

    anchor.appendChild(image);
    asset.appendChild(anchor);

    var size = document.createElement('div');
    size.classList.add('size');
    size.innerText = '...';
    asset.appendChild(size);

    assetsDiv.appendChild(asset);
}

function insertAsset(asset) {
    assetsDiv.appendChild(asset);

    numberAssets++;
}

function displayAssets() {
    var filter = searchInput.value;
    var regExp = new RegExp(filter, 'i');

    var displayHiDPI = displayHiDPICheckbox.checked;

    window.location.hash = filter;

    numberAssets = 0;
    results = [];

    assetsDiv.innerText = '';

    var i = 0;
    for (var i = 0; i < assets.length; i++) {
        var title = assets[i][1];
        var url = assets[i][0].replace(/\\/g, '/');
        if (!displayHiDPI)  url = url.replace('default_200_percent', 'default_100_percent');

        if (filter !== searchInput.value) break; 
        if (results.indexOf(url) !== -1) continue;
        if (notFoundUrls.indexOf(url) !== -1) continue;
        if (!filter || regExp.test(url.substr(baseUrl.length))) {
            if (url.indexOf('.wav', url.length - '.wav'.length) !== -1) {
                appendAudio(url, title);
            } else {
                appendImage(url, title);
            }
            results.push(url);
        }
    }
}

var timeout;

function triggerSearch() {
    window.stop();
    clearTimeout(timeout);
    timeout = setTimeout(displayAssets, 300);
}

onload = function() {
    searchInput.value = decodeURI(window.location.hash.substr(1));

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/json');
    xhr.onload = function() {
        assets = JSON.parse(xhr.response);
        assets.sort(function(a, b) {
            if (a[1] < b[1]) return -1;
            if (a[1] > b[1]) return 1;
            if (a[0] < b[0]) return -1;
            if (a[0] > b[0]) return 1;
            return 0;
        });
        displayAssets();

        // Search is triggered each time user enters a new character
        searchInput.addEventListener('input', triggerSearch);

        // Search is also triggered when user toggles HiDPI checkbox
        displayHiDPICheckbox.addEventListener('change', triggerSearch);

        // Pressing / focus the search
        document.addEventListener('keyup', function(e) {
            if (e.keyCode === 191 && document.activeElement !== searchInput) {
                e.preventDefault();
                searchInput.focus();
            }
        });

        // Toggle Darkroom Mode
        document.querySelector('#toggleBackground').addEventListener('change', function() {
            document.body.classList.toggle('darkroom');
        });
    }
    xhr.send(null);
}

var baseUrl = 'https://src.chromium.org/svn/trunk/src/';
