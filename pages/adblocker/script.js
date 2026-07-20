var blockedDomains = [
  'google-analytics.com', 'googletagmanager.com', 'googlesyndication.com',
  'doubleclick.net', 'facebook.com/tr', 'analytics.twitter.com',
  'hotjar.com', 'mixpanel.com', 'segment.io', 'sentry.io'
];

function renderList() {
  var list = document.getElementById('domain-list');
  list.innerHTML = '';
  document.getElementById('domains').textContent = blockedDomains.length;
  blockedDomains.forEach(function(d) {
    var item = document.createElement('div');
    item.className = 'domain-item';
    item.innerHTML = '<span>' + d + '</span><button onclick="removeDomain(\'' + d + '\')">&times;</span>';
    list.appendChild(item);
  });
}

function removeDomain(d) {
  blockedDomains = blockedDomains.filter(function(x) { return x !== d; });
  renderList();
}

document.getElementById('add-btn').addEventListener('click', function() {
  var input = document.getElementById('new-domain');
  var val = input.value.trim();
  if (val && blockedDomains.indexOf(val) === -1) {
    blockedDomains.push(val);
    input.value = '';
    renderList();
  }
});

renderList();
